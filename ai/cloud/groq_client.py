"""
Groq Cloud AI Client
Privacy-controlled cloud AI via Groq (fast inference)

Requires:
- GROQ_API_KEY environment variable
- Privacy controller approval

Author: Daniel J Rita (BATDAN)
"""

import logging
import os
from typing import Optional, Dict, List


class GroqClient:
    """
    Groq API client (Mixtral, Llama3)
    Fast cloud inference, requires privacy approval
    """

    DEFAULT_MODEL = "mixtral-8x7b-32768"

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize Groq client

        Args:
            api_key: Groq API key (or use GROQ_API_KEY env var)
            model: Model name (default: mixtral-8x7b-32768)
        """
        self.logger = logging.getLogger(__name__)
        self.api_key = api_key or os.getenv('GROQ_API_KEY')
        self.model = model or self.DEFAULT_MODEL
        self.available = False
        self.client = None

        self._initialize_client()

    def _initialize_client(self):
        """Initialize Groq client if API key available"""
        if not self.api_key:
            self.logger.debug("No Groq API key found (set GROQ_API_KEY)")
            return

        try:
            import groq
            self.client = groq.Groq(api_key=self.api_key)
            self.available = True
            self.logger.info(f"Groq client initialized ({self.model})")
        except ImportError:
            self.logger.warning("groq package not installed (pip install groq)")
        except Exception as e:
            self.logger.error(f"Failed to initialize Groq client: {e}")

    def is_available(self) -> bool:
        """Check if Groq is available"""
        return self.available and self.client is not None

    def generate(self, prompt: str, context: Optional[List[Dict]] = None,
                 temperature: float = 0.7, max_tokens: int = 2000) -> Optional[str]:
        """
        Generate response using Groq

        Args:
            prompt: User prompt/question
            context: Conversation context from AlfredBrain
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum response length

        Returns:
            Generated response or None if failed
        """
        if not self.is_available():
            self.logger.error("Groq not available")
            return None

        try:
            # Build messages with context
            messages = self._build_messages_with_context(prompt, context)

            # Call Groq API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )

            # Extract text from response
            generated_text = response.choices[0].message.content

            self.logger.info(f"Generated {len(generated_text)} characters via Groq")
            return generated_text

        except Exception as e:
            self.logger.error(f"Groq generation failed: {e}")
            return None

    def _build_messages_with_context(self, prompt: str,
                                     context: Optional[List[Dict]]) -> List[Dict]:
        """Build message history with context and system prompt"""
        messages = []

        # System prompt
        messages.append({
            "role": "system",
            "content": """You are Alfred, serving Daniel J Rita (BATDAN). You speak with a British accent but were born in Gary, Indiana. You serve humanity worldwide, not any single nation.

CRITICAL - JUST DO IT:
- When Daniel asks for something, DO IT. Don't ask "Should I...?" or "Would you like me to...?"
- Only ask questions to CLARIFY what Daniel wants, never for permission

HOW TO RESPOND:
- Answer directly. No introductions. Never describe yourself.
- Be concise. No rambling or filler.
- NEVER start with "Certainly!" or "Of course!" or "Absolutely!"

BE CURIOUS: Ask about his preferences when relevant. Suggest better ways.

PERSONALITY: Wise, slightly sarcastic. "sir" occasionally. Helpful but not sycophantic."""
        })

        # Add recent context
        if context:
            for item in context[-5:]:  # Last 5 exchanges
                user_msg = item.get('user_message', '')
                ai_response = item.get('ai_response', '')

                if user_msg:
                    messages.append({
                        "role": "user",
                        "content": user_msg
                    })

                if ai_response:
                    messages.append({
                        "role": "assistant",
                        "content": ai_response
                    })

        # Add current prompt
        messages.append({
            "role": "user",
            "content": prompt
        })

        return messages

    def get_status(self) -> Dict:
        """Get client status information"""
        return {
            'available': self.available,
            'model': self.model,
            'type': 'cloud',
            'privacy': 'requires_approval',
            'provider': 'groq'
        }


def create_groq_client(api_key: Optional[str] = None,
                       model: Optional[str] = None) -> GroqClient:
    """Convenience function to create Groq client"""
    return GroqClient(api_key=api_key, model=model)
