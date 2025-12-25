"""
Base Tool Class
Foundation for all Alfred tools
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass
import json


@dataclass
class ToolResult:
    """Result from tool execution"""
    success: bool
    output: str
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'success': self.success,
            'output': self.output,
            'error': self.error,
            'metadata': self.metadata or {}
        }


class Tool(ABC):
    """
    Base class for all tools

    Each tool must implement:
    - name: Tool identifier
    - description: What the tool does
    - parameters: JSON schema for parameters
    - execute: Run the tool
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name (used by AI for function calling)"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """What this tool does"""
        pass

    @property
    @abstractmethod
    def parameters(self) -> Dict[str, Any]:
        """
        JSON Schema for tool parameters

        Example:
        {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to file"
                }
            },
            "required": ["file_path"]
        }
        """
        pass

    @abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        """
        Execute the tool with given parameters

        Args:
            **kwargs: Parameters matching the schema

        Returns:
            ToolResult with output or error
        """
        pass

    def to_function_definition(self) -> Dict[str, Any]:
        """
        Convert tool to Claude/OpenAI function definition

        Returns:
            Function definition for AI function calling
        """
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters
        }

    def validate_parameters(self, **kwargs) -> bool:
        """
        Validate parameters against schema

        Args:
            **kwargs: Parameters to validate

        Returns:
            True if valid, False otherwise
        """
        schema = self.parameters
        required = schema.get('required', [])

        # Check required parameters
        for param in required:
            if param not in kwargs:
                return False

        return True
