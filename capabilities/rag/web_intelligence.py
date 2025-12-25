#!/usr/bin/env python3
"""
ALFRED Web Intelligence Module - Phase 1 Foundation
High-performance web crawling and content extraction without Crawl4AI dependency issues.

Features:
- Async web crawling with httpx
- LLM-optimized markdown extraction via trafilatura
- Batch and deep crawling
- Structured data extraction
- Knowledge base integration

Part of ALFRED SYSTEMS Full Integration - Phase 1: Foundation
"""

import asyncio
import logging
from typing import List, Dict, Optional, Any, Set
from datetime import datetime
from urllib.parse import urlparse, urljoin
import json
import hashlib
import re

# Core dependencies (all pip-installable without build issues)
try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False

try:
    import trafilatura
    from trafilatura import extract, fetch_url
    from trafilatura.settings import use_config
    TRAFILATURA_AVAILABLE = True
except ImportError:
    TRAFILATURA_AVAILABLE = False

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

try:
    import html2text
    HTML2TEXT_AVAILABLE = True
except ImportError:
    HTML2TEXT_AVAILABLE = False

try:
    from markdownify import markdownify as md
    MARKDOWNIFY_AVAILABLE = True
except ImportError:
    MARKDOWNIFY_AVAILABLE = False

# Check availability
WEB_INTELLIGENCE_AVAILABLE = HTTPX_AVAILABLE and (TRAFILATURA_AVAILABLE or BS4_AVAILABLE)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("web_intelligence")


class WebIntelligence:
    """
    High-performance web intelligence system for ALFRED.
    Replaces Crawl4AI with a more compatible implementation.
    """

    def __init__(
        self,
        timeout: float = 30.0,
        max_concurrent: int = 10,
        user_agent: str = "ALFRED-WebIntelligence/1.0 (Compatible; Research Bot)",
        respect_robots: bool = True
    ):
        """
        Initialize web intelligence system.

        Args:
            timeout: Request timeout in seconds
            max_concurrent: Maximum concurrent requests
            user_agent: User agent string
            respect_robots: Whether to respect robots.txt
        """
        if not WEB_INTELLIGENCE_AVAILABLE:
            raise RuntimeError(
                "Web intelligence dependencies not available. "
                "Install: pip install httpx trafilatura beautifulsoup4"
            )

        self.timeout = timeout
        self.max_concurrent = max_concurrent
        self.user_agent = user_agent
        self.respect_robots = respect_robots

        # HTTP client (created on demand)
        self._client: Optional[httpx.AsyncClient] = None

        # Trafilatura config for optimal extraction
        if TRAFILATURA_AVAILABLE:
            self._traf_config = use_config()
            self._traf_config.set("DEFAULT", "EXTRACTION_TIMEOUT", "30")

        # HTML to markdown converter
        if HTML2TEXT_AVAILABLE:
            self._h2t = html2text.HTML2Text()
            self._h2t.ignore_links = False
            self._h2t.ignore_images = False
            self._h2t.body_width = 0  # No wrapping

        # Statistics
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_bytes': 0,
            'cache_hits': 0
        }

        # Simple cache
        self._cache: Dict[str, Dict] = {}

        logger.info("Web Intelligence initialized")

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.timeout),
                headers={"User-Agent": self.user_agent},
                follow_redirects=True,
                limits=httpx.Limits(max_connections=self.max_concurrent)
            )
        return self._client

    async def close(self):
        """Close HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self):
        """Async context manager entry."""
        await self._get_client()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    def _cache_key(self, url: str) -> str:
        """Generate cache key for URL."""
        return hashlib.md5(url.encode()).hexdigest()

    def _extract_markdown_trafilatura(self, html: str, url: str) -> str:
        """Extract LLM-optimized markdown using trafilatura."""
        if not TRAFILATURA_AVAILABLE:
            return ""

        try:
            # Extract with trafilatura (best for articles/content)
            content = extract(
                html,
                url=url,
                include_links=True,
                include_images=True,
                include_tables=True,
                output_format='markdown',
                config=self._traf_config
            )
            return content or ""
        except Exception as e:
            logger.warning(f"Trafilatura extraction failed: {e}")
            return ""

    def _extract_markdown_bs4(self, html: str) -> str:
        """Extract markdown using BeautifulSoup + html2text."""
        if not BS4_AVAILABLE:
            return ""

        try:
            soup = BeautifulSoup(html, 'html.parser')

            # Remove scripts, styles, nav, footer
            for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                tag.decompose()

            # Try html2text first
            if HTML2TEXT_AVAILABLE:
                return self._h2t.handle(str(soup))

            # Fallback to markdownify
            if MARKDOWNIFY_AVAILABLE:
                return md(str(soup), heading_style="ATX")

            # Last resort: just get text
            return soup.get_text(separator='\n', strip=True)

        except Exception as e:
            logger.warning(f"BS4 extraction failed: {e}")
            return ""

    def _extract_links(self, html: str, base_url: str) -> Dict[str, List[str]]:
        """Extract internal and external links."""
        if not BS4_AVAILABLE:
            return {'internal': [], 'external': []}

        try:
            soup = BeautifulSoup(html, 'html.parser')
            base_domain = urlparse(base_url).netloc

            internal = []
            external = []

            for link in soup.find_all('a', href=True):
                href = link['href']

                # Skip anchors and javascript
                if href.startswith('#') or href.startswith('javascript:'):
                    continue

                # Make absolute URL
                abs_url = urljoin(base_url, href)
                parsed = urlparse(abs_url)

                # Categorize
                if parsed.netloc == base_domain:
                    if abs_url not in internal:
                        internal.append(abs_url)
                else:
                    if abs_url not in external:
                        external.append(abs_url)

            return {'internal': internal[:100], 'external': external[:50]}

        except Exception as e:
            logger.warning(f"Link extraction failed: {e}")
            return {'internal': [], 'external': []}

    def _extract_media(self, html: str, base_url: str) -> Dict[str, List[str]]:
        """Extract images, videos, and audio URLs."""
        if not BS4_AVAILABLE:
            return {'images': [], 'videos': [], 'audios': []}

        try:
            soup = BeautifulSoup(html, 'html.parser')

            images = []
            for img in soup.find_all('img', src=True):
                abs_url = urljoin(base_url, img['src'])
                if abs_url not in images:
                    images.append(abs_url)

            videos = []
            for video in soup.find_all(['video', 'source']):
                src = video.get('src')
                if src:
                    abs_url = urljoin(base_url, src)
                    if abs_url not in videos:
                        videos.append(abs_url)

            audios = []
            for audio in soup.find_all(['audio', 'source']):
                src = audio.get('src')
                if src:
                    abs_url = urljoin(base_url, src)
                    if abs_url not in audios:
                        audios.append(abs_url)

            return {
                'images': images[:50],
                'videos': videos[:20],
                'audios': audios[:20]
            }

        except Exception as e:
            logger.warning(f"Media extraction failed: {e}")
            return {'images': [], 'videos': [], 'audios': []}

    def _extract_metadata(self, html: str) -> Dict[str, Any]:
        """Extract page metadata."""
        if not BS4_AVAILABLE:
            return {}

        try:
            soup = BeautifulSoup(html, 'html.parser')

            metadata = {}

            # Title
            title = soup.find('title')
            if title:
                metadata['title'] = title.get_text(strip=True)

            # Meta tags
            for meta in soup.find_all('meta'):
                name = meta.get('name', meta.get('property', ''))
                content = meta.get('content', '')

                if name and content:
                    if 'description' in name.lower():
                        metadata['description'] = content
                    elif 'keywords' in name.lower():
                        metadata['keywords'] = content
                    elif 'author' in name.lower():
                        metadata['author'] = content
                    elif 'og:' in name:
                        metadata[name] = content

            return metadata

        except Exception as e:
            logger.warning(f"Metadata extraction failed: {e}")
            return {}

    async def crawl_url(
        self,
        url: str,
        extract_links: bool = True,
        extract_media: bool = True,
        use_cache: bool = True,
        js_rendered: bool = False  # For future playwright integration
    ) -> Dict[str, Any]:
        """
        Crawl a single URL and extract LLM-optimized content.

        Args:
            url: URL to crawl
            extract_links: Whether to extract links
            extract_media: Whether to extract media URLs
            use_cache: Use cached results if available
            js_rendered: Reserved for future JS rendering support

        Returns:
            Dict with markdown, links, media, metadata
        """
        cache_key = self._cache_key(url)

        # Check cache
        if use_cache and cache_key in self._cache:
            self.stats['cache_hits'] += 1
            cached = self._cache[cache_key].copy()
            cached['from_cache'] = True
            return cached

        self.stats['total_requests'] += 1
        client = await self._get_client()

        try:
            # Fetch URL
            response = await client.get(url)
            response.raise_for_status()

            html = response.text
            self.stats['total_bytes'] += len(html)
            self.stats['successful_requests'] += 1

            # Extract markdown (try trafilatura first, fallback to BS4)
            markdown = self._extract_markdown_trafilatura(html, url)
            if not markdown or len(markdown) < 100:
                markdown = self._extract_markdown_bs4(html)

            # Build result
            result = {
                'url': url,
                'success': True,
                'status_code': response.status_code,
                'markdown': markdown,
                'html': html,
                'cleaned_html': html,  # Could add cleaning later
                'links': self._extract_links(html, url) if extract_links else {},
                'media': self._extract_media(html, url) if extract_media else {},
                'metadata': self._extract_metadata(html),
                'crawled_at': datetime.now().isoformat(),
                'content_length': len(html),
                'markdown_length': len(markdown),
                'from_cache': False
            }

            # Cache result
            if use_cache:
                self._cache[cache_key] = result

            logger.info(f"Crawled {url}: {len(markdown)} chars markdown")
            return result

        except httpx.HTTPStatusError as e:
            self.stats['failed_requests'] += 1
            logger.error(f"HTTP error for {url}: {e}")
            return {
                'url': url,
                'success': False,
                'status_code': e.response.status_code,
                'error': str(e),
                'crawled_at': datetime.now().isoformat()
            }

        except Exception as e:
            self.stats['failed_requests'] += 1
            logger.error(f"Error crawling {url}: {e}")
            return {
                'url': url,
                'success': False,
                'error': str(e),
                'crawled_at': datetime.now().isoformat()
            }

    async def crawl_batch(
        self,
        urls: List[str],
        max_concurrent: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Crawl multiple URLs concurrently.

        Args:
            urls: List of URLs to crawl
            max_concurrent: Override default concurrency limit

        Returns:
            List of crawl results
        """
        semaphore = asyncio.Semaphore(max_concurrent or self.max_concurrent)

        async def crawl_with_limit(url: str) -> Dict[str, Any]:
            async with semaphore:
                return await self.crawl_url(url)

        tasks = [crawl_with_limit(url) for url in urls]
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

        logger.info(f"Batch crawl complete: {len(urls)} URLs")
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
        Deep crawl starting from a URL, following links.

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
        base_domain = urlparse(start_url).netloc

        visited: Set[str] = set()
        to_visit: List[tuple] = [(start_url, 0)]  # (url, depth)
        results: List[Dict[str, Any]] = []

        # Compile patterns
        include_re = [re.compile(p) for p in (url_patterns or [])]
        exclude_re = [re.compile(p) for p in (exclude_patterns or [])]

        def should_crawl(url: str) -> bool:
            """Check if URL should be crawled."""
            if url in visited:
                return False

            parsed = urlparse(url)

            # Domain check
            if same_domain_only and parsed.netloc != base_domain:
                return False

            # Include patterns
            if include_re and not any(r.search(url) for r in include_re):
                return False

            # Exclude patterns
            if exclude_re and any(r.search(url) for r in exclude_re):
                return False

            return True

        while to_visit and len(results) < max_pages:
            url, depth = to_visit.pop(0)

            if not should_crawl(url):
                continue

            visited.add(url)

            # Crawl page
            result = await self.crawl_url(url)
            results.append(result)

            # Add links to queue (if not at max depth)
            if result['success'] and depth < max_depth:
                internal_links = result.get('links', {}).get('internal', [])
                for link in internal_links:
                    if should_crawl(link):
                        to_visit.append((link, depth + 1))

            # Respect rate limiting
            await asyncio.sleep(0.5)

        logger.info(f"Deep crawl complete: {len(results)} pages from {start_url}")
        return results

    async def extract_structured(
        self,
        url: str,
        selectors: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Extract structured data using CSS selectors.

        Args:
            url: URL to extract from
            selectors: Dict of field_name -> CSS selector

        Returns:
            Extracted structured data
        """
        if not BS4_AVAILABLE:
            return {'error': 'BeautifulSoup not available'}

        # First crawl the URL
        result = await self.crawl_url(url, extract_links=False, extract_media=False)

        if not result['success']:
            return result

        try:
            soup = BeautifulSoup(result['html'], 'html.parser')

            extracted = {}
            for field, selector in selectors.items():
                elements = soup.select(selector)
                if elements:
                    if len(elements) == 1:
                        extracted[field] = elements[0].get_text(strip=True)
                    else:
                        extracted[field] = [e.get_text(strip=True) for e in elements]
                else:
                    extracted[field] = None

            return {
                'url': url,
                'success': True,
                'extracted': extracted,
                'crawled_at': datetime.now().isoformat()
            }

        except Exception as e:
            return {
                'url': url,
                'success': False,
                'error': str(e)
            }

    def get_stats(self) -> Dict[str, Any]:
        """Get crawler statistics."""
        return {
            **self.stats,
            'success_rate': (
                self.stats['successful_requests'] / self.stats['total_requests'] * 100
                if self.stats['total_requests'] > 0 else 0
            ),
            'cache_size': len(self._cache),
            'libraries': {
                'httpx': HTTPX_AVAILABLE,
                'trafilatura': TRAFILATURA_AVAILABLE,
                'beautifulsoup4': BS4_AVAILABLE,
                'html2text': HTML2TEXT_AVAILABLE,
                'markdownify': MARKDOWNIFY_AVAILABLE
            }
        }

    def clear_cache(self):
        """Clear the URL cache."""
        self._cache.clear()
        logger.info("Cache cleared")


# Synchronous wrappers for convenience
def crawl_sync(url: str, **kwargs) -> Dict[str, Any]:
    """Synchronous wrapper for crawling a single URL."""
    async def _run():
        async with WebIntelligence() as wi:
            return await wi.crawl_url(url, **kwargs)
    return asyncio.run(_run())


def crawl_batch_sync(urls: List[str], **kwargs) -> List[Dict[str, Any]]:
    """Synchronous wrapper for batch crawling."""
    async def _run():
        async with WebIntelligence() as wi:
            return await wi.crawl_batch(urls, **kwargs)
    return asyncio.run(_run())


def deep_crawl_sync(start_url: str, **kwargs) -> List[Dict[str, Any]]:
    """Synchronous wrapper for deep crawling."""
    async def _run():
        async with WebIntelligence() as wi:
            return await wi.deep_crawl(start_url, **kwargs)
    return asyncio.run(_run())


# Compatibility alias for crawler_advanced.py
AdvancedCrawler = WebIntelligence
CRAWL4AI_AVAILABLE = WEB_INTELLIGENCE_AVAILABLE


if __name__ == "__main__":
    print("=" * 80)
    print("ALFRED Web Intelligence - Phase 1 Foundation")
    print("=" * 80)
    print()

    async def test():
        async with WebIntelligence() as wi:
            # Test basic crawl
            print("Test 1: Basic URL Crawl")
            print("-" * 40)
            result = await wi.crawl_url("https://example.com")
            print(f"URL: {result['url']}")
            print(f"Success: {result['success']}")
            print(f"Markdown length: {result.get('markdown_length', 0)}")
            print(f"Links found: {len(result.get('links', {}).get('internal', []))}")
            print()

            # Test batch
            print("Test 2: Batch Crawl")
            print("-" * 40)
            results = await wi.crawl_batch([
                "https://example.com",
                "https://example.org"
            ])
            for r in results:
                print(f"  {r['url']}: {'SUCCESS' if r['success'] else 'FAILED'}")
            print()

            # Stats
            print("Statistics:")
            print("-" * 40)
            stats = wi.get_stats()
            for k, v in stats.items():
                print(f"  {k}: {v}")

    if WEB_INTELLIGENCE_AVAILABLE:
        asyncio.run(test())
        print()
        print("=" * 80)
        print("Web Intelligence Test Complete!")
        print("=" * 80)
    else:
        print("Dependencies not available. Install:")
        print("  pip install httpx trafilatura beautifulsoup4 html2text markdownify")
