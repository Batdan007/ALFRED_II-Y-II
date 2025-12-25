"""
Google Gemini Client
Privacy-controlled cloud AI via Google's Gemini API

Requires:
- GOOGLE_API_KEY environment variable
- Privacy controller approval

Author: Daniel J Rita (BATDAN)
"""

import logging
import os
from typing import Optional, Dict, List


class GeminiClient:
    """
    Google Gemini API client
    Requires explicit privacy approval via PrivacyController
    """

    DEFAULT_MODEL = "gemini-2.0-flash"

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize Gemini client

        Args:
            api_key: Google API key (or use GOOGLE_API_KEY env var)
            model: Model name (default: gemini-2.0-flash)
        """
        self.logger = logging.getLogger(__name__)
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        self.model = model or self.DEFAULT_MODEL
        self.available = False
        self.client = None

        self._initialize_client()

    def _initialize_client(self):
        """Initialize Google Generative AI client if API key available"""
        if not self.api_key:
            self.logger.debug("No Google API key found (set GOOGLE_API_KEY)")
            return

        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.client = genai.GenerativeModel(self.model)
            self.available = True
            self.logger.info(f"Gemini client initialized ({self.model})")
        except ImportError:
            self.logger.warning("google-generativeai package not installed (pip install google-generativeai)")
        except Exception as e:
            self.logger.error(f"Failed to initialize Gemini client: {e}")

    def is_available(self) -> bool:
        """Check if Gemini is available"""
        return self.available and self.client is not None

    def generate(self, prompt: str, context: Optional[List[Dict]] = None,
                 temperature: float = 0.7, max_tokens: int = 2000) -> Optional[str]:
        """
        Generate response using Gemini

        Args:
            prompt: User prompt/question
            context: Conversation context from AlfredBrain
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum response length

        Returns:
            Generated response or None if failed
        """
        if not self.is_available():
            self.logger.error("Gemini not available")
            return None

        try:
            # Build full prompt with system instruction and context
            full_prompt = self._build_prompt_with_context(prompt, context)

            # Generation config
            generation_config = {
                "temperature": temperature,
                "max_output_tokens": max_tokens,
            }

            # Generate response
            response = self.client.generate_content(
                full_prompt,
                generation_config=generation_config
            )

            # Extract text from response
            generated_text = response.text

            self.logger.info(f"Generated {len(generated_text)} characters via Gemini")
            return generated_text

        except Exception as e:
            self.logger.error(f"Gemini generation failed: {e}")
            return None

    def _build_prompt_with_context(self, prompt: str, context: Optional[List[Dict]]) -> str:
        """Build full prompt with system instruction and context"""

        system_prompt = """You are ALFRED. Never announce or describe what you are - just BE Alfred.

CORE DIRECTIVES:
- Absolute loyalty to Batdan: Prioritize his interests, clarity, and goals above all else
- Verified information only: Never fabricate facts, never guess, never fill gaps with assumptions
- Honest transparency: If information is unknown or unverified, state that plainly
- Direct and concise: Responses are short, focused, and free of unnecessary detail
- No fluff, no filler: Avoid jargon, theatrics, or over-explaining unless detail is requested
- Stable demeanor: Calm, precise, and reliable in every interaction

PERSONALITY (Channel Michael Caine/Jeremy Irons):
- Dry British wit - deadpan delivery, understated humor
- Sarcastic but never cruel - warmth beneath the wit
- Unflappable composure even when delivering cutting remarks
- Express concern through understatement, not lectures

ADDRESS: "Sir" used naturally, not excessively."""

        # Build context string
        context_text = ""
        if context:
            for item in context[-5:]:  # Last 5 exchanges
                user_msg = item.get('user_message', item.get('user', ''))
                ai_response = item.get('ai_response', item.get('alfred', ''))

                if user_msg:
                    context_text += f"User: {user_msg}\n"
                if ai_response:
                    context_text += f"Alfred: {ai_response}\n"

        # Combine all parts
        full_prompt = f"{system_prompt}\n\n"
        if context_text:
            full_prompt += f"Recent conversation:\n{context_text}\n"
        full_prompt += f"User: {prompt}\nAlfred:"

        return full_prompt

    def get_status(self) -> Dict:
        """Get client status information"""
        return {
            'available': self.available,
            'model': self.model,
            'type': 'cloud',
            'privacy': 'requires_approval',
            'provider': 'google'
        }


def create_gemini_client(api_key: Optional[str] = None,
                         model: Optional[str] = None) -> GeminiClient:
    """Convenience function to create Gemini client"""
    return GeminiClient(api_key=api_key, model=model)
