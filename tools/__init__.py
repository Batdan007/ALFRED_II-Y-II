"""
Alfred Tools System
Enables Alfred to use tools like Claude Code

Tools available:
- FileRead: Read file contents
- FileWrite: Write/create files
- FileEdit: Edit files with search/replace
- Bash: Execute shell commands
- Grep: Search file contents
- Glob: Find files by pattern
- WebSearch: Search the internet
- WebFetch: Fetch and parse web pages
- WebBrowser: Full browser automation
- WebNews: Search news articles
"""

from .base import Tool, ToolResult
from .file_ops import FileReadTool, FileWriteTool, FileEditTool
from .bash import BashTool
from .search import GrepTool, GlobTool

# Web tools (optional - graceful degradation)
try:
    from .web_tools import (
        WebSearchTool,
        WebFetchTool,
        WebBrowserTool,
        WebNewsSearchTool,
        get_web_tools,
        check_web_tools_availability
    )
    WEB_TOOLS_AVAILABLE = True
except ImportError:
    WEB_TOOLS_AVAILABLE = False
    WebSearchTool = None
    WebFetchTool = None
    WebBrowserTool = None
    WebNewsSearchTool = None
    get_web_tools = None
    check_web_tools_availability = None

__all__ = [
    'Tool',
    'ToolResult',
    'FileReadTool',
    'FileWriteTool',
    'FileEditTool',
    'BashTool',
    'GrepTool',
    'GlobTool',
    # Web tools
    'WebSearchTool',
    'WebFetchTool',
    'WebBrowserTool',
    'WebNewsSearchTool',
    'get_web_tools',
    'check_web_tools_availability',
    'WEB_TOOLS_AVAILABLE',
]
