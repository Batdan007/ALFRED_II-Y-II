"""
Tool Manager
Coordinates all tools and handles execution
"""

import logging
from typing import Dict, List, Any, Optional
from .base import Tool, ToolResult
from .file_ops import FileReadTool, FileWriteTool, FileEditTool
from .bash import BashTool
from .search import GrepTool, GlobTool

# Graceful import for Strix tool (optional dependency)
try:
    from .strix_tool import StrixTool
    STRIX_AVAILABLE = True
except ImportError:
    STRIX_AVAILABLE = False

# Graceful import for DontLookUp tool (optional dependency)
try:
    from .dontlookup_tool import DontLookUpTool
    DONTLOOKUP_AVAILABLE = True
except ImportError:
    DONTLOOKUP_AVAILABLE = False

# Graceful import for CAMDAN tool (optional dependency)
try:
    from .camdan_tool import CAMDANTool
    CAMDAN_AVAILABLE = True
except ImportError:
    CAMDAN_AVAILABLE = False

# Graceful import for Web tools (optional dependency)
try:
    from .web_tools import (
        WebSearchTool,
        WebFetchTool,
        WebBrowserTool,
        WebNewsSearchTool,
        check_web_tools_availability
    )
    WEB_TOOLS_AVAILABLE = True
except ImportError:
    WEB_TOOLS_AVAILABLE = False


class ToolManager:
    """
    Manages all available tools

    Provides:
    - Tool registration
    - Function definitions for AI
    - Tool execution
    - Result formatting
    """

    def __init__(self, privacy_controller=None, brain=None):
        """
        Initialize tool manager

        Args:
            privacy_controller: Optional PrivacyController for security tools
            brain: Optional AlfredBrain for storing results
        """
        self.logger = logging.getLogger(__name__)
        self.tools: Dict[str, Tool] = {}
        self.privacy_controller = privacy_controller
        self.brain = brain

        # Register default tools
        self._register_default_tools()

    def _register_default_tools(self):
        """Register all default tools"""
        default_tools = [
            FileReadTool(),
            FileWriteTool(),
            FileEditTool(),
            BashTool(),
            GrepTool(),
            GlobTool()
        ]

        for tool in default_tools:
            self.register_tool(tool)

        # Register Strix tool if available
        if STRIX_AVAILABLE:
            try:
                strix_tool = StrixTool(
                    privacy_controller=self.privacy_controller,
                    brain=self.brain
                )
                # Only register if Strix is actually installed
                if strix_tool.strix_available:
                    self.register_tool(strix_tool)
                    self.logger.info("Strix security scanner tool registered")
                else:
                    self.logger.info("Strix tool available but scanner not installed")
            except Exception as e:
                self.logger.warning(f"Could not register Strix tool: {e}")

        # Register DontLookUp tool if available
        if DONTLOOKUP_AVAILABLE:
            try:
                dontlookup_tool = DontLookUpTool(brain=self.brain)
                # Only register if DontLookUp is actually installed
                if dontlookup_tool.dontlookup_available:
                    self.register_tool(dontlookup_tool)
                    self.logger.info("DontLookUp DVB-S2 parser tool registered")
                else:
                    self.logger.info("DontLookUp tool available but parser not installed")
            except Exception as e:
                self.logger.warning(f"Could not register DontLookUp tool: {e}")

        # Register CAMDAN tool if available
        if CAMDAN_AVAILABLE:
            try:
                camdan_tool = CAMDANTool(brain=self.brain)
                # Only register if CAMDAN service is running
                if camdan_tool.camdan_available:
                    self.register_tool(camdan_tool)
                    self.logger.info("CAMDAN engineering tool registered")
                else:
                    self.logger.info("CAMDAN tool available but service not running")
            except Exception as e:
                self.logger.warning(f"Could not register CAMDAN tool: {e}")

        # Register Web tools if available
        if WEB_TOOLS_AVAILABLE:
            try:
                availability = check_web_tools_availability()
                web_tools_registered = 0

                # Always register WebSearchTool if duckduckgo-search is available
                if availability.get('duckduckgo_search'):
                    self.register_tool(WebSearchTool())
                    self.register_tool(WebNewsSearchTool())
                    web_tools_registered += 2
                    self.logger.info("Web search tools registered")

                # Register WebFetchTool if httpx and bs4 are available
                if availability.get('httpx') and availability.get('beautifulsoup4'):
                    self.register_tool(WebFetchTool())
                    web_tools_registered += 1
                    self.logger.info("Web fetch tool registered")

                # Register WebBrowserTool if playwright is available
                if availability.get('playwright'):
                    self.register_tool(WebBrowserTool())
                    web_tools_registered += 1
                    self.logger.info("Web browser tool registered")

                if web_tools_registered > 0:
                    self.logger.info(f"Registered {web_tools_registered} web tools")
                else:
                    self.logger.info("Web tools available but dependencies not installed")

            except Exception as e:
                self.logger.warning(f"Could not register web tools: {e}")

        self.logger.info(f"Registered {len(self.tools)} tools")

    def register_tool(self, tool: Tool):
        """
        Register a tool

        Args:
            tool: Tool instance to register
        """
        self.tools[tool.name] = tool
        self.logger.debug(f"Registered tool: {tool.name}")

    def get_tool(self, name: str) -> Optional[Tool]:
        """
        Get tool by name

        Args:
            name: Tool name

        Returns:
            Tool instance or None
        """
        return self.tools.get(name)

    def get_function_definitions(self) -> List[Dict[str, Any]]:
        """
        Get function definitions for all tools

        Returns:
            List of function definitions for Claude/OpenAI API
        """
        return [tool.to_function_definition() for tool in self.tools.values()]

    def execute_tool(self, tool_name: str, **parameters) -> ToolResult:
        """
        Execute a tool with parameters

        Args:
            tool_name: Name of tool to execute
            **parameters: Tool parameters

        Returns:
            ToolResult with output or error
        """
        tool = self.get_tool(tool_name)

        if not tool:
            return ToolResult(
                success=False,
                output="",
                error=f"Tool not found: {tool_name}"
            )

        # Validate parameters
        if not tool.validate_parameters(**parameters):
            return ToolResult(
                success=False,
                output="",
                error=f"Invalid parameters for tool: {tool_name}"
            )

        # Execute tool
        try:
            self.logger.info(f"Executing tool: {tool_name}")
            result = tool.execute(**parameters)
            self.logger.info(f"Tool {tool_name} completed: {'success' if result.success else 'failed'}")
            return result

        except Exception as e:
            self.logger.error(f"Tool {tool_name} error: {e}")
            return ToolResult(
                success=False,
                output="",
                error=f"Tool execution error: {str(e)}"
            )

    def list_tools(self) -> List[str]:
        """
        Get list of available tool names

        Returns:
            List of tool names
        """
        return list(self.tools.keys())

    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a tool

        Args:
            tool_name: Name of tool

        Returns:
            Tool information or None
        """
        tool = self.get_tool(tool_name)
        if not tool:
            return None

        return {
            'name': tool.name,
            'description': tool.description,
            'parameters': tool.parameters
        }
