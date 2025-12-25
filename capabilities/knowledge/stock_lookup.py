"""
Stock Price Lookup Module
Real-time stock data via Polygon.io API

Author: Daniel J Rita (BATDAN)
"""

import os
import re
import logging
import requests
from typing import Optional, Dict, List, Tuple
from datetime import datetime, timedelta


class StockLookup:
    """
    Real-time stock price lookup using Polygon.io

    Features:
    - Current price quotes
    - Daily change percentage
    - Company name resolution
    - Ticker symbol detection in natural language
    """

    # Common company name to ticker mappings
    COMPANY_TICKERS = {
        'apple': 'AAPL',
        'microsoft': 'MSFT',
        'google': 'GOOGL',
        'alphabet': 'GOOGL',
        'amazon': 'AMZN',
        'tesla': 'TSLA',
        'meta': 'META',
        'facebook': 'META',
        'nvidia': 'NVDA',
        'netflix': 'NFLX',
        'amd': 'AMD',
        'intel': 'INTC',
        'disney': 'DIS',
        'nike': 'NKE',
        'coca-cola': 'KO',
        'coke': 'KO',
        'pepsi': 'PEP',
        'walmart': 'WMT',
        'costco': 'COST',
        'starbucks': 'SBUX',
        'boeing': 'BA',
        'ford': 'F',
        'gm': 'GM',
        'general motors': 'GM',
        'uber': 'UBER',
        'lyft': 'LYFT',
        'airbnb': 'ABNB',
        'paypal': 'PYPL',
        'visa': 'V',
        'mastercard': 'MA',
        'jpmorgan': 'JPM',
        'goldman sachs': 'GS',
        'bank of america': 'BAC',
        'wells fargo': 'WFC',
        'berkshire': 'BRK.B',
        'johnson & johnson': 'JNJ',
        'pfizer': 'PFE',
        'moderna': 'MRNA',
        'spotify': 'SPOT',
        'twitter': 'X',
        'x corp': 'X',
        'snap': 'SNAP',
        'snapchat': 'SNAP',
        'pinterest': 'PINS',
        'salesforce': 'CRM',
        'oracle': 'ORCL',
        'ibm': 'IBM',
        'cisco': 'CSCO',
        'zoom': 'ZM',
        'shopify': 'SHOP',
        'square': 'SQ',
        'block': 'SQ',
        'coinbase': 'COIN',
        'robinhood': 'HOOD',
        'palantir': 'PLTR',
        'snowflake': 'SNOW',
        'crowdstrike': 'CRWD',
        'datadog': 'DDOG',
        'unity': 'U',
        'roblox': 'RBLX',
        'draftkings': 'DKNG',
        'lucid': 'LCID',
        'rivian': 'RIVN',
        'gamestop': 'GME',
        'amc': 'AMC',
        'blackberry': 'BB',
    }

    # Crypto mappings (Polygon supports crypto too)
    CRYPTO_TICKERS = {
        'bitcoin': 'X:BTCUSD',
        'btc': 'X:BTCUSD',
        'ethereum': 'X:ETHUSD',
        'eth': 'X:ETHUSD',
        'dogecoin': 'X:DOGEUSD',
        'doge': 'X:DOGEUSD',
        'solana': 'X:SOLUSD',
        'sol': 'X:SOLUSD',
        'cardano': 'X:ADAUSD',
        'ada': 'X:ADAUSD',
        'xrp': 'X:XRPUSD',
        'ripple': 'X:XRPUSD',
    }

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize stock lookup

        Args:
            api_key: Polygon.io API key (defaults to POLYGON_API_KEY env var)
        """
        self.logger = logging.getLogger(__name__)
        self.api_key = api_key or os.getenv('POLYGON_API_KEY')
        self.base_url = "https://api.polygon.io"

        if not self.api_key:
            self.logger.warning("No Polygon API key found - stock lookups will fail")

    def is_available(self) -> bool:
        """Check if stock lookup is available"""
        return bool(self.api_key)

    def extract_tickers(self, text: str) -> List[str]:
        """
        Extract stock tickers from natural language text

        Args:
            text: User message

        Returns:
            List of ticker symbols found
        """
        tickers = []
        text_lower = text.lower()

        # Check for company names
        for company, ticker in self.COMPANY_TICKERS.items():
            if company in text_lower:
                tickers.append(ticker)

        # Check for crypto
        for crypto, ticker in self.CRYPTO_TICKERS.items():
            if crypto in text_lower:
                tickers.append(ticker)

        # Check for explicit ticker symbols (uppercase 1-5 letters)
        # Pattern: $AAPL or just AAPL when surrounded by spaces
        ticker_pattern = r'\$([A-Z]{1,5})\b|\b([A-Z]{1,5})\b(?=\s+(?:stock|price|trading|share|at\?|today|\?))'
        matches = re.findall(ticker_pattern, text)
        for match in matches:
            ticker = match[0] or match[1]
            if ticker and ticker not in ['I', 'A', 'THE', 'IS', 'AT', 'FOR', 'AND', 'OR', 'NOT']:
                tickers.append(ticker)

        return list(set(tickers))  # Remove duplicates

    def is_stock_query(self, text: str) -> bool:
        """
        Detect if text is asking about stock prices

        Args:
            text: User message

        Returns:
            True if this appears to be a stock query
        """
        stock_keywords = [
            'stock', 'price', 'trading', 'share', 'shares',
            'market', 'ticker', 'quote', 'worth', 'value',
            'trading at', 'currently at', "what's", "what is",
            'how much is', 'how is', 'check', 'look up'
        ]

        text_lower = text.lower()

        # Check for stock keywords
        has_keyword = any(kw in text_lower for kw in stock_keywords)

        # Check for tickers
        has_ticker = len(self.extract_tickers(text)) > 0

        return has_keyword and has_ticker

    def get_quote(self, ticker: str) -> Optional[Dict]:
        """
        Get current stock quote

        Args:
            ticker: Stock ticker symbol

        Returns:
            Quote data or None if failed
        """
        if not self.api_key:
            return None

        try:
            # Clean ticker
            ticker = ticker.upper().strip()
            is_crypto = ticker.startswith('X:')

            # Use previous close endpoint for stocks
            if is_crypto:
                url = f"{self.base_url}/v2/aggs/ticker/{ticker}/prev"
            else:
                url = f"{self.base_url}/v2/aggs/ticker/{ticker}/prev"

            params = {'apiKey': self.api_key}

            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if data.get('results') and len(data['results']) > 0:
                    result = data['results'][0]
                    return {
                        'ticker': ticker,
                        'price': result.get('c'),  # Close price
                        'open': result.get('o'),
                        'high': result.get('h'),
                        'low': result.get('l'),
                        'volume': result.get('v'),
                        'change': round(result.get('c', 0) - result.get('o', 0), 2),
                        'change_percent': round(((result.get('c', 0) - result.get('o', 0)) / result.get('o', 1)) * 100, 2) if result.get('o') else 0,
                        'timestamp': datetime.now().isoformat()
                    }

            self.logger.warning(f"Polygon API returned {response.status_code} for {ticker}")
            return None

        except Exception as e:
            self.logger.error(f"Stock lookup failed for {ticker}: {e}")
            return None

    def get_multiple_quotes(self, tickers: List[str]) -> Dict[str, Dict]:
        """
        Get quotes for multiple tickers

        Args:
            tickers: List of ticker symbols

        Returns:
            Dict mapping ticker to quote data
        """
        quotes = {}
        for ticker in tickers:
            quote = self.get_quote(ticker)
            if quote:
                quotes[ticker] = quote
        return quotes

    def format_quote(self, quote: Dict) -> str:
        """
        Format quote for natural language response

        Args:
            quote: Quote data dict

        Returns:
            Formatted string for ALFRED to use
        """
        ticker = quote['ticker']
        price = quote['price']
        change = quote['change']
        change_pct = quote['change_percent']

        direction = "up" if change >= 0 else "down"
        sign = "+" if change >= 0 else ""

        return f"{ticker}: ${price:.2f} ({sign}{change_pct:.2f}% {direction})"

    def lookup_for_prompt(self, text: str) -> Tuple[bool, str]:
        """
        Main entry point: check if query needs stock data, fetch if so

        Args:
            text: User message

        Returns:
            Tuple of (was_stock_query, context_to_inject)
        """
        if not self.is_stock_query(text):
            return False, ""

        tickers = self.extract_tickers(text)
        if not tickers:
            return False, ""

        self.logger.info(f"Detected stock query for: {tickers}")

        quotes = self.get_multiple_quotes(tickers)
        if not quotes:
            return True, "[STOCK LOOKUP FAILED - Markets may be closed or ticker not found]"

        # Format for injection into prompt
        quote_lines = [self.format_quote(q) for q in quotes.values()]
        context = f"\n[LIVE STOCK DATA - Retrieved {datetime.now().strftime('%Y-%m-%d %H:%M')}]\n"
        context += "\n".join(quote_lines)
        context += "\n[Use this data to answer the user's question about stock prices]\n"

        return True, context


# Convenience function
def create_stock_lookup() -> StockLookup:
    """Create stock lookup instance"""
    return StockLookup()
