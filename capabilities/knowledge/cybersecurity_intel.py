"""
Cybersecurity Intelligence Module
Real-time threat intelligence, CVE tracking, and security awareness

Sources:
- NVD (National Vulnerability Database) - CVE lookups
- CISA (Cybersecurity & Infrastructure Security Agency) - Alerts & advisories
- MITRE ATT&CK - Threat tactics and techniques
- Exploit-DB references
- Security news aggregation

Author: Daniel J Rita (BATDAN)
For: ALFRED_J_RITA - State of the Art Cybersecurity Intelligence
"""

import os
import re
import logging
import requests
from typing import Optional, Dict, List, Tuple
from datetime import datetime, timedelta
import json


class CybersecurityIntel:
    """
    Real-time cybersecurity intelligence for ALFRED

    Capabilities:
    - CVE lookup and analysis
    - CISA security alerts
    - Threat actor tracking
    - Vulnerability severity assessment
    - Exploit availability checking
    - Security news aggregation
    - MITRE ATT&CK mapping
    """

    # CVSS Severity levels
    SEVERITY_LEVELS = {
        'CRITICAL': (9.0, 10.0, '[CRIT]'),
        'HIGH': (7.0, 8.9, '[HIGH]'),
        'MEDIUM': (4.0, 6.9, '[MED]'),
        'LOW': (0.1, 3.9, '[LOW]'),
        'NONE': (0.0, 0.0, '[NONE]')
    }

    # Common threat actor groups (for detection)
    THREAT_ACTORS = [
        'apt28', 'apt29', 'apt41', 'lazarus', 'cozy bear', 'fancy bear',
        'sandworm', 'turla', 'carbanak', 'fin7', 'revil', 'darkside',
        'conti', 'lockbit', 'blackcat', 'alphv', 'scattered spider',
        'lapsus', 'killnet', 'anonymous sudan', 'volt typhoon', 'salt typhoon'
    ]

    # Vulnerability types
    VULN_TYPES = {
        'rce': 'Remote Code Execution',
        'sqli': 'SQL Injection',
        'xss': 'Cross-Site Scripting',
        'csrf': 'Cross-Site Request Forgery',
        'ssrf': 'Server-Side Request Forgery',
        'lfi': 'Local File Inclusion',
        'rfi': 'Remote File Inclusion',
        'xxe': 'XML External Entity',
        'idor': 'Insecure Direct Object Reference',
        'deserialization': 'Insecure Deserialization',
        'buffer overflow': 'Buffer Overflow',
        'privilege escalation': 'Privilege Escalation',
        'authentication bypass': 'Authentication Bypass',
        'zero-day': 'Zero-Day Vulnerability',
        '0day': 'Zero-Day Vulnerability',
    }

    def __init__(self, nvd_api_key: Optional[str] = None):
        """
        Initialize cybersecurity intelligence

        Args:
            nvd_api_key: NVD API key (optional, increases rate limits)
        """
        self.logger = logging.getLogger(__name__)
        self.nvd_api_key = nvd_api_key or os.getenv('NVD_API_KEY')

        # API endpoints
        self.nvd_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
        self.cisa_url = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
        self.cisa_alerts_url = "https://www.cisa.gov/sites/default/files/feeds/alerts/cisa_alerts.json"

        # Cache for expensive lookups
        self._cisa_kev_cache = None
        self._cisa_kev_timestamp = None

    def is_available(self) -> bool:
        """Always available (NVD is public)"""
        return True

    def is_security_query(self, text: str) -> bool:
        """
        Detect if text is asking about cybersecurity

        Args:
            text: User message

        Returns:
            True if security-related query
        """
        security_keywords = [
            'cve', 'vulnerability', 'vulnerabilities', 'exploit', 'hack',
            'breach', 'malware', 'ransomware', 'threat', 'attack',
            'security', 'cybersecurity', 'cyber', 'patch', 'zero-day',
            '0day', 'apt', 'phishing', 'backdoor', 'trojan', 'botnet',
            'ddos', 'dos', 'injection', 'xss', 'csrf', 'rce',
            'privilege escalation', 'data breach', 'compromised',
            'indicators of compromise', 'ioc', 'ttps', 'mitre',
            'att&ck', 'pentest', 'penetration', 'red team', 'blue team'
        ]

        text_lower = text.lower()
        return any(kw in text_lower for kw in security_keywords)

    def extract_cve_ids(self, text: str) -> List[str]:
        """
        Extract CVE IDs from text

        Args:
            text: User message

        Returns:
            List of CVE IDs found
        """
        # Pattern: CVE-YYYY-NNNNN (4 digit year, 4-7 digit ID)
        pattern = r'CVE-\d{4}-\d{4,7}'
        matches = re.findall(pattern, text.upper())
        return list(set(matches))

    def get_cve_details(self, cve_id: str) -> Optional[Dict]:
        """
        Get detailed CVE information from NVD

        Args:
            cve_id: CVE identifier (e.g., CVE-2024-1234)

        Returns:
            CVE details or None
        """
        try:
            headers = {}
            if self.nvd_api_key:
                headers['apiKey'] = self.nvd_api_key

            params = {'cveId': cve_id.upper()}
            response = requests.get(self.nvd_url, params=params, headers=headers, timeout=15)

            if response.status_code == 200:
                data = response.json()
                if data.get('vulnerabilities'):
                    vuln = data['vulnerabilities'][0]['cve']

                    # Extract CVSS score
                    cvss_score = None
                    cvss_vector = None
                    severity = 'UNKNOWN'

                    # Try CVSS 3.1 first, then 3.0, then 2.0
                    metrics = vuln.get('metrics', {})
                    if metrics.get('cvssMetricV31'):
                        cvss_data = metrics['cvssMetricV31'][0]['cvssData']
                        cvss_score = cvss_data.get('baseScore')
                        cvss_vector = cvss_data.get('vectorString')
                        severity = cvss_data.get('baseSeverity', 'UNKNOWN')
                    elif metrics.get('cvssMetricV30'):
                        cvss_data = metrics['cvssMetricV30'][0]['cvssData']
                        cvss_score = cvss_data.get('baseScore')
                        cvss_vector = cvss_data.get('vectorString')
                        severity = cvss_data.get('baseSeverity', 'UNKNOWN')
                    elif metrics.get('cvssMetricV2'):
                        cvss_data = metrics['cvssMetricV2'][0]['cvssData']
                        cvss_score = cvss_data.get('baseScore')
                        cvss_vector = cvss_data.get('vectorString')

                    # Get description
                    descriptions = vuln.get('descriptions', [])
                    description = next(
                        (d['value'] for d in descriptions if d['lang'] == 'en'),
                        'No description available'
                    )

                    # Get affected products (CPE)
                    affected = []
                    for config in vuln.get('configurations', []):
                        for node in config.get('nodes', []):
                            for cpe in node.get('cpeMatch', []):
                                if cpe.get('vulnerable'):
                                    affected.append(cpe.get('criteria', ''))

                    # Get references
                    references = [
                        {'url': ref.get('url'), 'source': ref.get('source')}
                        for ref in vuln.get('references', [])[:5]
                    ]

                    return {
                        'id': cve_id.upper(),
                        'description': description,
                        'cvss_score': cvss_score,
                        'cvss_vector': cvss_vector,
                        'severity': severity,
                        'published': vuln.get('published', ''),
                        'modified': vuln.get('lastModified', ''),
                        'affected_products': affected[:10],
                        'references': references,
                        'weaknesses': [
                            w.get('description', [{}])[0].get('value', '')
                            for w in vuln.get('weaknesses', [])
                        ]
                    }

            return None

        except Exception as e:
            self.logger.error(f"CVE lookup failed for {cve_id}: {e}")
            return None

    def search_cves(self, keyword: str, days: int = 30, limit: int = 10) -> List[Dict]:
        """
        Search for recent CVEs by keyword

        Args:
            keyword: Search term (product, vendor, etc.)
            days: Look back period
            limit: Max results

        Returns:
            List of matching CVEs
        """
        try:
            headers = {}
            if self.nvd_api_key:
                headers['apiKey'] = self.nvd_api_key

            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            params = {
                'keywordSearch': keyword,
                'pubStartDate': start_date.strftime('%Y-%m-%dT00:00:00.000'),
                'pubEndDate': end_date.strftime('%Y-%m-%dT23:59:59.999'),
                'resultsPerPage': limit
            }

            response = requests.get(self.nvd_url, params=params, headers=headers, timeout=20)

            if response.status_code == 200:
                data = response.json()
                results = []

                for vuln_item in data.get('vulnerabilities', []):
                    vuln = vuln_item['cve']

                    # Get CVSS score
                    cvss_score = None
                    severity = 'UNKNOWN'
                    metrics = vuln.get('metrics', {})

                    if metrics.get('cvssMetricV31'):
                        cvss_score = metrics['cvssMetricV31'][0]['cvssData'].get('baseScore')
                        severity = metrics['cvssMetricV31'][0]['cvssData'].get('baseSeverity')
                    elif metrics.get('cvssMetricV30'):
                        cvss_score = metrics['cvssMetricV30'][0]['cvssData'].get('baseScore')
                        severity = metrics['cvssMetricV30'][0]['cvssData'].get('baseSeverity')

                    descriptions = vuln.get('descriptions', [])
                    description = next(
                        (d['value'] for d in descriptions if d['lang'] == 'en'),
                        'No description'
                    )

                    results.append({
                        'id': vuln.get('id'),
                        'description': description[:300],
                        'cvss_score': cvss_score,
                        'severity': severity,
                        'published': vuln.get('published', '')[:10]
                    })

                return results

            return []

        except Exception as e:
            self.logger.error(f"CVE search failed: {e}")
            return []

    def get_cisa_kev(self) -> List[Dict]:
        """
        Get CISA Known Exploited Vulnerabilities catalog

        Returns:
            List of actively exploited CVEs
        """
        # Use cache if fresh (1 hour)
        if self._cisa_kev_cache and self._cisa_kev_timestamp:
            if datetime.now() - self._cisa_kev_timestamp < timedelta(hours=1):
                return self._cisa_kev_cache

        try:
            response = requests.get(self.cisa_url, timeout=15)

            if response.status_code == 200:
                data = response.json()
                vulnerabilities = data.get('vulnerabilities', [])

                # Cache results
                self._cisa_kev_cache = vulnerabilities
                self._cisa_kev_timestamp = datetime.now()

                return vulnerabilities

            return []

        except Exception as e:
            self.logger.error(f"CISA KEV fetch failed: {e}")
            return []

    def get_recent_critical_cves(self, days: int = 7, min_severity: float = 7.0) -> List[Dict]:
        """
        Get recent critical/high severity CVEs

        Args:
            days: Look back period
            min_severity: Minimum CVSS score

        Returns:
            List of critical CVEs
        """
        try:
            headers = {}
            if self.nvd_api_key:
                headers['apiKey'] = self.nvd_api_key

            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            params = {
                'pubStartDate': start_date.strftime('%Y-%m-%dT00:00:00.000'),
                'pubEndDate': end_date.strftime('%Y-%m-%dT23:59:59.999'),
                'cvssV3Severity': 'CRITICAL' if min_severity >= 9.0 else 'HIGH',
                'resultsPerPage': 20
            }

            response = requests.get(self.nvd_url, params=params, headers=headers, timeout=20)

            if response.status_code == 200:
                data = response.json()
                results = []

                for vuln_item in data.get('vulnerabilities', []):
                    vuln = vuln_item['cve']
                    metrics = vuln.get('metrics', {})

                    cvss_score = None
                    if metrics.get('cvssMetricV31'):
                        cvss_score = metrics['cvssMetricV31'][0]['cvssData'].get('baseScore')
                    elif metrics.get('cvssMetricV30'):
                        cvss_score = metrics['cvssMetricV30'][0]['cvssData'].get('baseScore')

                    if cvss_score and cvss_score >= min_severity:
                        descriptions = vuln.get('descriptions', [])
                        description = next(
                            (d['value'] for d in descriptions if d['lang'] == 'en'),
                            'No description'
                        )

                        results.append({
                            'id': vuln.get('id'),
                            'description': description[:200],
                            'cvss_score': cvss_score,
                            'published': vuln.get('published', '')[:10]
                        })

                return sorted(results, key=lambda x: x.get('cvss_score', 0), reverse=True)

            return []

        except Exception as e:
            self.logger.error(f"Critical CVE fetch failed: {e}")
            return []

    def check_if_exploited(self, cve_id: str) -> Dict:
        """
        Check if a CVE is known to be actively exploited

        Args:
            cve_id: CVE identifier

        Returns:
            Exploitation status info
        """
        kev_list = self.get_cisa_kev()
        cve_upper = cve_id.upper()

        for vuln in kev_list:
            if vuln.get('cveID') == cve_upper:
                return {
                    'exploited': True,
                    'date_added': vuln.get('dateAdded'),
                    'due_date': vuln.get('dueDate'),
                    'ransomware_use': vuln.get('knownRansomwareCampaignUse'),
                    'required_action': vuln.get('requiredAction'),
                    'notes': vuln.get('notes')
                }

        return {'exploited': False}

    def format_cve(self, cve: Dict) -> str:
        """
        Format CVE for display

        Args:
            cve: CVE data dict

        Returns:
            Formatted string
        """
        severity = cve.get('severity', 'UNKNOWN')
        severity_tag = '[CRIT]' if severity == 'CRITICAL' else '[HIGH]' if severity == 'HIGH' else '[MED]' if severity == 'MEDIUM' else '[LOW]'

        lines = [
            f"{severity_tag} {cve['id']} - {severity} (CVSS {cve.get('cvss_score', 'N/A')})",
            f"   {cve.get('description', 'No description')[:200]}..."
        ]

        if cve.get('published'):
            lines.append(f"   Published: {cve['published'][:10]}")

        return "\n".join(lines)

    def get_threat_brief(self) -> Dict:
        """
        Get current threat landscape briefing

        Returns:
            Threat intelligence summary
        """
        brief = {
            'timestamp': datetime.now().isoformat(),
            'critical_cves': [],
            'actively_exploited': [],
            'total_kev_count': 0
        }

        # Get recent critical CVEs
        critical = self.get_recent_critical_cves(days=7, min_severity=9.0)
        brief['critical_cves'] = critical[:5]

        # Get CISA KEV stats
        kev = self.get_cisa_kev()
        brief['total_kev_count'] = len(kev)

        # Get most recent additions to KEV
        recent_kev = sorted(kev, key=lambda x: x.get('dateAdded', ''), reverse=True)[:5]
        brief['actively_exploited'] = [
            {
                'id': v.get('cveID'),
                'vendor': v.get('vendorProject'),
                'product': v.get('product'),
                'name': v.get('vulnerabilityName'),
                'date_added': v.get('dateAdded')
            }
            for v in recent_kev
        ]

        return brief

    def lookup_for_prompt(self, text: str) -> Tuple[bool, str]:
        """
        Main entry point for security queries

        Args:
            text: User message

        Returns:
            Tuple of (was_security_query, context_to_inject)
        """
        if not self.is_security_query(text):
            return False, ""

        self.logger.info("Security query detected")
        context_parts = []

        # Check for specific CVE IDs
        cve_ids = self.extract_cve_ids(text)
        if cve_ids:
            context_parts.append(f"[CVE INTELLIGENCE - Retrieved {datetime.now().strftime('%Y-%m-%d %H:%M')}]")
            for cve_id in cve_ids[:3]:  # Limit to 3 CVEs
                cve_data = self.get_cve_details(cve_id)
                if cve_data:
                    context_parts.append(self.format_cve(cve_data))

                    # Check exploitation status
                    exploit_status = self.check_if_exploited(cve_id)
                    if exploit_status['exploited']:
                        context_parts.append(f"   [!] ACTIVELY EXPLOITED - Added to CISA KEV: {exploit_status['date_added']}")
                        if exploit_status.get('ransomware_use') == 'Known':
                            context_parts.append("   [RANSOMWARE] Known use in ransomware campaigns")

        # Check for general threat queries
        threat_keywords = ['threat', 'critical', 'vulnerability', 'vulnerabilities', 'latest', 'recent', 'new']
        if any(kw in text.lower() for kw in threat_keywords) and not cve_ids:
            brief = self.get_threat_brief()
            context_parts.append(f"\n[THREAT LANDSCAPE BRIEF - {datetime.now().strftime('%Y-%m-%d')}]")
            context_parts.append(f"CISA Known Exploited Vulnerabilities: {brief['total_kev_count']} total")

            if brief['critical_cves']:
                context_parts.append("\nRecent Critical CVEs (CVSS 9.0+):")
                for cve in brief['critical_cves'][:3]:
                    context_parts.append(f"  • {cve['id']} (CVSS {cve['cvss_score']}): {cve['description'][:100]}...")

            if brief['actively_exploited']:
                context_parts.append("\nRecently Added to Exploitation Catalog:")
                for v in brief['actively_exploited'][:3]:
                    context_parts.append(f"  • {v['id']}: {v['vendor']} {v['product']} - {v['name']}")

        # Check for product-specific vulnerability search
        products = ['windows', 'linux', 'chrome', 'firefox', 'apache', 'nginx',
                   'wordpress', 'drupal', 'cisco', 'fortinet', 'palo alto',
                   'vmware', 'citrix', 'microsoft', 'adobe', 'oracle', 'sap']

        for product in products:
            if product in text.lower():
                search_results = self.search_cves(product, days=30, limit=5)
                if search_results:
                    context_parts.append(f"\nRecent {product.title()} Vulnerabilities:")
                    for cve in search_results[:3]:
                        context_parts.append(f"  • {cve['id']} ({cve.get('severity', 'N/A')}): {cve['description'][:80]}...")
                break

        if not context_parts:
            return False, ""

        context_parts.append("\n[Use this security intelligence to provide an informed response]")
        return True, "\n".join(context_parts)


# Convenience function
def create_cybersecurity_intel(nvd_api_key: Optional[str] = None) -> CybersecurityIntel:
    """Create cybersecurity intelligence instance"""
    return CybersecurityIntel(nvd_api_key=nvd_api_key)
