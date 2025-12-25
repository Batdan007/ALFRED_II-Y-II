#!/usr/bin/env python3
"""
Alfred Advanced Crawler - Crawl4AI Integration
LLM-optimized web crawling with markdown extraction, deep crawling, and intelligent content filtering
"""

import sys
import os
from pathlib import Path
import asyncio
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
import json

# Add Crawl4AI to path
crawl4ai_path = Path("C:/Alfred the Batcomputer/crawl4ai-main")
if crawl4ai_path.exists():
    sys.path.insert(0, str(crawl4ai_path))

try:
    from crawl4ai import (
        AsyncWebCrawler,
        BrowserConfig,
        CrawlerRunConfig,
        CacheMode,
        LLMExtractionStrategy,
        JsonCssExtractionStrategy,
        CosineStrategy,
        PruningContentFilter,
        BFSDeepCrawlStrategy,
        DeepCrawlDecorator,
        URLPatternFilter,
        DomainFilter,
        FilterChain,
        CrawlResult
    )
    CRAWL4AI_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Crawl4AI not available: {e}")
    CRAWL4AI_AVAILABLE = False


class AdvancedCrawler:
    """
    Advanced web crawler using Crawl4AI
    Features: Async, LLM-optimized markdown, deep crawling, intelligent filtering
    """

    def __init__(
        self,
        headless: bool = True,
        verbose: bool = False,
        cache_mode: str = "enabled"
    ):
        """
        Initialize advanced crawler

        Args:
            headless: Run browser in headless mode
            verbose: Enable verbose logging
            cache_mode: Cache strategy ('enabled', 'disabled', 'bypass', 'read_only', 'write_only')
        """
        if not CRAWL4AI_AVAILABLE:
            raise RuntimeError("Crawl4AI not available. Check installation.")

        self.headless = headless
        self.verbose = verbose

        # Map cache mode string to enum
        cache_modes = {
            'enabled': CacheMode.ENABLED,
            'disabled': CacheMode.DISABLED,
            'bypass': CacheMode.BYPASS,
            'read_only': CacheMode.READ_ONLY,
            'write_only': CacheMode.WRITE_ONLY
        }
        self.cache_mode = cache_modes.get(cache_mode, CacheMode.ENABLED)

        # Browser configuration
        self.browser_config = BrowserConfig(
            headless=headless,
            verbose=verbose,
            browser_type="chromium",  # chromium, firefox, or webkit
            ignore_https_errors=True,
            viewport={"width": 1920, "height": 1080}
        )

        # Crawler instance (created on demand)
        self.crawler = None

        # Statistics
        self.stats = {
            'total_crawls': 0,
            'successful_crawls': 0,
            'failed_crawls': 0,
            'total_pages': 0,
            'total_bytes': 0
        }

        logging.info("Advanced crawler initialized with Crawl4AI")

    async def __aenter__(self):
        """Async context manager entry"""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()

    async def start(self):
        """Start the crawler (initialize browser)"""
        if not self.crawler:
            self.crawler = AsyncWebCrawler(config=self.browser_config)
            await self.crawler.__aenter__()
            logging.info("Crawler browser started")

    async def close(self):
        """Close the crawler (cleanup browser)"""
        if self.crawler:
            await self.crawler.__aexit__(None, None, None)
            self.crawler = None
            logging.info("Crawler browser closed")

    async def crawl_url(
        self,
        url: str,
        extract_markdown: bool = True,
        wait_for_selector: Optional[str] = None,
        js_code: Optional[str] = None,
        cache_mode: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Crawl a single URL with LLM-optimized extraction

        Args:
            url: URL to crawl
            extract_markdown: Extract LLM-friendly markdown
            wait_for_selector: CSS selector to wait for before extracting
            js_code: JavaScript to execute before extraction
            cache_mode: Override default cache mode

        Returns:
            Crawl result with markdown, html, metadata
        """
        if not self.crawler:
            await self.start()

        # Determine cache mode
        cache = cache_mode if cache_mode else self.cache_mode

        # Create run configuration
        config = CrawlerRunConfig(
            cache_mode=cache,
            page_timeout=60000,  # 60 seconds
            wait_until="networkidle",  # Wait for network to be idle
        )

        # Add optional configurations
        if wait_for_selector:
            config.wait_for = wait_for_selector

        if js_code:
            config.js_code = js_code

        try:
            # Perform crawl
            result: CrawlResult = await self.crawler.arun(
                url=url,
                config=config
            )

            # Update statistics
            self.stats['total_crawls'] += 1
            if result.success:
                self.stats['successful_crawls'] += 1
                self.stats['total_pages'] += 1
                self.stats['total_bytes'] += len(result.html or '')
            else:
                self.stats['failed_crawls'] += 1

            # Extract key information
            crawl_data = {
                'url': url,
                'success': result.success,
                'status_code': result.status_code,
                'markdown': result.markdown if extract_markdown else None,
                'cleaned_html': result.cleaned_html,
                'html': result.html,
                'links': result.links.get('internal', []) if result.links else [],
                'external_links': result.links.get('external', []) if result.links else [],
                'media': {
                    'images': result.media.get('images', []) if result.media else [],
                    'videos': result.media.get('videos', []) if result.media else [],
                    'audios': result.media.get('audios', []) if result.media else []
                },
                'metadata': result.metadata if hasattr(result, 'metadata') else {},
                'crawled_at': datetime.now().isoformat(),
                'error': result.error_message if hasattr(result, 'error_message') and not result.success else None
            }

            logging.info(f"Crawled {url}: {'SUCCESS' if result.success else 'FAILED'}")
            return crawl_data

        except Exception as e:
            self.stats['failed_crawls'] += 1
            logging.error(f"Crawl failed for {url}: {e}")

            return {
                'url': url,
                'success': False,
                'error': str(e),
                'crawled_at': datetime.now().isoformat()
            }

    async def crawl_urls_batch(
        self,
        urls: List[str],
        max_concurrent: int = 5,
        **crawl_kwargs
    ) -> List[Dict[str, Any]]:
        """
        Crawl multiple URLs concurrently

        Args:
            urls: List of URLs to crawl
            max_concurrent: Maximum concurrent crawls
            **crawl_kwargs: Additional kwargs for crawl_url

        Returns:
            List of crawl results
        """
        if not self.crawler:
            await self.start()

        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(max_concurrent)

        async def crawl_with_semaphore(url):
            async with semaphore:
                return await self.crawl_url(url, **crawl_kwargs)

        # Crawl all URLs concurrently
        tasks = [crawl_with_semaphore(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Handle exceptions
        final_results = []
        for url, result in zip(urls, results):
            if isinstance(result, Exception):
                final_results.append({
                    'url': url,
                    'success': False,
                    'error': str(result),
                    'crawled_at': datetime.now().isoformat()
                })
            else:
                final_results.append(result)

        logging.info(f"Batch crawl complete: {len(urls)} URLs processed")
        return final_results

    async def deep_crawl(
        self,
        start_url: str,
        max_depth: int = 2,
        max_pages: int = 50,
        same_domain_only: bool = True,
        url_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Deep crawl starting from a URL (follows links)

        Args:
            start_url: Starting URL
            max_depth: Maximum crawl depth
            max_pages: Maximum total pages to crawl
            same_domain_only: Only crawl same domain
            url_patterns: URL patterns to include (regex)
            exclude_patterns: URL patterns to exclude (regex)

        Returns:
            List of crawled pages
        """
        if not self.crawler:
            await self.start()

        # Create filter chain
        filters = FilterChain()

        # Add domain filter
        if same_domain_only:
            from urllib.parse import urlparse
            domain = urlparse(start_url).netloc
            filters.add_filter(DomainFilter(allowed_domains=[domain]))

        # Add URL pattern filters
        if url_patterns or exclude_patterns:
            filters.add_filter(URLPatternFilter(
                include_patterns=url_patterns or [],
                exclude_patterns=exclude_patterns or []
            ))

        # Create deep crawl strategy
        strategy = BFSDeepCrawlStrategy(
            max_depth=max_depth,
            max_pages=max_pages,
            filter_chain=filters
        )

        # Create run configuration with deep crawl decorator
        config = CrawlerRunConfig(
            cache_mode=self.cache_mode,
            page_timeout=60000,
            wait_until="networkidle"
        )

        # Apply deep crawl decorator
        @DeepCrawlDecorator(strategy=strategy)
        async def deep_crawl_run():
            return await self.crawler.arun(url=start_url, config=config)

        try:
            # Execute deep crawl
            results = await deep_crawl_run()

            # Process results
            crawled_pages = []
            if isinstance(results, list):
                for result in results:
                    if result.success:
                        crawled_pages.append({
                            'url': result.url if hasattr(result, 'url') else start_url,
                            'markdown': result.markdown,
                            'links': result.links.get('internal', []) if result.links else [],
                            'metadata': result.metadata if hasattr(result, 'metadata') else {},
                            'success': True
                        })
            else:
                # Single result
                if results.success:
                    crawled_pages.append({
                        'url': start_url,
                        'markdown': results.markdown,
                        'links': results.links.get('internal', []) if results.links else [],
                        'metadata': results.metadata if hasattr(results, 'metadata') else {},
                        'success': True
                    })

            self.stats['total_pages'] += len(crawled_pages)
            logging.info(f"Deep crawl complete: {len(crawled_pages)} pages crawled from {start_url}")

            return crawled_pages

        except Exception as e:
            logging.error(f"Deep crawl failed: {e}")
            return []

    async def extract_with_llm(
        self,
        url: str,
        instruction: str,
        api_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract specific information using LLM

        Args:
            url: URL to crawl
            instruction: Extraction instruction for LLM
            api_token: API token for LLM (uses Anthropic/OpenAI/Groq)

        Returns:
            Extracted data
        """
        if not self.crawler:
            await self.start()

        # Create LLM extraction strategy
        strategy = LLMExtractionStrategy(
            provider="openai/gpt-4",  # Can be customized
            api_token=api_token,
            instruction=instruction
        )

        config = CrawlerRunConfig(
            cache_mode=self.cache_mode,
            extraction_strategy=strategy
        )

        try:
            result = await self.crawler.arun(url=url, config=config)

            return {
                'url': url,
                'success': result.success,
                'extracted_content': result.extracted_content if hasattr(result, 'extracted_content') else None,
                'markdown': result.markdown
            }

        except Exception as e:
            logging.error(f"LLM extraction failed: {e}")
            return {
                'url': url,
                'success': False,
                'error': str(e)
            }

    async def extract_structured_data(
        self,
        url: str,
        schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extract structured data using CSS selectors

        Args:
            url: URL to crawl
            schema: Extraction schema (JSON with CSS selectors)

        Returns:
            Extracted structured data
        """
        if not self.crawler:
            await self.start()

        # Create JSON CSS extraction strategy
        strategy = JsonCssExtractionStrategy(schema)

        config = CrawlerRunConfig(
            cache_mode=self.cache_mode,
            extraction_strategy=strategy
        )

        try:
            result = await self.crawler.arun(url=url, config=config)

            return {
                'url': url,
                'success': result.success,
                'extracted_content': result.extracted_content if hasattr(result, 'extracted_content') else None
            }

        except Exception as e:
            logging.error(f"Structured extraction failed: {e}")
            return {
                'url': url,
                'success': False,
                'error': str(e)
            }

    def get_stats(self) -> Dict[str, Any]:
        """Get crawler statistics"""
        return {
            **self.stats,
            'success_rate': (self.stats['successful_crawls'] / self.stats['total_crawls'] * 100)
            if self.stats['total_crawls'] > 0 else 0,
            'average_page_size': (self.stats['total_bytes'] / self.stats['total_pages'])
            if self.stats['total_pages'] > 0 else 0
        }


# Convenience functions for synchronous usage
def crawl_sync(url: str, **kwargs) -> Dict[str, Any]:
    """Synchronous wrapper for crawling a single URL"""
    async def _crawl():
        async with AdvancedCrawler(**kwargs) as crawler:
            return await crawler.crawl_url(url)

    return asyncio.run(_crawl())


def crawl_batch_sync(urls: List[str], **kwargs) -> List[Dict[str, Any]]:
    """Synchronous wrapper for batch crawling"""
    async def _crawl():
        async with AdvancedCrawler(**kwargs) as crawler:
            return await crawler.crawl_urls_batch(urls)

    return asyncio.run(_crawl())


def deep_crawl_sync(start_url: str, **kwargs) -> List[Dict[str, Any]]:
    """Synchronous wrapper for deep crawling"""
    async def _crawl():
        async with AdvancedCrawler(**kwargs) as crawler:
            return await crawler.deep_crawl(start_url, **kwargs)

    return asyncio.run(_crawl())


if __name__ == "__main__":
    # Test the advanced crawler
    print("=" * 80)
    print("Testing Alfred Advanced Crawler (Crawl4AI)")
    print("=" * 80)
    print()

    async def test_crawler():
        # Test basic crawl
        print("Test 1: Basic URL Crawl")
        print("-" * 80)
        async with AdvancedCrawler(headless=True, verbose=False) as crawler:
            result = await crawler.crawl_url("https://example.com")
            print(f"URL: {result['url']}")
            print(f"Success: {result['success']}")
            print(f"Status: {result['status_code']}")
            print(f"Markdown length: {len(result['markdown']) if result['markdown'] else 0}")
            print(f"Links found: {len(result['links'])}")
            print()

            # Test batch crawl
            print("Test 2: Batch Crawl")
            print("-" * 80)
            urls = ["https://example.com", "https://example.org"]
            results = await crawler.crawl_urls_batch(urls, max_concurrent=2)
            for r in results:
                print(f"  {r['url']}: {'SUCCESS' if r['success'] else 'FAILED'}")
            print()

            # Show stats
            print("Crawler Statistics:")
            print("-" * 80)
            stats = crawler.get_stats()
            for key, value in stats.items():
                print(f"  {key}: {value}")

    # Run tests
    if CRAWL4AI_AVAILABLE:
        asyncio.run(test_crawler())
        print()
        print("=" * 80)
        print("Advanced Crawler Test Complete!")
        print("=" * 80)
    else:
        print("Crawl4AI not available. Please install dependencies.")
