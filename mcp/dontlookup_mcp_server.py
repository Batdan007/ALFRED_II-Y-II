#!/usr/bin/env python3
"""
DontLookUp DVB-S2 MCP Server

Exposes DontLookUp DVB-S2(X) satellite communication parser to Claude Code.

Tools provided:
- parse_dvbs2_capture: Parse DVB-S2 capture file and extract IP packets
- list_available_parsers: List all available DVB-S2 parser variants
- analyze_capture_stats: Get statistics about a capture file
- convert_to_pcap: Convert parsed data to PCAP format
- extract_protocols: Extract specific protocols from parsed capture
- get_parse_results: Retrieve previous parse results
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

# Check if DontLookUp is available
DONTLOOKUP_AVAILABLE = False
try:
    # This would be the actual DontLookUp import
    # For now, we'll create a placeholder
    DONTLOOKUP_AVAILABLE = True
except ImportError:
    pass  # DontLookUp is optional

from core.brain import AlfredBrain


class DontLookUpMCPServer:
    """MCP Server for DontLookUp DVB-S2 Parser"""

    # Available parser types
    PARSERS = [
        "dvbs2-ip",
        "dvbs2-rev-ip",
        "dvbs2-mpegts",
        "dvbs2-mpegts-crc",
        "dvbs2-mpegts-newtec",
        "dvbs2-gse-stdlen-split-ip",
        "dvbs2-gse-stdlen-std-ip",
        "dvbs2-gse-len2-split-ip",
        "dvbs2-gse-len2-std-ip",
    ]

    def __init__(self):
        """Initialize DontLookUp MCP Server"""
        self.server = Server("dontlookup-dvbs2")
        self.brain = AlfredBrain()
        self._setup_handlers()

    def _parse_dvbs2_file(self, capture_path: str, parser_type: str, output_path: Optional[str] = None) -> dict:
        """
        Parse DVB-S2 capture file

        This is a placeholder - actual implementation would call DontLookUp parser
        """
        result = {
            "success": False,
            "message": "DontLookUp parser not fully integrated",
            "parser_type": parser_type,
            "input_file": capture_path,
            "output_file": output_path,
            "packets_extracted": 0,
            "bbframes_processed": 0,
            "errors": [],
            "note": "To use DontLookUp, clone from https://github.com/ucsdsysnet/dontlookup and integrate with tools/dontlookup_tool.py"
        }

        # Store parse attempt in brain
        self.brain.store_security_scan(
            target=capture_path,
            scan_type="dontlookup-dvbs2",
            results=result
        )

        return result

    def _setup_handlers(self):
        """Setup MCP request handlers"""

        @self.server.list_tools()
        async def list_tools() -> list[types.Tool]:
            """List all available tools"""
            return [
                types.Tool(
                    name="dontlookup_parse_capture",
                    description="Parse DVB-S2 satellite capture file and extract IP packets",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "capture_path": {"type": "string", "description": "Path to DVB-S2 capture file"},
                            "parser_type": {
                                "type": "string",
                                "description": "Parser variant to use",
                                "enum": DontLookUpMCPServer.PARSERS + ["auto", "all"],
                                "default": "dvbs2-ip"
                            },
                            "output_path": {"type": "string", "description": "Output PCAP file path (optional)"},
                            "auto_detect": {"type": "boolean", "description": "Try all parsers to find best match", "default": False},
                        },
                        "required": ["capture_path"],
                    },
                ),
                types.Tool(
                    name="dontlookup_list_parsers",
                    description="List all available DVB-S2 parser variants with descriptions",
                    inputSchema={"type": "object", "properties": {}},
                ),
                types.Tool(
                    name="dontlookup_analyze_stats",
                    description="Analyze DVB-S2 capture file and get statistics without full parse",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "capture_path": {"type": "string", "description": "Path to capture file"},
                        },
                        "required": ["capture_path"],
                    },
                ),
                types.Tool(
                    name="dontlookup_extract_protocols",
                    description="Extract specific protocols from parsed capture",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "capture_path": {"type": "string", "description": "Path to capture file"},
                            "protocols": {
                                "type": "array",
                                "description": "Protocols to extract (e.g., ['TCP', 'UDP', 'HTTP'])",
                                "items": {"type": "string"}
                            },
                            "parser_type": {
                                "type": "string",
                                "description": "Parser to use",
                                "enum": DontLookUpMCPServer.PARSERS,
                                "default": "dvbs2-ip"
                            },
                        },
                        "required": ["capture_path", "protocols"],
                    },
                ),
                types.Tool(
                    name="dontlookup_get_results",
                    description="Retrieve previous parse results from brain storage",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "capture_path": {"type": "string", "description": "Capture file path (optional)"},
                            "limit": {"type": "integer", "description": "Max results", "default": 10},
                        },
                    },
                ),
                types.Tool(
                    name="dontlookup_compare_parsers",
                    description="Compare results from multiple parsers on the same capture",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "capture_path": {"type": "string", "description": "Path to capture file"},
                            "parsers": {
                                "type": "array",
                                "description": "List of parsers to compare",
                                "items": {
                                    "type": "string",
                                    "enum": DontLookUpMCPServer.PARSERS
                                }
                            },
                        },
                        "required": ["capture_path"],
                    },
                ),
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> list[types.TextContent]:
            """Handle tool calls"""

            try:
                if name == "dontlookup_parse_capture":
                    capture_path = arguments["capture_path"]
                    parser_type = arguments.get("parser_type", "dvbs2-ip")
                    output_path = arguments.get("output_path")
                    auto_detect = arguments.get("auto_detect", False)

                    if auto_detect or parser_type == "all":
                        # Try all parsers
                        results = {}
                        for parser in self.PARSERS:
                            results[parser] = self._parse_dvbs2_file(capture_path, parser, output_path)

                        # Find best result
                        best_parser = max(results.items(), key=lambda x: x[1].get("packets_extracted", 0))

                        return [types.TextContent(
                            type="text",
                            text=json.dumps({
                                "best_parser": best_parser[0],
                                "best_result": best_parser[1],
                                "all_results": results
                            }, indent=2)
                        )]
                    else:
                        result = self._parse_dvbs2_file(capture_path, parser_type, output_path)
                        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

                elif name == "dontlookup_list_parsers":
                    parsers_info = {
                        "dvbs2-ip": "Direct IP extraction (fastest, try first)",
                        "dvbs2-rev-ip": "Byte-swapped IP extraction",
                        "dvbs2-mpegts": "Standard MPEG-TS extraction",
                        "dvbs2-mpegts-crc": "MPEG-TS with Generic CRC",
                        "dvbs2-mpegts-newtec": "MPEG-TS with Newtec CRC",
                        "dvbs2-gse-stdlen-split-ip": "GSE with standard length and split fragment ID",
                        "dvbs2-gse-stdlen-std-ip": "GSE with standard length and standard fragment ID",
                        "dvbs2-gse-len2-split-ip": "GSE with 2-byte header length and split fragment ID",
                        "dvbs2-gse-len2-std-ip": "GSE with 2-byte header length and standard fragment ID",
                    }
                    return [types.TextContent(type="text", text=json.dumps(parsers_info, indent=2))]

                elif name == "dontlookup_analyze_stats":
                    capture_path = arguments["capture_path"]

                    # Placeholder stats
                    stats = {
                        "file": capture_path,
                        "file_size_mb": 0,
                        "estimated_bbframes": 0,
                        "note": "Full implementation requires DontLookUp integration"
                    }

                    return [types.TextContent(type="text", text=json.dumps(stats, indent=2))]

                elif name == "dontlookup_extract_protocols":
                    capture_path = arguments["capture_path"]
                    protocols = arguments["protocols"]
                    parser_type = arguments.get("parser_type", "dvbs2-ip")

                    result = {
                        "capture": capture_path,
                        "parser": parser_type,
                        "requested_protocols": protocols,
                        "extracted": {},
                        "note": "Full implementation requires DontLookUp integration"
                    }

                    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

                elif name == "dontlookup_get_results":
                    capture_path = arguments.get("capture_path")
                    limit = arguments.get("limit", 10)

                    # Retrieve from brain
                    results = self.brain.get_security_scans(
                        scan_type="dontlookup-dvbs2",
                        limit=limit
                    )

                    if capture_path:
                        results = [r for r in results if r.get("target") == capture_path]

                    return [types.TextContent(type="text", text=json.dumps(results, indent=2))]

                elif name == "dontlookup_compare_parsers":
                    capture_path = arguments["capture_path"]
                    parsers = arguments.get("parsers", self.PARSERS[:3])  # Default to first 3

                    comparison = {}
                    for parser in parsers:
                        comparison[parser] = self._parse_dvbs2_file(capture_path, parser)

                    # Rank by packets extracted
                    ranked = sorted(
                        comparison.items(),
                        key=lambda x: x[1].get("packets_extracted", 0),
                        reverse=True
                    )

                    return [types.TextContent(
                        type="text",
                        text=json.dumps({
                            "comparison": comparison,
                            "ranked_parsers": [p[0] for p in ranked],
                            "recommendation": ranked[0][0] if ranked else None
                        }, indent=2)
                    )]

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
    server = DontLookUpMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
