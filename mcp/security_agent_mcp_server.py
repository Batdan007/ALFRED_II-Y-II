"""
ALFRED Security Agent MCP Server

Exposes the ALFRED Security Agent capabilities via the Model Context Protocol (MCP),
allowing Claude Code and other MCP clients to invoke autonomous security scans.

Tools Provided:
- security_scan: Run autonomous security scan on a target
- security_quick_scan: Quick scan without full ReAct loop
- security_status: Get security agent status
- security_get_findings: Get findings from recent scans
- security_analyze_code: Analyze code snippet for vulnerabilities

Author: Daniel J Rita (BATDAN)
License: Proprietary - Part of ALFRED-UBX
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Any, Optional
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import (
        TextContent,
        Tool,
        CallToolResult,
    )
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("MCP not available. Install with: pip install mcp", file=sys.stderr)

from agents.security_agent import AlfredSecurityAgent, quick_security_scan
from core.brain import AlfredBrain


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global instances
brain: Optional[AlfredBrain] = None
security_agent: Optional[AlfredSecurityAgent] = None


def get_brain() -> AlfredBrain:
    """Get or create AlfredBrain instance"""
    global brain
    if brain is None:
        brain = AlfredBrain()
    return brain


def get_security_agent() -> AlfredSecurityAgent:
    """Get or create Security Agent instance"""
    global security_agent
    if security_agent is None:
        security_agent = AlfredSecurityAgent(brain=get_brain())
    return security_agent


if MCP_AVAILABLE:
    # Create MCP server
    server = Server("alfred-security-agent")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List available security tools"""
        return [
            Tool(
                name="security_scan",
                description="""Run an autonomous security scan on a target using the ALFRED Security Agent.

The agent uses the ReAct (Reasoning + Acting) pattern to:
1. Analyze the target type (URL, path, GitHub repo)
2. Execute appropriate security scans (Strix, code analysis)
3. Analyze findings with Fabric AI patterns
4. Generate recommendations
5. Store results in Alfred Brain

Supports:
- Web application scanning (URLs)
- Code repository scanning (GitHub repos)
- Local directory/file scanning (paths)""",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "target": {
                            "type": "string",
                            "description": "Target to scan: URL, GitHub repo URL, or local path"
                        },
                        "task_description": {
                            "type": "string",
                            "description": "Optional description of what to look for",
                            "default": "Perform comprehensive security assessment"
                        }
                    },
                    "required": ["target"]
                }
            ),
            Tool(
                name="security_quick_scan",
                description="""Run a quick security scan without the full ReAct loop.

Faster but less thorough than security_scan. Good for:
- Quick vulnerability checks
- Pre-commit scanning
- Initial assessment before full scan""",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "target": {
                            "type": "string",
                            "description": "Target to scan: URL, GitHub repo URL, or local path"
                        }
                    },
                    "required": ["target"]
                }
            ),
            Tool(
                name="security_status",
                description="Get the current status of the ALFRED Security Agent",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
            Tool(
                name="security_get_findings",
                description="""Get security findings from Alfred Brain.

Retrieves stored security findings from previous scans.
Can filter by severity level.""",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "severity": {
                            "type": "string",
                            "description": "Filter by severity: critical, high, medium, low, or all",
                            "enum": ["critical", "high", "medium", "low", "all"],
                            "default": "all"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of findings to return",
                            "default": 10
                        }
                    },
                    "required": []
                }
            ),
            Tool(
                name="security_analyze_code",
                description="""Analyze a code snippet for security vulnerabilities.

Scans provided code for common security issues:
- SQL Injection
- Command Injection
- XSS vulnerabilities
- Hardcoded secrets
- Path traversal
- Insecure functions""",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "Code snippet to analyze"
                        },
                        "language": {
                            "type": "string",
                            "description": "Programming language",
                            "enum": ["python", "javascript", "typescript", "java", "go", "rust", "auto"],
                            "default": "auto"
                        }
                    },
                    "required": ["code"]
                }
            ),
            Tool(
                name="security_get_recommendations",
                description="""Get security recommendations based on scan history.

Analyzes past scans to provide:
- Most common vulnerability types
- Priority remediation list
- Trend analysis""",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            )
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        """Handle tool calls"""
        try:
            if name == "security_scan":
                result = await handle_security_scan(
                    arguments["target"],
                    arguments.get("task_description", "Perform comprehensive security assessment")
                )
            elif name == "security_quick_scan":
                result = await handle_quick_scan(arguments["target"])
            elif name == "security_status":
                result = handle_status()
            elif name == "security_get_findings":
                result = handle_get_findings(
                    arguments.get("severity", "all"),
                    arguments.get("limit", 10)
                )
            elif name == "security_analyze_code":
                result = handle_analyze_code(
                    arguments["code"],
                    arguments.get("language", "auto")
                )
            elif name == "security_get_recommendations":
                result = handle_get_recommendations()
            else:
                result = {"error": f"Unknown tool: {name}"}

            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2, default=str)
            )]

        except Exception as e:
            logger.error(f"Error in {name}: {e}")
            return [TextContent(
                type="text",
                text=json.dumps({"error": str(e)})
            )]


async def handle_security_scan(target: str, task_description: str) -> dict:
    """Handle full security scan"""
    agent = get_security_agent()

    logger.info(f"Starting security scan on: {target}")

    result = await agent.execute(task_description, target)

    return {
        "success": result.get("success", False),
        "target": target,
        "findings_count": result.get("findings_count", 0),
        "severity_summary": result.get("severity_summary", {}),
        "iterations": result.get("iterations", 0),
        "duration_seconds": result.get("duration_seconds", 0),
        "findings": result.get("findings", []),
        "thought_chain": result.get("thought_chain", []),
        "butler_commentary": _generate_butler_commentary(result)
    }


async def handle_quick_scan(target: str) -> dict:
    """Handle quick scan"""
    logger.info(f"Starting quick scan on: {target}")

    result = await quick_security_scan(target)

    return {
        "success": result.get("success", False),
        "target": target,
        "findings_count": result.get("findings_count", 0),
        "severity_summary": result.get("severity_summary", {}),
        "findings": result.get("findings", [])[:5],  # Limit to top 5
        "butler_commentary": _generate_butler_commentary(result)
    }


def handle_status() -> dict:
    """Handle status request"""
    agent = get_security_agent()
    status = agent.get_status()

    return {
        "agent_status": status,
        "brain_connected": brain is not None,
        "available_capabilities": [
            "directory_scanning",
            "url_scanning",
            "github_scanning",
            "code_analysis",
            "fabric_patterns"
        ],
        "last_check": datetime.now().isoformat()
    }


def handle_get_findings(severity: str, limit: int) -> dict:
    """Handle get findings request"""
    brain = get_brain()

    try:
        # Search for security findings in brain
        all_findings = []

        # Get from security_findings category
        findings_raw = brain.search_knowledge("security_findings", limit=50)

        for f in findings_raw:
            try:
                finding_data = json.loads(f.get("value", "{}"))
                if severity == "all" or finding_data.get("severity") == severity:
                    all_findings.append(finding_data)
            except:
                pass

        return {
            "findings": all_findings[:limit],
            "total_found": len(all_findings),
            "filter": severity,
            "limit": limit
        }
    except Exception as e:
        return {"error": str(e), "findings": []}


def handle_analyze_code(code: str, language: str) -> dict:
    """Handle code analysis request"""
    import re

    findings = []

    # Security patterns for different languages
    patterns = {
        "sql_injection": [
            (r'execute\s*\(\s*["\'].*%s', "Potential SQL injection via string formatting"),
            (r'cursor\.execute\s*\(\s*f["\']', "Potential SQL injection via f-string"),
            (r'\+\s*["\'].*SELECT.*FROM', "Potential SQL injection via concatenation"),
        ],
        "command_injection": [
            (r'os\.system\s*\(', "Dangerous os.system() call - use subprocess instead"),
            (r'subprocess\.call\s*\([^,\]]+,\s*shell\s*=\s*True', "Shell=True in subprocess is dangerous"),
            (r'eval\s*\(', "Dangerous eval() call"),
            (r'exec\s*\(', "Dangerous exec() call"),
        ],
        "hardcoded_secrets": [
            (r'password\s*=\s*["\'][^"\']{4,}["\']', "Potential hardcoded password"),
            (r'api_key\s*=\s*["\'][^"\']{10,}["\']', "Potential hardcoded API key"),
            (r'secret\s*=\s*["\'][^"\']{4,}["\']', "Potential hardcoded secret"),
            (r'token\s*=\s*["\'][A-Za-z0-9]{20,}["\']', "Potential hardcoded token"),
        ],
        "xss": [
            (r'innerHTML\s*=', "Potential XSS via innerHTML"),
            (r'document\.write\s*\(', "Potential XSS via document.write"),
            (r'\.html\s*\([^)]*\+', "Potential XSS via jQuery .html()"),
        ],
        "path_traversal": [
            (r'open\s*\([^)]*\+[^)]*\)', "Potential path traversal in file open"),
        ],
    }

    for category, category_patterns in patterns.items():
        for pattern, description in category_patterns:
            matches = re.finditer(pattern, code, re.IGNORECASE)
            for match in matches:
                line_num = code[:match.start()].count('\n') + 1
                findings.append({
                    "type": category,
                    "severity": "high" if "injection" in category else "medium",
                    "line": line_num,
                    "description": description,
                    "match": match.group(0)[:50]
                })

    # Store in brain
    brain = get_brain()
    brain.store_knowledge(
        "code_analysis",
        f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        json.dumps({"findings": findings, "code_length": len(code)}),
        importance=7 if findings else 3,
        confidence=0.85
    )

    return {
        "findings": findings,
        "findings_count": len(findings),
        "language": language,
        "code_length": len(code),
        "security_score": max(0, 100 - (len(findings) * 10)),
        "butler_commentary": _generate_code_analysis_commentary(findings)
    }


def handle_get_recommendations() -> dict:
    """Handle recommendations request"""
    brain = get_brain()

    try:
        # Get recent findings
        findings = brain.search_knowledge("security_findings", limit=100)

        # Count by type
        type_counts = {}
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}

        for f in findings:
            try:
                data = json.loads(f.get("value", "{}"))
                severity = data.get("severity", "medium")
                if severity in severity_counts:
                    severity_counts[severity] += 1

                vuln_type = data.get("title", "Unknown")
                type_counts[vuln_type] = type_counts.get(vuln_type, 0) + 1
            except:
                pass

        # Generate recommendations
        recommendations = []

        if severity_counts["critical"] > 0:
            recommendations.append({
                "priority": 1,
                "action": f"Address {severity_counts['critical']} critical vulnerabilities IMMEDIATELY",
                "impact": "Critical vulnerabilities pose immediate security risk"
            })

        if severity_counts["high"] > 0:
            recommendations.append({
                "priority": 2,
                "action": f"Remediate {severity_counts['high']} high-severity issues within 7 days",
                "impact": "High severity issues can lead to data breaches"
            })

        # Add most common vulnerability type
        if type_counts:
            most_common = max(type_counts.items(), key=lambda x: x[1])
            recommendations.append({
                "priority": 3,
                "action": f"Focus on '{most_common[0]}' - found {most_common[1]} times",
                "impact": "Addressing common patterns improves overall security posture"
            })

        recommendations.append({
            "priority": 4,
            "action": "Schedule regular security scans (weekly recommended)",
            "impact": "Continuous monitoring catches new vulnerabilities early"
        })

        return {
            "recommendations": recommendations,
            "severity_summary": severity_counts,
            "total_findings_analyzed": len(findings),
            "vulnerability_types": dict(sorted(type_counts.items(), key=lambda x: -x[1])[:5])
        }

    except Exception as e:
        return {"error": str(e), "recommendations": []}


def _generate_butler_commentary(result: dict) -> str:
    """Generate British butler commentary"""
    findings = result.get("findings_count", 0)
    critical = result.get("severity_summary", {}).get("critical", 0)
    high = result.get("severity_summary", {}).get("high", 0)

    if critical > 0:
        return f"Most concerning, sir. I've discovered {critical} critical vulnerabilities that require immediate attention."
    elif high > 0:
        return f"Sir, I must inform you of {high} high-severity vulnerabilities. I recommend addressing these promptly."
    elif findings > 0:
        return f"Security assessment complete, sir. Found {findings} potential issues of moderate concern."
    else:
        return "Excellent news, sir. No significant vulnerabilities detected. The target appears secure."


def _generate_code_analysis_commentary(findings: list) -> str:
    """Generate commentary for code analysis"""
    if not findings:
        return "The code appears secure, sir. No obvious vulnerabilities detected."

    high_count = len([f for f in findings if f.get("severity") == "high"])
    if high_count > 0:
        return f"I've identified {high_count} high-severity issues in this code, sir. Immediate attention recommended."
    else:
        return f"Found {len(findings)} potential concerns in the code, sir. Review recommended."


async def main():
    """Main entry point for MCP server"""
    if not MCP_AVAILABLE:
        print("MCP not available. Install with: pip install mcp")
        sys.exit(1)

    logger.info("Starting ALFRED Security Agent MCP Server")

    # Initialize brain
    global brain
    brain = AlfredBrain()

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
