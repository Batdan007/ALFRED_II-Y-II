#!/usr/bin/env python3
"""
Strix Security MCP Server

Exposes Strix AI-powered security testing framework to Claude Code.

Tools provided:
- scan_directory: Scan local directory for vulnerabilities
- scan_url: Scan web application URL
- scan_github_repo: Scan GitHub repository
- get_scan_results: Retrieve scan results by ID
- list_recent_scans: List recent security scans
- get_vulnerability_details: Get details on specific vulnerability
- retest_vulnerability: Retest a specific vulnerability
"""

import asyncio
import json
from typing import Any, Optional
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp import types
except ImportError:
    print("Error: MCP library not installed. Run: pip install mcp")
    sys.exit(1)

# Check if Strix is available
try:
    from capabilities.security.strix_scanner import StrixScanner
    STRIX_AVAILABLE = True
except ImportError:
    STRIX_AVAILABLE = False
    print("Warning: Strix not installed. Run: pipx install strix-agent")

from core.brain import AlfredBrain


class StrixMCPServer:
    """MCP Server for Strix Security Scanner"""

    def __init__(self):
        """Initialize Strix MCP Server"""
        self.server = Server("strix-security")
        self.brain = AlfredBrain()  # For storing scan results
        self.scanner = StrixScanner() if STRIX_AVAILABLE else None
        self._setup_handlers()

    def _setup_handlers(self):
        """Setup MCP request handlers"""

        @self.server.list_tools()
        async def list_tools() -> list[types.Tool]:
            """List all available tools"""
            if not STRIX_AVAILABLE:
                return []

            return [
                types.Tool(
                    name="strix_scan_directory",
                    description="Scan a local directory for security vulnerabilities",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "directory_path": {"type": "string", "description": "Path to directory to scan"},
                            "scan_depth": {
                                "type": "string",
                                "description": "Scan depth",
                                "enum": ["quick", "standard", "deep"],
                                "default": "standard"
                            },
                            "file_types": {
                                "type": "array",
                                "description": "File types to scan (e.g., ['py', 'js', 'php'])",
                                "items": {"type": "string"}
                            },
                        },
                        "required": ["directory_path"],
                    },
                ),
                types.Tool(
                    name="strix_scan_url",
                    description="Scan a web application URL for vulnerabilities",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "url": {"type": "string", "description": "Web application URL to scan"},
                            "scan_type": {
                                "type": "string",
                                "description": "Type of scan",
                                "enum": ["owasp-top-10", "full", "api", "authentication", "xss", "sqli", "custom"],
                                "default": "owasp-top-10"
                            },
                            "max_depth": {"type": "integer", "description": "Max crawl depth", "default": 3},
                            "include_authenticated": {"type": "boolean", "description": "Include authenticated scans", "default": False},
                        },
                        "required": ["url"],
                    },
                ),
                types.Tool(
                    name="strix_scan_github",
                    description="Scan a GitHub repository for security issues",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "repo_url": {"type": "string", "description": "GitHub repository URL"},
                            "branch": {"type": "string", "description": "Branch to scan", "default": "main"},
                            "scan_secrets": {"type": "boolean", "description": "Scan for leaked secrets", "default": True},
                            "scan_dependencies": {"type": "boolean", "description": "Scan dependencies", "default": True},
                        },
                        "required": ["repo_url"],
                    },
                ),
                types.Tool(
                    name="strix_get_scan_results",
                    description="Get results from a specific scan by ID",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "scan_id": {"type": "string", "description": "Scan ID"},
                            "severity_filter": {
                                "type": "string",
                                "description": "Filter by severity",
                                "enum": ["all", "critical", "high", "medium", "low", "info"],
                                "default": "all"
                            },
                        },
                        "required": ["scan_id"],
                    },
                ),
                types.Tool(
                    name="strix_list_scans",
                    description="List recent security scans",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "limit": {"type": "integer", "description": "Max scans to return", "default": 10},
                            "target_type": {
                                "type": "string",
                                "description": "Filter by target type",
                                "enum": ["all", "directory", "url", "github"],
                                "default": "all"
                            },
                        },
                    },
                ),
                types.Tool(
                    name="strix_get_vulnerability_details",
                    description="Get detailed information about a specific vulnerability",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "vulnerability_id": {"type": "string", "description": "Vulnerability ID"},
                            "include_remediation": {"type": "boolean", "description": "Include fix recommendations", "default": True},
                            "include_poc": {"type": "boolean", "description": "Include proof-of-concept", "default": True},
                        },
                        "required": ["vulnerability_id"],
                    },
                ),
                types.Tool(
                    name="strix_retest_vulnerability",
                    description="Retest a specific vulnerability to verify if it's been fixed",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "vulnerability_id": {"type": "string", "description": "Vulnerability ID to retest"},
                        },
                        "required": ["vulnerability_id"],
                    },
                ),
                types.Tool(
                    name="strix_get_vulnerability_trends",
                    description="Get vulnerability trends and statistics from brain storage",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "time_period_days": {"type": "integer", "description": "Days to analyze", "default": 30},
                        },
                    },
                ),
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> list[types.TextContent]:
            """Handle tool calls"""

            if not STRIX_AVAILABLE:
                return [types.TextContent(
                    type="text",
                    text="Strix not installed. Run: pipx install strix-agent"
                )]

            try:
                if name == "strix_scan_directory":
                    result = self.scanner.scan_directory(
                        directory=arguments["directory_path"],
                        depth=arguments.get("scan_depth", "standard"),
                        file_types=arguments.get("file_types")
                    )

                    # Store in brain
                    self.brain.store_security_scan(
                        target=arguments["directory_path"],
                        scan_type="directory",
                        results=result
                    )

                    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

                elif name == "strix_scan_url":
                    result = self.scanner.scan_url(
                        url=arguments["url"],
                        scan_type=arguments.get("scan_type", "owasp-top-10"),
                        max_depth=arguments.get("max_depth", 3),
                        authenticated=arguments.get("include_authenticated", False)
                    )

                    # Store in brain
                    self.brain.store_security_scan(
                        target=arguments["url"],
                        scan_type="url",
                        results=result
                    )

                    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

                elif name == "strix_scan_github":
                    result = self.scanner.scan_github(
                        repo_url=arguments["repo_url"],
                        branch=arguments.get("branch", "main"),
                        scan_secrets=arguments.get("scan_secrets", True),
                        scan_dependencies=arguments.get("scan_dependencies", True)
                    )

                    # Store in brain
                    self.brain.store_security_scan(
                        target=arguments["repo_url"],
                        scan_type="github",
                        results=result
                    )

                    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

                elif name == "strix_get_scan_results":
                    scan_id = arguments["scan_id"]
                    severity_filter = arguments.get("severity_filter", "all")

                    # Retrieve from brain
                    results = self.brain.get_security_scan(scan_id)

                    if severity_filter != "all" and results:
                        results["vulnerabilities"] = [
                            v for v in results.get("vulnerabilities", [])
                            if v.get("severity", "").lower() == severity_filter
                        ]

                    return [types.TextContent(type="text", text=json.dumps(results, indent=2))]

                elif name == "strix_list_scans":
                    limit = arguments.get("limit", 10)
                    target_type = arguments.get("target_type", "all")

                    scans = self.brain.get_security_scans(limit=limit, scan_type=target_type if target_type != "all" else None)

                    return [types.TextContent(type="text", text=json.dumps(scans, indent=2))]

                elif name == "strix_get_vulnerability_details":
                    vuln_id = arguments["vulnerability_id"]
                    include_remediation = arguments.get("include_remediation", True)
                    include_poc = arguments.get("include_poc", True)

                    details = self.scanner.get_vulnerability_details(
                        vuln_id,
                        include_remediation=include_remediation,
                        include_poc=include_poc
                    )

                    return [types.TextContent(type="text", text=json.dumps(details, indent=2))]

                elif name == "strix_retest_vulnerability":
                    vuln_id = arguments["vulnerability_id"]
                    result = self.scanner.retest_vulnerability(vuln_id)

                    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

                elif name == "strix_get_vulnerability_trends":
                    days = arguments.get("time_period_days", 30)
                    trends = self.brain.get_vulnerability_trends(days=days)

                    return [types.TextContent(type="text", text=json.dumps(trends, indent=2))]

                else:
                    return [types.TextContent(type="text", text=f"Unknown tool: {name}")]

            except Exception as e:
                return [types.TextContent(type="text", text=f"Error executing {name}: {str(e)}")]

    async def run(self):
        """Run the MCP server"""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


async def main():
    """Main entry point"""
    server = StrixMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
