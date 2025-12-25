#!/usr/bin/env python3
"""
Crawl4AI MCP Server - Advanced Web Intelligence for Claude Code

Exposes Crawl4AI's powerful web crawling capabilities to Claude Code via MCP.

Tools provided:
- crawl_url: Crawl single URL with LLM-optimized markdown extraction
- crawl_batch: Crawl multiple URLs concurrently
- deep_crawl: Deep crawl following links (BFS strategy)
- research_topic: Full RAG pipeline (crawl → chunk → embed → store)
- extract_structured: Extract structured data with CSS selectors
- extract_with_llm: LLM-powered intelligent extraction
- search_knowledge: Search vector knowledge base
- ask_question: RAG-powered question answering
- get_crawl_stats: Get crawler statistics
- clear_cache: Clear crawler cache

Part of ALFRED SYSTEMS Phase 1: Foundation
"""

import asyncio
import json
from typing import Any, Optional, List, Dict
from pathlib import Path
from datetime import datetime
import sys
import logging

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp import types
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    Server = None
    stdio_server = None
    # Create mock types for graceful degradation
    class MockTypes:
        class Tool: pass
        class TextContent: pass
        class CallToolResult: pass
    types = MockTypes()
    print("MCP not available. Install with: pip install mcp", file=sys.stderr)

# Check if Crawl4AI components are available
try:
    from capabilities.rag.crawler_advanced import AdvancedCrawler, CRAWL4AI_AVAILABLE
    from capabilities.rag.rag_module import RAGSystem
    from capabilities.rag.vector_knowledge import VectorKnowledgeBase
    CRAWLER_AVAILABLE = CRAWL4AI_AVAILABLE
except ImportError as e:
    CRAWLER_AVAILABLE = False
    AdvancedCrawler = None  # Placeholder for type hints
    RAGSystem = None
    VectorKnowledgeBase = None
    logging.warning(f"Crawl4AI components not available: {e}")

# Import AlfredBrain for persistent storage
try:
    from core.brain import AlfredBrain
    BRAIN_AVAILABLE = True
except ImportError:
    BRAIN_AVAILABLE = False

# Import Fabric patterns for content analysis
try:
    from capabilities.knowledge.fabric_patterns import FabricPatterns
    FABRIC_AVAILABLE = True
except ImportError:
    FABRIC_AVAILABLE = False


class Crawl4AIMCPServer:
    """MCP Server for Crawl4AI Web Intelligence"""

    def __init__(self):
        """Initialize Crawl4AI MCP Server"""
        if not MCP_AVAILABLE:
            logging.warning("Crawl4AI MCP Server not available - MCP library not installed")
            self.server = None
            return
        self.server = Server("crawl4ai-intelligence")

        # Initialize components
        self.brain = AlfredBrain() if BRAIN_AVAILABLE else None
        self.crawler = None  # Created on demand
        self.rag = None  # Created on demand
        self.kb = None  # Knowledge base
        self.fabric = FabricPatterns() if FABRIC_AVAILABLE else None

        # Statistics
        self.session_stats = {
            'urls_crawled': 0,
            'pages_stored': 0,
            'queries_answered': 0,
            'errors': 0,
            'session_start': datetime.now().isoformat()
        }

        self._setup_handlers()
        logging.info("Crawl4AI MCP Server initialized")

    async def _get_crawler(self) -> Optional[AdvancedCrawler]:
        """Get or create crawler instance"""
        if not CRAWLER_AVAILABLE:
            return None
        if not self.crawler:
            self.crawler = AdvancedCrawler(headless=True, verbose=False)
            await self.crawler.start()
        return self.crawler

    async def _get_rag(self) -> Optional[RAGSystem]:
        """Get or create RAG system"""
        if not CRAWLER_AVAILABLE:
            return None
        if not self.rag:
            self.rag = RAGSystem()
        return self.rag

    def _setup_handlers(self):
        """Setup MCP request handlers"""

        @self.server.list_tools()
        async def list_tools() -> list[types.Tool]:
            """List all available tools"""
            tools = []

            if CRAWLER_AVAILABLE:
                tools.extend([
                    # Core Crawling Tools
                    types.Tool(
                        name="crawl4ai_crawl_url",
                        description="Crawl a single URL and extract LLM-optimized markdown content. Returns clean markdown, links, images, and metadata.",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "url": {"type": "string", "description": "URL to crawl"},
                                "wait_for_selector": {"type": "string", "description": "CSS selector to wait for before extracting (for dynamic content)"},
                                "js_code": {"type": "string", "description": "JavaScript to execute before extraction (for SPAs)"},
                                "extract_links": {"type": "boolean", "description": "Extract all links from page", "default": True},
                                "extract_images": {"type": "boolean", "description": "Extract image URLs", "default": True},
                                "cache_mode": {
                                    "type": "string",
                                    "description": "Cache strategy",
                                    "enum": ["enabled", "disabled", "bypass", "read_only", "write_only"],
                                    "default": "enabled"
                                },
                            },
                            "required": ["url"],
                        },
                    ),
                    types.Tool(
                        name="crawl4ai_crawl_batch",
                        description="Crawl multiple URLs concurrently. Efficient for researching multiple sources at once.",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "urls": {
                                    "type": "array",
                                    "description": "List of URLs to crawl",
                                    "items": {"type": "string"}
                                },
                                "max_concurrent": {"type": "integer", "description": "Max concurrent crawls", "default": 5},
                            },
                            "required": ["urls"],
                        },
                    ),
                    types.Tool(
                        name="crawl4ai_deep_crawl",
                        description="Deep crawl starting from a URL, following links up to specified depth. Great for site-wide research.",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "start_url": {"type": "string", "description": "Starting URL"},
                                "max_depth": {"type": "integer", "description": "Maximum link depth", "default": 2},
                                "max_pages": {"type": "integer", "description": "Maximum pages to crawl", "default": 50},
                                "same_domain_only": {"type": "boolean", "description": "Only crawl same domain", "default": True},
                                "url_patterns": {
                                    "type": "array",
                                    "description": "URL patterns to include (regex)",
                                    "items": {"type": "string"}
                                },
                                "exclude_patterns": {
                                    "type": "array",
                                    "description": "URL patterns to exclude (regex)",
                                    "items": {"type": "string"}
                                },
                            },
                            "required": ["start_url"],
                        },
                    ),

                    # Research & RAG Tools
                    types.Tool(
                        name="crawl4ai_research_topic",
                        description="Full research pipeline: crawl URL(s), chunk content, embed in vector DB, ready for Q&A. Use this for building knowledge bases.",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "urls": {
                                    "type": "array",
                                    "description": "URLs to research",
                                    "items": {"type": "string"}
                                },
                                "topic": {"type": "string", "description": "Topic name for organizing knowledge"},
                                "deep_crawl": {"type": "boolean", "description": "Enable deep crawl for each URL", "default": False},
                                "max_depth": {"type": "integer", "description": "Depth for deep crawl", "default": 2},
                                "store_in_brain": {"type": "boolean", "description": "Also store in Alfred Brain", "default": True},
                            },
                            "required": ["urls"],
                        },
                    ),
                    types.Tool(
                        name="crawl4ai_ask_question",
                        description="Ask a question using RAG. Searches vector knowledge base for relevant context and generates answer.",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "question": {"type": "string", "description": "Question to answer"},
                                "n_contexts": {"type": "integer", "description": "Number of context chunks to use", "default": 5},
                                "min_similarity": {"type": "number", "description": "Minimum similarity score (0-1)", "default": 0.3},
                                "include_sources": {"type": "boolean", "description": "Include source URLs", "default": True},
                            },
                            "required": ["question"],
                        },
                    ),
                    types.Tool(
                        name="crawl4ai_search_knowledge",
                        description="Search the vector knowledge base for relevant content without generating an answer.",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "query": {"type": "string", "description": "Search query"},
                                "n_results": {"type": "integer", "description": "Number of results", "default": 10},
                                "filter_topic": {"type": "string", "description": "Filter by topic"},
                            },
                            "required": ["query"],
                        },
                    ),

                    # Extraction Tools
                    types.Tool(
                        name="crawl4ai_extract_structured",
                        description="Extract structured data from a page using CSS selectors. Returns JSON data.",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "url": {"type": "string", "description": "URL to extract from"},
                                "schema": {
                                    "type": "object",
                                    "description": "Extraction schema with CSS selectors",
                                    "additionalProperties": True
                                },
                            },
                            "required": ["url", "schema"],
                        },
                    ),
                    types.Tool(
                        name="crawl4ai_extract_with_llm",
                        description="Use LLM to intelligently extract specific information from a page.",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "url": {"type": "string", "description": "URL to extract from"},
                                "instruction": {"type": "string", "description": "What to extract (natural language instruction)"},
                            },
                            "required": ["url", "instruction"],
                        },
                    ),

                    # Management Tools
                    types.Tool(
                        name="crawl4ai_get_stats",
                        description="Get crawler and knowledge base statistics",
                        inputSchema={
                            "type": "object",
                            "properties": {},
                        },
                    ),
                    types.Tool(
                        name="crawl4ai_clear_knowledge",
                        description="Clear the vector knowledge base (careful - deletes all stored research)",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "confirm": {"type": "boolean", "description": "Must be true to confirm deletion"},
                            },
                            "required": ["confirm"],
                        },
                    ),
                ])

            # Fabric pattern analysis (if available)
            if FABRIC_AVAILABLE:
                tools.append(
                    types.Tool(
                        name="crawl4ai_analyze_content",
                        description="Analyze crawled content using Fabric AI patterns (extract_wisdom, summarize, analyze_claims, etc.)",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "content": {"type": "string", "description": "Content to analyze (or URL to crawl first)"},
                                "pattern": {
                                    "type": "string",
                                    "description": "Fabric pattern to apply",
                                    "enum": ["extract_wisdom", "summarize", "analyze_claims", "extract_insights",
                                             "extract_main_idea", "analyze_paper", "create_summary", "rate_content"]
                                },
                                "crawl_url": {"type": "string", "description": "Optional: URL to crawl for content"},
                            },
                            "required": ["pattern"],
                        },
                    )
                )

            return tools

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> list[types.TextContent]:
            """Handle tool calls"""

            try:
                # ============== CORE CRAWLING ==============
                if name == "crawl4ai_crawl_url":
                    crawler = await self._get_crawler()
                    if not crawler:
                        return [types.TextContent(type="text", text="Crawl4AI not available. Check installation.")]

                    result = await crawler.crawl_url(
                        url=arguments["url"],
                        wait_for_selector=arguments.get("wait_for_selector"),
                        js_code=arguments.get("js_code"),
                        cache_mode=arguments.get("cache_mode")
                    )

                    self.session_stats['urls_crawled'] += 1

                    # Store in brain if available
                    if self.brain and result['success']:
                        self.brain.cache_web_content(
                            url=arguments["url"],
                            content=result.get('markdown', '')[:10000],  # Limit size
                            metadata={
                                'links_count': len(result.get('links', [])),
                                'images_count': len(result.get('media', {}).get('images', [])),
                                'crawled_at': result.get('crawled_at')
                            }
                        )

                    # Format response
                    response = {
                        'url': result['url'],
                        'success': result['success'],
                        'markdown_length': len(result.get('markdown', '')),
                        'links_found': len(result.get('links', [])),
                        'images_found': len(result.get('media', {}).get('images', [])),
                        'markdown_preview': result.get('markdown', '')[:2000] + '...' if result.get('markdown') else None,
                        'error': result.get('error')
                    }

                    return [types.TextContent(type="text", text=json.dumps(response, indent=2))]

                elif name == "crawl4ai_crawl_batch":
                    crawler = await self._get_crawler()
                    if not crawler:
                        return [types.TextContent(type="text", text="Crawl4AI not available.")]

                    results = await crawler.crawl_urls_batch(
                        urls=arguments["urls"],
                        max_concurrent=arguments.get("max_concurrent", 5)
                    )

                    self.session_stats['urls_crawled'] += len(results)

                    summary = {
                        'total_urls': len(results),
                        'successful': sum(1 for r in results if r.get('success')),
                        'failed': sum(1 for r in results if not r.get('success')),
                        'results': [
                            {
                                'url': r['url'],
                                'success': r['success'],
                                'markdown_length': len(r.get('markdown', '')) if r.get('success') else 0,
                                'error': r.get('error')
                            }
                            for r in results
                        ]
                    }

                    return [types.TextContent(type="text", text=json.dumps(summary, indent=2))]

                elif name == "crawl4ai_deep_crawl":
                    crawler = await self._get_crawler()
                    if not crawler:
                        return [types.TextContent(type="text", text="Crawl4AI not available.")]

                    results = await crawler.deep_crawl(
                        start_url=arguments["start_url"],
                        max_depth=arguments.get("max_depth", 2),
                        max_pages=arguments.get("max_pages", 50),
                        same_domain_only=arguments.get("same_domain_only", True),
                        url_patterns=arguments.get("url_patterns"),
                        exclude_patterns=arguments.get("exclude_patterns")
                    )

                    self.session_stats['urls_crawled'] += len(results)

                    summary = {
                        'start_url': arguments["start_url"],
                        'pages_crawled': len(results),
                        'total_content_length': sum(len(r.get('markdown', '')) for r in results),
                        'pages': [
                            {
                                'url': r.get('url', 'unknown'),
                                'success': r.get('success', False),
                                'markdown_length': len(r.get('markdown', ''))
                            }
                            for r in results
                        ]
                    }

                    return [types.TextContent(type="text", text=json.dumps(summary, indent=2))]

                # ============== RESEARCH & RAG ==============
                elif name == "crawl4ai_research_topic":
                    rag = await self._get_rag()
                    if not rag:
                        return [types.TextContent(type="text", text="RAG system not available.")]

                    urls = arguments["urls"]
                    topic = arguments.get("topic", "general")
                    deep_crawl = arguments.get("deep_crawl", False)

                    results = []
                    for url in urls:
                        if deep_crawl:
                            result = await rag.deep_research(
                                start_url=url,
                                max_depth=arguments.get("max_depth", 2),
                                max_pages=20
                            )
                        else:
                            result = await rag.research_url(
                                url=url,
                                metadata={'topic': topic}
                            )
                        results.append(result)

                    # Store in brain
                    if self.brain and arguments.get("store_in_brain", True):
                        total_chunks = sum(r.get('num_chunks', 0) or r.get('total_chunks', 0) for r in results)
                        self.brain.store_knowledge(
                            category="research",
                            key=topic,
                            value=f"Researched {len(urls)} URLs with {total_chunks} chunks stored",
                            importance=7
                        )

                    self.session_stats['pages_stored'] += sum(r.get('num_chunks', 0) or r.get('total_chunks', 0) for r in results)

                    summary = {
                        'topic': topic,
                        'urls_researched': len(urls),
                        'successful': sum(1 for r in results if r.get('success')),
                        'total_chunks_stored': sum(r.get('num_chunks', 0) or r.get('total_chunks', 0) for r in results),
                        'ready_for_questions': True
                    }

                    return [types.TextContent(type="text", text=json.dumps(summary, indent=2))]

                elif name == "crawl4ai_ask_question":
                    rag = await self._get_rag()
                    if not rag:
                        return [types.TextContent(type="text", text="RAG system not available.")]

                    result = await rag.ask(
                        question=arguments["question"],
                        n_contexts=arguments.get("n_contexts", 5),
                        min_similarity=arguments.get("min_similarity", 0.3),
                        include_sources=arguments.get("include_sources", True)
                    )

                    self.session_stats['queries_answered'] += 1

                    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

                elif name == "crawl4ai_search_knowledge":
                    rag = await self._get_rag()
                    if not rag:
                        return [types.TextContent(type="text", text="RAG system not available.")]

                    results = rag.kb.search(
                        query=arguments["query"],
                        n_results=arguments.get("n_results", 10)
                    )

                    # Format results
                    formatted = {
                        'query': arguments["query"],
                        'num_results': len(results.get('results', [])),
                        'results': [
                            {
                                'text': r['text'][:500] + '...' if len(r['text']) > 500 else r['text'],
                                'similarity': r.get('similarity'),
                                'url': r.get('metadata', {}).get('url'),
                                'topic': r.get('metadata', {}).get('topic')
                            }
                            for r in results.get('results', [])
                        ]
                    }

                    return [types.TextContent(type="text", text=json.dumps(formatted, indent=2))]

                # ============== EXTRACTION ==============
                elif name == "crawl4ai_extract_structured":
                    crawler = await self._get_crawler()
                    if not crawler:
                        return [types.TextContent(type="text", text="Crawl4AI not available.")]

                    result = await crawler.extract_structured_data(
                        url=arguments["url"],
                        schema=arguments["schema"]
                    )

                    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

                elif name == "crawl4ai_extract_with_llm":
                    crawler = await self._get_crawler()
                    if not crawler:
                        return [types.TextContent(type="text", text="Crawl4AI not available.")]

                    result = await crawler.extract_with_llm(
                        url=arguments["url"],
                        instruction=arguments["instruction"]
                    )

                    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

                # ============== CONTENT ANALYSIS ==============
                elif name == "crawl4ai_analyze_content":
                    if not FABRIC_AVAILABLE:
                        return [types.TextContent(type="text", text="Fabric patterns not available.")]

                    content = arguments.get("content", "")

                    # Crawl URL if provided
                    if arguments.get("crawl_url"):
                        crawler = await self._get_crawler()
                        if crawler:
                            result = await crawler.crawl_url(arguments["crawl_url"])
                            if result['success']:
                                content = result.get('markdown', '')

                    if not content:
                        return [types.TextContent(type="text", text="No content to analyze. Provide content or crawl_url.")]

                    # Apply fabric pattern
                    pattern = arguments["pattern"]
                    analysis = self.fabric.apply_pattern(pattern, content)

                    return [types.TextContent(type="text", text=json.dumps({
                        'pattern': pattern,
                        'content_length': len(content),
                        'analysis': analysis
                    }, indent=2))]

                # ============== MANAGEMENT ==============
                elif name == "crawl4ai_get_stats":
                    stats = {
                        'session': self.session_stats,
                        'crawler': self.crawler.get_stats() if self.crawler else None,
                        'rag': self.rag.get_stats() if self.rag else None,
                        'brain_available': BRAIN_AVAILABLE,
                        'fabric_available': FABRIC_AVAILABLE
                    }

                    return [types.TextContent(type="text", text=json.dumps(stats, indent=2))]

                elif name == "crawl4ai_clear_knowledge":
                    if not arguments.get("confirm"):
                        return [types.TextContent(type="text", text="Must set confirm=true to clear knowledge base.")]

                    rag = await self._get_rag()
                    if rag:
                        await rag.clear_knowledge_base()
                        return [types.TextContent(type="text", text="Knowledge base cleared.")]

                    return [types.TextContent(type="text", text="RAG system not available.")]

                else:
                    return [types.TextContent(type="text", text=f"Unknown tool: {name}")]

            except Exception as e:
                self.session_stats['errors'] += 1
                logging.error(f"Error in {name}: {e}")
                return [types.TextContent(type="text", text=f"Error executing {name}: {str(e)}")]

    async def cleanup(self):
        """Cleanup resources"""
        if self.crawler:
            await self.crawler.close()

    async def run(self):
        """Run the MCP server"""
        try:
            async with stdio_server() as (read_stream, write_stream):
                await self.server.run(
                    read_stream,
                    write_stream,
                    self.server.create_initialization_options()
                )
        finally:
            await self.cleanup()


async def main():
    """Main entry point"""
    logging.basicConfig(level=logging.INFO)
    server = Crawl4AIMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
