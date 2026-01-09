"""
Multi-Model AI Orchestrator
Cascading fallback across local and cloud AI providers

Fallback Chain: Ollama (local) → Claude → Groq → OpenAI

Features:
- Auto-lookup: Detects when ALFRED doesn't know something and fetches from web
- Stock prices: Real-time stock data via Polygon.io
- Web search: General knowledge lookup via DuckDuckGo

Author: Daniel J Rita (BATDAN)
"""

import logging
from typing import Optional, Dict, List
from enum import Enum

from .local.ollama_client import OllamaClient
from .cloud.claude_client import ClaudeClient
from .cloud.openai_client import OpenAIClient
from .cloud.groq_client import GroqClient
from .cloud.gemini_client import GeminiClient

# Knowledge lookup imports
try:
    from capabilities.knowledge.stock_lookup import StockLookup
    from capabilities.knowledge.web_lookup import WebLookup, KnowledgeDetector
    from capabilities.knowledge.weather_lookup import WeatherLookup
    from capabilities.knowledge.news_lookup import NewsLookup, BusinessIntelligence
    from capabilities.knowledge.cybersecurity_intel import CybersecurityIntel
    from capabilities.knowledge.tech_pulse import TechPulse
    from capabilities.knowledge.encyclopedia_lookup import EncyclopediaLookup
    KNOWLEDGE_AVAILABLE = True
except ImportError:
    KNOWLEDGE_AVAILABLE = False


class CloudProvider(Enum):
    """Cloud AI provider types"""
    CLAUDE = "claude"
    GEMINI = "gemini"
    OPENAI = "openai"
    GROQ = "groq"


class MultiModelOrchestrator:
    """
    Multi-model AI orchestrator with privacy-first cascading fallback

    Fallback Chain:
    1. Ollama (local) - Privacy-first, no internet
    2. Claude (cloud) - High quality, requires approval
    3. Gemini (cloud) - Google's Gemini, requires approval
    4. Groq (cloud) - Fast inference, requires approval
    5. OpenAI (cloud) - Reliable fallback, requires approval
    """

    def __init__(self, privacy_controller=None, auto_lookup: bool = True):
        """
        Initialize multi-model orchestrator

        Args:
            privacy_controller: PrivacyController instance for cloud approval
            auto_lookup: Enable automatic web/stock lookup when ALFRED doesn't know
        """
        self.logger = logging.getLogger(__name__)
        self.privacy_controller = privacy_controller
        self.auto_lookup_enabled = auto_lookup

        # Initialize all clients
        self.ollama = OllamaClient()
        self.claude = ClaudeClient()
        self.gemini = GeminiClient()
        self.openai = OpenAIClient()
        self.groq = GroqClient()

        # Initialize knowledge lookup (full intelligence suite)
        self.stock_lookup = None
        self.web_lookup = None
        self.weather_lookup = None
        self.news_lookup = None
        self.business_intel = None
        self.cyber_intel = None
        self.tech_pulse = None
        self.encyclopedia = None
        self.knowledge_detector = None

        if KNOWLEDGE_AVAILABLE and auto_lookup:
            self.stock_lookup = StockLookup()
            self.web_lookup = WebLookup()
            self.weather_lookup = WeatherLookup()
            self.news_lookup = NewsLookup()
            self.business_intel = BusinessIntelligence()
            self.cyber_intel = CybersecurityIntel()
            self.tech_pulse = TechPulse()
            self.encyclopedia = EncyclopediaLookup()
            self.knowledge_detector = KnowledgeDetector()
            self.logger.info("ALFRED Intelligence Suite: stocks, weather, news, cyber, tech, encyclopedia, web")

        # Track performance
        self.stats = {
            'ollama': {'requests': 0, 'successes': 0, 'failures': 0},
            'claude': {'requests': 0, 'successes': 0, 'failures': 0},
            'gemini': {'requests': 0, 'successes': 0, 'failures': 0},
            'openai': {'requests': 0, 'successes': 0, 'failures': 0},
            'groq': {'requests': 0, 'successes': 0, 'failures': 0},
            'auto_lookups': {
                'stock': 0, 'weather': 0, 'news': 0,
                'cyber': 0, 'tech': 0, 'encyclopedia': 0, 'web': 0, 'retries': 0
            }
        }

        self._log_availability()

    def _log_availability(self):
        """Log which AI backends are available"""
        available = []
        if self.ollama.is_available():
            available.append(f"Ollama ({self.ollama.model})")
        if self.claude.is_available():
            available.append(f"Claude ({self.claude.model})")
        if self.gemini.is_available():
            available.append(f"Gemini ({self.gemini.model})")
        if self.openai.is_available():
            available.append(f"OpenAI ({self.openai.model})")
        if self.groq.is_available():
            available.append(f"Groq ({self.groq.model})")

        if available:
            self.logger.info(f"AI backends available: {', '.join(available)}")
        else:
            self.logger.warning("No AI backends available")

    def generate(self, prompt: str, context: Optional[List[Dict]] = None,
                 temperature: float = 0.7, max_tokens: int = 2000,
                 force_cloud: bool = False, consensus: bool = True) -> Optional[str]:
        """
        Generate AI response using multi-model CONSENSUS (not fallback)

        TRUTH DERIVATION: Query ALL available models, compare responses,
        find consistencies, analyze nuances, synthesize truth.

        Args:
            prompt: User prompt/question
            context: Conversation context from AlfredBrain
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum response length
            force_cloud: Skip local and force cloud AI
            consensus: Use multi-model consensus (default True)

        Returns:
            Synthesized truthful response based on model consensus
        """
        if context is None:
            context = []

        # PHASE 1: Pre-lookup for real-time data
        knowledge_context = ""
        if self.auto_lookup_enabled and self.knowledge_detector:
            knowledge_context = self._pre_lookup(prompt)

        augmented_context = context.copy() if context else []
        if knowledge_context:
            augmented_context.insert(0, {'role': 'system', 'content': knowledge_context})

        # PHASE 2: Multi-model consensus OR fallback
        if consensus:
            response = self._generate_with_consensus(prompt, augmented_context, temperature, max_tokens)
        else:
            response = self._generate_with_fallback(prompt, augmented_context, temperature, max_tokens, force_cloud)

        if not response:
            return None

        # PHASE 3: Check uncertainty
        if self.auto_lookup_enabled and self.knowledge_detector:
            if self.knowledge_detector.needs_lookup_after(response) and not knowledge_context:
                self.logger.info("ALFRED uncertain - triggering auto-lookup")
                response = self._retry_with_lookup(prompt, context, temperature, max_tokens, force_cloud)

        return response

    def _generate_with_consensus(self, prompt: str, context: Optional[List[Dict]],
                                  temperature: float, max_tokens: int) -> Optional[str]:
        """
        Query ALL available models, compare responses, derive truth.

        NEVER make things up. Find consistencies across narratives.
        """
        import concurrent.futures

        responses = {}
        available_models = []

        # Identify available models
        if self.ollama.is_available():
            available_models.append(('ollama', self.ollama))
        if self._can_use_cloud(CloudProvider.CLAUDE):
            available_models.append(('claude', self.claude))
        if self._can_use_cloud(CloudProvider.GEMINI):
            available_models.append(('gemini', self.gemini))
        if self._can_use_cloud(CloudProvider.GROQ):
            available_models.append(('groq', self.groq))
        if self._can_use_cloud(CloudProvider.OPENAI):
            available_models.append(('openai', self.openai))

        if not available_models:
            self.logger.error("No AI models available for consensus")
            return None

        # If only one model, just use it directly
        if len(available_models) == 1:
            name, client = available_models[0]
            self.stats[name]['requests'] += 1
            response = client.generate(prompt, context, temperature, max_tokens)
            if response:
                self.stats[name]['successes'] += 1
            return response

        self.logger.info(f"CONSENSUS MODE: Querying {len(available_models)} models...")

        # Query all models in parallel
        def query_model(name_client):
            name, client = name_client
            try:
                self.stats[name]['requests'] += 1
                response = client.generate(prompt, context, temperature, max_tokens)
                if response:
                    self.stats[name]['successes'] += 1
                    return (name, response)
                else:
                    self.stats[name]['failures'] += 1
                    return (name, None)
            except Exception as e:
                self.logger.error(f"{name} failed: {e}")
                self.stats[name]['failures'] += 1
                return (name, None)

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(query_model, available_models))

        # Collect successful responses
        for name, response in results:
            if response:
                responses[name] = response

        if not responses:
            self.logger.error("All models failed")
            return None

        if len(responses) == 1:
            # Only one succeeded
            return list(responses.values())[0]

        # SYNTHESIZE TRUTH from multiple responses
        return self._synthesize_consensus(prompt, responses)

    def _synthesize_consensus(self, original_prompt: str, responses: Dict[str, str]) -> str:
        """
        Analyze multiple model responses, find consistencies, derive truth.

        Logic:
        1. Find common claims across responses
        2. Note disagreements/nuances
        3. Weight by model reliability
        4. Synthesize truthful answer
        """
        self.logger.info(f"Synthesizing truth from {len(responses)} model responses")

        # Build synthesis prompt
        synthesis_prompt = f"""TASK: Derive truth from multiple AI responses.

ORIGINAL QUESTION: {original_prompt}

RESPONSES FROM DIFFERENT AI MODELS:
"""
        for model, response in responses.items():
            synthesis_prompt += f"\n--- {model.upper()} ---\n{response}\n"

        synthesis_prompt += """
--- END RESPONSES ---

INSTRUCTIONS:
1. Find CONSISTENCIES - facts that multiple models agree on
2. Note DISAGREEMENTS - where models differ
3. For disagreements: favor verifiable facts, distrust speculation
4. NEVER add information not present in any response
5. If all models are uncertain, say "insufficient data"
6. Be concise. State facts only.

SYNTHESIZED TRUTHFUL ANSWER:"""

        # Use the best available model to synthesize
        # Prefer Claude > Gemini > GPT > Groq > Ollama for synthesis
        synthesis_client = None
        if self._can_use_cloud(CloudProvider.CLAUDE):
            synthesis_client = self.claude
        elif self._can_use_cloud(CloudProvider.GEMINI):
            synthesis_client = self.gemini
        elif self._can_use_cloud(CloudProvider.OPENAI):
            synthesis_client = self.openai
        elif self._can_use_cloud(CloudProvider.GROQ):
            synthesis_client = self.groq
        elif self.ollama.is_available():
            synthesis_client = self.ollama

        if synthesis_client:
            synthesized = synthesis_client.generate(synthesis_prompt, temperature=0.3, max_tokens=1000)
            if synthesized:
                return synthesized

        # Fallback: return longest response (usually most detailed)
        return max(responses.values(), key=len)

    def _pre_lookup(self, prompt: str) -> str:
        """
        Check if query needs real-time data and fetch it

        ALFRED Intelligence Suite:
        - Stocks (Polygon.io)
        - Weather (OpenWeatherMap/MECA)
        - News (NewsAPI/Polygon)
        - Cybersecurity (NVD/CISA)
        - Tech Pulse (GitHub/HackerNews)
        - Web (DuckDuckGo fallback)

        Args:
            prompt: User prompt

        Returns:
            Knowledge context to inject, or empty string
        """
        knowledge_parts = []

        # Check for stock queries (highest priority for financial data)
        if self.stock_lookup and self.stock_lookup.is_available():
            is_stock, stock_context = self.stock_lookup.lookup_for_prompt(prompt)
            if is_stock and stock_context:
                self.stats['auto_lookups']['stock'] += 1
                self.logger.info("Pre-fetched stock data for query")
                knowledge_parts.append(stock_context)

        # Check for weather queries (MECA integration)
        if self.weather_lookup and self.weather_lookup.is_available():
            is_weather, weather_context = self.weather_lookup.lookup_for_prompt(prompt)
            if is_weather and weather_context:
                self.stats['auto_lookups']['weather'] += 1
                self.logger.info("Pre-fetched weather data for query")
                knowledge_parts.append(weather_context)

        # Check for cybersecurity queries (CVEs, threats, vulnerabilities)
        if self.cyber_intel and self.cyber_intel.is_available():
            is_cyber, cyber_context = self.cyber_intel.lookup_for_prompt(prompt)
            if is_cyber and cyber_context:
                self.stats['auto_lookups']['cyber'] += 1
                self.logger.info("Pre-fetched cybersecurity intelligence for query")
                knowledge_parts.append(cyber_context)

        # Check for tech queries (cutting-edge tech, AI, GitHub trending)
        if self.tech_pulse and self.tech_pulse.is_available():
            is_tech, tech_context = self.tech_pulse.lookup_for_prompt(prompt)
            if is_tech and tech_context:
                self.stats['auto_lookups']['tech'] += 1
                self.logger.info("Pre-fetched tech pulse data for query")
                knowledge_parts.append(tech_context)

        # Check for news queries (general + business)
        if self.news_lookup and self.news_lookup.is_available():
            is_news, news_context = self.news_lookup.lookup_for_prompt(prompt)
            if is_news and news_context:
                self.stats['auto_lookups']['news'] += 1
                self.logger.info("Pre-fetched news data for query")
                knowledge_parts.append(news_context)

        # Check for encyclopedia queries (Wikipedia)
        if self.encyclopedia and self.encyclopedia.is_available() and not knowledge_parts:
            is_knowledge, wiki_context = self.encyclopedia.lookup_for_prompt(prompt)
            if is_knowledge and wiki_context:
                self.stats['auto_lookups']['encyclopedia'] += 1
                self.logger.info("Pre-fetched encyclopedia data for query")
                knowledge_parts.append(wiki_context)

        # Check for other real-time queries (web search fallback)
        if self.knowledge_detector and self.knowledge_detector.needs_lookup_before(prompt):
            if self.web_lookup and not knowledge_parts:  # Don't double-lookup
                query = self.knowledge_detector.extract_lookup_query(prompt)
                found, web_context = self.web_lookup.lookup_for_prompt(query)
                if found and web_context:
                    self.stats['auto_lookups']['web'] += 1
                    self.logger.info("Pre-fetched web data for query")
                    knowledge_parts.append(web_context)

        return "\n".join(knowledge_parts)

    def _retry_with_lookup(self, prompt: str, context: Optional[List[Dict]],
                           temperature: float, max_tokens: int, force_cloud: bool) -> Optional[str]:
        """
        Retry generation after fetching knowledge

        Args:
            prompt: Original prompt
            context: Original context
            temperature: Temperature
            max_tokens: Max tokens
            force_cloud: Force cloud flag

        Returns:
            New response with knowledge, or original if lookup fails
        """
        self.stats['auto_lookups']['retries'] += 1

        # Try web lookup
        if self.web_lookup:
            query = self.knowledge_detector.extract_lookup_query(prompt)
            found, web_context = self.web_lookup.lookup_for_prompt(query)

            if found and web_context:
                self.logger.info("Retrying with web knowledge")
                augmented_context = context.copy() if context else []
                augmented_context.insert(0, {'role': 'system', 'content': web_context})

                return self._generate_with_fallback(prompt, augmented_context, temperature, max_tokens, force_cloud)

        return None

    def _generate_with_fallback(self, prompt: str, context: Optional[List[Dict]],
                                 temperature: float, max_tokens: int, force_cloud: bool) -> Optional[str]:
        """
        Core generation with cascading fallback (no auto-lookup logic)

        Args:
            prompt: User prompt
            context: Context with any knowledge already injected
            temperature: Temperature
            max_tokens: Max tokens
            force_cloud: Force cloud

        Returns:
            Generated response or None
        """
        # Try Ollama first (privacy-first, local)
        if not force_cloud and self.ollama.is_available():
            self.logger.info("Trying Ollama (local)...")
            self.stats['ollama']['requests'] += 1

            response = self.ollama.generate(prompt, context, temperature, max_tokens)
            if response:
                self.stats['ollama']['successes'] += 1
                return response
            else:
                self.stats['ollama']['failures'] += 1
                self.logger.warning("Ollama failed, trying cloud...")

        # Try Claude (high quality cloud)
        if self._can_use_cloud(CloudProvider.CLAUDE):
            self.logger.info("Trying Claude (cloud)...")
            self.stats['claude']['requests'] += 1

            response = self.claude.generate(prompt, context, temperature, max_tokens)
            if response:
                self.stats['claude']['successes'] += 1
                return response
            else:
                self.stats['claude']['failures'] += 1
                self.logger.warning("Claude failed, trying Gemini...")

        # Try Gemini (Google cloud)
        if self._can_use_cloud(CloudProvider.GEMINI):
            self.logger.info("Trying Gemini (cloud)...")
            self.stats['gemini']['requests'] += 1

            response = self.gemini.generate(prompt, context, temperature, max_tokens)
            if response:
                self.stats['gemini']['successes'] += 1
                return response
            else:
                self.stats['gemini']['failures'] += 1
                self.logger.warning("Gemini failed, trying Groq...")

        # Try Groq (fast cloud)
        if self._can_use_cloud(CloudProvider.GROQ):
            self.logger.info("Trying Groq (cloud)...")
            self.stats['groq']['requests'] += 1

            response = self.groq.generate(prompt, context, temperature, max_tokens)
            if response:
                self.stats['groq']['successes'] += 1
                return response
            else:
                self.stats['groq']['failures'] += 1
                self.logger.warning("Groq failed, trying OpenAI...")

        # Try OpenAI (reliable fallback)
        if self._can_use_cloud(CloudProvider.OPENAI):
            self.logger.info("Trying OpenAI (cloud)...")
            self.stats['openai']['requests'] += 1

            response = self.openai.generate(prompt, context, temperature, max_tokens)
            if response:
                self.stats['openai']['successes'] += 1
                return response
            else:
                self.stats['openai']['failures'] += 1

        # All failed
        self.logger.error("All AI backends failed")
        return None

    def _can_use_cloud(self, provider: CloudProvider) -> bool:
        """
        Check if cloud provider can be used

        Args:
            provider: Cloud provider to check

        Returns:
            True if provider is available and approved
        """
        # Check if client is available
        if provider == CloudProvider.CLAUDE and not self.claude.is_available():
            return False
        elif provider == CloudProvider.GEMINI and not self.gemini.is_available():
            return False
        elif provider == CloudProvider.OPENAI and not self.openai.is_available():
            return False
        elif provider == CloudProvider.GROQ and not self.groq.is_available():
            return False

        # Check privacy controller approval
        if self.privacy_controller:
            return self.privacy_controller.request_cloud_access(provider)

        # No privacy controller, allow if available
        return True

    def get_status(self) -> Dict:
        """Get comprehensive status of all AI backends and knowledge lookup"""
        status = {
            'ollama': {
                **self.ollama.get_status(),
                **self.stats['ollama']
            },
            'claude': {
                **self.claude.get_status(),
                **self.stats['claude']
            },
            'gemini': {
                **self.gemini.get_status(),
                **self.stats['gemini']
            },
            'openai': {
                **self.openai.get_status(),
                **self.stats['openai']
            },
            'groq': {
                **self.groq.get_status(),
                **self.stats['groq']
            },
            'auto_lookup': {
                'enabled': self.auto_lookup_enabled,
                'stock_available': self.stock_lookup.is_available() if self.stock_lookup else False,
                'weather_available': self.weather_lookup.is_available() if self.weather_lookup else False,
                'news_available': self.news_lookup.is_available() if self.news_lookup else False,
                'cyber_available': self.cyber_intel.is_available() if self.cyber_intel else False,
                'tech_available': self.tech_pulse.is_available() if self.tech_pulse else False,
                'encyclopedia_available': self.encyclopedia.is_available() if self.encyclopedia else False,
                'web_available': self.web_lookup.is_available() if self.web_lookup else False,
                **self.stats['auto_lookups']
            }
        }
        return status

    def get_performance_stats(self) -> Dict:
        """Get performance statistics"""
        return self.stats.copy()


def create_orchestrator(privacy_controller=None) -> MultiModelOrchestrator:
    """Convenience function to create orchestrator"""
    return MultiModelOrchestrator(privacy_controller=privacy_controller)
