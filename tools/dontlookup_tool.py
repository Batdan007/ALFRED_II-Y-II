"""
DontLookUp DVB-S2(X) Parser Tool
Satellite communication analysis for Alfred Tool Mode
"""

import logging
from typing import Dict, Any
from tools.base import Tool, ToolResult


class DontLookUpTool(Tool):
    """
    DontLookUp DVB-S2(X) satellite communication parser tool

    Allows Alfred to analyze satellite captures during conversations:
    - User: "Parse this DVB-S2 capture and extract IP traffic"
    - Alfred: [Uses dontlookup_parse tool to analyze the capture]
    """

    def __init__(self, brain=None):
        """
        Initialize DontLookUp tool

        Args:
            brain: AlfredBrain for storing parse results
        """
        self.logger = logging.getLogger(__name__)
        self.brain = brain
        self.dontlookup_available = False

        self._check_availability()

    def _check_availability(self):
        """Check if DontLookUp scanner capability is available"""
        try:
            from capabilities.security.dontlookup_scanner import DontLookUpScanner
            scanner = DontLookUpScanner(self.brain)
            self.dontlookup_available = scanner.dontlookup_available
            if self.dontlookup_available:
                self.logger.info("DontLookUp tool initialized successfully")
            else:
                self.logger.debug("DontLookUp not installed - tool disabled")
        except Exception as e:
            self.logger.error(f"Error initializing DontLookUp tool: {e}")
            self.dontlookup_available = False

    @property
    def name(self) -> str:
        return "dontlookup_parse"

    @property
    def description(self) -> str:
        return (
            "Parse DVB-S2(X) satellite communication captures to extract IP packets and analyze satellite protocols. "
            "Supports multiple encapsulation standards including GSE, MPEG-TS, and direct IP. "
            "Useful for security research on satellite communications, protocol analysis, and traffic extraction."
        )

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "capture_file": {
                    "type": "string",
                    "description": (
                        "Path to DVB-S2(X) capture file to parse. Usually a .ts file containing "
                        "raw satellite signal data. The file should contain BBFrame data from "
                        "a DVB-S2 or DVB-S2X transmission."
                    )
                },
                "parser_type": {
                    "type": "string",
                    "enum": [
                        "dvbs2-ip",
                        "dvbs2-rev-ip",
                        "dvbs2-mpegts",
                        "dvbs2-mpegts-crc",
                        "dvbs2-mpegts-newtec",
                        "dvbs2-gse-stdlen-split-ip",
                        "dvbs2-gse-stdlen-std-ip",
                        "dvbs2-gse-len2-split-ip",
                        "dvbs2-gse-len2-std-ip",
                        "all"
                    ],
                    "description": (
                        "Parser type to use:\n"
                        "- dvbs2-ip: Direct IP extraction (fastest, try this first)\n"
                        "- dvbs2-rev-ip: Byte-swapped IP extraction\n"
                        "- dvbs2-mpegts: Standard MPEG-TS extraction\n"
                        "- dvbs2-mpegts-crc: MPEG-TS with Generic CRC\n"
                        "- dvbs2-mpegts-newtec: MPEG-TS with Newtec CRC\n"
                        "- dvbs2-gse-stdlen-split-ip: GSE with standard length and split fragment ID\n"
                        "- dvbs2-gse-stdlen-std-ip: GSE with standard length and standard fragment ID\n"
                        "- dvbs2-gse-len2-split-ip: GSE with 2-byte header length and split fragment ID\n"
                        "- dvbs2-gse-len2-std-ip: GSE with 2-byte header length and standard fragment ID\n"
                        "- all: Run all parsers (slow but comprehensive)"
                    ),
                    "default": "dvbs2-ip"
                },
                "verbose": {
                    "type": "boolean",
                    "description": "Enable verbose logging to see detailed parsing progress",
                    "default": False
                },
                "show_progress": {
                    "type": "boolean",
                    "description": "Show progress bars during parsing",
                    "default": True
                }
            },
            "required": ["capture_file"]
        }

    def execute(
        self,
        capture_file: str,
        parser_type: str = "dvbs2-ip",
        verbose: bool = False,
        show_progress: bool = True
    ) -> ToolResult:
        """
        Execute DontLookUp parser on satellite capture

        Args:
            capture_file: Path to DVB-S2 capture file
            parser_type: Type of parser to use
            verbose: Enable verbose logging
            show_progress: Show progress bars

        Returns:
            ToolResult with parse results or error
        """
        # Check if DontLookUp is available
        if not self.dontlookup_available:
            return ToolResult(
                success=False,
                output="",
                error=(
                    "DontLookUp satellite parser is not installed. "
                    "Clone from: https://github.com/ucsdsysnet/dontlookup.git"
                )
            )

        try:
            # Import scanner and parser type
            from capabilities.security.dontlookup_scanner import DontLookUpScanner, ParserType

            # Map parser type string to enum
            parser_type_map = {
                'dvbs2-ip': ParserType.DVBS2_IP,
                'dvbs2-rev-ip': ParserType.DVBS2_REV_IP,
                'dvbs2-mpegts': ParserType.DVBS2_MPEGTS,
                'dvbs2-mpegts-crc': ParserType.DVBS2_MPEGTS_CRC,
                'dvbs2-mpegts-newtec': ParserType.DVBS2_MPEGTS_NEWTEC,
                'dvbs2-gse-stdlen-split-ip': ParserType.DVBS2_GSE_STDLEN_SPLIT_IP,
                'dvbs2-gse-stdlen-std-ip': ParserType.DVBS2_GSE_STDLEN_STD_IP,
                'dvbs2-gse-len2-split-ip': ParserType.DVBS2_GSE_LEN2_SPLIT_IP,
                'dvbs2-gse-len2-std-ip': ParserType.DVBS2_GSE_LEN2_STD_IP,
                'all': ParserType.ALL
            }

            parser_type_enum = parser_type_map.get(parser_type.lower(), ParserType.DVBS2_IP)

            # Initialize scanner
            scanner = DontLookUpScanner(brain=self.brain)

            # Run parse
            self.logger.info(f"Starting DontLookUp parse: {capture_file} ({parser_type})")

            results = scanner.parse_capture(
                capture_file=capture_file,
                parser_type=parser_type_enum,
                verbose=verbose,
                show_progress=show_progress
            )

            # Check if parse succeeded
            if not results['success']:
                return ToolResult(
                    success=False,
                    output="",
                    error=results.get('error', 'Parse failed')
                )

            # Format output for AI
            output = self._format_parse_output(results)

            # Return success
            return ToolResult(
                success=True,
                output=output,
                metadata={
                    'capture_file': capture_file,
                    'parser_type': parser_type,
                    'bbframes': results.get('bbframes', 0),
                    'packets_extracted': results.get('packets_extracted', 0),
                    'output_files': results.get('output_files', [])
                }
            )

        except Exception as e:
            self.logger.error(f"Error executing DontLookUp parse: {e}")
            return ToolResult(
                success=False,
                output="",
                error=f"Parse execution error: {str(e)}"
            )

    def _format_parse_output(self, results: Dict[str, Any]) -> str:
        """
        Format parse results for AI consumption

        Args:
            results: Parse results dictionary

        Returns:
            Formatted output string
        """
        output_lines = []

        # Header
        output_lines.append(f"DVB-S2 Parse Complete - Capture: {results['capture_file']}")
        output_lines.append("=" * 70)

        # Parser info
        output_lines.append(f"\nParser Used: {results['parser_used']}")

        # Results
        output_lines.append(f"\nBBFrames Processed: {results['bbframes']:,}")
        output_lines.append(f"Packets Extracted: {results['packets_extracted']:,}")

        # Output files
        output_files = results.get('output_files', [])
        if output_files:
            output_lines.append(f"\nGenerated {len(output_files)} output file(s):")
            for i, file_path in enumerate(output_files[:5], 1):  # Show first 5
                output_lines.append(f"  {i}. {file_path}")

            if len(output_files) > 5:
                output_lines.append(f"  ... and {len(output_files) - 5} more files")

            output_lines.append("\nThese files can be opened in Wireshark for detailed analysis.")
        else:
            output_lines.append("\nNo output files were generated. The capture may not contain valid data.")

        # Butler commentary
        commentary = results.get('butler_commentary', '')
        if commentary:
            output_lines.append(f"\n{commentary}")

        # Recommendations
        if results['packets_extracted'] > 0:
            output_lines.append("\nRecommendations:")
            output_lines.append("  - Open the .pcap files in Wireshark to examine extracted traffic")
            output_lines.append("  - Look for anomalous patterns or unexpected protocols")
            output_lines.append("  - Consider running additional parser variants for comparison")

        return "\n".join(output_lines)


# Graceful import check
def create_dontlookup_tool(brain=None) -> DontLookUpTool:
    """
    Factory function to create DontLookUp tool with graceful degradation

    Args:
        brain: AlfredBrain instance

    Returns:
        DontLookUpTool instance (may be unavailable if not installed)
    """
    return DontLookUpTool(brain)
