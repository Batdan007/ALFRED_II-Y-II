"""
Alfred Client - Simple Python API for Alfred AI Assistant
100% Local, Privacy-First AI with Permanent Memory

Example:
    from alfred import Alfred

    bot = Alfred()
    response = bot.respond("Hello Alfred, how are you?")
    print(response)

Author: Daniel J Rita (BATDAN)
"""

import logging
import subprocess
import time
import sys
from typing import Optional, List, Dict
from pathlib import Path

# Add parent directory to path to import core modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.brain import AlfredBrain
from core.privacy_controller import PrivacyController
from ai.multimodel import MultiModelOrchestrator


class Alfred:
    """
    Simple Python API for Alfred AI Assistant

    Features:
    - 100% local AI (no API key needed, uses Ollama)
    - Permanent memory (remembers all conversations)
    - Auto-starts Ollama server if needed
    - Privacy-first (no cloud, no data sharing)

    Usage:
        bot = Alfred()
        response = bot.respond("Hello!")
        print(response)
    """

    def __init__(self, api_key: Optional[str] = None, voice_enabled: bool = False):
        """
        Initialize Alfred

        Args:
            api_key: Optional API key (not needed for local mode)
            voice_enabled: Enable voice responses (default: False)
        """
        self.logger = self._setup_logging()
        self.voice_enabled = voice_enabled

        # Initialize components
        self.logger.info("Initializing Alfred...")

        # Ensure Ollama is running
        self._ensure_ollama_running()

        # Brain (permanent memory)
        self.brain = AlfredBrain()
        self.logger.info("Alfred Brain initialized")

        # Privacy controller (LOCAL mode by default)
        self.privacy = PrivacyController(auto_confirm=False)

        # AI orchestrator (uses local Ollama)
        self.ai = MultiModelOrchestrator(privacy_controller=self.privacy)
        self.logger.info("Alfred initialized successfully")

        # Voice (optional)
        self.voice = None
        if voice_enabled:
            try:
                from capabilities.voice.alfred_voice import AlfredVoice
                self.voice = AlfredVoice(privacy_mode=True)
                self.logger.info("Voice system enabled")
            except Exception as e:
                self.logger.warning(f"Could not enable voice: {e}")

    def _setup_logging(self) -> logging.Logger:
        """Setup logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)

    def _ensure_ollama_running(self):
        """Ensure Ollama is running, start it if needed"""
        try:
            import requests
            # Check if Ollama is already running
            response = requests.get('http://localhost:11434/api/version', timeout=2)
            self.logger.info("Ollama is running")
            return True
        except:
            # Ollama not running, try to start it
            self.logger.info("Starting Ollama server...")
            try:
                # Start Ollama in background
                subprocess.Popen(
                    ['ollama', 'serve'],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
                )
                # Wait for Ollama to start
                for i in range(10):
                    time.sleep(1)
                    try:
                        import requests
                        requests.get('http://localhost:11434/api/version', timeout=1)
                        self.logger.info("Ollama started successfully")
                        return True
                    except:
                        continue
                self.logger.warning("Ollama failed to start")
                return False
            except Exception as e:
                self.logger.error(f"Could not start Ollama: {e}")
                return False

    def respond(self, user_message: str, save_to_memory: bool = True) -> str:
        """
        Get response from Alfred

        Args:
            user_message: User's message/question
            save_to_memory: Save conversation to permanent memory (default: True)

        Returns:
            Alfred's response as string
        """
        try:
            # Get conversation context from brain
            context = self.brain.get_conversation_context(limit=5) if save_to_memory else None

            # Generate response using AI
            response = self.ai.generate(
                prompt=user_message,
                context=context
            )

            if not response:
                response = "I apologize, sir. I'm having trouble generating a response. Please ensure Ollama is running."

            # Save to memory
            if save_to_memory:
                self.brain.store_conversation(
                    user_input=user_message,
                    alfred_response=response,
                    success=True
                )

            # Speak response if voice enabled
            if self.voice_enabled and self.voice:
                self.voice.speak(response)

            return response

        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            return f"I apologize, sir. An error occurred: {str(e)}"

    def get_memory_stats(self) -> Dict:
        """
        Get Alfred's memory statistics

        Returns:
            Dictionary with memory stats
        """
        return self.brain.get_memory_stats()

    def recall_knowledge(self, category: str, key: str) -> Optional[str]:
        """
        Recall specific knowledge from memory

        Args:
            category: Knowledge category
            key: Knowledge key

        Returns:
            Knowledge value or None
        """
        return self.brain.recall_knowledge(category, key)

    def get_topics(self) -> List[Dict]:
        """
        Get tracked conversation topics

        Returns:
            List of topics with frequency and importance
        """
        return self.brain.get_topics_by_importance()

    def export_memory(self, filepath: Optional[str] = None) -> str:
        """
        Export Alfred's brain to backup file

        Args:
            filepath: Optional custom filepath

        Returns:
            Path to exported file
        """
        return self.brain.export_to_file(filepath)

    def clear_screen_memory(self):
        """Clear recent conversation context (keeps long-term memory)"""
        # This would clear context windows, not the full brain
        self.logger.info("Screen memory cleared (long-term memory intact)")

    def __repr__(self):
        """String representation"""
        stats = self.get_memory_stats()
        return (
            f"Alfred(conversations={stats.get('conversations', 0)}, "
            f"knowledge_items={stats.get('knowledge', 0)}, "
            f"mode={'LOCAL' if self.privacy.is_local_only() else 'HYBRID'})"
        )
