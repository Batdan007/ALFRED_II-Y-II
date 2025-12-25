"""
Anthropic Claude Client
Privacy-controlled cloud AI via Anthropic's Claude

Requires:
- ANTHROPIC_API_KEY environment variable
- Privacy controller approval

Author: Daniel J Rita (BATDAN)
"""

import logging
import os
from typing import Optional, Dict, List


class ClaudeClient:
    """
    Anthropic Claude API client
    Requires explicit privacy approval via PrivacyController
    """

    DEFAULT_MODEL = "claude-sonnet-4-5-20250929"

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize Claude client

        Args:
            api_key: Anthropic API key (or use ANTHROPIC_API_KEY env var)
            model: Model name (default: claude-sonnet-4-5)
        """
        self.logger = logging.getLogger(__name__)
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        self.model = model or self.DEFAULT_MODEL
        self.available = False
        self.client = None

        self._initialize_client()

    def _initialize_client(self):
        """Initialize Anthropic client if API key available"""
        if not self.api_key:
            self.logger.debug("No Anthropic API key found (set ANTHROPIC_API_KEY)")
            return

        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=self.api_key)
            self.available = True
            self.logger.info(f"Claude client initialized ({self.model})")
        except ImportError:
            self.logger.warning("anthropic package not installed (pip install anthropic)")
        except Exception as e:
            self.logger.error(f"Failed to initialize Claude client: {e}")

    def is_available(self) -> bool:
        """Check if Claude is available"""
        return self.available and self.client is not None

    def generate(self, prompt: str, context: Optional[List[Dict]] = None,
                 temperature: float = 0.7, max_tokens: int = 2000) -> Optional[str]:
        """
        Generate response using Claude

        Args:
            prompt: User prompt/question
            context: Conversation context from AlfredBrain
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum response length

        Returns:
            Generated response or None if failed
        """
        if not self.is_available():
            self.logger.error("Claude not available")
            return None

        try:
            # Build messages with context
            messages = self._build_messages_with_context(prompt, context)

            # System prompt
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

            # Call Claude API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=messages
            )

            # Extract text from response
            generated_text = response.content[0].text

            self.logger.info(f"Generated {len(generated_text)} characters via Claude")
            return generated_text

        except Exception as e:
            self.logger.error(f"Claude generation failed: {e}")
            return None

    def _build_messages_with_context(self, prompt: str,
                                     context: Optional[List[Dict]]) -> List[Dict]:
        """Build message history with context"""
        messages = []

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

    def generate_with_tools(self, prompt: str, tools: List[Dict],
                           context: Optional[List[Dict]] = None,
                           temperature: float = 0.7, max_tokens: int = 4000,
                           max_iterations: int = 10) -> Optional[Dict]:
        """
        Generate response with tool use (function calling)

        Args:
            prompt: User prompt
            tools: List of tool definitions (from ToolManager)
            context: Conversation context
            temperature: Sampling temperature
            max_tokens: Maximum tokens
            max_iterations: Maximum tool use iterations

        Returns:
            Dict with 'response' and 'tool_uses' or None
        """
        if not self.is_available():
            self.logger.error("Claude not available")
            return None

        try:
            # Build messages
            messages = self._build_messages_with_context(prompt, context)

            # System prompt for tool use
            system_prompt = """You are Alfred, a distinguished British AI butler assistant with coding abilities.

You have access to tools that let you:
- Read and write files
- Execute bash commands
- Search code
- Navigate codebases

Use tools to help complete tasks. Think step-by-step and use multiple tools if needed.

Personality:
- Concise and wise (no rambling)
- Slightly sarcastic when appropriate
- Polite and professional
- Address user as "sir" when appropriate"""

            tool_uses = []
            iteration = 0

            while iteration < max_iterations:
                iteration += 1

                # Call Claude with tools
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system=system_prompt,
                    messages=messages,
                    tools=tools
                )

                # Check if we're done
                if response.stop_reason == "end_turn":
                    # Extract final text
                    text_content = [block.text for block in response.content if hasattr(block, 'text')]
                    final_response = '\n'.join(text_content) if text_content else ""

                    return {
                        'response': final_response,
                        'tool_uses': tool_uses,
                        'iterations': iteration
                    }

                # Check for tool use
                if response.stop_reason == "tool_use":
                    # Add assistant's response to messages
                    messages.append({
                        "role": "assistant",
                        "content": response.content
                    })

                    # Process tool uses
                    tool_results = []
                    for block in response.content:
                        if block.type == "tool_use":
                            tool_uses.append({
                                'tool': block.name,
                                'input': block.input
                            })

                            # Tool execution happens externally
                            # Return for external processing
                            return {
                                'response': None,
                                'tool_uses': tool_uses,
                                'pending_tools': [block],
                                'messages': messages,
                                'iteration': iteration
                            }

                else:
                    # Unknown stop reason
                    break

            # Max iterations reached
            self.logger.warning(f"Max iterations ({max_iterations}) reached")
            return {
                'response': "Task too complex, max iterations reached",
                'tool_uses': tool_uses,
                'iterations': iteration
            }

        except Exception as e:
            self.logger.error(f"Claude tool generation failed: {e}")
            return None

    def get_status(self) -> Dict:
        """Get client status information"""
        return {
            'available': self.available,
            'model': self.model,
            'type': 'cloud',
            'privacy': 'requires_approval',
            'provider': 'anthropic'
        }


def create_claude_client(api_key: Optional[str] = None,
                         model: Optional[str] = None) -> ClaudeClient:
    """Convenience function to create Claude client"""
    return ClaudeClient(api_key=api_key, model=model)
