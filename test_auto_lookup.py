"""
ALFRED_J_RITA Intelligence Suite Test
State-of-the-art auto-lookup testing:
- Stock prices
- Weather (MECA)
- News & Business Intel
- Cybersecurity Intelligence (CVEs, threats)
- Tech Pulse (cutting-edge tech, AI, GitHub)
- Web search

Author: Daniel J Rita (BATDAN)
For: ALFRED_J_RITA - Edge of Tomorrow Intelligence
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set API keys
os.environ['POLYGON_API_KEY'] = 'EFi9PcjomiO4KnuJafU1lEOf3UfwqwxR'
os.environ['ALPHA_VANTAGE_API_KEY'] = 'Y86Q9V81KY4T3NUE'
os.environ['OPEN_WEATHER_KEY'] = 'ed1a752e0aa0976597e05c0ec5a16d0e'
os.environ['NEWSAPI_KEY'] = '6a78f9b1571d4af2abb886bf98496b17'
# Get a free NVD API key at: https://nvd.nist.gov/developers/request-an-api-key
# os.environ['NVD_API_KEY'] = 'your_key_here'  # Optional, increases rate limits

from capabilities.knowledge.stock_lookup import StockLookup
from capabilities.knowledge.web_lookup import WebLookup, KnowledgeDetector
from capabilities.knowledge.weather_lookup import WeatherLookup
from capabilities.knowledge.news_lookup import NewsLookup, BusinessIntelligence
from capabilities.knowledge.cybersecurity_intel import CybersecurityIntel
from capabilities.knowledge.tech_pulse import TechPulse


def test_stock_lookup():
    """Test stock price lookups"""
    print("\n" + "="*60)
    print("TESTING STOCK LOOKUP")
    print("="*60)

    stock = StockLookup()
    print(f"Stock lookup available: {stock.is_available()}")

    # Test ticker extraction
    test_queries = [
        "What's Tesla trading at?",
        "How much is AAPL stock worth?",
        "Check the price of Microsoft",
        "What is $NVDA at today?",
        "Bitcoin price please",
    ]

    for query in test_queries:
        tickers = stock.extract_tickers(query)
        is_stock = stock.is_stock_query(query)
        print(f"\nQuery: {query}")
        print(f"  Is stock query: {is_stock}")
        print(f"  Tickers found: {tickers}")

    # Test actual API call
    print("\n--- Testing actual stock lookup ---")
    test_tickers = ['TSLA', 'AAPL', 'MSFT']
    for ticker in test_tickers:
        quote = stock.get_quote(ticker)
        if quote:
            print(f"\n{stock.format_quote(quote)}")
        else:
            print(f"\n{ticker}: Failed to get quote (markets may be closed)")


def test_web_lookup():
    """Test web search"""
    print("\n" + "="*60)
    print("TESTING WEB LOOKUP")
    print("="*60)

    web = WebLookup()
    print(f"Web lookup available: {web.is_available()}")

    test_queries = [
        "Python programming language",
        "Who is Elon Musk",
        "What is machine learning",
    ]

    for query in test_queries:
        print(f"\nSearching: {query}")
        found, context = web.lookup_for_prompt(query)
        if found:
            print(f"Result: {context[:300]}...")
        else:
            print("No results found")


def test_weather_lookup():
    """Test weather lookups (MECA integration)"""
    print("\n" + "="*60)
    print("TESTING WEATHER LOOKUP (MECA)")
    print("="*60)

    weather = WeatherLookup()
    print(f"Weather lookup available: {weather.is_available()}")

    if not weather.is_available():
        print("Set OPEN_WEATHER_KEY environment variable")
        return

    # Test location extraction
    test_queries = [
        "What's the weather in New York?",
        "Weather forecast for Los Angeles",
        "Is it raining in Seattle?",
        "Temperature in Miami",
    ]

    print("\n--- Location extraction ---")
    for query in test_queries:
        location = weather.extract_location(query)
        is_weather = weather.is_weather_query(query)
        print(f"Query: {query}")
        print(f"  Is weather query: {is_weather}")
        print(f"  Location: {location}")

    # Test actual API call
    print("\n--- Testing actual weather lookup ---")
    test_locations = ['New York', 'London', 'Tokyo']
    for location in test_locations:
        current = weather.get_current(location)
        if current:
            print(f"\n{weather.format_current(current)}")
        else:
            print(f"\n{location}: Failed to get weather")

    # Test MECA-ready data format
    print("\n--- MECA Data Format ---")
    meca_data = weather.get_meca_data('New York')
    if meca_data:
        print(f"MECA Weather Data: {meca_data}")


def test_news_lookup():
    """Test news lookups"""
    print("\n" + "="*60)
    print("TESTING NEWS LOOKUP")
    print("="*60)

    news = NewsLookup()
    print(f"News lookup available: {news.is_available()}")
    print(f"  - Polygon (financial): {bool(news.polygon_key)}")
    print(f"  - Alpha Vantage (sentiment): {bool(news.alphavantage_key)}")
    print(f"  - NewsAPI (general): {bool(news.newsapi_key)}")

    # Test query detection
    test_queries = [
        "What's the latest news?",
        "Business news today",
        "News about Tesla",
        "What's happening in the stock market?",
        "Latest tech news",
    ]

    print("\n--- Query detection ---")
    for query in test_queries:
        is_news = news.is_news_query(query)
        is_business = news.is_business_news_query(query)
        category = news.detect_category(query)
        topic = news.extract_topic(query)
        print(f"Query: {query}")
        print(f"  Is news: {is_news}, Is business: {is_business}")
        print(f"  Category: {category}, Topic: {topic}")

    # Test financial news from Polygon
    print("\n--- Financial News (Polygon) ---")
    financial_news = news.get_polygon_news(limit=5)
    if financial_news:
        for i, article in enumerate(financial_news[:3], 1):
            print(f"{i}. {article['title'][:80]}... ({article['source']})")
    else:
        print("No financial news (check Polygon API key)")

    # Test full lookup
    print("\n--- Full news lookup ---")
    found, context = news.lookup_for_prompt("What's the latest business news?")
    if found:
        print(f"Result:\n{context[:500]}...")
    else:
        print("No news found")


def test_business_intel():
    """Test business intelligence module"""
    print("\n" + "="*60)
    print("TESTING BUSINESS INTELLIGENCE")
    print("="*60)

    bi = BusinessIntelligence()

    # Test market overview
    print("\n--- Market Overview ---")
    overview = bi.get_market_overview()
    print(f"Timestamp: {overview['timestamp']}")
    print(f"Top Headlines:")
    for headline in overview['top_news'][:3]:
        print(f"  - {headline[:70]}...")

    # Test query detection
    test_queries = [
        "Give me a market overview",
        "What's the economic outlook?",
        "Sector analysis for tech",
    ]

    print("\n--- Business Intel Query Detection ---")
    for query in test_queries:
        is_bi = bi.is_business_intel_query(query)
        print(f"'{query}' -> Is BI query: {is_bi}")


def test_cybersecurity_intel():
    """Test cybersecurity intelligence lookups"""
    print("\n" + "="*60)
    print("TESTING CYBERSECURITY INTELLIGENCE")
    print("="*60)

    cyber = CybersecurityIntel()
    print(f"Cybersecurity intel available: {cyber.is_available()}")

    # Test CVE ID extraction
    test_texts = [
        "Tell me about CVE-2024-3400",
        "What is the Log4Shell vulnerability CVE-2021-44228?",
        "Are CVE-2023-4966 and CVE-2023-46747 related?",
    ]

    print("\n--- CVE ID Extraction ---")
    for text in test_texts:
        cves = cyber.extract_cve_ids(text)
        print(f"Text: {text[:50]}...")
        print(f"  CVEs found: {cves}")

    # Test security query detection
    test_queries = [
        "What are the latest critical vulnerabilities?",
        "Tell me about ransomware threats",
        "Is there a zero-day in Chrome?",
        "What's the weather like?",  # Should NOT be security
    ]

    print("\n--- Security Query Detection ---")
    for query in test_queries:
        is_sec = cyber.is_security_query(query)
        print(f"'{query[:40]}...' -> Is security: {is_sec}")

    # Test actual CVE lookup
    print("\n--- CVE Lookup (NVD API) ---")
    test_cves = ['CVE-2024-3400', 'CVE-2021-44228', 'CVE-2023-4966']
    for cve_id in test_cves:
        print(f"\nLooking up {cve_id}...")
        cve_data = cyber.get_cve_details(cve_id)
        if cve_data:
            print(cyber.format_cve(cve_data))
            # Check if actively exploited
            exploit_status = cyber.check_if_exploited(cve_id)
            if exploit_status['exploited']:
                print(f"   [!] ACTIVELY EXPLOITED (CISA KEV)")
        else:
            print(f"   Failed to fetch (rate limited?)")

    # Test threat brief
    print("\n--- Threat Landscape Brief ---")
    brief = cyber.get_threat_brief()
    print(f"CISA KEV Total: {brief['total_kev_count']} known exploited vulnerabilities")
    if brief['critical_cves']:
        print("\nRecent Critical CVEs:")
        for cve in brief['critical_cves'][:3]:
            print(f"  • {cve['id']} (CVSS {cve['cvss_score']})")
    if brief['actively_exploited']:
        print("\nRecently Added to CISA KEV:")
        for v in brief['actively_exploited'][:3]:
            print(f"  • {v['id']}: {v['vendor']} {v['product']}")


def test_tech_pulse():
    """Test tech pulse (cutting-edge tech intelligence)"""
    print("\n" + "="*60)
    print("TESTING TECH PULSE (CUTTING EDGE)")
    print("="*60)

    tech = TechPulse()
    print(f"Tech pulse available: {tech.is_available()}")

    # Test tech domain detection
    test_queries = [
        "What's new in AI and machine learning?",
        "Latest cybersecurity tools",
        "Trending GitHub repositories",
        "What's the weather?",  # Should NOT be tech
    ]

    print("\n--- Tech Domain Detection ---")
    for query in test_queries:
        is_tech = tech.is_tech_query(query)
        domains = tech.detect_tech_domain(query)
        print(f"'{query[:40]}...'")
        print(f"  Is tech: {is_tech}, Domains: {domains}")

    # Test GitHub trending
    print("\n--- GitHub Trending Repositories ---")
    trending = tech.get_github_trending()
    if trending:
        print(tech.format_trending_repos(trending[:5]))
    else:
        print("Failed to fetch (rate limited?)")

    # Test Hacker News
    print("\n--- Hacker News Top Stories ---")
    hn = tech.get_hacker_news_top(5)
    if hn:
        print(tech.format_hn_stories(hn))
    else:
        print("Failed to fetch")

    # Test security tools updates
    print("\n--- Security Tool Updates ---")
    sec_tools = tech.get_security_tools_updates()
    if sec_tools:
        for tool in sec_tools[:5]:
            print(f"  • {tool['tool']} {tool['version']} ({tool['published']})")
    else:
        print("Failed to fetch (rate limited?)")

    # Test AI developments
    print("\n--- AI Developments ---")
    ai_dev = tech.get_ai_developments()
    if ai_dev['trending_repos']:
        print("AI/ML Trending:")
        for repo in ai_dev['trending_repos'][:3]:
            print(f"  - {repo['name']} ({repo['stars']} stars)")
    if ai_dev['news']:
        print("AI News:")
        for story in ai_dev['news'][:3]:
            print(f"  • {story['title'][:60]}...")


def test_knowledge_detector():
    """Test the knowledge detector"""
    print("\n" + "="*60)
    print("TESTING KNOWLEDGE DETECTOR")
    print("="*60)

    detector = KnowledgeDetector()

    # Test queries that should trigger pre-lookup
    pre_lookup_queries = [
        "What's the current price of Tesla?",
        "Latest news about AI",
        "What's Bitcoin trading at right now?",
        "Today's weather in New York",
    ]

    print("\n--- Pre-lookup detection ---")
    for query in pre_lookup_queries:
        needs = detector.needs_lookup_before(query)
        print(f"Query: {query}")
        print(f"  Needs pre-lookup: {needs}\n")

    # Test responses that indicate uncertainty
    uncertain_responses = [
        "I don't have access to real-time data.",
        "As of my knowledge cutoff in January 2024...",
        "I'm not sure about current prices.",
        "I cannot provide live stock quotes.",
    ]

    confident_responses = [
        "The capital of France is Paris.",
        "Python is a programming language.",
        "Here is how to write a function...",
    ]

    print("\n--- Post-response detection ---")
    print("Uncertain responses:")
    for response in uncertain_responses:
        needs = detector.needs_lookup_after(response)
        print(f"  '{response[:50]}...' -> needs lookup: {needs}")

    print("\nConfident responses:")
    for response in confident_responses:
        needs = detector.needs_lookup_after(response)
        print(f"  '{response[:50]}...' -> needs lookup: {needs}")


def test_full_integration():
    """Test full integration with MultiModelOrchestrator"""
    print("\n" + "="*60)
    print("TESTING FULL INTEGRATION")
    print("="*60)

    try:
        from ai.multimodel import MultiModelOrchestrator
        from core.privacy_controller import PrivacyController

        privacy = PrivacyController(auto_confirm=True)
        ai = MultiModelOrchestrator(privacy_controller=privacy, auto_lookup=True)

        status = ai.get_status()
        print("\nOrchestrator Status:")
        print(f"  Auto-lookup enabled: {status['auto_lookup']['enabled']}")
        print(f"  Stock lookup available: {status['auto_lookup']['stock_available']}")
        print(f"  Web lookup available: {status['auto_lookup']['web_available']}")

        # Test a stock query (if Ollama is running)
        if status['ollama']['available']:
            print("\n--- Testing stock query through ALFRED ---")
            response = ai.generate("What's Apple stock trading at?")
            if response:
                print(f"ALFRED: {response[:500]}...")
            else:
                print("No response generated")

            print(f"\nAuto-lookup stats: {status['auto_lookup']}")
        else:
            print("\nOllama not available - skipping full integration test")
            print("Start Ollama with: ollama serve")

    except Exception as e:
        print(f"Integration test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("="*70)
    print("  ALFRED_J_RITA INTELLIGENCE SUITE TEST")
    print("  State of the Art - Edge of Tomorrow")
    print("="*70)
    print("\nTesting: Stocks | Weather | News | Cyber Intel | Tech Pulse | Web")
    print("="*70)

    test_stock_lookup()
    test_weather_lookup()
    test_news_lookup()
    test_business_intel()
    test_cybersecurity_intel()
    test_tech_pulse()
    test_web_lookup()
    test_knowledge_detector()
    test_full_integration()

    print("\n" + "="*70)
    print("  ALL TESTS COMPLETE - ALFRED INTELLIGENCE SUITE OPERATIONAL")
    print("="*70)
    print("""
┌─────────────────────────────────────────────────────────────────────┐
│  ALFRED_J_RITA INTELLIGENCE CAPABILITIES                            │
├─────────────────────────────────────────────────────────────────────┤
│  FINANCIAL                                                          │
│    • Stocks: Real-time prices via Polygon.io                        │
│    • Business Intel: Market sentiment via Alpha Vantage             │
│    • News: Financial headlines & analysis                           │
├─────────────────────────────────────────────────────────────────────┤
│  ENVIRONMENT (MECA)                                                 │
│    • Weather: Current conditions + 5-day forecast                   │
│    • MECA-ready structured data output                              │
├─────────────────────────────────────────────────────────────────────┤
│  CYBERSECURITY                                                      │
│    • CVE Intelligence: Real-time from NVD                           │
│    • CISA KEV: Known exploited vulnerabilities                      │
│    • Threat Landscape: Critical vulns & active exploits             │
│    • Product Vulnerability Search                                   │
├─────────────────────────────────────────────────────────────────────┤
│  TECH PULSE (CUTTING EDGE)                                          │
│    • GitHub Trending: Hot repositories                              │
│    • Hacker News: Tech community pulse                              │
│    • AI Developments: Latest ML/AI news                             │
│    • Security Tools: Pentest tool updates                           │
├─────────────────────────────────────────────────────────────────────┤
│  GENERAL KNOWLEDGE                                                  │
│    • Web Search: DuckDuckGo fallback                                │
│    • Auto-retry on uncertainty                                      │
└─────────────────────────────────────────────────────────────────────┘

Example queries ALFRED_J_RITA now handles:

  FINANCIAL:
    "What's Tesla trading at?"
    "Latest business news"
    "Market sentiment for NVDA"

  WEATHER (MECA):
    "Weather in New York"
    "Will it rain tomorrow?"

  CYBERSECURITY:
    "Tell me about CVE-2024-3400"
    "Latest critical vulnerabilities"
    "What threats are actively exploited?"
    "Any new Chrome zero-days?"

  TECH PULSE:
    "What's trending on GitHub?"
    "Latest AI developments"
    "New security tools released"
    "What's hot on Hacker News?"
""")
    print("="*70)
