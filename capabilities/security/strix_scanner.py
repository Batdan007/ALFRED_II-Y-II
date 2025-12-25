"""
Strix Security Scanner Integration for Alfred

This module provides a privacy-first wrapper around the Strix AI security scanner.
Strix is treated as an external dependency (like OpenAI/Claude) with no Alfred code exposed.

Author: Daniel J Rita (BATDAN)
License: Proprietary - Part of ALFRED-UBX
"""

import json
import logging
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from enum import Enum


class ScanType(Enum):
    """Types of security scans"""
    FULL = "full"
    QUICK = "quick"
    SPECIFIC = "specific"
    AUTHENTICATED = "authenticated"


class SeverityLevel(Enum):
    """Vulnerability severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class StrixScanner:
    """
    Alfred's wrapper for Strix AI security scanner

    Provides privacy-first security scanning with:
    - Graceful degradation if Strix not installed
    - Hybrid privacy checking (local Ollama = allowed, cloud = requires approval)
    - British butler commentary on findings
    - Integration with AlfredBrain for persistent memory
    """

    def __init__(self, privacy_controller=None, brain=None):
        """
        Initialize Strix scanner

        Args:
            privacy_controller: PrivacyController instance for cloud access approval
            brain: AlfredBrain instance for storing scan results
        """
        self.logger = logging.getLogger(__name__)
        self.privacy_controller = privacy_controller
        self.brain = brain
        self.strix_available = False
        self.enabled = True

        self._check_strix_availability()

    def _check_strix_availability(self):
        """Check if Strix is installed and available"""
        try:
            # Try to run strix --version
            result = subprocess.run(
                ['strix', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                self.strix_available = True
                self.logger.info("Strix security scanner detected and available")
            else:
                self.logger.debug("Strix command found but returned error")
        except FileNotFoundError:
            self.logger.debug("Strix not installed. Install with: pipx install strix-agent")
        except Exception as e:
            self.logger.debug(f"Error checking Strix availability: {e}")

    def _check_strix_llm_config(self) -> tuple[bool, Optional[str]]:
        """
        Check Strix's LLM configuration to determine if privacy approval needed

        Returns:
            (is_local, provider_name) - True if using local Ollama, False if cloud
        """
        strix_llm = os.getenv('STRIX_LLM', '')

        if not strix_llm:
            return (False, "unset - defaults to cloud")

        # Check if using local Ollama
        if strix_llm.lower().startswith('ollama/'):
            return (True, "Ollama (local)")

        # Detect cloud providers
        if strix_llm.lower().startswith('openai/'):
            return (False, "OpenAI")
        elif strix_llm.lower().startswith('anthropic/'):
            return (False, "Anthropic Claude")
        elif strix_llm.lower().startswith('groq/'):
            return (False, "Groq")
        else:
            return (False, strix_llm)

    def _request_privacy_approval(self, provider: str) -> bool:
        """
        Request privacy approval for cloud-based scanning

        Args:
            provider: Name of cloud provider (OpenAI, Claude, etc.)

        Returns:
            True if approved, False if denied
        """
        if not self.privacy_controller:
            # No privacy controller, default to deny for safety
            self.logger.warning("No privacy controller - denying cloud scan by default")
            return False

        # Map provider names to CloudProvider enum
        from core.privacy_controller import CloudProvider

        provider_map = {
            'openai': CloudProvider.OPENAI,
            'anthropic claude': CloudProvider.CLAUDE,
            'claude': CloudProvider.CLAUDE,
            'groq': CloudProvider.GROQ
        }

        provider_enum = provider_map.get(provider.lower())
        if not provider_enum:
            # Unknown provider, ask generically
            self.logger.warning(f"Unknown cloud provider: {provider}")
            return False

        return self.privacy_controller.request_cloud_access(
            provider_enum,
            f"Strix security scan using {provider}"
        )

    def scan(
        self,
        target: str,
        scan_type: ScanType = ScanType.QUICK,
        instructions: Optional[str] = None,
        authenticated: bool = False,
        credentials: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Run Strix security scan on target

        Args:
            target: Path to directory/file, URL, or GitHub repo
            scan_type: Type of scan to perform
            instructions: Custom instructions for Strix
            authenticated: Whether to perform authenticated testing
            credentials: Credentials for authenticated testing (format: "user:pass")

        Returns:
            Dictionary with scan results:
            {
                'success': bool,
                'target': str,
                'vulnerabilities': List[Dict],
                'severity_summary': Dict,
                'report_path': str,
                'butler_commentary': str,
                'error': Optional[str]
            }
        """
        # Check if Strix is available
        if not self.strix_available:
            return {
                'success': False,
                'target': target,
                'vulnerabilities': [],
                'severity_summary': {},
                'report_path': '',
                'butler_commentary': "I'm afraid Strix is not installed, sir. Install with: pipx install strix-agent",
                'error': 'Strix not available'
            }

        # Check LLM configuration and privacy
        is_local, provider = self._check_strix_llm_config()

        if not is_local:
            # Cloud provider detected, request approval
            approval = self._request_privacy_approval(provider)
            if not approval:
                return {
                    'success': False,
                    'target': target,
                    'vulnerabilities': [],
                    'severity_summary': {},
                    'report_path': '',
                    'butler_commentary': f"Privacy approval denied for {provider} scanning, sir. Set STRIX_LLM to use local Ollama.",
                    'error': 'Privacy approval denied'
                }

        # Build Strix command
        cmd = ['strix', '-n', '--target', target]  # -n = non-interactive mode

        if instructions:
            cmd.extend(['--instruction', instructions])

        if authenticated and credentials:
            auth_instruction = f"Perform authenticated testing using credentials: {credentials}"
            cmd.extend(['--instruction', auth_instruction])

        # Run Strix scan
        self.logger.info(f"Starting Strix scan on: {target}")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout for large scans
            )

            # Parse Strix output
            scan_results = self._parse_strix_output(result.stdout, result.stderr, target)

            # Add butler commentary
            scan_results['butler_commentary'] = self._generate_butler_commentary(scan_results)

            # Store in brain if available
            if self.brain:
                self._store_in_brain(scan_results)

            return scan_results

        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'target': target,
                'vulnerabilities': [],
                'severity_summary': {},
                'report_path': '',
                'butler_commentary': "The security scan has exceeded the time limit, sir. Consider scanning a smaller target.",
                'error': 'Scan timeout'
            }
        except Exception as e:
            self.logger.error(f"Error running Strix scan: {e}")
            return {
                'success': False,
                'target': target,
                'vulnerabilities': [],
                'severity_summary': {},
                'report_path': '',
                'butler_commentary': f"I encountered an error during the scan, sir: {str(e)}",
                'error': str(e)
            }

    def _parse_strix_output(self, stdout: str, stderr: str, target: str) -> Dict[str, Any]:
        """
        Parse Strix CLI output to extract vulnerabilities

        Args:
            stdout: Standard output from Strix
            stderr: Standard error from Strix
            target: Scan target

        Returns:
            Parsed scan results dictionary
        """
        vulnerabilities = []
        severity_counts = {
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0,
            'info': 0
        }

        # Strix outputs vulnerabilities in real-time during scan
        # Look for vulnerability patterns in output
        lines = stdout.split('\n')

        for line in lines:
            # Look for vulnerability indicators
            # (Strix format may vary - this is a basic parser)
            if 'vulnerability' in line.lower() or 'vuln' in line.lower():
                vuln = self._extract_vulnerability_from_line(line)
                if vuln:
                    vulnerabilities.append(vuln)
                    severity = vuln.get('severity', 'info').lower()
                    if severity in severity_counts:
                        severity_counts[severity] += 1

        # Look for report path in output
        report_path = ''
        for line in lines:
            if 'agent_runs/' in line or 'Results saved to' in line:
                # Extract path
                parts = line.split()
                for part in parts:
                    if 'agent_runs/' in part:
                        report_path = part
                        break

        success = len(vulnerabilities) >= 0  # Even 0 vulns is success
        has_criticals = severity_counts['critical'] > 0

        return {
            'success': success,
            'target': target,
            'vulnerabilities': vulnerabilities,
            'severity_summary': severity_counts,
            'report_path': report_path,
            'scan_date': datetime.now().isoformat(),
            'has_critical_findings': has_criticals
        }

    def _extract_vulnerability_from_line(self, line: str) -> Optional[Dict[str, Any]]:
        """
        Extract vulnerability details from a single output line

        Args:
            line: Line of output from Strix

        Returns:
            Vulnerability dictionary or None
        """
        # Basic extraction - can be enhanced based on actual Strix output format
        vuln = {
            'title': line.strip(),
            'severity': 'medium',  # Default
            'description': line.strip(),
            'proof_of_concept': '',
            'recommendation': ''
        }

        # Detect severity keywords
        line_lower = line.lower()
        if 'critical' in line_lower:
            vuln['severity'] = 'critical'
        elif 'high' in line_lower:
            vuln['severity'] = 'high'
        elif 'medium' in line_lower:
            vuln['severity'] = 'medium'
        elif 'low' in line_lower:
            vuln['severity'] = 'low'
        elif 'info' in line_lower:
            vuln['severity'] = 'info'

        return vuln

    def _generate_butler_commentary(self, scan_results: Dict[str, Any]) -> str:
        """
        Generate British butler commentary on scan results

        Args:
            scan_results: Parsed scan results

        Returns:
            Butler-style commentary string
        """
        if not scan_results['success']:
            return "The security assessment encountered difficulties, sir."

        severity = scan_results['severity_summary']
        total_vulns = sum(severity.values())

        if total_vulns == 0:
            return "Excellent news, sir. No vulnerabilities detected in the target. The application appears secure."

        # Count critical/high
        critical_count = severity.get('critical', 0)
        high_count = severity.get('high', 0)

        if critical_count > 0:
            return f"Most concerning, sir. I've discovered {critical_count} critical vulnerabilities that require immediate attention."
        elif high_count > 0:
            return f"Sir, I must inform you of {high_count} high-severity vulnerabilities. I recommend addressing these promptly."
        else:
            return f"Security assessment complete, sir. Found {total_vulns} potential issues of moderate concern."

    def _store_in_brain(self, scan_results: Dict[str, Any]):
        """
        Store scan results in AlfredBrain

        Args:
            scan_results: Parsed scan results to store
        """
        if not self.brain:
            return

        try:
            # Calculate importance based on severity
            severity = scan_results['severity_summary']
            critical = severity.get('critical', 0)
            high = severity.get('high', 0)

            if critical > 0:
                importance = 10  # Maximum importance
            elif high > 0:
                importance = 8
            elif severity.get('medium', 0) > 0:
                importance = 6
            else:
                importance = 4

            # Prepare findings JSON
            findings = {
                'vulnerabilities': scan_results['vulnerabilities'],
                'severity_summary': scan_results['severity_summary'],
                'scan_date': scan_results['scan_date']
            }

            # Prepare recommendations
            recommendations = [
                f"Review {len(scan_results['vulnerabilities'])} findings in detail",
                f"Check full report at: {scan_results['report_path']}"
            ]

            # Store in brain
            self.brain.store_security_scan(
                target=scan_results['target'],
                scan_type='strix',
                findings=findings,
                severity_summary=f"Critical: {critical}, High: {high}",
                recommendations=recommendations,
                authorized=True,  # User initiated scan
                notes=scan_results['butler_commentary']
            )

            self.logger.info(f"Stored scan results in brain (importance: {importance})")

        except Exception as e:
            self.logger.error(f"Error storing scan in brain: {e}")

    def get_status(self) -> Dict[str, Any]:
        """
        Get scanner status information

        Returns:
            Status dictionary with availability, LLM config, etc.
        """
        is_local, provider = self._check_strix_llm_config()

        return {
            'available': self.strix_available,
            'enabled': self.enabled,
            'llm_provider': provider,
            'is_local': is_local,
            'requires_privacy_approval': not is_local,
            'strix_llm_env': os.getenv('STRIX_LLM', 'not set')
        }


# Graceful import handling
STRIX_AVAILABLE = False
try:
    scanner = StrixScanner()
    STRIX_AVAILABLE = scanner.strix_available
except Exception as e:
    logging.getLogger(__name__).warning(f"Strix scanner initialization failed: {e}")
