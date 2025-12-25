"""
News Lookup Module
Real-time news for general and business/financial topics

Supports:
- Breaking news
- Topic-specific news
- Business/financial news
- Company-specific news
- Market analysis headlines

Author: Daniel J Rita (BATDAN)
"""

import os
import re
import logging
import requests
from typing import Optional, Dict, List, Tuple
from datetime import datetime, timedelta


class NewsLookup:
    """
    Real-time news lookup using multiple sources

    Sources:
    - NewsAPI.org (general news)
    - Polygon.io (financial news)
    - Alpha Vantage (market news & sentiment)

    Categories:
    - General/Breaking news
    - Business news
    - Technology news
    - Financial/Market news
    - Company-specific news
    """

    # News categories mapping
    CATEGORIES = {
        'business': ['business', 'economy', 'economic', 'corporate', 'company', 'companies', 'market', 'markets'],
        'technology': ['tech', 'technology', 'ai', 'artificial intelligence', 'software', 'startup'],
        'finance': ['stock', 'stocks', 'trading', 'finance', 'financial', 'investment', 'crypto', 'bitcoin'],
        'general': ['news', 'breaking', 'latest', 'today', 'headlines'],
        'politics': ['politics', 'political', 'government', 'election', 'congress', 'senate'],
        'science': ['science', 'research', 'study', 'discovery'],
    }

    # Company name to search term mapping (for targeted news)
    COMPANY_TERMS = {
        'apple': 'Apple Inc AAPL',
        'microsoft': 'Microsoft MSFT',
        'google': 'Google Alphabet GOOGL',
        'amazon': 'Amazon AMZN',
        'tesla': 'Tesla TSLA Elon Musk',
        'meta': 'Meta Facebook META',
        'nvidia': 'NVIDIA NVDA',
        'openai': 'OpenAI ChatGPT',
        'anthropic': 'Anthropic Claude AI',
    }

    def __init__(self, newsapi_key: Optional[str] = None,
                 polygon_key: Optional[str] = None,
                 alphavantage_key: Optional[str] = None):
        """
        Initialize news lookup

        Args:
            newsapi_key: NewsAPI.org API key
            polygon_key: Polygon.io API key (for financial news)
            alphavantage_key: Alpha Vantage API key (for market sentiment)
        """
        self.logger = logging.getLogger(__name__)

        self.newsapi_key = newsapi_key or os.getenv('NEWSAPI_KEY')
        self.polygon_key = polygon_key or os.getenv('POLYGON_API_KEY')
        self.alphavantage_key = alphavantage_key or os.getenv('ALPHA_VANTAGE_API_KEY')

        self.newsapi_url = "https://newsapi.org/v2"
        self.polygon_url = "https://api.polygon.io/v2/reference/news"
        self.alphavantage_url = "https://www.alphavantage.co/query"

        if not any([self.newsapi_key, self.polygon_key]):
            self.logger.warning("No news API keys found - news lookups may be limited")

    def is_available(self) -> bool:
        """Check if any news source is available"""
        return bool(self.newsapi_key or self.polygon_key or self.alphavantage_key)

    def detect_category(self, text: str) -> str:
        """
        Detect news category from text

        Args:
            text: User message

        Returns:
            Category name
        """
        text_lower = text.lower()

        for category, keywords in self.CATEGORIES.items():
            if any(kw in text_lower for kw in keywords):
                return category

        return 'general'

    def extract_topic(self, text: str) -> Optional[str]:
        """
        Extract specific topic/company from text

        Args:
            text: User message

        Returns:
            Topic to search for
        """
        text_lower = text.lower()

        # Check for company names
        for company, search_term in self.COMPANY_TERMS.items():
            if company in text_lower:
                return search_term

        # Extract topic from patterns
        patterns = [
            r"news (?:about|on|for|regarding) ([a-zA-Z\s]+?)(?:\?|$|today|latest)",
            r"(?:about|on|for|regarding) ([a-zA-Z\s]+?) news",
            r"what(?:'s| is) (?:happening|going on) (?:with|in|at) ([a-zA-Z\s]+)",
            r"([a-zA-Z\s]+?) (?:news|headlines|updates)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                topic = match.group(1).strip()
                if len(topic) > 2 and topic not in ['the', 'latest', 'breaking', 'today']:
                    return topic.title()

        return None

    def is_news_query(self, text: str) -> bool:
        """
        Detect if text is asking about news

        Args:
            text: User message

        Returns:
            True if this is a news query
        """
        news_keywords = [
            'news', 'headlines', 'breaking', 'latest',
            'happening', 'going on', 'update', 'updates',
            'announced', 'announcement', 'report', 'reported'
        ]

        text_lower = text.lower()
        return any(kw in text_lower for kw in news_keywords)

    def is_business_news_query(self, text: str) -> bool:
        """
        Detect if specifically asking for business/financial news

        Args:
            text: User message

        Returns:
            True if business news query
        """
        business_keywords = [
            'business', 'market', 'markets', 'stock', 'stocks',
            'economy', 'economic', 'financial', 'finance',
            'corporate', 'earnings', 'trading', 'investment',
            'wall street', 'nasdaq', 'dow', 's&p', 'crypto'
        ]

        text_lower = text.lower()
        return any(kw in text_lower for kw in business_keywords)

    def get_newsapi_headlines(self, category: str = 'general',
                              query: Optional[str] = None,
                              country: str = 'us') -> List[Dict]:
        """
        Get headlines from NewsAPI

        Args:
            category: News category
            query: Search query
            country: Country code

        Returns:
            List of news articles
        """
        if not self.newsapi_key:
            return []

        try:
            if query:
                url = f"{self.newsapi_url}/everything"
                params = {
                    'q': query,
                    'apiKey': self.newsapi_key,
                    'language': 'en',
                    'sortBy': 'publishedAt',
                    'pageSize': 10
                }
            else:
                url = f"{self.newsapi_url}/top-headlines"
                params = {
                    'category': category if category != 'finance' else 'business',
                    'country': country,
                    'apiKey': self.newsapi_key,
                    'pageSize': 10
                }

            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                articles = []

                for article in data.get('articles', [])[:10]:
                    articles.append({
                        'title': article.get('title', ''),
                        'description': article.get('description', ''),
                        'source': article.get('source', {}).get('name', 'Unknown'),
                        'url': article.get('url', ''),
                        'published': article.get('publishedAt', ''),
                        'type': 'general'
                    })

                return articles

            return []

        except Exception as e:
            self.logger.error(f"NewsAPI lookup failed: {e}")
            return []

    def get_polygon_news(self, ticker: Optional[str] = None,
                         limit: int = 10) -> List[Dict]:
        """
        Get financial news from Polygon.io

        Args:
            ticker: Stock ticker (optional)
            limit: Number of articles

        Returns:
            List of financial news articles
        """
        if not self.polygon_key:
            return []

        try:
            params = {
                'apiKey': self.polygon_key,
                'limit': limit,
                'order': 'desc',
                'sort': 'published_utc'
            }

            if ticker:
                params['ticker'] = ticker.upper()

            response = requests.get(self.polygon_url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                articles = []

                for article in data.get('results', []):
                    articles.append({
                        'title': article.get('title', ''),
                        'description': article.get('description', ''),
                        'source': article.get('publisher', {}).get('name', 'Unknown'),
                        'url': article.get('article_url', ''),
                        'published': article.get('published_utc', ''),
                        'tickers': article.get('tickers', []),
                        'type': 'financial'
                    })

                return articles

            return []

        except Exception as e:
            self.logger.error(f"Polygon news lookup failed: {e}")
            return []

    def get_market_sentiment(self, ticker: str) -> Optional[Dict]:
        """
        Get market sentiment from Alpha Vantage

        Args:
            ticker: Stock ticker

        Returns:
            Sentiment data or None
        """
        if not self.alphavantage_key:
            return None

        try:
            params = {
                'function': 'NEWS_SENTIMENT',
                'tickers': ticker.upper(),
                'apikey': self.alphavantage_key,
                'limit': 10
            }

            response = requests.get(self.alphavantage_url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()

                if 'feed' in data:
                    articles = []
                    overall_sentiment = 0

                    for item in data['feed'][:10]:
                        sentiment_score = float(item.get('overall_sentiment_score', 0))
                        overall_sentiment += sentiment_score

                        articles.append({
                            'title': item.get('title', ''),
                            'source': item.get('source', 'Unknown'),
                            'sentiment': item.get('overall_sentiment_label', 'Neutral'),
                            'sentiment_score': sentiment_score,
                            'url': item.get('url', ''),
                            'published': item.get('time_published', ''),
                            'type': 'sentiment'
                        })

                    avg_sentiment = overall_sentiment / len(articles) if articles else 0
                    sentiment_label = 'Bullish' if avg_sentiment > 0.15 else 'Bearish' if avg_sentiment < -0.15 else 'Neutral'

                    return {
                        'ticker': ticker,
                        'sentiment': sentiment_label,
                        'sentiment_score': round(avg_sentiment, 3),
                        'articles': articles
                    }

            return None

        except Exception as e:
            self.logger.error(f"Alpha Vantage sentiment lookup failed: {e}")
            return None

    def format_articles(self, articles: List[Dict], max_articles: int = 5) -> str:
        """
        Format articles for natural language output

        Args:
            articles: List of article dicts
            max_articles: Maximum articles to include

        Returns:
            Formatted string
        """
        if not articles:
            return "No articles found."

        lines = []
        for i, article in enumerate(articles[:max_articles], 1):
            title = article.get('title', 'No title')
            source = article.get('source', 'Unknown')
            lines.append(f"{i}. {title} ({source})")

            if article.get('description'):
                desc = article['description'][:150]
                if len(article['description']) > 150:
                    desc += "..."
                lines.append(f"   {desc}")

        return "\n".join(lines)

    def lookup_for_prompt(self, text: str) -> Tuple[bool, str]:
        """
        Main entry point: check if query needs news data, fetch if so

        Args:
            text: User message

        Returns:
            Tuple of (was_news_query, context_to_inject)
        """
        if not self.is_news_query(text):
            return False, ""

        category = self.detect_category(text)
        topic = self.extract_topic(text)
        is_business = self.is_business_news_query(text)

        self.logger.info(f"News query - Category: {category}, Topic: {topic}, Business: {is_business}")

        articles = []
        sentiment_info = ""

        # For business/financial news, prioritize Polygon
        if is_business or category in ['finance', 'business']:
            # Check for specific ticker
            ticker = None
            if topic:
                # Try to extract ticker from company terms
                for company, terms in self.COMPANY_TERMS.items():
                    if company in topic.lower():
                        ticker = terms.split()[-1] if ' ' in terms else terms
                        break

            # Get financial news
            financial_articles = self.get_polygon_news(ticker=ticker)
            if financial_articles:
                articles.extend(financial_articles)

            # Get sentiment if we have a ticker
            if ticker and self.alphavantage_key:
                sentiment = self.get_market_sentiment(ticker)
                if sentiment:
                    sentiment_info = f"\nMarket Sentiment for {ticker}: {sentiment['sentiment']} (score: {sentiment['sentiment_score']})"

        # Also get general news (or use as fallback)
        if not articles or category not in ['finance', 'business']:
            general_articles = self.get_newsapi_headlines(
                category=category if not topic else 'general',
                query=topic
            )
            articles.extend(general_articles)

        if not articles:
            return True, "[NEWS LOOKUP FAILED - No articles found or API unavailable]"

        # Remove duplicates by title
        seen_titles = set()
        unique_articles = []
        for article in articles:
            if article['title'] not in seen_titles:
                seen_titles.add(article['title'])
                unique_articles.append(article)

        context = f"\n[LIVE NEWS DATA - Retrieved {datetime.now().strftime('%Y-%m-%d %H:%M')}]\n"

        if topic:
            context += f"News about: {topic}\n"
        elif is_business:
            context += "Business/Financial News:\n"
        else:
            context += f"Top {category.title()} Headlines:\n"

        context += self.format_articles(unique_articles)

        if sentiment_info:
            context += sentiment_info

        context += "\n[Use this news data to answer the user's question]\n"

        return True, context


class BusinessIntelligence:
    """
    Business intelligence and economic analysis module

    Provides:
    - Market overview
    - Sector analysis
    - Economic indicators
    - Corporate news aggregation
    """

    def __init__(self, polygon_key: Optional[str] = None,
                 alphavantage_key: Optional[str] = None):
        """
        Initialize business intelligence

        Args:
            polygon_key: Polygon.io API key
            alphavantage_key: Alpha Vantage API key
        """
        self.logger = logging.getLogger(__name__)
        self.polygon_key = polygon_key or os.getenv('POLYGON_API_KEY')
        self.alphavantage_key = alphavantage_key or os.getenv('ALPHA_VANTAGE_API_KEY')
        self.news = NewsLookup(polygon_key=polygon_key, alphavantage_key=alphavantage_key)

    def get_market_overview(self) -> Dict:
        """
        Get overall market overview

        Returns:
            Market overview data
        """
        # Major indices to track
        indices = ['SPY', 'QQQ', 'DIA', 'IWM']

        overview = {
            'timestamp': datetime.now().isoformat(),
            'indices': {},
            'top_news': [],
            'sentiment': 'Neutral'
        }

        # Get news for market overview
        news_articles = self.news.get_polygon_news(limit=5)
        overview['top_news'] = [a['title'] for a in news_articles[:5]]

        return overview

    def get_sector_news(self, sector: str) -> List[Dict]:
        """
        Get news for a specific sector

        Args:
            sector: Sector name (tech, finance, healthcare, etc.)

        Returns:
            List of sector-specific news
        """
        sector_keywords = {
            'tech': 'technology software AI',
            'finance': 'banking financial services',
            'healthcare': 'pharmaceutical biotech medical',
            'energy': 'oil gas renewable energy',
            'retail': 'retail consumer e-commerce',
        }

        query = sector_keywords.get(sector.lower(), sector)
        return self.news.get_newsapi_headlines(query=query)

    def is_business_intel_query(self, text: str) -> bool:
        """
        Check if query is asking for business intelligence

        Args:
            text: User message

        Returns:
            True if business intel query
        """
        intel_keywords = [
            'market overview', 'market analysis', 'economic',
            'sector', 'industry', 'corporate', 'business intelligence',
            'market sentiment', 'economic indicators', 'market trends'
        ]

        text_lower = text.lower()
        return any(kw in text_lower for kw in intel_keywords)


# Convenience functions
def create_news_lookup() -> NewsLookup:
    """Create news lookup instance"""
    return NewsLookup()


def create_business_intel() -> BusinessIntelligence:
    """Create business intelligence instance"""
    return BusinessIntelligence()
