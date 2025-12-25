"""
Code Search Tools
Search for files and content
"""

import os
import re
from pathlib import Path
from typing import Dict, Any, List
from .base import Tool, ToolResult


class GlobTool(Tool):
    """Find files by pattern"""

    @property
    def name(self) -> str:
        return "glob"

    @property
    def description(self) -> str:
        return "Find files matching a glob pattern (e.g., '**/*.py', 'src/**/*.js')"

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": "Glob pattern to match files (e.g., '**/*.py')"
                },
                "path": {
                    "type": "string",
                    "description": "Directory to search in (default: current directory)",
                    "default": "."
                }
            },
            "required": ["pattern"]
        }

    def execute(self, pattern: str, path: str = ".") -> ToolResult:
        """
        Find files matching pattern

        Args:
            pattern: Glob pattern
            path: Directory to search (default: current)

        Returns:
            ToolResult with list of matching files
        """
        try:
            search_path = Path(path).resolve()

            if not search_path.exists():
                return ToolResult(
                    success=False,
                    output="",
                    error=f"Path not found: {path}"
                )

            # Find matching files
            matches = list(search_path.glob(pattern))

            # Sort by modification time (most recent first)
            matches.sort(key=lambda p: p.stat().st_mtime, reverse=True)

            if not matches:
                return ToolResult(
                    success=True,
                    output=f"No files found matching: {pattern}",
                    metadata={'count': 0}
                )

            # Format output
            output_lines = [f"Found {len(matches)} files matching '{pattern}':\n"]
            for match in matches:
                rel_path = match.relative_to(search_path) if match.is_relative_to(search_path) else match
                output_lines.append(str(rel_path))

            return ToolResult(
                success=True,
                output='\n'.join(output_lines),
                metadata={
                    'count': len(matches),
                    'files': [str(m) for m in matches]
                }
            )

        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=f"Error searching files: {str(e)}"
            )


class GrepTool(Tool):
    """Search file contents with regex"""

    @property
    def name(self) -> str:
        return "grep"

    @property
    def description(self) -> str:
        return "Search for text pattern in files. Returns matching lines with line numbers."

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": "Regular expression pattern to search for"
                },
                "path": {
                    "type": "string",
                    "description": "File or directory to search in (default: current directory)",
                    "default": "."
                },
                "file_pattern": {
                    "type": "string",
                    "description": "Glob pattern to filter files (e.g., '*.py')",
                    "default": "*"
                },
                "case_sensitive": {
                    "type": "boolean",
                    "description": "Case sensitive search (default: false)",
                    "default": False
                }
            },
            "required": ["pattern"]
        }

    def execute(self, pattern: str, path: str = ".", file_pattern: str = "*",
                case_sensitive: bool = False) -> ToolResult:
        """
        Search for pattern in files

        Args:
            pattern: Regex pattern to search
            path: File or directory to search
            file_pattern: Glob pattern for files to search
            case_sensitive: Case sensitive search

        Returns:
            ToolResult with matching lines
        """
        try:
            search_path = Path(path).resolve()

            if not search_path.exists():
                return ToolResult(
                    success=False,
                    output="",
                    error=f"Path not found: {path}"
                )

            # Compile regex
            flags = 0 if case_sensitive else re.IGNORECASE
            regex = re.compile(pattern, flags)

            matches = []

            # Search files
            if search_path.is_file():
                files_to_search = [search_path]
            else:
                files_to_search = list(search_path.rglob(file_pattern))

            for file_path in files_to_search:
                if not file_path.is_file():
                    continue

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        for line_num, line in enumerate(f, 1):
                            if regex.search(line):
                                matches.append({
                                    'file': str(file_path),
                                    'line_num': line_num,
                                    'line': line.rstrip()
                                })
                except (UnicodeDecodeError, PermissionError):
                    # Skip binary files or files we can't read
                    continue

            if not matches:
                return ToolResult(
                    success=True,
                    output=f"No matches found for pattern: {pattern}",
                    metadata={'count': 0}
                )

            # Format output
            output_lines = [f"Found {len(matches)} matches for '{pattern}':\n"]
            for match in matches:
                output_lines.append(
                    f"{match['file']}:{match['line_num']}: {match['line']}"
                )

            return ToolResult(
                success=True,
                output='\n'.join(output_lines),
                metadata={
                    'count': len(matches),
                    'matches': matches
                }
            )

        except re.error as e:
            return ToolResult(
                success=False,
                output="",
                error=f"Invalid regex pattern: {str(e)}"
            )
        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=f"Error searching files: {str(e)}"
            )
