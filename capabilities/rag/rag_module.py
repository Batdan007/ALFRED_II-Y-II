#!/usr/bin/env python3
"""
Alfred RAG (Retrieval Augmented Generation) Module
Combines web crawling, vector knowledge base, and LLM for intelligent research
"""

# Fix protobuf compatibility issues
import os
os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'

import asyncio
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
from pathlib import Path

# Import Alfred modules
from vector_knowledge import VectorKnowledgeBase, DocumentChunker
from crawler_advanced import AdvancedCrawler

# Try to import AI clients
try:
    from anthropic import AsyncAnthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    from groq import AsyncGroq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

import os
from dotenv import load_dotenv

load_dotenv()


class RAGSystem:
    """
    Retrieval Augmented Generation System
    Research topics, store in vector DB, answer questions using context
    """

    def __init__(
        self,
        knowledge_base: Optional[VectorKnowledgeBase] = None,
        crawler: Optional[AdvancedCrawler] = None,
        default_ai: str = "groq",
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ):
        """
        Initialize RAG system

        Args:
            knowledge_base: Vector knowledge base instance
            crawler: Advanced crawler instance
            default_ai: Default AI provider ('groq', 'claude', 'openai')
            chunk_size: Document chunk size
            chunk_overlap: Overlap between chunks
        """
        # Initialize components
        self.kb = knowledge_base or VectorKnowledgeBase()
        self.crawler = crawler  # Crawler is optional (can be created per request)
        self.chunker = DocumentChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

        self.default_ai = default_ai

        # Initialize AI clients
        self.anthropic = None
        self.groq = None

        if ANTHROPIC_AVAILABLE and os.getenv('ANTHROPIC_API_KEY'):
            self.anthropic = AsyncAnthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

        if GROQ_AVAILABLE and os.getenv('GROQ_API_KEY'):
            self.groq = AsyncGroq(api_key=os.getenv('GROQ_API_KEY'))

        # Statistics
        self.stats = {
            'research_sessions': 0,
            'urls_crawled': 0,
            'documents_stored': 0,
            'queries_answered': 0
        }

        logging.info("RAG system initialized")

    async def research_url(
        self,
        url: str,
        store_in_kb: bool = True,
        chunk_content: bool = True,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Research a URL: crawl, extract, chunk, and store in knowledge base

        Args:
            url: URL to research
            store_in_kb: Store extracted content in knowledge base
            chunk_content: Chunk large content into smaller pieces
            metadata: Additional metadata to store

        Returns:
            Research result with content and storage info
        """
        # Create crawler if needed
        crawler = self.crawler
        should_close_crawler = False

        if not crawler:
            crawler = AdvancedCrawler(headless=True, verbose=False)
            await crawler.start()
            should_close_crawler = True

        try:
            # Crawl URL
            logging.info(f"Researching URL: {url}")
            result = await crawler.crawl_url(url, extract_markdown=True)

            if not result['success']:
                return {
                    'url': url,
                    'success': False,
                    'error': result.get('error', 'Crawl failed')
                }

            # Extract markdown content
            markdown = result.get('markdown', '')
            if not markdown:
                return {
                    'url': url,
                    'success': False,
                    'error': 'No content extracted'
                }

            # Prepare metadata
            meta = metadata or {}
            meta.update({
                'url': url,
                'source': 'crawl',
                'crawled_at': datetime.now().isoformat(),
                'content_type': 'markdown',
                'status_code': result.get('status_code')
            })

            # Store in knowledge base
            doc_ids = []
            if store_in_kb:
                if chunk_content and len(markdown) > 2000:
                    # Chunk large content
                    chunks = self.chunker.chunk_text(markdown, metadata=meta)
                    texts = [c['text'] for c in chunks]
                    metadatas = [c['metadata'] for c in chunks]

                    doc_ids = self.kb.add_documents_batch(texts, metadatas=metadatas)
                    logging.info(f"Stored {len(chunks)} chunks in knowledge base")
                else:
                    # Store as single document
                    doc_id = self.kb.add_document(markdown, metadata=meta)
                    doc_ids = [doc_id]
                    logging.info(f"Stored 1 document in knowledge base")

            # Update statistics
            self.stats['urls_crawled'] += 1
            self.stats['documents_stored'] += len(doc_ids)

            return {
                'url': url,
                'success': True,
                'markdown': markdown,
                'markdown_length': len(markdown),
                'doc_ids': doc_ids,
                'num_chunks': len(doc_ids),
                'links': result.get('links', []),
                'metadata': meta
            }

        finally:
            if should_close_crawler:
                await crawler.close()

    async def research_urls_batch(
        self,
        urls: List[str],
        max_concurrent: int = 3,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Research multiple URLs concurrently

        Args:
            urls: List of URLs to research
            max_concurrent: Maximum concurrent requests
            **kwargs: Additional arguments for research_url

        Returns:
            List of research results
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def research_with_semaphore(url):
            async with semaphore:
                return await self.research_url(url, **kwargs)

        results = await asyncio.gather(
            *[research_with_semaphore(url) for url in urls],
            return_exceptions=True
        )

        self.stats['research_sessions'] += 1
        return results

    async def deep_research(
        self,
        start_url: str,
        max_depth: int = 2,
        max_pages: int = 20,
        same_domain_only: bool = True
    ) -> Dict[str, Any]:
        """
        Deep research: crawl multiple pages from a starting point

        Args:
            start_url: Starting URL
            max_depth: Maximum link depth to follow
            max_pages: Maximum number of pages to crawl
            same_domain_only: Only crawl same domain

        Returns:
            Deep research results with all crawled content
        """
        # Create crawler
        crawler = self.crawler
        should_close_crawler = False

        if not crawler:
            crawler = AdvancedCrawler(headless=True, verbose=False)
            await crawler.start()
            should_close_crawler = True

        try:
            logging.info(f"Starting deep research from: {start_url}")

            # Perform deep crawl
            crawled_pages = await crawler.deep_crawl(
                start_url,
                max_depth=max_depth,
                max_pages=max_pages,
                same_domain_only=same_domain_only
            )

            # Process and store each page
            stored_docs = []
            for page in crawled_pages:
                if page['success'] and page.get('markdown'):
                    meta = {
                        'url': page['url'],
                        'source': 'deep_crawl',
                        'start_url': start_url,
                        'crawled_at': datetime.now().isoformat()
                    }

                    # Chunk and store
                    chunks = self.chunker.chunk_text(page['markdown'], metadata=meta)
                    texts = [c['text'] for c in chunks]
                    metadatas = [c['metadata'] for c in chunks]

                    doc_ids = self.kb.add_documents_batch(texts, metadatas=metadatas)
                    stored_docs.append({
                        'url': page['url'],
                        'doc_ids': doc_ids,
                        'num_chunks': len(doc_ids)
                    })

            self.stats['research_sessions'] += 1
            self.stats['urls_crawled'] += len(crawled_pages)
            self.stats['documents_stored'] += sum(len(d['doc_ids']) for d in stored_docs)

            logging.info(f"Deep research complete: {len(stored_docs)} pages stored")

            return {
                'start_url': start_url,
                'success': True,
                'pages_crawled': len(crawled_pages),
                'pages_stored': len(stored_docs),
                'total_chunks': sum(len(d['doc_ids']) for d in stored_docs),
                'pages': stored_docs
            }

        finally:
            if should_close_crawler:
                await crawler.close()

    async def ask(
        self,
        question: str,
        n_contexts: int = 5,
        ai_provider: Optional[str] = None,
        include_sources: bool = True,
        min_similarity: float = 0.3
    ) -> Dict[str, Any]:
        """
        Ask a question using RAG (retrieve relevant context, generate answer)

        Args:
            question: Question to answer
            n_contexts: Number of context chunks to retrieve
            ai_provider: AI provider to use ('groq', 'claude', 'openai')
            include_sources: Include source URLs in response
            min_similarity: Minimum similarity score for context

        Returns:
            Answer with sources and context
        """
        # Search knowledge base for relevant context
        search_results = self.kb.search(question, n_results=n_contexts)

        if not search_results['results']:
            return {
                'question': question,
                'answer': "I don't have any information to answer this question. Please research the topic first.",
                'success': False,
                'sources': []
            }

        # Filter by similarity
        contexts = [
            r for r in search_results['results']
            if r.get('similarity', 0) >= min_similarity
        ]

        if not contexts:
            return {
                'question': question,
                'answer': "I found some related information, but it doesn't seem relevant enough to answer your question confidently.",
                'success': False,
                'sources': []
            }

        # Build context for LLM
        context_text = "\n\n---\n\n".join([
            f"Source {i+1} (from {c['metadata'].get('url', 'unknown')}):\n{c['text']}"
            for i, c in enumerate(contexts)
        ])

        # Generate answer using AI
        provider = ai_provider or self.default_ai

        if provider == 'groq' and self.groq:
            answer = await self._ask_groq(question, context_text)
        elif provider == 'claude' and self.anthropic:
            answer = await self._ask_claude(question, context_text)
        else:
            # Fallback: simple extractive answer
            answer = f"Based on the context:\n\n{contexts[0]['text'][:500]}..."

        # Extract sources
        sources = []
        if include_sources:
            seen_urls = set()
            for c in contexts:
                url = c['metadata'].get('url')
                if url and url not in seen_urls:
                    sources.append({
                        'url': url,
                        'similarity': c.get('similarity', 0),
                        'crawled_at': c['metadata'].get('crawled_at')
                    })
                    seen_urls.add(url)

        self.stats['queries_answered'] += 1

        return {
            'question': question,
            'answer': answer,
            'success': True,
            'sources': sources,
            'contexts_used': len(contexts),
            'total_contexts_found': len(search_results['results'])
        }

    async def _ask_groq(self, question: str, context: str) -> str:
        """Generate answer using Groq"""
        try:
            response = await self.groq.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful research assistant. Answer the user's question based on the provided context. Be concise and accurate. If the context doesn't contain enough information, say so."
                    },
                    {
                        "role": "user",
                        "content": f"Context:\n{context}\n\nQuestion: {question}"
                    }
                ],
                temperature=0.3,
                max_tokens=1000
            )

            return response.choices[0].message.content

        except Exception as e:
            logging.error(f"Groq error: {e}")
            return f"Error generating answer: {e}"

    async def _ask_claude(self, question: str, context: str) -> str:
        """Generate answer using Claude"""
        try:
            response = await self.anthropic.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1000,
                temperature=0.3,
                messages=[
                    {
                        "role": "user",
                        "content": f"Context:\n{context}\n\nQuestion: {question}\n\nPlease answer the question based on the provided context. Be concise and accurate."
                    }
                ]
            )

            return response.content[0].text

        except Exception as e:
            logging.error(f"Claude error: {e}")
            return f"Error generating answer: {e}"

    def get_stats(self) -> Dict[str, Any]:
        """Get RAG system statistics"""
        kb_stats = self.kb.get_stats()

        return {
            **self.stats,
            'knowledge_base': kb_stats
        }

    async def clear_knowledge_base(self):
        """Clear all stored knowledge"""
        self.kb.clear()
        self.stats['documents_stored'] = 0
        logging.warning("Knowledge base cleared")


# Convenience function for quick research
async def quick_research(topic: str, max_results: int = 3) -> Dict[str, Any]:
    """
    Quick research: search web, crawl top results, answer question

    Args:
        topic: Topic to research
        max_results: Maximum search results to crawl

    Returns:
        Research summary and answer capability
    """
    rag = RAGSystem()

    # For demo, use example URLs (in production, integrate with search API)
    # Example: search for topic, get URLs, then research
    urls = [
        f"https://en.wikipedia.org/wiki/{topic.replace(' ', '_')}"
    ]

    # Research URLs
    results = await rag.research_urls_batch(urls[:max_results])

    successful = [r for r in results if r.get('success')]

    return {
        'topic': topic,
        'urls_researched': len(successful),
        'total_chunks_stored': sum(r.get('num_chunks', 0) for r in successful),
        'ready_for_questions': len(successful) > 0,
        'rag_system': rag
    }


if __name__ == "__main__":
    # Test RAG system
    print("=" * 80)
    print("Testing Alfred RAG System")
    print("=" * 80)
    print()

    async def test_rag():
        # Initialize RAG
        rag = RAGSystem()

        # Test: Research a URL
        print("Test 1: Research URL")
        print("-" * 80)
        result = await rag.research_url("https://example.com")
        print(f"URL: {result['url']}")
        print(f"Success: {result['success']}")
        print(f"Chunks stored: {result.get('num_chunks', 0)}")
        print()

        # Test: Ask question
        print("Test 2: Ask Question")
        print("-" * 80)
        answer = await rag.ask("What is this website about?")
        print(f"Question: {answer['question']}")
        print(f"Answer: {answer['answer'][:200]}...")
        print(f"Sources: {len(answer['sources'])}")
        print()

        # Test: Statistics
        print("RAG Statistics:")
        print("-" * 80)
        stats = rag.get_stats()
        print(f"Research sessions: {stats['research_sessions']}")
        print(f"URLs crawled: {stats['urls_crawled']}")
        print(f"Documents stored: {stats['documents_stored']}")
        print(f"Queries answered: {stats['queries_answered']}")
        print(f"KB total documents: {stats['knowledge_base']['total_documents']}")
        print()

    asyncio.run(test_rag())

    print("=" * 80)
    print("RAG System Test Complete!")
    print("=" * 80)
