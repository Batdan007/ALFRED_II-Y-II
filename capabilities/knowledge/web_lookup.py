"""
Web Search / Knowledge Lookup Module
General knowledge retrieval from the internet

Author: Daniel J Rita (BATDAN)
"""

import logging
import requests
from typing import Optional, List, Dict, Tuple
from datetime import datetime
import re


class WebLookup:
    """
    Web search and knowledge lookup for ALFRED

    Uses DuckDuckGo Instant Answer API (free, no API key needed)
    Falls back to basic web scraping if needed
    """

    def __init__(self):
        """Initialize web lookup"""
        self.logger = logging.getLogger(__name__)
        self.ddg_url = "https://api.duckduckgo.com/"

    def is_available(self) -> bool:
        """Web lookup is always available"""
        return True

    def search(self, query: str) -> Optional[Dict]:
        """
        Search for information using DuckDuckGo

        Args:
            query: Search query

        Returns:
            Search results or None
        """
        try:
            params = {
                'q': query,
                'format': 'json',
                'no_html': 1,
                'skip_disambig': 1
            }

            response = requests.get(self.ddg_url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                return {
                    'abstract': data.get('Abstract', ''),
                    'abstract_source': data.get('AbstractSource', ''),
                    'abstract_url': data.get('AbstractURL', ''),
                    'answer': data.get('Answer', ''),
                    'definition': data.get('Definition', ''),
                    'related_topics': [
                        {
                            'text': t.get('Text', ''),
                            'url': t.get('FirstURL', '')
                        }
                        for t in data.get('RelatedTopics', [])[:5]
                        if isinstance(t, dict) and t.get('Text')
                    ],
                    'infobox': data.get('Infobox', {}),
                    'type': data.get('Type', ''),
                    'heading': data.get('Heading', '')
                }

            return None

        except Exception as e:
            self.logger.error(f"Web search failed: {e}")
            return None

    def get_news(self, topic: str) -> List[Dict]:
        """
        Get news headlines for a topic

        Args:
            topic: News topic

        Returns:
            List of news items
        """
        # DuckDuckGo doesn't have a dedicated news API in their instant answer
        # For now, we'll search with "news" appended
        results = self.search(f"{topic} latest news")
        if results and results.get('related_topics'):
            return results['related_topics']
        return []

    def format_search_result(self, result: Dict) -> str:
        """
        Format search result for ALFRED's context

        Args:
            result: Search result dict

        Returns:
            Formatted string
        """
        parts = []

        if result.get('answer'):
            parts.append(f"Direct Answer: {result['answer']}")

        if result.get('abstract'):
            source = result.get('abstract_source', 'Unknown')
            parts.append(f"From {source}: {result['abstract']}")

        if result.get('definition'):
            parts.append(f"Definition: {result['definition']}")

        if result.get('related_topics'):
            parts.append("Related information:")
            for topic in result['related_topics'][:3]:
                if topic.get('text'):
                    parts.append(f"  - {topic['text'][:200]}")

        return "\n".join(parts) if parts else ""

    def lookup_for_prompt(self, query: str) -> Tuple[bool, str]:
        """
        Search and format results for injection into prompt

        Args:
            query: Search query

        Returns:
            Tuple of (found_results, context_to_inject)
        """
        self.logger.info(f"Web lookup for: {query}")

        result = self.search(query)
        if not result:
            return False, ""

        formatted = self.format_search_result(result)
        if not formatted:
            return False, ""

        context = f"\n[WEB KNOWLEDGE - Retrieved {datetime.now().strftime('%Y-%m-%d %H:%M')}]\n"
        context += formatted
        context += "\n[Use this information to answer the user's question]\n"

        return True, context


class KnowledgeDetector:
    """
    Detects when ALFRED needs to look something up

    Analyzes both:
    1. User queries that require real-time data
    2. ALFRED's responses that indicate uncertainty
    """

    # Patterns indicating ALFRED doesn't know
    UNCERTAINTY_PATTERNS = [
        r"i don'?t (?:know|have)",
        r"i'?m not (?:sure|certain|aware)",
        r"i cannot (?:provide|give|tell)",
        r"as of my (?:knowledge|training|last update)",
        r"my (?:knowledge|information) (?:cutoff|ends)",
        r"i don'?t have (?:access|information|data)",
        r"unable to (?:provide|access|retrieve)",
        r"no (?:information|data) (?:available|on)",
        r"beyond my (?:knowledge|capabilities)",
        r"i would need to (?:look|search|check)",
        r"real-?time (?:data|information|prices)",
        r"current (?:price|value|status)",
    ]

    # Query patterns that always need lookup
    REALTIME_PATTERNS = [
        r"what(?:'s| is) the (?:current|latest|today'?s?)",
        r"how much is .+ (?:right now|today|currently|trading)",
        r"(?:current|latest|today'?s?) (?:price|value|news|weather)",
        r"what(?:'s| is) .+ (?:trading|worth|valued) at",
        r"(?:stock|share|crypto) price",
        r"market (?:update|status|news)",
        r"(?:latest|recent|breaking) news",
        r"what(?:'s| is) happening (?:with|to|in)",
        r"(?:score|result) of .+ game",
        r"weather (?:in|for|at)",
    ]

    def __init__(self):
        """Initialize detector"""
        self.logger = logging.getLogger(__name__)
        self.uncertainty_re = [re.compile(p, re.IGNORECASE) for p in self.UNCERTAINTY_PATTERNS]
        self.realtime_re = [re.compile(p, re.IGNORECASE) for p in self.REALTIME_PATTERNS]

    def needs_lookup_before(self, user_query: str) -> bool:
        """
        Check if query needs lookup BEFORE asking the LLM

        Args:
            user_query: User's question

        Returns:
            True if we should lookup first
        """
        # Check for real-time query patterns
        for pattern in self.realtime_re:
            if pattern.search(user_query):
                self.logger.info(f"Query matched real-time pattern: {pattern.pattern}")
                return True

        return False

    def needs_lookup_after(self, response: str) -> bool:
        """
        Check if ALFRED's response indicates it needs help

        Args:
            response: ALFRED's initial response

        Returns:
            True if response shows uncertainty
        """
        for pattern in self.uncertainty_re:
            if pattern.search(response):
                self.logger.info(f"Response matched uncertainty pattern: {pattern.pattern}")
                return True

        return False

    def extract_lookup_query(self, user_query: str, response: Optional[str] = None) -> str:
        """
        Extract what to search for

        Args:
            user_query: Original user query
            response: Optional ALFRED response

        Returns:
            Optimized search query
        """
        # Remove common question words to get the core topic
        query = user_query.lower()
        remove_words = [
            "what's", "what is", "who is", "where is", "when is",
            "how is", "how much is", "tell me about", "can you tell me",
            "do you know", "please", "alfred", "hey", "hi"
        ]

        for word in remove_words:
            query = query.replace(word, "")

        return query.strip()


# Convenience functions
def create_web_lookup() -> WebLookup:
    """Create web lookup instance"""
    return WebLookup()


def create_knowledge_detector() -> KnowledgeDetector:
    """Create knowledge detector instance"""
    return KnowledgeDetector()
