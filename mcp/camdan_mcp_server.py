#!/usr/bin/env python3
"""
CAMDAN Engineering MCP Server

Exposes CAMDAN (Comprehensive AI Management for Design, Architecture & Engineering)
to Claude Code for building codes, cost estimation, compliance checking, and more.

Tools provided:
- query_engineering_knowledge: Ask engineering questions (NIST, EBSCO, codes)
- estimate_construction_cost: AI-powered cost estimation
- check_building_code_compliance: Verify code compliance (all 50 US states)
- analyze_building_plan: Computer vision analysis of building plans
- predict_maintenance: Predict component maintenance needs
- get_building_codes: Get applicable building codes for location/type
- search_nist_data: Search NIST Standard Reference Data
- search_ebsco_research: Search EBSCO Engineering Source
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

# Check if CAMDAN tool is available
try:
    from tools.camdan_tool import (
        query_engineering_knowledge,
        estimate_construction_cost,
        check_building_code_compliance,
        analyze_building_plan,
        predict_maintenance
    )
    CAMDAN_AVAILABLE = True
except ImportError:
    CAMDAN_AVAILABLE = False
    print("Warning: CAMDAN tool not found. Install CAMDAN or check tools/camdan_tool.py")


class CAMDANMCPServer:
    """MCP Server for CAMDAN Engineering System"""

    def __init__(self):
        """Initialize CAMDAN MCP Server"""
        self.server = Server("camdan-engineering")
        self._setup_handlers()

    def _setup_handlers(self):
        """Setup MCP request handlers"""

        @self.server.list_tools()
        async def list_tools() -> list[types.Tool]:
            """List all available tools"""
            if not CAMDAN_AVAILABLE:
                return []

            return [
                types.Tool(
                    name="camdan_query_engineering",
                    description="Query engineering knowledge from NIST data, EBSCO research, and building codes",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Engineering question or query"},
                            "domain": {
                                "type": "string",
                                "description": "Engineering domain (structural, electrical, mechanical, civil, etc.)",
                                "default": "general"
                            },
                        },
                        "required": ["query"],
                    },
                ),
                types.Tool(
                    name="camdan_estimate_cost",
                    description="Estimate construction costs with AI-powered analysis",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_description": {"type": "string", "description": "Description of construction project"},
                            "square_footage": {"type": "number", "description": "Building square footage"},
                            "building_type": {
                                "type": "string",
                                "description": "Type of building",
                                "enum": ["residential", "commercial", "industrial", "warehouse", "office", "retail", "mixed-use"]
                            },
                            "location": {"type": "string", "description": "City and state (e.g., 'Seattle, WA')"},
                            "quality_level": {
                                "type": "string",
                                "description": "Construction quality level",
                                "enum": ["basic", "standard", "high-end", "luxury"],
                                "default": "standard"
                            },
                        },
                        "required": ["project_description", "square_footage", "building_type", "location"],
                    },
                ),
                types.Tool(
                    name="camdan_check_compliance",
                    description="Check building code compliance for all 50 US states",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "building_description": {"type": "string", "description": "Description of building design"},
                            "building_type": {"type": "string", "description": "Type of building (office, residential, etc.)"},
                            "location": {"type": "string", "description": "State or city for code compliance"},
                            "specifications": {
                                "type": "object",
                                "description": "Building specifications (stories, occupancy, etc.)",
                                "properties": {
                                    "stories": {"type": "integer"},
                                    "occupancy_type": {"type": "string"},
                                    "construction_type": {"type": "string"},
                                }
                            },
                        },
                        "required": ["building_description", "building_type", "location"],
                    },
                ),
                types.Tool(
                    name="camdan_analyze_plan",
                    description="Analyze building plans using computer vision (requires image path)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "plan_image_path": {"type": "string", "description": "Path to building plan image"},
                            "analysis_type": {
                                "type": "string",
                                "description": "Type of analysis",
                                "enum": ["component_detection", "specification_extraction", "lifespan_prediction", "maintenance_schedule"],
                                "default": "component_detection"
                            },
                        },
                        "required": ["plan_image_path"],
                    },
                ),
                types.Tool(
                    name="camdan_predict_maintenance",
                    description="Predict maintenance needs for building components",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "component_type": {
                                "type": "string",
                                "description": "Building component type",
                                "enum": ["HVAC", "roof", "electrical", "plumbing", "elevator", "fire_safety", "structural"]
                            },
                            "installation_date": {"type": "string", "description": "Installation date (YYYY-MM-DD)"},
                            "current_condition": {
                                "type": "string",
                                "description": "Current condition",
                                "enum": ["excellent", "good", "fair", "poor", "critical"],
                                "default": "good"
                            },
                            "usage_intensity": {
                                "type": "string",
                                "description": "Usage intensity",
                                "enum": ["light", "moderate", "heavy"],
                                "default": "moderate"
                            },
                        },
                        "required": ["component_type", "installation_date"],
                    },
                ),
                types.Tool(
                    name="camdan_get_building_codes",
                    description="Get applicable building codes for location and building type",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "location": {"type": "string", "description": "State or city"},
                            "building_type": {"type": "string", "description": "Type of building"},
                            "code_category": {
                                "type": "string",
                                "description": "Code category",
                                "enum": ["all", "structural", "fire", "electrical", "plumbing", "mechanical", "accessibility"],
                                "default": "all"
                            },
                        },
                        "required": ["location", "building_type"],
                    },
                ),
                types.Tool(
                    name="camdan_search_nist",
                    description="Search NIST Standard Reference Data",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search query for NIST data"},
                            "data_type": {
                                "type": "string",
                                "description": "Type of NIST data",
                                "enum": ["materials", "thermodynamics", "chemistry", "physics", "all"],
                                "default": "all"
                            },
                        },
                        "required": ["query"],
                    },
                ),
                types.Tool(
                    name="camdan_search_ebsco",
                    description="Search EBSCO Engineering Source research database",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Research query"},
                            "publication_year": {"type": "integer", "description": "Filter by publication year (optional)"},
                            "limit": {"type": "integer", "description": "Max results", "default": 10},
                        },
                        "required": ["query"],
                    },
                ),
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> list[types.TextContent]:
            """Handle tool calls"""

            if not CAMDAN_AVAILABLE:
                return [types.TextContent(
                    type="text",
                    text="CAMDAN system not available. Please install CAMDAN or check configuration."
                )]

            try:
                if name == "camdan_query_engineering":
                    result = query_engineering_knowledge(
                        query=arguments["query"],
                        domain=arguments.get("domain", "general")
                    )
                    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

                elif name == "camdan_estimate_cost":
                    result = estimate_construction_cost(
                        project_description=arguments["project_description"],
                        square_footage=arguments["square_footage"],
                        building_type=arguments["building_type"],
                        location=arguments["location"],
                        quality_level=arguments.get("quality_level", "standard")
                    )
                    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

                elif name == "camdan_check_compliance":
                    result = check_building_code_compliance(
                        building_description=arguments["building_description"],
                        building_type=arguments["building_type"],
                        location=arguments["location"],
                        specifications=arguments.get("specifications", {})
                    )
                    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

                elif name == "camdan_analyze_plan":
                    result = analyze_building_plan(
                        plan_image_path=arguments["plan_image_path"],
                        analysis_type=arguments.get("analysis_type", "component_detection")
                    )
                    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

                elif name == "camdan_predict_maintenance":
                    result = predict_maintenance(
                        component_type=arguments["component_type"],
                        installation_date=arguments["installation_date"],
                        current_condition=arguments.get("current_condition", "good"),
                        usage_intensity=arguments.get("usage_intensity", "moderate")
                    )
                    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

                elif name == "camdan_get_building_codes":
                    # This would call CAMDAN API to get building codes
                    result = {
                        "location": arguments["location"],
                        "building_type": arguments["building_type"],
                        "codes": ["IBC", "NEC", "IPC"],  # Placeholder
                        "note": "Full implementation requires CAMDAN API integration"
                    }
                    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

                elif name == "camdan_search_nist":
                    result = {
                        "query": arguments["query"],
                        "results": [],
                        "note": "Full implementation requires CAMDAN NIST integration"
                    }
                    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

                elif name == "camdan_search_ebsco":
                    result = {
                        "query": arguments["query"],
                        "results": [],
                        "note": "Full implementation requires CAMDAN EBSCO integration"
                    }
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
    server = CAMDANMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
