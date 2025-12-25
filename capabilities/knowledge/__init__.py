"""
Knowledge Lookup Capabilities
Auto-lookup for real-time information when ALFRED doesn't know

Capabilities:
- Stock prices (Polygon.io)
- Weather (OpenWeatherMap) - MECA integration ready
- News (NewsAPI, Polygon, Alpha Vantage)
- Business intelligence
- Cybersecurity intelligence (NVD, CISA, threat intel)
- Tech pulse (cutting-edge tech, AI developments, GitHub trending)
- Encyclopedia (Wikipedia, Wikidata)
- Web search (DuckDuckGo)

Author: Daniel J Rita (BATDAN)
For: ALFRED_J_RITA - State of the Art Intelligence System
"""

from .stock_lookup import StockLookup, create_stock_lookup
from .web_lookup import WebLookup, KnowledgeDetector, create_web_lookup, create_knowledge_detector
from .weather_lookup import WeatherLookup, create_weather_lookup
from .news_lookup import NewsLookup, BusinessIntelligence, create_news_lookup, create_business_intel
from .cybersecurity_intel import CybersecurityIntel, create_cybersecurity_intel
from .tech_pulse import TechPulse, create_tech_pulse
from .encyclopedia_lookup import EncyclopediaLookup, create_encyclopedia_lookup

__all__ = [
    # Stock
    'StockLookup',
    'create_stock_lookup',
    # Web
    'WebLookup',
    'KnowledgeDetector',
    'create_web_lookup',
    'create_knowledge_detector',
    # Weather (MECA)
    'WeatherLookup',
    'create_weather_lookup',
    # News
    'NewsLookup',
    'BusinessIntelligence',
    'create_news_lookup',
    'create_business_intel',
    # Cybersecurity Intelligence
    'CybersecurityIntel',
    'create_cybersecurity_intel',
    # Tech Pulse (Cutting Edge)
    'TechPulse',
    'create_tech_pulse',
    # Encyclopedia (Wikipedia)
    'EncyclopediaLookup',
    'create_encyclopedia_lookup',
]
