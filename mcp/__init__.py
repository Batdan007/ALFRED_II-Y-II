"""
ALFRED MCP Servers Package

Model Context Protocol servers for ALFRED-UBX and integrated systems.

Available servers:
- alfred_mcp_server: Core ALFRED brain, voice, privacy, AI orchestration
- camdan_mcp_server: CAMDAN engineering (building codes, cost estimation)
- strix_mcp_server: Strix security testing and vulnerability scanning
- dontlookup_mcp_server: DontLookUp DVB-S2 satellite communication parser
- caipe_mcp_server: CAIPE multi-agent system (GitHub, ArgoCD, Jira, etc.)

Usage:
    python -m mcp.alfred_mcp_server
    python -m mcp.camdan_mcp_server
    python -m mcp.strix_mcp_server
    python -m mcp.dontlookup_mcp_server
    python -m mcp.caipe_mcp_server
"""

__version__ = "1.0.0"
__author__ = "Daniel J Rita (BATDAN)"

__all__ = [
    "alfred_mcp_server",
    "camdan_mcp_server",
    "strix_mcp_server",
    "dontlookup_mcp_server",
    "caipe_mcp_server",
]
