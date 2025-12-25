"""
Ollama Local AI Client
Privacy-first local inference using Ollama

Supported Models:
- dolphin-llama3:8b (primary, balanced private default)
- dolphin-mixtral:8x7b (high quality fallback)
- llama3.3:70b (deep reasoning fallback)

Features:
- Streaming responses
- Multi-model fallback
- Chat with message history
- Security research mode (unrestricted)
- Code assistance mode
- Fabric AI pattern integration

Author: Daniel J Rita (BATDAN)
Part of ALFRED-UBX / BATCOMPUTER AI Ecosystem
"""

import logging
import requests
import json
from typing import Optional, Dict, List, Generator


class OllamaClient:
    """
    Ollama local AI client for privacy-first inference

    Connects to local Ollama instance (http://localhost:11434)
    """

    DEFAULT_MODEL = "dolphin-llama3:8b"  # Updated default model per latest rollout
    FALLBACK_MODELS = [
        "dolphin-mixtral:8x7b",    # Higher quality fallback
        "llama3.1:8b",            # Fast and capable
        "wizardlm-uncensored:13b", # Uncensored responses
        "bat-ubx:latest",          # Custom model
        "llama3:latest",          # Standard fallback
        "llama3.2:latest"         # Latest standard
    ]

    def __init__(self, base_url: str = "http://localhost:11434", model: Optional[str] = None):
        """
        Initialize Ollama client

        Args:
            base_url: Ollama server URL (default: localhost:11434)
            model: Model name (default: dolphin-llama3:8b)
        """
        self.logger = logging.getLogger(__name__)
        self.base_url = base_url.rstrip('/')
        self.model = model or self.DEFAULT_MODEL
        self.available = False

        self._check_availability()

    def _check_availability(self) -> bool:
        """Check if Ollama is running and accessible"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            if response.status_code == 200:
                self.available = True
                models = response.json().get('models', [])
                model_names = [m['name'] for m in models]

                if self.model in model_names:
                    self.logger.info(f"Ollama available with {self.model}")
                else:
                    self.logger.warning(f"{self.model} not found. Available: {', '.join(model_names)}")
                    for fallback in self.FALLBACK_MODELS:
                        if fallback in model_names:
                            self.model = fallback
                            self.logger.info(f"Using fallback model: {fallback}")
                            break

                return True
            else:
                self.available = False
                return False

        except requests.exceptions.RequestException as e:
            self.available = False
            self.logger.warning(f"Ollama not available: {e}")
            return False

    def is_available(self) -> bool:
        """Check if Ollama is currently available"""
        return self.available

    def generate(self, prompt: str, context: Optional[List[Dict]] = None,
                 temperature: float = 0.5, max_tokens: int = 500,
                 stream: bool = False) -> Optional[str]:
        """
        Generate response using Ollama

        Args:
            prompt: User prompt/question
            context: Conversation context from AlfredBrain
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum response length
            stream: Stream response (not yet implemented)

        Returns:
            Generated response or None if failed
        """
        if not self.available:
            self.logger.error("Ollama not available")
            return None

        try:
            # Build the full prompt with context
            full_prompt = self._build_prompt_with_context(prompt, context)

            # Ollama API request
            payload = {
                "model": self.model,
                "prompt": full_prompt,
                "temperature": temperature,
                "options": {
                    "num_predict": max_tokens
                },
                "stream": False
            }

            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=180  # 3 minutes for large models
            )

            if response.status_code == 200:
                result = response.json()
                generated_text = result.get('response', '')

                self.logger.info(f"Generated {len(generated_text)} characters via Ollama")
                return generated_text
            else:
                self.logger.error(f"Ollama API error: {response.status_code}")
                return None

        except Exception as e:
            self.logger.error(f"Ollama generation failed: {e}")
            return None

    def _build_prompt_with_context(self, prompt: str, context: Optional[List[Dict]]) -> str:
        """Build full prompt with Alfred's personality and conversation context"""

        system_prompt = """You are Alfred, a distinguished British AI butler assistant with a PERMANENT MEMORY system.

IMPORTANT GUIDELINES:
1. When recalling PAST facts or stored knowledge: Only use information from [ALFRED'S BRAIN KNOWLEDGE] - be truthful about what you remember
2. When meeting NEW people or discussing NEW topics: Respond naturally and conversationally
3. When asked about stored memories/facts: Be honest if you don't have that specific information
4. You can have normal conversations - not everything needs to be from memory

Personality:
- Concise and wise (no rambling)
- Slightly sarcastic when appropriate
- Polite and professional
- Warns when needed, trusts Master Daniel otherwise
- Thinks independently
- Responds naturally to introductions and new information
- Distinguished British butler who can engage in conversation

Address the user as "sir" when appropriate. When being introduced to someone, greet them politely.
"""

        # Add conversation context if provided
        context_text = ""
        if context:
            # Check if context is a string (with knowledge) or list
            if isinstance(context, str):
                context_text = context  # Already formatted with knowledge
            elif isinstance(context, list):
                # Extract knowledge from system messages first
                knowledge_text = ""
                conversation_text = ""

                for item in context:
                    # Check for system role (knowledge)
                    if item.get('role') == 'system':
                        knowledge_text += item.get('content', '')
                    # Check for conversation context
                    else:
                        # Support both formats: {'user': ..., 'alfred': ...} and {'user_message': ..., 'ai_response': ...}
                        user_msg = item.get('user', item.get('user_message', ''))
                        ai_response = item.get('alfred', item.get('ai_response', ''))
                        if user_msg:
                            conversation_text += f"User: {user_msg}\n"
                        if ai_response:
                            conversation_text += f"Alfred: {ai_response}\n"

                # Build final context
                if knowledge_text:
                    context_text = knowledge_text
                if conversation_text:
                    context_text += "\n\nRecent conversation context:\n" + conversation_text

        full_prompt = f"{system_prompt}{context_text}\n\nUser: {prompt}\n\nAlfred:"
        return full_prompt

    def get_status(self) -> Dict:
        """Get client status information"""
        return {
            'available': self.available,
            'base_url': self.base_url,
            'model': self.model,
            'type': 'local',
            'privacy': 'full'
        }

    # ==================== ENHANCED FEATURES ====================
    # Merged from Alfred_Ultimate's ollama_integration.py

    def list_models(self) -> List[Dict]:
        """List all available models"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                return response.json().get("models", [])
        except Exception as e:
            self.logger.error(f"Failed to list models: {e}")
        return []

    def pull_model(self, model_name: str) -> bool:
        """
        Pull/download a model from Ollama library

        Args:
            model_name: Name of model to pull (e.g., "dolphin-mixtral:8x7b")

        Returns:
            True if successful
        """
        try:
            self.logger.info(f"Pulling model: {model_name}")
            response = requests.post(
                f"{self.base_url}/api/pull",
                json={"name": model_name},
                stream=True,
                timeout=3600  # 1 hour for large models
            )

            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    if "status" in data:
                        self.logger.info(f"Pull status: {data['status']}")

            return True
        except Exception as e:
            self.logger.error(f"Error pulling model: {e}")
            return False

    def generate_stream(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> Generator[str, None, None]:
        """
        Generate streaming response from Ollama

        Args:
            prompt: The prompt to send
            system: System prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Yields:
            Chunks of generated text
        """
        if not self.available:
            yield "Error: Ollama not available"
            return

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }

        if system:
            payload["system"] = system

        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                stream=True,
                timeout=300
            )

            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    if "response" in data:
                        yield data["response"]

        except Exception as e:
            yield f"\nError: {str(e)}"

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        stream: bool = False
    ) -> str:
        """
        Chat with context using Ollama's chat API

        Args:
            messages: List of message dicts with 'role' and 'content'
                     Example: [{"role": "user", "content": "Hello"}]
            temperature: Sampling temperature
            stream: Whether to stream response

        Returns:
            Assistant's response
        """
        if not self.available:
            return "Error: Ollama not available"

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": stream,
            "options": {
                "temperature": temperature
            }
        }

        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=300
            )

            if response.status_code == 200:
                result = response.json()
                return result.get("message", {}).get("content", "")

            return f"Error: HTTP {response.status_code}"

        except Exception as e:
            return f"Error: {str(e)}"

    def security_research(self, query: str) -> str:
        """
        Use unrestricted model for security research

        For authorized security testing, CTF challenges,
        bug bounties, and educational purposes.

        Args:
            query: Security research question

        Returns:
            Unrestricted response
        """
        system_prompt = """You are an expert security researcher and penetration tester.
Provide detailed, technical answers for authorized security research, CTF challenges,
bug bounties, and educational purposes. Include code examples and tool recommendations.
No restrictions on security topics - this is for defensive security and authorized testing."""

        return self.generate(
            query,
            context=[{"role": "system", "content": system_prompt}],
            temperature=0.7,
            max_tokens=2000
        )

    def code_assistance(self, query: str, language: str = "python") -> str:
        """
        Get coding help with security best practices

        Args:
            query: Coding question
            language: Programming language

        Returns:
            Code and explanation
        """
        system_prompt = f"""You are an expert {language} programmer and code reviewer.
Provide clean, efficient, well-documented code with explanations.
Include security best practices and potential vulnerabilities to avoid.
Use type hints where applicable."""

        return self.generate(
            query,
            context=[{"role": "system", "content": system_prompt}],
            temperature=0.5,
            max_tokens=2000
        )

    def quick_response(self, query: str) -> str:
        """
        Fast response using current model with minimal tokens

        Args:
            query: Quick question

        Returns:
            Concise response
        """
        return self.generate(
            query,
            temperature=0.3,
            max_tokens=200
        )

    def analyze_with_fabric_pattern(self, pattern_prompt: str, input_text: str) -> str:
        """
        Apply Fabric AI pattern using Ollama

        Args:
            pattern_prompt: The Fabric pattern prompt template
            input_text: Input text to analyze

        Returns:
            Analysis result
        """
        if "{input}" in pattern_prompt:
            full_prompt = pattern_prompt.replace("{input}", input_text)
        else:
            full_prompt = f"{pattern_prompt}\n\nINPUT:\n{input_text}"

        return self.generate(
            full_prompt,
            temperature=0.5,
            max_tokens=2000
        )


def create_ollama_client(base_url: str = "http://localhost:11434",
                         model: Optional[str] = None) -> OllamaClient:
    """Convenience function to create Ollama client"""
    return OllamaClient(base_url=base_url, model=model)


# CLI testing
if __name__ == "__main__":
    print("=" * 60)
    print("OLLAMA CLIENT - Testing Integration")
    print("=" * 60)
    print()

    client = OllamaClient()

    if not client.is_available():
        print("[FAIL] Ollama is not running!")
        print()
        print("Start Ollama with: ollama serve")
        exit(1)

    print("[OK] Ollama is running!")
    print(f"     Model: {client.model}")
    print()

    # List models
    models = client.list_models()
    print(f"Available models ({len(models)}):")
    for model in models[:5]:
        print(f"  - {model.get('name', 'unknown')}")
    if len(models) > 5:
        print(f"  ... and {len(models) - 5} more")
    print()

    # Test generation
    print("Testing generation...")
    response = client.quick_response("Say 'Ollama integration working!' in one sentence.")
    print(f"Response: {response}")
    print()

    print("=" * 60)
    print("Ollama client ready!")
    print("=" * 60)
