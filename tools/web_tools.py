"""
ALFRED Web Tools
Full web interaction capabilities: search, browse, and interact

Author: Daniel J Rita (BATDAN)
Part of ALFRED_IV-Y-VI

Requirements:
    pip install httpx beautifulsoup4 duckduckgo-search playwright
    playwright install chromium
"""

import logging
import re
import json
from typing import Optional, Dict, List, Any
from dataclasses import dataclass

# Core tool imports
try:
    from .base import Tool, ToolResult
except ImportError:
    from base import Tool, ToolResult

# HTTP client
try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False

# HTML parsing
try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

# DuckDuckGo search
try:
    from duckduckgo_search import DDGS
    DDGS_AVAILABLE = True
except ImportError:
    DDGS_AVAILABLE = False

# Browser automation
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

logger = logging.getLogger(__name__)


class WebSearchTool(Tool):
    """Search the internet using DuckDuckGo"""

    name = "web_search"
    description = "Search the internet for information. Returns search results with titles, URLs, and snippets."

    parameters = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query"
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of results to return (default: 5)",
                "default": 5
            },
            "region": {
                "type": "string",
                "description": "Region for search results (e.g., 'us-en', 'uk-en')",
                "default": "us-en"
            }
        },
        "required": ["query"]
    }

    def execute(self, query: str, max_results: int = 5, region: str = "us-en") -> ToolResult:
        """Execute web search"""
        if not DDGS_AVAILABLE:
            return ToolResult(
                success=False,
                output="",
                error="duckduckgo-search not installed. Run: pip install duckduckgo-search"
            )

        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, region=region, max_results=max_results))

            if not results:
                return ToolResult(
                    success=True,
                    output="No results found for the query.",
                    metadata={"query": query, "count": 0}
                )

            # Format results
            formatted = []
            for i, r in enumerate(results, 1):
                formatted.append(f"{i}. {r.get('title', 'No title')}")
                formatted.append(f"   URL: {r.get('href', 'No URL')}")
                formatted.append(f"   {r.get('body', 'No description')}")
                formatted.append("")

            return ToolResult(
                success=True,
                output="\n".join(formatted),
                metadata={"query": query, "count": len(results), "results": results}
            )

        except Exception as e:
            logger.error(f"Web search failed: {e}")
            return ToolResult(success=False, output="", error=str(e))


class WebFetchTool(Tool):
    """Fetch and parse web page content"""

    name = "web_fetch"
    description = "Fetch a web page and extract its text content. Good for reading articles, documentation, etc."

    parameters = {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "The URL to fetch"
            },
            "extract_links": {
                "type": "boolean",
                "description": "Also extract links from the page",
                "default": False
            },
            "max_length": {
                "type": "integer",
                "description": "Maximum characters to return (default: 10000)",
                "default": 10000
            }
        },
        "required": ["url"]
    }

    def execute(self, url: str, extract_links: bool = False, max_length: int = 10000) -> ToolResult:
        """Fetch and parse web page"""
        if not HTTPX_AVAILABLE:
            return ToolResult(
                success=False,
                output="",
                error="httpx not installed. Run: pip install httpx"
            )

        if not BS4_AVAILABLE:
            return ToolResult(
                success=False,
                output="",
                error="beautifulsoup4 not installed. Run: pip install beautifulsoup4"
            )

        try:
            # Fetch the page
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }

            with httpx.Client(follow_redirects=True, timeout=30) as client:
                response = client.get(url, headers=headers)
                response.raise_for_status()

            # Parse HTML
            soup = BeautifulSoup(response.text, "html.parser")

            # Remove script and style elements
            for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
                element.decompose()

            # Get title
            title = soup.title.string if soup.title else "No title"

            # Get main content
            # Try to find main content area
            main = soup.find("main") or soup.find("article") or soup.find("div", {"class": re.compile(r"content|article|post")})
            if main:
                text = main.get_text(separator="\n", strip=True)
            else:
                text = soup.get_text(separator="\n", strip=True)

            # Clean up whitespace
            lines = [line.strip() for line in text.split("\n") if line.strip()]
            text = "\n".join(lines)

            # Truncate if needed
            if len(text) > max_length:
                text = text[:max_length] + "\n\n[Content truncated...]"

            output = f"Title: {title}\nURL: {url}\n\n{text}"

            metadata = {"url": url, "title": title, "length": len(text)}

            # Extract links if requested
            if extract_links:
                links = []
                for a in soup.find_all("a", href=True):
                    href = a["href"]
                    link_text = a.get_text(strip=True)[:50]
                    if href.startswith("http"):
                        links.append({"text": link_text, "url": href})

                metadata["links"] = links[:20]  # Limit to 20 links
                output += "\n\n--- Links ---\n"
                for link in links[:20]:
                    output += f"- {link['text']}: {link['url']}\n"

            return ToolResult(success=True, output=output, metadata=metadata)

        except httpx.HTTPStatusError as e:
            return ToolResult(success=False, output="", error=f"HTTP {e.response.status_code}: {str(e)}")
        except Exception as e:
            logger.error(f"Web fetch failed: {e}")
            return ToolResult(success=False, output="", error=str(e))


class WebBrowserTool(Tool):
    """
    Full browser automation for interactive web tasks.
    Can click buttons, fill forms, navigate, and extract content.
    """

    name = "web_browser"
    description = """Automate web browser interactions. Can:
- Navigate to URLs
- Click elements (buttons, links)
- Fill form fields
- Take screenshots
- Extract page content
Use for interactive websites that require JavaScript or user actions."""

    parameters = {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "URL to navigate to (optional if already on a page)"
            },
            "action": {
                "type": "string",
                "enum": ["navigate", "click", "fill", "screenshot", "content", "scroll"],
                "description": "Action to perform"
            },
            "selector": {
                "type": "string",
                "description": "CSS selector for the element to interact with"
            },
            "value": {
                "type": "string",
                "description": "Value to fill in (for 'fill' action)"
            },
            "wait_for": {
                "type": "string",
                "description": "CSS selector to wait for before proceeding"
            }
        },
        "required": ["action"]
    }

    _browser = None
    _page = None

    def _ensure_browser(self):
        """Ensure browser is running"""
        if not PLAYWRIGHT_AVAILABLE:
            raise RuntimeError("playwright not installed. Run: pip install playwright && playwright install chromium")

        if self._browser is None:
            self._playwright = sync_playwright().start()
            self._browser = self._playwright.chromium.launch(headless=True)
            self._page = self._browser.new_page()

    def execute(
        self,
        action: str,
        url: str = None,
        selector: str = None,
        value: str = None,
        wait_for: str = None
    ) -> ToolResult:
        """Execute browser action"""
        try:
            self._ensure_browser()

            # Navigate if URL provided
            if url and action == "navigate":
                self._page.goto(url, wait_until="networkidle")
                title = self._page.title()
                return ToolResult(
                    success=True,
                    output=f"Navigated to: {url}\nTitle: {title}",
                    metadata={"url": url, "title": title}
                )

            elif url:
                self._page.goto(url, wait_until="networkidle")

            # Wait for element if specified
            if wait_for:
                self._page.wait_for_selector(wait_for, timeout=10000)

            # Perform action
            if action == "click":
                if not selector:
                    return ToolResult(success=False, output="", error="Selector required for click action")
                self._page.click(selector)
                self._page.wait_for_load_state("networkidle")
                return ToolResult(
                    success=True,
                    output=f"Clicked element: {selector}",
                    metadata={"action": "click", "selector": selector}
                )

            elif action == "fill":
                if not selector or not value:
                    return ToolResult(success=False, output="", error="Selector and value required for fill action")
                self._page.fill(selector, value)
                return ToolResult(
                    success=True,
                    output=f"Filled '{selector}' with value",
                    metadata={"action": "fill", "selector": selector}
                )

            elif action == "screenshot":
                import tempfile
                import os
                screenshot_path = os.path.join(tempfile.gettempdir(), "alfred_screenshot.png")
                self._page.screenshot(path=screenshot_path)
                return ToolResult(
                    success=True,
                    output=f"Screenshot saved to: {screenshot_path}",
                    metadata={"path": screenshot_path}
                )

            elif action == "content":
                content = self._page.content()
                soup = BeautifulSoup(content, "html.parser") if BS4_AVAILABLE else None

                if soup:
                    for element in soup(["script", "style"]):
                        element.decompose()
                    text = soup.get_text(separator="\n", strip=True)
                else:
                    text = content

                # Truncate if too long
                if len(text) > 10000:
                    text = text[:10000] + "\n\n[Truncated...]"

                return ToolResult(
                    success=True,
                    output=text,
                    metadata={"url": self._page.url, "title": self._page.title()}
                )

            elif action == "scroll":
                direction = value or "down"
                if direction == "down":
                    self._page.evaluate("window.scrollBy(0, window.innerHeight)")
                elif direction == "up":
                    self._page.evaluate("window.scrollBy(0, -window.innerHeight)")
                elif direction == "top":
                    self._page.evaluate("window.scrollTo(0, 0)")
                elif direction == "bottom":
                    self._page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

                return ToolResult(
                    success=True,
                    output=f"Scrolled {direction}",
                    metadata={"action": "scroll", "direction": direction}
                )

            else:
                return ToolResult(success=False, output="", error=f"Unknown action: {action}")

        except Exception as e:
            logger.error(f"Browser action failed: {e}")
            return ToolResult(success=False, output="", error=str(e))

    def close(self):
        """Close the browser"""
        if self._browser:
            self._browser.close()
            self._playwright.stop()
            self._browser = None
            self._page = None


class WebNewsSearchTool(Tool):
    """Search for news articles"""

    name = "web_news"
    description = "Search for recent news articles on a topic"

    parameters = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "News search query"
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum results (default: 5)",
                "default": 5
            }
        },
        "required": ["query"]
    }

    def execute(self, query: str, max_results: int = 5) -> ToolResult:
        """Search news"""
        if not DDGS_AVAILABLE:
            return ToolResult(
                success=False,
                output="",
                error="duckduckgo-search not installed"
            )

        try:
            with DDGS() as ddgs:
                results = list(ddgs.news(query, max_results=max_results))

            if not results:
                return ToolResult(
                    success=True,
                    output="No news found for the query.",
                    metadata={"query": query, "count": 0}
                )

            formatted = []
            for i, r in enumerate(results, 1):
                formatted.append(f"{i}. {r.get('title', 'No title')}")
                formatted.append(f"   Source: {r.get('source', 'Unknown')}")
                formatted.append(f"   Date: {r.get('date', 'Unknown')}")
                formatted.append(f"   URL: {r.get('url', 'No URL')}")
                formatted.append(f"   {r.get('body', '')[:200]}")
                formatted.append("")

            return ToolResult(
                success=True,
                output="\n".join(formatted),
                metadata={"query": query, "count": len(results)}
            )

        except Exception as e:
            return ToolResult(success=False, output="", error=str(e))


# Convenience function to get all web tools
def get_web_tools() -> List[Tool]:
    """Get all web tools"""
    return [
        WebSearchTool(),
        WebFetchTool(),
        WebBrowserTool(),
        WebNewsSearchTool()
    ]


# Check availability
def check_web_tools_availability() -> Dict[str, bool]:
    """Check which web tool dependencies are available"""
    return {
        "httpx": HTTPX_AVAILABLE,
        "beautifulsoup4": BS4_AVAILABLE,
        "duckduckgo_search": DDGS_AVAILABLE,
        "playwright": PLAYWRIGHT_AVAILABLE
    }


if __name__ == "__main__":
    # Test web tools
    print("Web Tools Availability:")
    for name, available in check_web_tools_availability().items():
        status = "OK" if available else "MISSING"
        print(f"  {name}: {status}")

    print("\n--- Testing Web Search ---")
    search = WebSearchTool()
    result = search.execute("Gary Indiana weather today")
    print(result.output if result.success else f"Error: {result.error}")
