"""
Cloud AI Models (Privacy-Controlled)
Requires explicit user consent via PrivacyController

Author: Daniel J Rita (BATDAN)
"""

from .claude_client import ClaudeClient
from .openai_client import OpenAIClient
from .groq_client import GroqClient
from .gemini_client import GeminiClient

__all__ = ['ClaudeClient', 'OpenAIClient', 'GroqClient', 'GeminiClient']
