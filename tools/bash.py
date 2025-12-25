"""
Bash Execution Tool
Execute shell commands
"""

import subprocess
import platform
from typing import Dict, Any
from .base import Tool, ToolResult


class BashTool(Tool):
    """Execute bash/shell commands"""

    def __init__(self, timeout: int = 30):
        """
        Initialize Bash tool

        Args:
            timeout: Command timeout in seconds (default: 30)
        """
        self.timeout = timeout
        self.is_windows = platform.system() == 'Windows'

    @property
    def name(self) -> str:
        return "bash"

    @property
    def description(self) -> str:
        return "Execute a bash command and return the output. Use for running scripts, git commands, npm, etc."

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The bash command to execute"
                },
                "timeout": {
                    "type": "integer",
                    "description": "Timeout in seconds (optional, default: 30)",
                    "default": 30
                }
            },
            "required": ["command"]
        }

    def execute(self, command: str, timeout: int = None) -> ToolResult:
        """
        Execute bash command

        Args:
            command: Command to execute
            timeout: Timeout in seconds (optional)

        Returns:
            ToolResult with command output
        """
        if timeout is None:
            timeout = self.timeout

        try:
            # On Windows, use PowerShell or cmd
            if self.is_windows:
                # Try to run in PowerShell if available, else cmd
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    encoding='utf-8',
                    errors='replace'
                )
            else:
                # Unix: use bash
                result = subprocess.run(
                    command,
                    shell=True,
                    executable='/bin/bash',
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )

            # Combine stdout and stderr
            output = result.stdout
            if result.stderr:
                output += f"\n[STDERR]:\n{result.stderr}"

            success = result.returncode == 0

            return ToolResult(
                success=success,
                output=output or "(no output)",
                error=None if success else f"Command exited with code {result.returncode}",
                metadata={
                    'return_code': result.returncode,
                    'command': command
                }
            )

        except subprocess.TimeoutExpired:
            return ToolResult(
                success=False,
                output="",
                error=f"Command timed out after {timeout} seconds"
            )
        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=f"Error executing command: {str(e)}"
            )
