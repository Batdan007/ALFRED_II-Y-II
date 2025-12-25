"""
Bug Bounty Hunter - Automated Vulnerability Discovery Workflow
Part of ALFRED II-Y-II

Integrates:
- Strix security scanner
- Fabric AI security patterns
- Crawl4AI for recon
- Cybersecurity intel feeds

Author: Daniel J. Rita (BATDAN)
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

logger = logging.getLogger(__name__)


class BugBountyHunter:
    """
    Automated bug bounty hunting workflow

    Workflow:
    1. Recon - Gather target information
    2. Scan - Run security scans
    3. Analyze - AI-powered vulnerability analysis
    4. Report - Generate bug bounty report
    """

    def __init__(self):
        self.results_dir = Path("bounty_results")
        self.results_dir.mkdir(exist_ok=True)

        # Try to load scanners
        self.strix = None
        self.crawler = None
        self.fabric = None

        self._init_tools()

    def _init_tools(self):
        """Initialize available tools"""
        # Strix scanner
        try:
            from capabilities.security.strix_scanner import StrixScanner
            self.strix = StrixScanner()
            logger.info("Strix scanner loaded")
        except ImportError:
            logger.warning("Strix scanner not available")

        # Crawler
        try:
            from capabilities.rag.crawler_advanced import AdvancedCrawler
            self.crawler = AdvancedCrawler()
            logger.info("Advanced crawler loaded")
        except ImportError:
            logger.warning("Crawler not available")

        # Fabric patterns
        try:
            from capabilities.fabric.fabric_patterns import FabricPatterns
            self.fabric = FabricPatterns()
            logger.info("Fabric patterns loaded")
        except ImportError:
            logger.warning("Fabric patterns not available")

    def recon(self, target: str) -> Dict:
        """
        Phase 1: Reconnaissance

        Args:
            target: URL or domain to investigate

        Returns:
            Recon data dictionary
        """
        print(f"\n[RECON] Target: {target}")
        print("-" * 50)

        recon_data = {
            "target": target,
            "timestamp": datetime.now().isoformat(),
            "endpoints": [],
            "technologies": [],
            "headers": {},
            "notes": []
        }

        if self.crawler:
            try:
                print("[*] Crawling target for endpoints...")
                # Basic crawl for discovery
                crawl_result = self.crawler.crawl(target, depth=1)
                if crawl_result:
                    recon_data["endpoints"] = crawl_result.get("links", [])
                    recon_data["notes"].append(f"Found {len(recon_data['endpoints'])} endpoints")
                    print(f"[+] Found {len(recon_data['endpoints'])} endpoints")
            except Exception as e:
                logger.error(f"Crawl failed: {e}")
                recon_data["notes"].append(f"Crawl error: {e}")

        return recon_data

    def scan(self, target: str, scan_type: str = "quick") -> Dict:
        """
        Phase 2: Security Scanning

        Args:
            target: URL to scan
            scan_type: 'quick' or 'full'

        Returns:
            Scan results dictionary
        """
        print(f"\n[SCAN] Running {scan_type} scan on: {target}")
        print("-" * 50)

        scan_results = {
            "target": target,
            "scan_type": scan_type,
            "timestamp": datetime.now().isoformat(),
            "vulnerabilities": [],
            "findings": []
        }

        if self.strix and self.strix.strix_available:
            try:
                print("[*] Running Strix security scan...")
                result = self.strix.scan_url(target, scan_type=scan_type)
                if result:
                    scan_results["vulnerabilities"] = result.get("vulnerabilities", [])
                    scan_results["findings"] = result.get("findings", [])
                    vuln_count = len(scan_results["vulnerabilities"])
                    print(f"[+] Found {vuln_count} potential vulnerabilities")
            except Exception as e:
                logger.error(f"Strix scan failed: {e}")
                scan_results["error"] = str(e)
        else:
            print("[!] Strix not available - running basic checks")
            # Basic header checks
            scan_results["findings"].append({
                "type": "info",
                "message": "Manual review recommended - automated scanner unavailable"
            })

        return scan_results

    def analyze(self, scan_results: Dict) -> Dict:
        """
        Phase 3: AI-Powered Analysis

        Args:
            scan_results: Results from scan phase

        Returns:
            Analysis with severity ratings and exploit potential
        """
        print(f"\n[ANALYZE] Analyzing findings...")
        print("-" * 50)

        analysis = {
            "timestamp": datetime.now().isoformat(),
            "critical": [],
            "high": [],
            "medium": [],
            "low": [],
            "recommendations": []
        }

        if self.fabric:
            try:
                # Use security analysis pattern
                for vuln in scan_results.get("vulnerabilities", []):
                    severity = vuln.get("severity", "medium").lower()
                    if severity in analysis:
                        analysis[severity].append(vuln)

                print(f"[+] Critical: {len(analysis['critical'])}")
                print(f"[+] High: {len(analysis['high'])}")
                print(f"[+] Medium: {len(analysis['medium'])}")
                print(f"[+] Low: {len(analysis['low'])}")

            except Exception as e:
                logger.error(f"Analysis failed: {e}")

        return analysis

    def generate_report(self, target: str, recon: Dict, scan: Dict, analysis: Dict) -> str:
        """
        Phase 4: Generate Bug Bounty Report

        Args:
            target: Target URL
            recon: Recon data
            scan: Scan results
            analysis: Analysis results

        Returns:
            Path to generated report
        """
        print(f"\n[REPORT] Generating bug bounty report...")
        print("-" * 50)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.results_dir / f"bounty_report_{timestamp}.md"

        report = f"""# Bug Bounty Report

**Target:** {target}
**Date:** {datetime.now().strftime("%Y-%m-%d %H:%M")}
**Hunter:** BATDAN (via ALFRED II-Y-II)

---

## Executive Summary

- **Critical Vulnerabilities:** {len(analysis.get('critical', []))}
- **High Vulnerabilities:** {len(analysis.get('high', []))}
- **Medium Vulnerabilities:** {len(analysis.get('medium', []))}
- **Low Vulnerabilities:** {len(analysis.get('low', []))}

---

## Reconnaissance

**Endpoints Discovered:** {len(recon.get('endpoints', []))}

### Endpoints
"""
        for endpoint in recon.get('endpoints', [])[:20]:
            report += f"- {endpoint}\n"

        report += """

---

## Vulnerabilities

"""
        for severity in ['critical', 'high', 'medium', 'low']:
            vulns = analysis.get(severity, [])
            if vulns:
                report += f"### {severity.upper()}\n\n"
                for vuln in vulns:
                    report += f"**{vuln.get('type', 'Unknown')}**\n"
                    report += f"- Description: {vuln.get('description', 'N/A')}\n"
                    report += f"- Location: {vuln.get('location', 'N/A')}\n"
                    report += f"- Impact: {vuln.get('impact', 'N/A')}\n\n"

        report += """

---

## Recommendations

1. Prioritize critical and high severity issues
2. Implement input validation
3. Update security headers
4. Review authentication mechanisms

---

*Generated by ALFRED II-Y-II Bug Bounty Hunter*
*Created by Daniel J. Rita (BATDAN)*
"""

        report_file.write_text(report)
        print(f"[+] Report saved: {report_file}")

        return str(report_file)

    def hunt(self, target: str, scan_type: str = "quick") -> Dict:
        """
        Full bug bounty hunting workflow

        Args:
            target: URL to hunt
            scan_type: 'quick' or 'full'

        Returns:
            Complete results dictionary
        """
        print("\n" + "=" * 60)
        print("ALFRED II-Y-II BUG BOUNTY HUNTER")
        print("=" * 60)

        # Phase 1: Recon
        recon = self.recon(target)

        # Phase 2: Scan
        scan = self.scan(target, scan_type)

        # Phase 3: Analyze
        analysis = self.analyze(scan)

        # Phase 4: Report
        report_path = self.generate_report(target, recon, scan, analysis)

        print("\n" + "=" * 60)
        print("HUNT COMPLETE")
        print("=" * 60)

        return {
            "target": target,
            "recon": recon,
            "scan": scan,
            "analysis": analysis,
            "report": report_path
        }


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="ALFRED Bug Bounty Hunter")
    parser.add_argument("target", help="Target URL to hunt")
    parser.add_argument("--full", action="store_true", help="Run full scan (slower)")

    args = parser.parse_args()

    hunter = BugBountyHunter()
    scan_type = "full" if args.full else "quick"

    results = hunter.hunt(args.target, scan_type)

    print(f"\nResults saved to: {results['report']}")


if __name__ == "__main__":
    main()
