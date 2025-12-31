#!/usr/bin/env python3
"""
ALFRED Voice Mode - Full Brain Integration
===========================================
Voice interface that uses the COMPLETE ALFRED system:
- 11-table SQLite brain
- MultiModel orchestrator
- All capabilities (vision, tools, RAG, etc.)

This is NOT a basic chat wrapper - it's the full ALFRED with voice.

Usage:
    python alfred_voice_mode.py

Author: Daniel J Rita (BATDAN)
"""

import sys
import logging
from pathlib import Path

# Add project root
sys.path.insert(0, str(Path(__file__).parent))

from rich.console import Console
from rich.panel import Panel
from rich import box

# Core ALFRED components
from core.brain import AlfredBrain
from core.privacy_controller import PrivacyController
from ai.multimodel import MultiModelOrchestrator

# New voice system
try:
    from capabilities.voice.alfred_voice_unified import create_voice_interface, VoiceInterface
    VOICE_AVAILABLE = True
except ImportError as e:
    print(f"Voice not available: {e}")
    print("Run: python setup_voice.py")
    VOICE_AVAILABLE = False
    VoiceInterface = None

# Optional components (graceful degradation)
try:
    from tools.manager import ToolManager
    TOOLS_AVAILABLE = True
except ImportError:
    ToolManager = None
    TOOLS_AVAILABLE = False

try:
    from core.guardian import protect_response
    GUARDIAN_AVAILABLE = True
except ImportError:
    protect_response = lambda x, y="confirmation": x
    GUARDIAN_AVAILABLE = False


# ============================================================
# Configuration
# ============================================================

EXIT_PHRASES = [
    "goodbye alfred", "goodbye", "that will be all",
    "dismissed", "exit", "quit", "stop listening"
]


# ============================================================
# ALFRED Voice Mode
# ============================================================

class AlfredVoiceMode:
    """
    Full ALFRED with voice interface.

    Uses the complete brain, multi-model AI, and all capabilities.
    """

    def __init__(self):
        self.console = Console()
        self.logger = logging.getLogger(__name__)
        self.running = False

        # Core components
        self.brain = None
        self.privacy = None
        self.ai = None
        self.voice = None
        self.tools = None

        self._initialize()

    def _initialize(self):
        """Initialize all ALFRED systems"""
        self._print_header()

        # Brain (11-table SQLite)
        print("  Loading brain...", end=" ", flush=True)
        try:
            self.brain = AlfredBrain()
            print("OK")
        except Exception as e:
            print(f"FAILED: {e}")
            return

        # Privacy controller
        print("  Loading privacy controller...", end=" ", flush=True)
        try:
            self.privacy = PrivacyController()
            print("OK")
        except Exception as e:
            print(f"FAILED: {e}")

        # Multi-model AI
        print("  Loading AI orchestrator...", end=" ", flush=True)
        try:
            self.ai = MultiModelOrchestrator(privacy_controller=self.privacy)
            print("OK")
        except Exception as e:
            print(f"FAILED: {e}")
            return

        # Tools (optional)
        if TOOLS_AVAILABLE:
            print("  Loading tools...", end=" ", flush=True)
            try:
                self.tools = ToolManager(brain=self.brain)
                print(f"OK ({len(self.tools.tools)} tools)")
            except Exception as e:
                print(f"PARTIAL: {e}")

        # Voice (new unified system)
        if VOICE_AVAILABLE:
            print("  Loading voice...", end=" ", flush=True)
            try:
                self.voice = create_voice_interface()
                status = self.voice.get_status()
                if status['stt']['available'] and status['tts']['available']:
                    print(f"OK (Whisper + Edge TTS)")
                else:
                    print("PARTIAL")
            except Exception as e:
                print(f"FAILED: {e}")
        else:
            print("  Voice: NOT AVAILABLE (run setup_voice.py)")

        print()

    def _print_header(self):
        """Print startup header"""
        print("\n" + "=" * 60)
        print("  A.L.F.R.E.D. Voice Mode")
        print("  Full Brain Integration")
        print("=" * 60)
        print()

    def speak(self, text: str):
        """Speak text and print to console"""
        self.console.print(f"\n  [bold cyan]ALFRED:[/bold cyan] {text}\n")
        if self.voice and self.voice.tts_available:
            self.voice.speak(text)

    def listen(self) -> str:
        """Listen for speech"""
        if not self.voice or not self.voice.stt_available:
            return ""

        print("  [Listening...]")
        return self.voice.listen()

    def process(self, user_input: str) -> str:
        """
        Process user input through the FULL ALFRED system.

        This uses:
        - Brain for context and memory
        - Multi-model AI for response
        - Tools if enabled
        - Privacy controls
        """
        # Check for exit
        if any(phrase in user_input.lower() for phrase in EXIT_PHRASES):
            return None

        # Get context from brain
        context = ""
        if self.brain:
            # Get recent conversations for context
            recent = self.brain.get_recent_conversations(limit=5)
            if recent:
                context = "Recent conversation context:\n"
                for conv in recent[-3:]:
                    context += f"User: {conv['user_input'][:100]}...\n"
                    context += f"Alfred: {conv['alfred_response'][:100]}...\n"

            # Get relevant knowledge
            knowledge = self.brain.search_knowledge(user_input, limit=3)
            if knowledge:
                context += "\nRelevant knowledge:\n"
                for k in knowledge:
                    context += f"- {k['content'][:100]}...\n"

        # Generate response using multi-model AI
        try:
            response = self.ai.generate(
                user_input,
                context=[{'role': 'system', 'content': context}] if context else None
            )

            # Protect response (if Guardian available)
            response = protect_response(response, "information")

            # Store in brain
            if self.brain:
                self.brain.store_conversation(
                    user_input=user_input,
                    alfred_response=response,
                    context=context[:500],
                    models_used="voice_mode"
                )

            return response

        except Exception as e:
            self.logger.error(f"Processing error: {e}")
            return f"I apologize, sir, but I encountered a difficulty: {str(e)}"

    def run(self):
        """Main voice conversation loop"""
        if not self.ai:
            print("  ERROR: AI not initialized. Cannot run.")
            return 1

        if not self.voice or not self.voice.stt_available:
            print("  ERROR: Voice not available. Run setup_voice.py first.")
            return 1

        # Show status
        self.console.print(Panel(
            "[bold cyan]ALFRED Voice Mode[/bold cyan]\n"
            "[dim]Full brain • Multi-model AI • Voice I/O[/dim]\n\n"
            "Press [bold]ENTER[/bold] to speak\n"
            "Type [bold]q[/bold] to quit\n"
            "Say [bold]goodbye[/bold] to exit",
            border_style="cyan",
            box=box.ROUNDED
        ))
        print()

        # Greeting
        self.speak("Good day, Master Batdan. The full ALFRED system is at your service.")

        self.running = True

        while self.running:
            try:
                cmd = input("  [ENTER=speak, q=quit] > ").strip().lower()

                if cmd in ['q', 'quit']:
                    self.speak("Very good, sir. Until next time.")
                    break

                if cmd:
                    # Typed input
                    text = cmd
                else:
                    # Voice input
                    text = self.listen()

                if not text:
                    print("  [No speech detected]")
                    continue

                self.console.print(f"\n  [bold green]You:[/bold green] {text}")

                # Process through full ALFRED system
                response = self.process(text)

                if response is None:
                    self.speak("Very good, sir. I shall be here if you need me.")
                    break

                self.speak(response)

            except KeyboardInterrupt:
                print()
                self.speak("As you wish, sir.")
                break
            except Exception as e:
                self.logger.error(f"Error: {e}")
                print(f"\n  [Error: {e}]")

        self.running = False

        # Show memory stats on exit
        if self.brain:
            stats = self.brain.get_memory_stats()
            print(f"\n  Brain stats: {stats['conversations']} conversations, {stats['knowledge']} knowledge items")

        print("\n  ALFRED signing off.\n")
        return 0


# ============================================================
# Entry Point
# ============================================================

def main():
    logging.basicConfig(
        level=logging.WARNING,
        format='%(levelname)s: %(message)s'
    )

    alfred = AlfredVoiceMode()
    return alfred.run()


if __name__ == "__main__":
    sys.exit(main())
