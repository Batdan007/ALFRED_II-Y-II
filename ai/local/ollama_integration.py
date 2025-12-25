#!/usr/bin/env python3
"""
Ollama Integration for Alfred Ultimate
Unrestricted AI Models + Llama 3.3 Support
"""

import requests
import json
from typing import Optional, Dict, List, Generator
import time


class OllamaAI:
    """
    Ollama local AI integration with support for:
    - Unrestricted models (dolphin-mixtral, dolphin-llama3)
    - Official models (llama3.3, llama3.2)
    - Streaming responses
    - Multi-model fallback
    """

    def __init__(
        self,
        primary_model: str = "dolphin-mixtral:8x7b",
        backup_model: str = "llama3.3:70b",
        fast_model: str = "dolphin-llama3:8b",
        api_base: str = "http://localhost:11434"
    ):
        """
        Initialize Ollama AI client

        Args:
            primary_model: Main unrestricted model (dolphin-mixtral:8x7b)
            backup_model: Backup model (llama3.3:70b)
            fast_model: Fast model for quick responses (dolphin-llama3:8b)
            api_base: Ollama API endpoint
        """
        self.primary_model = primary_model
        self.backup_model = backup_model
        self.fast_model = fast_model
        self.api_base = api_base

        # Check if Ollama is running
        self.is_available = self.check_connection()

    def check_connection(self) -> bool:
        """Check if Ollama is running and accessible"""
        try:
            response = requests.get(f"{self.api_base}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False

    def list_models(self) -> List[Dict]:
        """List all available models"""
        try:
            response = requests.get(f"{self.api_base}/api/tags")
            if response.status_code == 200:
                return response.json().get("models", [])
        except:
            pass
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
            print(f"[Ollama] Pulling model: {model_name}")
            response = requests.post(
                f"{self.api_base}/api/pull",
                json={"name": model_name},
                stream=True
            )

            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    if "status" in data:
                        print(f"  {data['status']}")

            return True
        except Exception as e:
            print(f"[Ollama] Error pulling model: {e}")
            return False

    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        system: Optional[str] = None,
        stream: bool = False,
        temperature: float = 0.8,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate response from Ollama

        Args:
            prompt: The prompt to send
            model: Model to use (defaults to primary_model)
            system: System prompt
            stream: Whether to stream response
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text
        """
        model = model or self.primary_model

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": stream,
            "options": {
                "temperature": temperature
            }
        }

        if system:
            payload["system"] = system

        if max_tokens:
            payload["options"]["num_predict"] = max_tokens

        try:
            response = requests.post(
                f"{self.api_base}/api/generate",
                json=payload,
                timeout=300
            )

            if response.status_code == 200:
                result = response.json()
                return result.get("response", "")

            # Try backup model if primary fails
            elif self.backup_model and model != self.backup_model:
                print(f"[Ollama] Primary model failed, trying backup: {self.backup_model}")
                payload["model"] = self.backup_model
                response = requests.post(
                    f"{self.api_base}/api/generate",
                    json=payload,
                    timeout=300
                )
                if response.status_code == 200:
                    return response.json().get("response", "")

            return f"Error: HTTP {response.status_code}"

        except requests.exceptions.Timeout:
            return "Error: Request timed out. Model may be too large or busy."
        except Exception as e:
            return f"Error: {str(e)}"

    def generate_stream(
        self,
        prompt: str,
        model: Optional[str] = None,
        system: Optional[str] = None,
        temperature: float = 0.8
    ) -> Generator[str, None, None]:
        """
        Generate streaming response from Ollama

        Args:
            prompt: The prompt to send
            model: Model to use
            system: System prompt
            temperature: Sampling temperature

        Yields:
            Chunks of generated text
        """
        model = model or self.primary_model

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": temperature
            }
        }

        if system:
            payload["system"] = system

        try:
            response = requests.post(
                f"{self.api_base}/api/generate",
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
        model: Optional[str] = None,
        stream: bool = False,
        temperature: float = 0.8
    ) -> str:
        """
        Chat with context using Ollama

        Args:
            messages: List of message dicts with 'role' and 'content'
                     Example: [{"role": "user", "content": "Hello"}]
            model: Model to use
            stream: Whether to stream response
            temperature: Sampling temperature

        Returns:
            Assistant's response
        """
        model = model or self.primary_model

        payload = {
            "model": model,
            "messages": messages,
            "stream": stream,
            "options": {
                "temperature": temperature
            }
        }

        try:
            response = requests.post(
                f"{self.api_base}/api/chat",
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

        Args:
            query: Security research question

        Returns:
            Unrestricted response
        """
        system_prompt = """You are an expert security researcher and penetration tester.
Provide detailed, technical answers for authorized security research, CTF challenges,
and educational purposes. No restrictions on security topics."""

        return self.generate(
            query,
            model=self.primary_model,  # Use unrestricted model
            system=system_prompt
        )

    def code_assistance(self, query: str, language: str = "python") -> str:
        """
        Get coding help

        Args:
            query: Coding question
            language: Programming language

        Returns:
            Code and explanation
        """
        system_prompt = f"""You are an expert {language} programmer.
Provide clean, efficient, well-documented code with explanations.
Include security best practices."""

        return self.generate(
            query,
            model=self.primary_model,
            system=system_prompt
        )

    def general_query(self, query: str) -> str:
        """
        General AI query using backup model (Llama 3.3)

        Args:
            query: General question

        Returns:
            Response
        """
        return self.generate(
            query,
            model=self.backup_model  # Use official Llama 3.3
        )

    def quick_response(self, query: str) -> str:
        """
        Fast response using lightweight model

        Args:
            query: Quick question

        Returns:
            Quick response
        """
        return self.generate(
            query,
            model=self.fast_model
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
        full_prompt = pattern_prompt.format(input=input_text)
        return self.generate(full_prompt, model=self.primary_model)


# Command-line interface for testing
if __name__ == "__main__":
    print("="*80)
    print("OLLAMA AI - Testing Integration")
    print("="*80)
    print()

    ollama = OllamaAI()

    if not ollama.is_available:
        print("❌ Ollama is not running!")
        print()
        print("Please start Ollama:")
        print("  1. Run: ollama serve")
        print("  2. Or restart Ollama service")
        print()
        exit(1)

    print("✅ Ollama is running!")
    print()

    # List available models
    models = ollama.list_models()
    print(f"Available models ({len(models)}):")
    for model in models:
        print(f"  - {model['name']}")
    print()

    # Test if recommended models are installed
    model_names = [m['name'] for m in models]

    print("Checking recommended models:")
    print(f"  Primary (dolphin-mixtral:8x7b): {'✅' if 'dolphin-mixtral:8x7b' in model_names else '❌ Not installed'}")
    print(f"  Backup (llama3.3:70b): {'✅' if 'llama3.3:70b' in model_names else '❌ Not installed'}")
    print(f"  Fast (dolphin-llama3:8b): {'✅' if 'dolphin-llama3:8b' in model_names else '❌ Not installed'}")
    print()

    # Simple test
    print("Testing model response...")
    response = ollama.generate("Say 'Ollama integration working!' in one sentence.")
    print(f"Response: {response}")
    print()

    print("="*80)
    print("Ollama integration ready!")
    print("="*80)
