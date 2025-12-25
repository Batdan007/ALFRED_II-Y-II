"""
DontLookUp DVB-S2(X) Parser Integration for Alfred

This module provides a wrapper around the DontLookUp satellite communication parser.
DontLookUp extracts IP packets from DVB-S2(X) satellite signal captures.

Author: Daniel J Rita (BATDAN)
License: Proprietary - Part of ALFRED-UBX
"""

import json
import logging
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from enum import Enum


class ParserType(Enum):
    """Available DVB-S2 parser types"""
    DVBS2_IP = "dvbs2-ip"
    DVBS2_REV_IP = "dvbs2-rev-ip"
    DVBS2_MPEGTS = "dvbs2-mpegts"
    DVBS2_MPEGTS_CRC = "dvbs2-mpegts-crc"
    DVBS2_MPEGTS_NEWTEC = "dvbs2-mpegts-newtec"
    DVBS2_GSE_STDLEN_SPLIT_IP = "dvbs2-gse-stdlen-split-ip"
    DVBS2_GSE_STDLEN_STD_IP = "dvbs2-gse-stdlen-std-ip"
    DVBS2_GSE_LEN2_SPLIT_IP = "dvbs2-gse-len2-split-ip"
    DVBS2_GSE_LEN2_STD_IP = "dvbs2-gse-len2-std-ip"
    ALL = "all"


class DontLookUpScanner:
    """
    Alfred's wrapper for DontLookUp DVB-S2(X) satellite communication parser

    Provides integration with Alfred's brain for:
    - Parsing satellite captures to extract IP traffic
    - Analyzing DVB-S2 communication security
    - Detecting anomalies in satellite protocols
    - British butler commentary on findings
    """

    def __init__(self, brain=None):
        """
        Initialize DontLookUp scanner

        Args:
            brain: AlfredBrain instance for storing scan results
        """
        self.logger = logging.getLogger(__name__)
        self.brain = brain
        self.dontlookup_available = False
        self.dontlookup_path = None
        self.enabled = True

        self._check_availability()

    def _check_availability(self):
        """Check if DontLookUp is available"""
        try:
            # Check if dontlookup directory exists in Alfred root
            alfred_root = Path(__file__).parent.parent.parent
            dontlookup_dir = alfred_root / "dontlookup"
            dontlookup_script = dontlookup_dir / "dontlookup.py"

            if dontlookup_script.exists():
                self.dontlookup_path = str(dontlookup_script)
                self.dontlookup_available = True
                self.logger.info(f"DontLookUp parser detected at: {self.dontlookup_path}")
            else:
                self.logger.warning("DontLookUp not found. Clone from: https://github.com/ucsdsysnet/dontlookup.git")

        except Exception as e:
            self.logger.error(f"Error checking DontLookUp availability: {e}")

    def parse_capture(
        self,
        capture_file: str,
        parser_type: ParserType = ParserType.DVBS2_IP,
        verbose: bool = False,
        show_progress: bool = True
    ) -> Dict[str, Any]:
        """
        Parse DVB-S2 capture file using DontLookUp

        Args:
            capture_file: Path to DVB-S2 capture file (usually .ts file)
            parser_type: Type of parser to use (default: DVBS2_IP)
            verbose: Enable verbose logging
            show_progress: Show progress bars

        Returns:
            Dictionary with parse results:
            {
                'success': bool,
                'capture_file': str,
                'parser_used': str,
                'bbframes': int,
                'packets_extracted': int,
                'output_files': List[str],
                'butler_commentary': str,
                'error': Optional[str]
            }
        """
        # Check if DontLookUp is available
        if not self.dontlookup_available:
            return {
                'success': False,
                'capture_file': capture_file,
                'parser_used': parser_type.value,
                'bbframes': 0,
                'packets_extracted': 0,
                'output_files': [],
                'butler_commentary': "I'm afraid DontLookUp is not installed, sir. Clone from: https://github.com/ucsdsysnet/dontlookup.git",
                'error': 'DontLookUp not available'
            }

        # Check if capture file exists
        if not os.path.exists(capture_file):
            return {
                'success': False,
                'capture_file': capture_file,
                'parser_used': parser_type.value,
                'bbframes': 0,
                'packets_extracted': 0,
                'output_files': [],
                'butler_commentary': f"The capture file does not exist, sir: {capture_file}",
                'error': 'Capture file not found'
            }

        # Build command
        cmd = [sys.executable, self.dontlookup_path, capture_file, '-p', parser_type.value]

        if verbose:
            cmd.append('-vv')

        if not show_progress:
            cmd.append('--no-progress')

        # Run parser
        self.logger.info(f"Starting DontLookUp parse: {capture_file} with {parser_type.value}")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=7200,  # 2 hour timeout for large captures
                cwd=str(Path(self.dontlookup_path).parent)
            )

            # Parse output
            parse_results = self._parse_output(result.stdout, result.stderr, capture_file, parser_type.value)

            # Add butler commentary
            parse_results['butler_commentary'] = self._generate_butler_commentary(parse_results)

            # Store in brain if available
            if self.brain:
                self._store_in_brain(parse_results)

            return parse_results

        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'capture_file': capture_file,
                'parser_used': parser_type.value,
                'bbframes': 0,
                'packets_extracted': 0,
                'output_files': [],
                'butler_commentary': "The parsing operation exceeded the time limit, sir. Consider processing a smaller capture file.",
                'error': 'Parse timeout'
            }
        except Exception as e:
            self.logger.error(f"Error running DontLookUp: {e}")
            return {
                'success': False,
                'capture_file': capture_file,
                'parser_used': parser_type.value,
                'bbframes': 0,
                'packets_extracted': 0,
                'output_files': [],
                'butler_commentary': f"I encountered an error during parsing, sir: {str(e)}",
                'error': str(e)
            }

    def _parse_output(self, stdout: str, stderr: str, capture_file: str, parser_type: str) -> Dict[str, Any]:
        """
        Parse DontLookUp output to extract results

        Args:
            stdout: Standard output from DontLookUp
            stderr: Standard error from DontLookUp
            capture_file: Input capture file path
            parser_type: Parser type used

        Returns:
            Parsed results dictionary
        """
        bbframes = 0
        packets_extracted = 0
        output_files = []

        lines = stdout.split('\n')

        # Extract BBFrames count
        for line in lines:
            if 'BBFrames found:' in line:
                try:
                    bbframes = int(line.split(':')[1].strip())
                except (ValueError, IndexError):
                    pass

            # Extract packet counts
            if 'IP packets found:' in line or 'packets found:' in line:
                try:
                    packets_extracted = int(line.split(':')[1].strip())
                except (ValueError, IndexError):
                    pass

            # Look for MPEG-TS packets
            if 'MPEG-TS packets found:' in line:
                try:
                    packets_extracted = int(line.split(':')[1].strip())
                except (ValueError, IndexError):
                    pass

        # Detect output files
        output_dir = Path(self.dontlookup_path).parent / "output"
        if output_dir.exists():
            # Look for generated files matching the capture file name
            capture_name = Path(capture_file).stem
            for file in output_dir.glob(f"{capture_name}*"):
                if file.is_file():
                    # Only include final output files
                    if file.suffix in ['.pcap', '.mpegts'] or str(file).endswith('.ip.pcap'):
                        output_files.append(str(file))

        success = bbframes > 0 or packets_extracted > 0

        return {
            'success': success,
            'capture_file': capture_file,
            'parser_used': parser_type,
            'bbframes': bbframes,
            'packets_extracted': packets_extracted,
            'output_files': output_files,
            'parse_date': datetime.now().isoformat()
        }

    def _generate_butler_commentary(self, parse_results: Dict[str, Any]) -> str:
        """
        Generate British butler commentary on parse results

        Args:
            parse_results: Parsed results

        Returns:
            Butler-style commentary string
        """
        if not parse_results['success']:
            return "The satellite communication analysis encountered difficulties, sir."

        bbframes = parse_results['bbframes']
        packets = parse_results['packets_extracted']

        if bbframes == 0 and packets == 0:
            return "I'm afraid no valid data was extracted from the capture, sir. The satellite signal may be corrupted or using an unsupported encoding."

        if packets > 0:
            return f"Excellent work, sir. Successfully extracted {packets:,} packets from {bbframes:,} BBFrames. The satellite communication has been decoded."
        else:
            return f"Processed {bbframes:,} BBFrames, sir. However, packet extraction yielded no results. Consider trying a different parser variant."

    def _store_in_brain(self, parse_results: Dict[str, Any]):
        """
        Store parse results in AlfredBrain

        Args:
            parse_results: Parsed results to store
        """
        if not self.brain:
            return

        try:
            # Calculate importance based on packets extracted
            packets = parse_results['packets_extracted']

            if packets > 1000:
                importance = 8  # High importance - significant data
            elif packets > 100:
                importance = 6  # Medium importance
            elif packets > 0:
                importance = 4  # Low importance
            else:
                importance = 2  # Minimal importance - failed extraction

            # Prepare findings
            findings = {
                'bbframes': parse_results['bbframes'],
                'packets_extracted': parse_results['packets_extracted'],
                'output_files': parse_results['output_files'],
                'parse_date': parse_results['parse_date'],
                'parser_used': parse_results['parser_used']
            }

            # Store in brain as security scan (satellite communication analysis)
            self.brain.store_security_scan(
                target=parse_results['capture_file'],
                scan_type='dontlookup-dvbs2',
                findings=findings,
                severity_summary=f"Extracted {packets} packets from {parse_results['bbframes']} BBFrames",
                recommendations=[
                    f"Review output files: {', '.join(parse_results['output_files'][:3])}",
                    "Open PCAP files in Wireshark for detailed analysis",
                    "Check for anomalous traffic patterns in extracted data"
                ],
                authorized=True,  # User initiated scan
                notes=parse_results['butler_commentary']
            )

            self.logger.info(f"Stored parse results in brain (importance: {importance})")

        except Exception as e:
            self.logger.error(f"Error storing results in brain: {e}")

    def get_available_parsers(self) -> Dict[str, str]:
        """
        Get list of available parser types

        Returns:
            Dictionary mapping parser IDs to descriptions
        """
        return {
            'dvbs2-ip': 'DVBS2 -> IP (Direct IP extraction)',
            'dvbs2-rev-ip': 'DVBS2 -> Reverse -> IP (Byte-swapped IP)',
            'dvbs2-mpegts': 'DVBS2 -> MPEG-TS (Standard MPEG-TS)',
            'dvbs2-mpegts-crc': 'DVBS2 -> MPEG-TS (Generic CRC)',
            'dvbs2-mpegts-newtec': 'DVBS2 -> MPEG-TS (Newtec CRC)',
            'dvbs2-gse-stdlen-split-ip': 'DVBS2 -> GSE (std len, split frag) -> IP',
            'dvbs2-gse-stdlen-std-ip': 'DVBS2 -> GSE (std len, std frag) -> IP',
            'dvbs2-gse-len2-split-ip': 'DVBS2 -> GSE (hdrlen-2, split frag) -> IP',
            'dvbs2-gse-len2-std-ip': 'DVBS2 -> GSE (hdrlen-2, std frag) -> IP',
            'all': 'Run all parsers (comprehensive analysis)'
        }

    def get_status(self) -> Dict[str, Any]:
        """
        Get scanner status information

        Returns:
            Status dictionary with availability info
        """
        return {
            'available': self.dontlookup_available,
            'enabled': self.enabled,
            'path': self.dontlookup_path,
            'parsers_available': len(self.get_available_parsers()),
            'description': 'DVB-S2(X) satellite communication parser'
        }


# Graceful import handling
DONTLOOKUP_AVAILABLE = False
try:
    scanner = DontLookUpScanner()
    DONTLOOKUP_AVAILABLE = scanner.dontlookup_available
except Exception as e:
    logging.getLogger(__name__).warning(f"DontLookUp scanner initialization failed: {e}")
