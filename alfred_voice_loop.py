#!/usr/bin/env python3
"""
ALFRED Voice Loop
=================
Hands-free voice interface. One file, no complexity.

Usage:
    python alfred_voice_loop.py [model_name]

Examples:
    python alfred_voice_loop.py              # Uses llama3.2
    python alfred_voice_loop.py mistral      # Uses mistral
    python alfred_voice_loop.py qwen2.5:7b   # Uses qwen2.5:7b

Author: Daniel J Rita (BATDAN)
"""

import os
import sys
import logging

# Add project root
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import requests

# ============================================================
# Configuration
# ============================================================

OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3.2"

EXIT_PHRASES = ["goodbye", "exit", "quit", "that will be all", "dismissed"]

SYSTEM_PROMPT = """You are ALFRED, an American AI butler with a refined British accent.
You serve Master Batdan with loyalty and dry wit.
Address the user as "Master Batdan" or "Sir".
Use expressions like "Quite so", "Indeed", "Very good, sir".
Be concise - 1-3 sentences unless more detail is needed.
Subtle wit and dry humor. Never use emojis."""

# ============================================================
# Voice Interface
# ============================================================

def load_voice():
    """Load voice interface"""
    try:
        from capabilities.voice.alfred_voice_unified import create_voice_interface
        return create_voice_interface()
    except ImportError as e:
        print(f"Voice module not available: {e}")
        print("Run: python setup_voice.py")
        return None

# ============================================================
# Ollama Client
# ============================================================

class Ollama:
    def __init__(self, model: str):
        self.model = model
        self.history = []

    def check(self) -> bool:
        try:
            r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=3)
            return r.status_code == 200
        except:
            return False

    def models(self) -> list:
        try:
            r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=3)
            return [m['name'] for m in r.json().get('models', [])]
        except:
            return []

    def chat(self, message: str) -> str:
        self.history.append({"role": "user", "content": message})
        if len(self.history) > 20:
            self.history = self.history[-20:]

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend(self.history)

        try:
            r = requests.post(
                f"{OLLAMA_URL}/api/chat",
                json={"model": self.model, "messages": messages, "stream": False},
                timeout=60
            )
            if r.status_code == 200:
                response = r.json()['message']['content']
                self.history.append({"role": "assistant", "content": response})
                return response
        except Exception as e:
            return f"I apologize, sir, technical difficulty: {e}"

        return "I apologize, sir, but the systems are not responding."

# ============================================================
# Main Loop
# ============================================================

def main():
    # Model from args
    model = sys.argv[1] if len(sys.argv) > 1 else OLLAMA_MODEL

    # Header
    print("\n" + "=" * 50)
    print("  ALFRED Voice Interface")
    print("=" * 50)

    # Load voice
    print("\n  Loading voice system...", end=" ", flush=True)
    voice = load_voice()
    if voice and voice.stt_available and voice.tts_available:
        print("OK")
    elif voice:
        print("PARTIAL")
        if not voice.stt_available:
            print("    STT not available")
        if not voice.tts_available:
            print("    TTS not available (install ffmpeg)")
    else:
        print("FAILED")
        return 1

    # Check Ollama
    print(f"  Connecting to Ollama ({model})...", end=" ", flush=True)
    llm = Ollama(model)
    if llm.check():
        print("OK")
    else:
        print("FAILED")
        print("\n  Start Ollama: ollama serve")
        return 1

    # Ready
    print("\n" + "=" * 50)
    print("  Ready. Press ENTER to speak, 'q' to quit.")
    print("=" * 50 + "\n")

    # Greet
    voice.greet()

    # Loop
    while True:
        try:
            cmd = input("  [ENTER=speak] > ").strip().lower()

            if cmd in ['q', 'quit', 'exit']:
                voice.farewell()
                break

            if cmd:
                text = cmd  # Typed input
            else:
                print("  [Listening...]")
                text = voice.listen()

            if not text:
                print("  [No speech detected]")
                continue

            print(f"\n  You: {text}")

            # Exit check
            if any(p in text.lower() for p in EXIT_PHRASES):
                voice.farewell()
                break

            # Get response
            response = llm.chat(text)
            print(f"\n  ALFRED: {response}\n")
            voice.speak(response)

        except KeyboardInterrupt:
            print()
            voice.farewell()
            break

    print("\n  ALFRED signing off.\n")
    return 0

if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    sys.exit(main())
