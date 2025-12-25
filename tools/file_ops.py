"""
File Operation Tools
Read, write, and edit files
"""

import os
from pathlib import Path
from typing import Dict, Any
from .base import Tool, ToolResult


class FileReadTool(Tool):
    """Read file contents"""

    @property
    def name(self) -> str:
        return "read_file"

    @property
    def description(self) -> str:
        return "Read the contents of a file. Returns the full file content."

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Absolute or relative path to the file to read"
                }
            },
            "required": ["file_path"]
        }

    def execute(self, file_path: str) -> ToolResult:
        """
        Read file contents

        Args:
            file_path: Path to file

        Returns:
            ToolResult with file contents
        """
        try:
            path = Path(file_path).resolve()

            if not path.exists():
                return ToolResult(
                    success=False,
                    output="",
                    error=f"File not found: {file_path}"
                )

            if not path.is_file():
                return ToolResult(
                    success=False,
                    output="",
                    error=f"Not a file: {file_path}"
                )

            # Read file
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Add line numbers (like cat -n)
            lines = content.split('\n')
            numbered_lines = [f"{i+1:6d}\t{line}" for i, line in enumerate(lines)]
            output = '\n'.join(numbered_lines)

            return ToolResult(
                success=True,
                output=output,
                metadata={
                    'file_path': str(path),
                    'size': len(content),
                    'lines': len(lines)
                }
            )

        except UnicodeDecodeError:
            return ToolResult(
                success=False,
                output="",
                error=f"Cannot read file (binary or unsupported encoding): {file_path}"
            )
        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=f"Error reading file: {str(e)}"
            )


class FileWriteTool(Tool):
    """Write content to a file"""

    @property
    def name(self) -> str:
        return "write_file"

    @property
    def description(self) -> str:
        return "Write content to a file. Creates the file if it doesn't exist, overwrites if it does."

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the file to write"
                },
                "content": {
                    "type": "string",
                    "description": "Content to write to the file"
                }
            },
            "required": ["file_path", "content"]
        }

    def execute(self, file_path: str, content: str) -> ToolResult:
        """
        Write content to file

        Args:
            file_path: Path to file
            content: Content to write

        Returns:
            ToolResult with success status
        """
        try:
            path = Path(file_path).resolve()

            # Create parent directories if needed
            path.parent.mkdir(parents=True, exist_ok=True)

            # Write file
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)

            return ToolResult(
                success=True,
                output=f"Successfully wrote {len(content)} characters to {file_path}",
                metadata={
                    'file_path': str(path),
                    'size': len(content)
                }
            )

        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=f"Error writing file: {str(e)}"
            )


class FileEditTool(Tool):
    """Edit file with search and replace"""

    @property
    def name(self) -> str:
        return "edit_file"

    @property
    def description(self) -> str:
        return "Edit a file by replacing old_text with new_text. Exact string match required."

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the file to edit"
                },
                "old_text": {
                    "type": "string",
                    "description": "Text to find (must match exactly)"
                },
                "new_text": {
                    "type": "string",
                    "description": "Text to replace with"
                }
            },
            "required": ["file_path", "old_text", "new_text"]
        }

    def execute(self, file_path: str, old_text: str, new_text: str) -> ToolResult:
        """
        Edit file with search/replace

        Args:
            file_path: Path to file
            old_text: Text to find
            new_text: Replacement text

        Returns:
            ToolResult with success status
        """
        try:
            path = Path(file_path).resolve()

            if not path.exists():
                return ToolResult(
                    success=False,
                    output="",
                    error=f"File not found: {file_path}"
                )

            # Read current content
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check if old_text exists
            if old_text not in content:
                return ToolResult(
                    success=False,
                    output="",
                    error=f"Text not found in file: {old_text[:100]}..."
                )

            # Replace
            new_content = content.replace(old_text, new_text, 1)  # Replace first occurrence

            # Write back
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            return ToolResult(
                success=True,
                output=f"Successfully edited {file_path}",
                metadata={
                    'file_path': str(path),
                    'old_length': len(content),
                    'new_length': len(new_content)
                }
            )

        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=f"Error editing file: {str(e)}"
            )
