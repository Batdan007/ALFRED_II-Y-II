"""
Encyclopedia & Knowledge Base Module
Wikipedia and general knowledge lookups

Sources:
- Wikipedia API (free, no key required)
- Wikidata (structured data)

Author: Daniel J Rita (BATDAN)
For: ALFRED_J_RITA - Human Knowledge Database
"""

import logging
import requests
from typing import Optional, Dict, List, Tuple
from datetime import datetime
import re


class EncyclopediaLookup:
    """
    Encyclopedia and knowledge base lookups for ALFRED

    Capabilities:
    - Wikipedia article summaries
    - Full article content
    - Search across Wikipedia
    - Related topics
    - Wikidata structured facts
    - Multi-language support
    """

    # Wikipedia API endpoints
    WIKIPEDIA_API = "https://en.wikipedia.org/api/rest_v1"
    WIKIPEDIA_ACTION_API = "https://en.wikipedia.org/w/api.php"
    WIKIDATA_API = "https://www.wikidata.org/w/api.php"

    # Query patterns that suggest encyclopedia lookup
    KNOWLEDGE_PATTERNS = [
        r"what is (?:a |an |the )?(.+?)(?:\?|$)",
        r"who is (?:a |an |the )?(.+?)(?:\?|$)",
        r"who was (?:a |an |the )?(.+?)(?:\?|$)",
        r"what are (?:a |an |the )?(.+?)(?:\?|$)",
        r"what was (?:a |an |the )?(.+?)(?:\?|$)",
        r"define (.+?)(?:\?|$)",
        r"tell me about (.+?)(?:\?|$)",
        r"explain (.+?)(?:\?|$)",
        r"history of (.+?)(?:\?|$)",
        r"meaning of (.+?)(?:\?|$)",
        r"who invented (.+?)(?:\?|$)",
        r"who created (.+?)(?:\?|$)",
        r"when was (.+?) (?:born|created|invented|founded|discovered)",
        r"where is (.+?)(?:\?|$)",
        r"where was (.+?)(?:\?|$)",
    ]

    # Categories that benefit from encyclopedia lookup
    KNOWLEDGE_KEYWORDS = [
        'history', 'biography', 'science', 'geography', 'culture',
        'philosophy', 'art', 'literature', 'music', 'religion',
        'politics', 'economics', 'mathematics', 'physics', 'chemistry',
        'biology', 'medicine', 'engineering', 'architecture',
        'country', 'city', 'person', 'event', 'war', 'revolution',
        'invention', 'discovery', 'theory', 'concept', 'definition'
    ]

    def __init__(self, language: str = 'en'):
        """
        Initialize encyclopedia lookup

        Args:
            language: Wikipedia language code (default: English)
        """
        self.logger = logging.getLogger(__name__)
        self.language = language
        self.base_api = f"https://{language}.wikipedia.org/api/rest_v1"
        self.action_api = f"https://{language}.wikipedia.org/w/api.php"

    def is_available(self) -> bool:
        """Wikipedia API is always available (public, no key needed)"""
        return True

    def is_knowledge_query(self, text: str) -> bool:
        """
        Detect if text is asking for encyclopedia/factual knowledge

        Args:
            text: User message

        Returns:
            True if this appears to be a knowledge query
        """
        text_lower = text.lower()

        # Check for knowledge patterns
        for pattern in self.KNOWLEDGE_PATTERNS:
            if re.search(pattern, text_lower):
                return True

        # Check for knowledge keywords
        if any(kw in text_lower for kw in self.KNOWLEDGE_KEYWORDS):
            return True

        return False

    def extract_topic(self, text: str) -> Optional[str]:
        """
        Extract the topic to look up from user text

        Args:
            text: User message

        Returns:
            Topic to search for
        """
        text_lower = text.lower()

        # Try patterns first
        for pattern in self.KNOWLEDGE_PATTERNS:
            match = re.search(pattern, text_lower)
            if match:
                topic = match.group(1).strip()
                # Clean up common words
                topic = re.sub(r'^(a |an |the )', '', topic)
                return topic.title() if topic else None

        # Fallback: remove question words and extract main phrase
        remove_words = [
            'what', 'who', 'where', 'when', 'why', 'how',
            'is', 'are', 'was', 'were', 'tell', 'me', 'about',
            'explain', 'define', 'the', 'a', 'an', 'please', '?'
        ]

        words = text_lower.split()
        filtered = [w for w in words if w not in remove_words]
        if filtered:
            return ' '.join(filtered).title()

        return None

    def get_summary(self, title: str) -> Optional[Dict]:
        """
        Get Wikipedia article summary

        Args:
            title: Article title

        Returns:
            Summary data or None
        """
        try:
            # Use the REST API for summaries
            url = f"{self.base_api}/page/summary/{title.replace(' ', '_')}"

            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                return {
                    'title': data.get('title', title),
                    'description': data.get('description', ''),
                    'extract': data.get('extract', ''),
                    'url': data.get('content_urls', {}).get('desktop', {}).get('page', ''),
                    'thumbnail': data.get('thumbnail', {}).get('source', ''),
                    'type': data.get('type', 'standard'),
                    'timestamp': data.get('timestamp', '')
                }

            # If direct lookup fails, try search
            if response.status_code == 404:
                return self._search_and_get_summary(title)

            return None

        except Exception as e:
            self.logger.error(f"Wikipedia summary failed for {title}: {e}")
            return None

    def _search_and_get_summary(self, query: str) -> Optional[Dict]:
        """
        Search Wikipedia and get summary of best match

        Args:
            query: Search query

        Returns:
            Summary of best match or None
        """
        try:
            # Search for articles
            params = {
                'action': 'query',
                'list': 'search',
                'srsearch': query,
                'srlimit': 1,
                'format': 'json'
            }

            response = requests.get(self.action_api, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                results = data.get('query', {}).get('search', [])

                if results:
                    # Get summary of first result
                    best_match = results[0]['title']
                    return self.get_summary(best_match)

            return None

        except Exception as e:
            self.logger.error(f"Wikipedia search failed: {e}")
            return None

    def search(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Search Wikipedia for articles

        Args:
            query: Search query
            limit: Max results

        Returns:
            List of search results
        """
        try:
            params = {
                'action': 'query',
                'list': 'search',
                'srsearch': query,
                'srlimit': limit,
                'srprop': 'snippet|titlesnippet',
                'format': 'json'
            }

            response = requests.get(self.action_api, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                results = []

                for item in data.get('query', {}).get('search', []):
                    # Clean HTML from snippet
                    snippet = re.sub(r'<[^>]+>', '', item.get('snippet', ''))
                    results.append({
                        'title': item.get('title', ''),
                        'snippet': snippet,
                        'pageid': item.get('pageid'),
                        'url': f"https://{self.language}.wikipedia.org/wiki/{item.get('title', '').replace(' ', '_')}"
                    })

                return results

            return []

        except Exception as e:
            self.logger.error(f"Wikipedia search failed: {e}")
            return []

    def get_full_article(self, title: str, sentences: int = 10) -> Optional[Dict]:
        """
        Get full article content (first N sentences)

        Args:
            title: Article title
            sentences: Number of sentences to extract

        Returns:
            Article content or None
        """
        try:
            params = {
                'action': 'query',
                'titles': title,
                'prop': 'extracts|info|categories',
                'exsentences': sentences,
                'exintro': True,
                'explaintext': True,
                'inprop': 'url',
                'format': 'json'
            }

            response = requests.get(self.action_api, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                pages = data.get('query', {}).get('pages', {})

                for page_id, page in pages.items():
                    if page_id != '-1':  # -1 means not found
                        return {
                            'title': page.get('title', title),
                            'content': page.get('extract', ''),
                            'url': page.get('fullurl', ''),
                            'categories': [
                                c.get('title', '').replace('Category:', '')
                                for c in page.get('categories', [])[:5]
                            ],
                            'pageid': page_id
                        }

            return None

        except Exception as e:
            self.logger.error(f"Wikipedia article fetch failed: {e}")
            return None

    def get_related_topics(self, title: str, limit: int = 5) -> List[str]:
        """
        Get related topics/articles

        Args:
            title: Article title
            limit: Max results

        Returns:
            List of related topic titles
        """
        try:
            params = {
                'action': 'query',
                'titles': title,
                'prop': 'links',
                'pllimit': limit * 2,  # Get more than needed, filter later
                'plnamespace': 0,  # Main namespace only
                'format': 'json'
            }

            response = requests.get(self.action_api, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                pages = data.get('query', {}).get('pages', {})

                for page in pages.values():
                    links = page.get('links', [])
                    return [link.get('title', '') for link in links[:limit]]

            return []

        except Exception as e:
            self.logger.error(f"Wikipedia related topics failed: {e}")
            return []

    def get_wikidata_facts(self, title: str) -> Optional[Dict]:
        """
        Get structured facts from Wikidata

        Args:
            title: Entity name

        Returns:
            Structured facts or None
        """
        try:
            # First, get Wikidata entity ID from Wikipedia
            params = {
                'action': 'query',
                'titles': title,
                'prop': 'pageprops',
                'format': 'json'
            }

            response = requests.get(self.action_api, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                pages = data.get('query', {}).get('pages', {})

                for page in pages.values():
                    wikibase_id = page.get('pageprops', {}).get('wikibase_item')
                    if wikibase_id:
                        return self._fetch_wikidata_entity(wikibase_id)

            return None

        except Exception as e:
            self.logger.error(f"Wikidata lookup failed: {e}")
            return None

    def _fetch_wikidata_entity(self, entity_id: str) -> Optional[Dict]:
        """Fetch Wikidata entity details"""
        try:
            params = {
                'action': 'wbgetentities',
                'ids': entity_id,
                'props': 'labels|descriptions|claims',
                'languages': self.language,
                'format': 'json'
            }

            response = requests.get(self.WIKIDATA_API, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                entity = data.get('entities', {}).get(entity_id, {})

                return {
                    'id': entity_id,
                    'label': entity.get('labels', {}).get(self.language, {}).get('value', ''),
                    'description': entity.get('descriptions', {}).get(self.language, {}).get('value', ''),
                    'claims_count': len(entity.get('claims', {}))
                }

            return None

        except Exception as e:
            self.logger.error(f"Wikidata entity fetch failed: {e}")
            return None

    def format_summary(self, summary: Dict) -> str:
        """
        Format Wikipedia summary for display

        Args:
            summary: Summary data dict

        Returns:
            Formatted string
        """
        lines = []

        if summary.get('title'):
            lines.append(f"[{summary['title']}]")

        if summary.get('description'):
            lines.append(f"({summary['description']})")

        if summary.get('extract'):
            lines.append(summary['extract'])

        if summary.get('url'):
            lines.append(f"Source: {summary['url']}")

        return "\n".join(lines)

    def lookup_for_prompt(self, text: str) -> Tuple[bool, str]:
        """
        Main entry point: check if query needs encyclopedia data, fetch if so

        Args:
            text: User message

        Returns:
            Tuple of (was_knowledge_query, context_to_inject)
        """
        if not self.is_knowledge_query(text):
            return False, ""

        topic = self.extract_topic(text)
        if not topic:
            return False, ""

        self.logger.info(f"Encyclopedia query detected for: {topic}")

        # Get Wikipedia summary
        summary = self.get_summary(topic)
        if not summary or not summary.get('extract'):
            # Try search as fallback
            results = self.search(topic, limit=1)
            if results:
                summary = self.get_summary(results[0]['title'])

        if not summary or not summary.get('extract'):
            return True, f"[ENCYCLOPEDIA LOOKUP: No Wikipedia article found for '{topic}']"

        context = f"\n[ENCYCLOPEDIA DATA - Wikipedia - Retrieved {datetime.now().strftime('%Y-%m-%d %H:%M')}]\n"
        context += self.format_summary(summary)

        # Get related topics if available
        related = self.get_related_topics(summary.get('title', topic), limit=3)
        if related:
            context += f"\n\nRelated topics: {', '.join(related)}"

        context += "\n[Use this encyclopedia data to provide an informed, factual response]\n"

        return True, context


# Convenience function
def create_encyclopedia_lookup(language: str = 'en') -> EncyclopediaLookup:
    """Create encyclopedia lookup instance"""
    return EncyclopediaLookup(language=language)
