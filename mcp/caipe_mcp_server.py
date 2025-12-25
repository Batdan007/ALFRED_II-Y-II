#!/usr/bin/env python3
"""
CAIPE Multi-Agent MCP Server

Exposes Community AI Platform Engineering (CAIPE) multi-agent system to Claude Code.

Available Agents:
- GitHub: Repository operations, PR management, issue tracking
- ArgoCD: Continuous deployment, application synchronization
- PagerDuty: Incident management, on-call scheduling
- Jira: Issue tracking, project management
- Slack: Team communication, notifications
- Confluence: Documentation and knowledge management
- Backstage: Developer portal integration
- Komodor: Kubernetes troubleshooting
- Atlassian: Atlassian suite integration

Tools provided:
- call_agent: Call any CAIPE agent with a task
- list_agents: List all available agents
- get_agent_capabilities: Get capabilities of a specific agent
- orchestrate_multi_agent: Orchestrate multiple agents for complex task
"""

import asyncio
import json
from typing import Any, Optional, List
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


class CAIPEMCPServer:
    """MCP Server for CAIPE Multi-Agent System"""

    # Available CAIPE agents
    AGENTS = {
        "github": {
            "name": "GitHub Agent",
            "description": "Repository operations, PR management, issue tracking",
            "capabilities": [
                "create_repository",
                "create_pull_request",
                "create_issue",
                "review_pull_request",
                "merge_pull_request",
                "search_code",
                "get_repository_info",
            ]
        },
        "argocd": {
            "name": "ArgoCD Agent",
            "description": "Continuous deployment and GitOps operations",
            "capabilities": [
                "deploy_application",
                "sync_application",
                "get_application_status",
                "rollback_application",
                "create_application",
                "delete_application",
            ]
        },
        "pagerduty": {
            "name": "PagerDuty Agent",
            "description": "Incident management and on-call operations",
            "capabilities": [
                "create_incident",
                "acknowledge_incident",
                "resolve_incident",
                "escalate_incident",
                "get_oncall_schedule",
                "trigger_alert",
            ]
        },
        "jira": {
            "name": "Jira Agent",
            "description": "Issue tracking and project management",
            "capabilities": [
                "create_issue",
                "update_issue",
                "transition_issue",
                "assign_issue",
                "search_issues",
                "create_sprint",
                "add_comment",
            ]
        },
        "slack": {
            "name": "Slack Agent",
            "description": "Team communication and notifications",
            "capabilities": [
                "send_message",
                "create_channel",
                "invite_users",
                "post_file",
                "search_messages",
                "set_reminder",
            ]
        },
        "confluence": {
            "name": "Confluence Agent",
            "description": "Documentation and knowledge management",
            "capabilities": [
                "create_page",
                "update_page",
                "search_content",
                "add_comment",
                "attach_file",
                "get_page",
            ]
        },
        "backstage": {
            "name": "Backstage Agent",
            "description": "Developer portal and service catalog",
            "capabilities": [
                "register_component",
                "update_component",
                "search_catalog",
                "get_component_docs",
                "create_template",
            ]
        },
        "komodor": {
            "name": "Komodor Agent",
            "description": "Kubernetes troubleshooting and monitoring",
            "capabilities": [
                "analyze_deployment",
                "get_pod_logs",
                "check_resource_health",
                "investigate_incident",
                "get_timeline",
            ]
        },
        "atlassian": {
            "name": "Atlassian Agent",
            "description": "Atlassian suite integration (Jira, Confluence, Bitbucket)",
            "capabilities": [
                "cross_tool_search",
                "link_items",
                "sync_data",
            ]
        },
    }

    def __init__(self):
        """Initialize CAIPE MCP Server"""
        self.server = Server("caipe-multi-agent")
        self._setup_handlers()

    def _call_agent(self, agent_name: str, action: str, parameters: dict) -> dict:
        """
        Call a CAIPE agent

        This is a placeholder - actual implementation would integrate with CAIPE system
        """
        if agent_name not in self.AGENTS:
            return {
                "success": False,
                "error": f"Unknown agent: {agent_name}",
                "available_agents": list(self.AGENTS.keys())
            }

        return {
            "success": False,
            "agent": agent_name,
            "action": action,
            "parameters": parameters,
            "result": None,
            "note": "CAIPE integration requires running CAIPE docker containers or services. See .claude/CLAUDE.md for setup."
        }

    def _orchestrate_agents(self, task: str, agents: List[str]) -> dict:
        """
        Orchestrate multiple agents for a complex task

        This would use LangGraph supervisor pattern
        """
        return {
            "task": task,
            "agents": agents,
            "workflow": [],
            "note": "Multi-agent orchestration requires CAIPE platform-engineer or incident-engineer personas"
        }

    def _setup_handlers(self):
        """Setup MCP request handlers"""

        @self.server.list_tools()
        async def list_tools() -> list[types.Tool]:
            """List all available tools"""
            return [
                types.Tool(
                    name="caipe_list_agents",
                    description="List all available CAIPE agents with their capabilities",
                    inputSchema={"type": "object", "properties": {}},
                ),
                types.Tool(
                    name="caipe_get_agent_capabilities",
                    description="Get detailed capabilities of a specific agent",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "agent_name": {
                                "type": "string",
                                "description": "Name of the agent",
                                "enum": list(CAIPEMCPServer.AGENTS.keys())
                            },
                        },
                        "required": ["agent_name"],
                    },
                ),
                types.Tool(
                    name="caipe_call_github_agent",
                    description="Call GitHub agent for repository operations",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "action": {
                                "type": "string",
                                "description": "Action to perform",
                                "enum": ["create_pr", "create_issue", "review_pr", "merge_pr", "search_code", "get_repo_info"]
                            },
                            "parameters": {"type": "object", "description": "Action parameters"},
                        },
                        "required": ["action", "parameters"],
                    },
                ),
                types.Tool(
                    name="caipe_call_argocd_agent",
                    description="Call ArgoCD agent for deployment operations",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "action": {
                                "type": "string",
                                "description": "Action to perform",
                                "enum": ["deploy", "sync", "get_status", "rollback", "create_app", "delete_app"]
                            },
                            "parameters": {"type": "object", "description": "Action parameters"},
                        },
                        "required": ["action", "parameters"],
                    },
                ),
                types.Tool(
                    name="caipe_call_pagerduty_agent",
                    description="Call PagerDuty agent for incident management",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "action": {
                                "type": "string",
                                "description": "Action to perform",
                                "enum": ["create_incident", "acknowledge", "resolve", "escalate", "get_oncall"]
                            },
                            "parameters": {"type": "object", "description": "Action parameters"},
                        },
                        "required": ["action", "parameters"],
                    },
                ),
                types.Tool(
                    name="caipe_call_jira_agent",
                    description="Call Jira agent for issue tracking",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "action": {
                                "type": "string",
                                "description": "Action to perform",
                                "enum": ["create_issue", "update_issue", "transition", "assign", "search", "comment"]
                            },
                            "parameters": {"type": "object", "description": "Action parameters"},
                        },
                        "required": ["action", "parameters"],
                    },
                ),
                types.Tool(
                    name="caipe_call_slack_agent",
                    description="Call Slack agent for team communication",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "action": {
                                "type": "string",
                                "description": "Action to perform",
                                "enum": ["send_message", "create_channel", "invite_users", "post_file", "search"]
                            },
                            "parameters": {"type": "object", "description": "Action parameters"},
                        },
                        "required": ["action", "parameters"],
                    },
                ),
                types.Tool(
                    name="caipe_orchestrate_multi_agent",
                    description="Orchestrate multiple agents to complete a complex platform engineering task",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "task": {"type": "string", "description": "High-level task description"},
                            "agents": {
                                "type": "array",
                                "description": "Agents to involve in the task",
                                "items": {"type": "string", "enum": list(CAIPEMCPServer.AGENTS.keys())}
                            },
                            "priority": {
                                "type": "string",
                                "description": "Task priority",
                                "enum": ["low", "medium", "high", "critical"],
                                "default": "medium"
                            },
                        },
                        "required": ["task"],
                    },
                ),
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> list[types.TextContent]:
            """Handle tool calls"""

            try:
                if name == "caipe_list_agents":
                    return [types.TextContent(
                        type="text",
                        text=json.dumps(self.AGENTS, indent=2)
                    )]

                elif name == "caipe_get_agent_capabilities":
                    agent_name = arguments["agent_name"]
                    agent_info = self.AGENTS.get(agent_name)

                    if not agent_info:
                        return [types.TextContent(
                            type="text",
                            text=f"Unknown agent: {agent_name}"
                        )]

                    return [types.TextContent(
                        type="text",
                        text=json.dumps(agent_info, indent=2)
                    )]

                elif name.startswith("caipe_call_") and name != "caipe_call_agent":
                    # Extract agent name from tool name
                    agent_name = name.replace("caipe_call_", "").replace("_agent", "")
                    action = arguments["action"]
                    parameters = arguments["parameters"]

                    result = self._call_agent(agent_name, action, parameters)
                    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

                elif name == "caipe_orchestrate_multi_agent":
                    task = arguments["task"]
                    agents = arguments.get("agents", [])

                    result = self._orchestrate_agents(task, agents)
                    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

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
    server = CAIPEMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
