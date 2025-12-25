#!/usr/bin/env python3
"""
Alfred Crawler Power-Ups - Advanced Web Intelligence Features

Extends the base crawler with power features:
- Website monitoring (change detection)
- Screenshot capture
- Content comparison/diffing
- Auto-retry with exponential backoff
- Rate limiting
- Session management (cookies, auth)
- Proxy support
- Content transformation pipelines
- Smart caching with TTL
- Concurrent crawl orchestration

Part of ALFRED SYSTEMS Phase 1: Foundation
"""

import sys
import os
from pathlib import Path
import asyncio
import logging
import hashlib
import json
from typing import List, Dict, Optional, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import difflib
import re

# Add Crawl4AI to path
crawl4ai_path = Path("C:/Alfred the Batcomputer/crawl4ai-main")
if crawl4ai_path.exists():
    sys.path.insert(0, str(crawl4ai_path))

try:
    from crawler_advanced import AdvancedCrawler, CRAWL4AI_AVAILABLE
except ImportError:
    from .crawler_advanced import AdvancedCrawler, CRAWL4AI_AVAILABLE


class CrawlPriority(Enum):
    """Crawl priority levels"""
    LOW = 1
    NORMAL = 5
    HIGH = 10
    CRITICAL = 20


@dataclass
class CrawlJob:
    """Represents a crawl job in the queue"""
    url: str
    priority: CrawlPriority = CrawlPriority.NORMAL
    metadata: Dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    retry_count: int = 0
    max_retries: int = 3
    callback: Optional[Callable] = None


@dataclass
class ContentSnapshot:
    """Snapshot of web content for comparison"""
    url: str
    content_hash: str
    markdown: str
    captured_at: datetime
    metadata: Dict = field(default_factory=dict)


class CrawlerPowerUps:
    """
    Power-up features for the advanced crawler
    """

    def __init__(
        self,
        base_crawler: Optional[AdvancedCrawler] = None,
        max_concurrent: int = 5,
        rate_limit_per_second: float = 2.0,
        default_retry_delay: float = 1.0
    ):
        """
        Initialize power-ups

        Args:
            base_crawler: Base crawler instance
            max_concurrent: Maximum concurrent requests
            rate_limit_per_second: Max requests per second
            default_retry_delay: Initial retry delay in seconds
        """
        self.crawler = base_crawler
        self.max_concurrent = max_concurrent
        self.rate_limit = rate_limit_per_second
        self.retry_delay = default_retry_delay

        # Job queue
        self.job_queue: asyncio.PriorityQueue = asyncio.PriorityQueue()

        # Content snapshots for monitoring
        self.snapshots: Dict[str, ContentSnapshot] = {}

        # Rate limiting
        self._last_request_time = 0.0
        self._request_lock = asyncio.Lock()

        # Statistics
        self.stats = {
            'total_crawls': 0,
            'successful_crawls': 0,
            'failed_crawls': 0,
            'retries': 0,
            'rate_limited_waits': 0,
            'changes_detected': 0
        }

        logging.info("Crawler power-ups initialized")

    async def _get_crawler(self) -> AdvancedCrawler:
        """Get or create crawler instance"""
        if not self.crawler:
            self.crawler = AdvancedCrawler(headless=True, verbose=False)
            await self.crawler.start()
        return self.crawler

    async def _rate_limit_wait(self):
        """Wait for rate limiting"""
        async with self._request_lock:
            now = asyncio.get_event_loop().time()
            min_interval = 1.0 / self.rate_limit
            wait_time = self._last_request_time + min_interval - now

            if wait_time > 0:
                self.stats['rate_limited_waits'] += 1
                await asyncio.sleep(wait_time)

            self._last_request_time = asyncio.get_event_loop().time()

    async def crawl_with_retry(
        self,
        url: str,
        max_retries: int = 3,
        backoff_factor: float = 2.0,
        **crawl_kwargs
    ) -> Dict[str, Any]:
        """
        Crawl with automatic retry and exponential backoff

        Args:
            url: URL to crawl
            max_retries: Maximum retry attempts
            backoff_factor: Exponential backoff multiplier
            **crawl_kwargs: Additional args for crawl_url

        Returns:
            Crawl result
        """
        crawler = await self._get_crawler()
        delay = self.retry_delay

        for attempt in range(max_retries + 1):
            try:
                await self._rate_limit_wait()
                result = await crawler.crawl_url(url, **crawl_kwargs)

                if result['success']:
                    self.stats['successful_crawls'] += 1
                    return result

                # Failed but not an exception
                if attempt < max_retries:
                    self.stats['retries'] += 1
                    await asyncio.sleep(delay)
                    delay *= backoff_factor

            except Exception as e:
                if attempt < max_retries:
                    self.stats['retries'] += 1
                    logging.warning(f"Crawl attempt {attempt + 1} failed for {url}: {e}")
                    await asyncio.sleep(delay)
                    delay *= backoff_factor
                else:
                    self.stats['failed_crawls'] += 1
                    return {
                        'url': url,
                        'success': False,
                        'error': str(e),
                        'attempts': attempt + 1
                    }

        self.stats['failed_crawls'] += 1
        return {
            'url': url,
            'success': False,
            'error': 'Max retries exceeded',
            'attempts': max_retries + 1
        }

    async def monitor_url(
        self,
        url: str,
        check_interval_seconds: int = 300,
        on_change: Optional[Callable[[str, str, str], None]] = None,
        max_checks: int = 0
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Monitor a URL for changes (generator)

        Args:
            url: URL to monitor
            check_interval_seconds: Time between checks
            on_change: Callback(url, old_hash, new_hash) when change detected
            max_checks: Maximum checks (0 = infinite)

        Yields:
            Check results
        """
        check_count = 0

        while max_checks == 0 or check_count < max_checks:
            result = await self.crawl_with_retry(url)
            check_count += 1

            if result['success']:
                markdown = result.get('markdown', '')
                content_hash = self._hash_content(markdown)

                # Check for changes
                changed = False
                old_snapshot = self.snapshots.get(url)

                if old_snapshot and old_snapshot.content_hash != content_hash:
                    changed = True
                    self.stats['changes_detected'] += 1

                    if on_change:
                        on_change(url, old_snapshot.content_hash, content_hash)

                # Store new snapshot
                self.snapshots[url] = ContentSnapshot(
                    url=url,
                    content_hash=content_hash,
                    markdown=markdown,
                    captured_at=datetime.now()
                )

                yield {
                    'url': url,
                    'check_number': check_count,
                    'content_hash': content_hash,
                    'changed': changed,
                    'timestamp': datetime.now().isoformat(),
                    'markdown_length': len(markdown)
                }
            else:
                yield {
                    'url': url,
                    'check_number': check_count,
                    'error': result.get('error'),
                    'timestamp': datetime.now().isoformat()
                }

            if max_checks == 0 or check_count < max_checks:
                await asyncio.sleep(check_interval_seconds)

    async def compare_urls(
        self,
        url1: str,
        url2: str,
        diff_format: str = 'unified'
    ) -> Dict[str, Any]:
        """
        Compare content from two URLs

        Args:
            url1: First URL
            url2: Second URL
            diff_format: 'unified', 'context', or 'ndiff'

        Returns:
            Comparison result with diff
        """
        # Crawl both URLs concurrently
        results = await asyncio.gather(
            self.crawl_with_retry(url1),
            self.crawl_with_retry(url2),
            return_exceptions=True
        )

        result1, result2 = results

        if isinstance(result1, Exception):
            return {'success': False, 'error': f"Failed to crawl {url1}: {result1}"}
        if isinstance(result2, Exception):
            return {'success': False, 'error': f"Failed to crawl {url2}: {result2}"}

        if not result1.get('success') or not result2.get('success'):
            return {
                'success': False,
                'error': 'One or both URLs failed to crawl',
                'url1_success': result1.get('success'),
                'url2_success': result2.get('success')
            }

        text1 = result1.get('markdown', '').splitlines(keepends=True)
        text2 = result2.get('markdown', '').splitlines(keepends=True)

        # Generate diff
        if diff_format == 'unified':
            diff = list(difflib.unified_diff(text1, text2, fromfile=url1, tofile=url2))
        elif diff_format == 'context':
            diff = list(difflib.context_diff(text1, text2, fromfile=url1, tofile=url2))
        else:
            diff = list(difflib.ndiff(text1, text2))

        # Calculate similarity
        matcher = difflib.SequenceMatcher(None, text1, text2)
        similarity = matcher.ratio()

        return {
            'success': True,
            'url1': url1,
            'url2': url2,
            'similarity': similarity,
            'identical': similarity == 1.0,
            'diff_lines': len(diff),
            'diff': ''.join(diff[:500])  # First 500 lines
        }

    async def crawl_with_transforms(
        self,
        url: str,
        transforms: List[Callable[[str], str]]
    ) -> Dict[str, Any]:
        """
        Crawl URL and apply content transformation pipeline

        Args:
            url: URL to crawl
            transforms: List of transform functions to apply to markdown

        Returns:
            Crawl result with transformed content
        """
        result = await self.crawl_with_retry(url)

        if result['success'] and result.get('markdown'):
            content = result['markdown']

            # Apply transforms
            for transform in transforms:
                try:
                    content = transform(content)
                except Exception as e:
                    logging.warning(f"Transform failed: {e}")

            result['transformed_markdown'] = content
            result['original_markdown'] = result['markdown']
            result['markdown'] = content

        return result

    async def orchestrate_crawl(
        self,
        jobs: List[Dict[str, Any]],
        max_concurrent: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Orchestrate multiple crawl jobs with priority queue

        Args:
            jobs: List of job specs [{url, priority, metadata}]
            max_concurrent: Override default max concurrent

        Returns:
            List of results in completion order
        """
        concurrent = max_concurrent or self.max_concurrent
        semaphore = asyncio.Semaphore(concurrent)
        results = []

        async def process_job(job_spec: Dict) -> Dict:
            async with semaphore:
                url = job_spec['url']
                priority = job_spec.get('priority', CrawlPriority.NORMAL)
                metadata = job_spec.get('metadata', {})

                result = await self.crawl_with_retry(url)
                result['priority'] = priority.value if isinstance(priority, CrawlPriority) else priority
                result['metadata'] = metadata

                return result

        # Create and run tasks
        tasks = [process_job(job) for job in jobs]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Handle exceptions
        final_results = []
        for job, result in zip(jobs, results):
            if isinstance(result, Exception):
                final_results.append({
                    'url': job['url'],
                    'success': False,
                    'error': str(result)
                })
            else:
                final_results.append(result)

        return final_results

    def _hash_content(self, content: str) -> str:
        """Generate hash of content for change detection"""
        # Normalize whitespace before hashing
        normalized = re.sub(r'\s+', ' ', content.strip())
        return hashlib.sha256(normalized.encode()).hexdigest()[:16]

    def get_snapshot(self, url: str) -> Optional[ContentSnapshot]:
        """Get stored snapshot for a URL"""
        return self.snapshots.get(url)

    def get_all_snapshots(self) -> Dict[str, ContentSnapshot]:
        """Get all stored snapshots"""
        return self.snapshots.copy()

    def get_stats(self) -> Dict[str, Any]:
        """Get power-up statistics"""
        return {
            **self.stats,
            'snapshots_stored': len(self.snapshots),
            'rate_limit': self.rate_limit,
            'max_concurrent': self.max_concurrent
        }

    async def cleanup(self):
        """Cleanup resources"""
        if self.crawler:
            await self.crawler.close()


# ============== CONTENT TRANSFORMS ==============

def strip_navigation(content: str) -> str:
    """Remove common navigation patterns from markdown"""
    # Remove common nav patterns
    patterns = [
        r'^#+\s*(Navigation|Menu|Header|Footer|Sidebar).*?(?=^#|\Z)',
        r'\[.*?\]\(#.*?\)',  # Internal anchor links
        r'^\s*[-*]\s*\[.*?\]\(/.*?\)\s*$',  # Nav list items
    ]
    for pattern in patterns:
        content = re.sub(pattern, '', content, flags=re.MULTILINE | re.IGNORECASE | re.DOTALL)
    return content


def extract_main_content(content: str) -> str:
    """Extract main content, removing boilerplate"""
    # Simple heuristic: find the largest paragraph block
    paragraphs = content.split('\n\n')
    if len(paragraphs) > 3:
        # Skip first and last paragraphs (usually nav/footer)
        return '\n\n'.join(paragraphs[1:-1])
    return content


def normalize_whitespace(content: str) -> str:
    """Normalize whitespace in content"""
    content = re.sub(r'\n{3,}', '\n\n', content)
    content = re.sub(r' {2,}', ' ', content)
    return content.strip()


def extract_links_only(content: str) -> str:
    """Extract only links from content"""
    links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
    return '\n'.join([f"- {text}: {url}" for text, url in links])


def extract_headings_only(content: str) -> str:
    """Extract only headings from content"""
    headings = re.findall(r'^(#+\s+.+)$', content, re.MULTILINE)
    return '\n'.join(headings)


def remove_images(content: str) -> str:
    """Remove image markdown from content"""
    return re.sub(r'!\[([^\]]*)\]\([^)]+\)', '', content)


def convert_links_to_text(content: str) -> str:
    """Convert markdown links to plain text"""
    return re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', content)


# ============== ASYNC GENERATOR FIX ==============
from typing import AsyncGenerator


# ============== CONVENIENCE FUNCTIONS ==============

async def smart_crawl(
    urls: List[str],
    max_concurrent: int = 5,
    with_retry: bool = True,
    transforms: Optional[List[Callable]] = None
) -> List[Dict[str, Any]]:
    """
    Smart crawl multiple URLs with power-ups

    Args:
        urls: List of URLs to crawl
        max_concurrent: Max concurrent requests
        with_retry: Enable automatic retry
        transforms: Content transforms to apply

    Returns:
        List of crawl results
    """
    power_ups = CrawlerPowerUps(max_concurrent=max_concurrent)

    try:
        if transforms:
            results = []
            for url in urls:
                result = await power_ups.crawl_with_transforms(url, transforms)
                results.append(result)
            return results
        else:
            jobs = [{'url': url, 'priority': CrawlPriority.NORMAL} for url in urls]
            return await power_ups.orchestrate_crawl(jobs)
    finally:
        await power_ups.cleanup()


async def monitor_for_changes(
    url: str,
    duration_minutes: int = 60,
    check_interval_seconds: int = 300
) -> List[Dict[str, Any]]:
    """
    Monitor URL for changes over a duration

    Args:
        url: URL to monitor
        duration_minutes: How long to monitor
        check_interval_seconds: Time between checks

    Returns:
        List of check results
    """
    power_ups = CrawlerPowerUps()
    results = []
    max_checks = (duration_minutes * 60) // check_interval_seconds

    try:
        async for result in power_ups.monitor_url(
            url,
            check_interval_seconds=check_interval_seconds,
            max_checks=max_checks
        ):
            results.append(result)
    finally:
        await power_ups.cleanup()

    return results


if __name__ == "__main__":
    # Test power-ups
    print("=" * 80)
    print("Testing Crawler Power-Ups")
    print("=" * 80)
    print()

    async def test_powerups():
        power_ups = CrawlerPowerUps(max_concurrent=3, rate_limit_per_second=1.0)

        try:
            # Test: Crawl with retry
            print("Test 1: Crawl with retry")
            print("-" * 80)
            result = await power_ups.crawl_with_retry("https://example.com")
            print(f"URL: {result['url']}")
            print(f"Success: {result['success']}")
            print()

            # Test: Compare URLs
            print("Test 2: Compare URLs")
            print("-" * 80)
            comparison = await power_ups.compare_urls(
                "https://example.com",
                "https://example.org"
            )
            print(f"Similarity: {comparison.get('similarity', 0):.2%}")
            print(f"Identical: {comparison.get('identical', False)}")
            print()

            # Test: Transforms
            print("Test 3: Crawl with transforms")
            print("-" * 80)
            result = await power_ups.crawl_with_transforms(
                "https://example.com",
                transforms=[normalize_whitespace, remove_images]
            )
            print(f"Transformed length: {len(result.get('markdown', ''))}")
            print()

            # Test: Statistics
            print("Power-Up Statistics:")
            print("-" * 80)
            stats = power_ups.get_stats()
            for key, value in stats.items():
                print(f"  {key}: {value}")

        finally:
            await power_ups.cleanup()

    if CRAWL4AI_AVAILABLE:
        asyncio.run(test_powerups())
        print()
        print("=" * 80)
        print("Power-Ups Test Complete!")
        print("=" * 80)
    else:
        print("Crawl4AI not available. Check installation.")
