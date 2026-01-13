"""
Lightweight AI Client for Cloud Deployment
Uses cloud APIs only (no local Ollama, no voice dependencies)

Author: Daniel J Rita (BATDAN)
"""

import os
import logging
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)

# Try to import AI providers
ANTHROPIC_AVAILABLE = False
OPENAI_AVAILABLE = False
GROQ_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    pass

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    pass

try:
    import groq
    GROQ_AVAILABLE = True
except ImportError:
    pass


class CloudAI:
    """Lightweight AI client for cloud deployment"""

    def __init__(self):
        self.provider = None
        self.client = None

        # Try Anthropic first
        if ANTHROPIC_AVAILABLE and os.getenv("ANTHROPIC_API_KEY"):
            self.provider = "anthropic"
            self.client = anthropic.Anthropic()
            logger.info("CloudAI: Using Anthropic Claude")
        # Then OpenAI
        elif OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
            self.provider = "openai"
            self.client = openai.OpenAI()
            logger.info("CloudAI: Using OpenAI")
        # Then Groq
        elif GROQ_AVAILABLE and os.getenv("GROQ_API_KEY"):
            self.provider = "groq"
            self.client = groq.Groq()
            logger.info("CloudAI: Using Groq")
        else:
            logger.warning("CloudAI: No AI provider configured!")

    def generate(
        self,
        prompt: str,
        context: Optional[List[Dict]] = None,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> Optional[str]:
        """Generate AI response"""

        if not self.client:
            return "AI not configured. Please set ANTHROPIC_API_KEY, OPENAI_API_KEY, or GROQ_API_KEY."

        # Build messages
        messages = []

        if context:
            for msg in context:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if role == "system" and self.provider == "anthropic":
                    system = content  # Anthropic uses separate system param
                else:
                    messages.append({"role": role, "content": content})

        # Add current prompt
        messages.append({"role": "user", "content": prompt})

        try:
            if self.provider == "anthropic":
                response = self.client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=max_tokens,
                    system=system or "You are a helpful AI assistant.",
                    messages=messages
                )
                return response.content[0].text

            elif self.provider == "openai":
                if system:
                    messages.insert(0, {"role": "system", "content": system})
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    max_tokens=max_tokens,
                    temperature=temperature,
                    messages=messages
                )
                return response.choices[0].message.content

            elif self.provider == "groq":
                if system:
                    messages.insert(0, {"role": "system", "content": system})
                response = self.client.chat.completions.create(
                    model="llama-3.1-70b-versatile",
                    max_tokens=max_tokens,
                    temperature=temperature,
                    messages=messages
                )
                return response.choices[0].message.content

        except Exception as e:
            logger.error(f"CloudAI generation error: {e}")
            return f"AI error: {str(e)}"

        return None


# Singleton instance
_cloud_ai = None

def get_cloud_ai() -> CloudAI:
    """Get or create CloudAI singleton"""
    global _cloud_ai
    if _cloud_ai is None:
        _cloud_ai = CloudAI()
    return _cloud_ai
