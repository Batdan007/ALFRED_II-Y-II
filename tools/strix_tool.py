"""
Strix Security Scanner Tool
AI-powered security testing for Alfred Tool Mode
"""

import logging
from typing import Dict, Any
from tools.base import Tool, ToolResult


class StrixTool(Tool):
    """
    Strix security scanner tool for AI-driven security testing

    Allows Alfred to perform security scans during conversations:
    - User: "Check my app for SQL injection vulnerabilities"
    - Alfred: [Uses strix_scan tool to analyze the target]
    """

    def __init__(self, privacy_controller=None, brain=None):
        """
        Initialize Strix tool

        Args:
            privacy_controller: PrivacyController for cloud access approval
            brain: AlfredBrain for storing scan results
        """
        self.logger = logging.getLogger(__name__)
        self.privacy_controller = privacy_controller
        self.brain = brain
        self.strix_available = False

        self._check_strix_availability()

    def _check_strix_availability(self):
        """Check if Strix scanner capability is available"""
        try:
            from capabilities.security.strix_scanner import StrixScanner
            scanner = StrixScanner(self.privacy_controller, self.brain)
            self.strix_available = scanner.strix_available
            if self.strix_available:
                self.logger.info("Strix tool initialized successfully")
            else:
                self.logger.debug("Strix not installed - tool will be unavailable")
        except Exception as e:
            self.logger.debug(f"Error initializing Strix tool: {e}")
            self.strix_available = False

    @property
    def name(self) -> str:
        return "strix_scan"

    @property
    def description(self) -> str:
        return (
            "Run AI-powered security scan on a target directory, file, URL, or GitHub repository. "
            "Detects vulnerabilities like SQL injection, XSS, SSRF, authentication bypasses, and more. "
            "Returns detailed findings with proof-of-concepts and remediation recommendations."
        )

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "target": {
                    "type": "string",
                    "description": (
                        "Target to scan. Can be:\n"
                        "- Local directory path (e.g., './my-app')\n"
                        "- Local file path (e.g., './src/api.py')\n"
                        "- URL (e.g., 'https://example.com')\n"
                        "- GitHub repository (e.g., 'https://github.com/org/repo')"
                    )
                },
                "scan_type": {
                    "type": "string",
                    "enum": ["quick", "full", "specific", "authenticated"],
                    "description": (
                        "Type of scan to perform:\n"
                        "- quick: Fast scan of common vulnerabilities (default)\n"
                        "- full: Comprehensive deep scan (takes longer)\n"
                        "- specific: Focused scan based on instructions\n"
                        "- authenticated: Scan with authentication"
                    ),
                    "default": "quick"
                },
                "instructions": {
                    "type": "string",
                    "description": (
                        "Optional custom instructions for the scan. Examples:\n"
                        "- 'Focus on API endpoints'\n"
                        "- 'Check for IDOR vulnerabilities'\n"
                        "- 'Test authentication flows'"
                    )
                },
                "credentials": {
                    "type": "string",
                    "description": (
                        "Credentials for authenticated testing (format: 'user:pass'). "
                        "Only used when scan_type is 'authenticated'."
                    )
                }
            },
            "required": ["target"]
        }

    def execute(
        self,
        target: str,
        scan_type: str = "quick",
        instructions: str = None,
        credentials: str = None
    ) -> ToolResult:
        """
        Execute Strix security scan

        Args:
            target: Path/URL/repo to scan
            scan_type: Type of scan to perform
            instructions: Optional custom instructions
            credentials: Optional credentials for authenticated testing

        Returns:
            ToolResult with scan findings or error
        """
        # Check if Strix is available
        if not self.strix_available:
            return ToolResult(
                success=False,
                output="",
                error=(
                    "Strix security scanner is not installed. "
                    "Install with: pipx install strix-agent"
                )
            )

        try:
            # Import scanner
            from capabilities.security.strix_scanner import StrixScanner, ScanType

            # Map scan type string to enum
            scan_type_map = {
                'quick': ScanType.QUICK,
                'full': ScanType.FULL,
                'specific': ScanType.SPECIFIC,
                'authenticated': ScanType.AUTHENTICATED
            }

            scan_type_enum = scan_type_map.get(scan_type.lower(), ScanType.QUICK)

            # Initialize scanner
            scanner = StrixScanner(
                privacy_controller=self.privacy_controller,
                brain=self.brain
            )

            # Run scan
            self.logger.info(f"Starting Strix scan: {target} ({scan_type})")

            authenticated = scan_type.lower() == 'authenticated'
            results = scanner.scan(
                target=target,
                scan_type=scan_type_enum,
                instructions=instructions,
                authenticated=authenticated,
                credentials=credentials
            )

            # Check if scan succeeded
            if not results['success']:
                return ToolResult(
                    success=False,
                    output="",
                    error=results.get('error', 'Scan failed')
                )

            # Format output for AI
            output = self._format_scan_output(results)

            # Return success
            return ToolResult(
                success=True,
                output=output,
                metadata={
                    'target': target,
                    'scan_type': scan_type,
                    'vulnerabilities_found': len(results.get('vulnerabilities', [])),
                    'severity_summary': results.get('severity_summary', {}),
                    'report_path': results.get('report_path', '')
                }
            )

        except Exception as e:
            self.logger.error(f"Error executing Strix scan: {e}")
            return ToolResult(
                success=False,
                output="",
                error=f"Scan execution error: {str(e)}"
            )

    def _format_scan_output(self, results: Dict[str, Any]) -> str:
        """
        Format scan results for AI consumption

        Args:
            results: Scan results dictionary

        Returns:
            Formatted output string
        """
        output_lines = []

        # Header
        output_lines.append(f"Security Scan Complete - Target: {results['target']}")
        output_lines.append("=" * 60)

        # Severity summary
        severity = results.get('severity_summary', {})
        output_lines.append("\nSeverity Summary:")
        output_lines.append(f"  Critical: {severity.get('critical', 0)}")
        output_lines.append(f"  High: {severity.get('high', 0)}")
        output_lines.append(f"  Medium: {severity.get('medium', 0)}")
        output_lines.append(f"  Low: {severity.get('low', 0)}")
        output_lines.append(f"  Info: {severity.get('info', 0)}")

        # Vulnerabilities
        vulnerabilities = results.get('vulnerabilities', [])
        if vulnerabilities:
            output_lines.append(f"\nFound {len(vulnerabilities)} vulnerabilities:")
            for i, vuln in enumerate(vulnerabilities[:10], 1):  # Show first 10
                output_lines.append(f"\n{i}. {vuln.get('title', 'Unnamed vulnerability')}")
                output_lines.append(f"   Severity: {vuln.get('severity', 'unknown').upper()}")
                if vuln.get('description'):
                    output_lines.append(f"   Description: {vuln['description']}")
                if vuln.get('recommendation'):
                    output_lines.append(f"   Recommendation: {vuln['recommendation']}")

            if len(vulnerabilities) > 10:
                output_lines.append(f"\n... and {len(vulnerabilities) - 10} more vulnerabilities")

        # Butler commentary
        commentary = results.get('butler_commentary', '')
        if commentary:
            output_lines.append(f"\n{commentary}")

        # Report path
        report_path = results.get('report_path', '')
        if report_path:
            output_lines.append(f"\nFull report available at: {report_path}")

        return "\n".join(output_lines)


# Graceful import check
def create_strix_tool(privacy_controller=None, brain=None) -> StrixTool:
    """
    Factory function to create Strix tool with graceful degradation

    Args:
        privacy_controller: PrivacyController instance
        brain: AlfredBrain instance

    Returns:
        StrixTool instance (may be unavailable if Strix not installed)
    """
    return StrixTool(privacy_controller, brain)
