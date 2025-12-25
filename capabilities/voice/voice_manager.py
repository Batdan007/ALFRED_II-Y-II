"""
Alfred's Unified Voice Manager
Combines STT and TTS with privacy-first fallback chains

STT Chain: VOSK (offline) -> Google Speech (online)
TTS Chain: ElevenLabs (premium) -> pyttsx3 (local)

Author: Daniel J Rita (BATDAN)
"""

import logging
from typing import Optional, Callable, Dict, Any
from dataclasses import dataclass
from enum import Enum


class VoiceMode(Enum):
    """Voice system operating modes"""
    LOCAL = "local"        # 100% offline (VOSK + pyttsx3)
    HYBRID = "hybrid"      # Prefer offline, fallback to cloud
    CLOUD = "cloud"        # Prefer cloud (ElevenLabs + Google)


@dataclass
class VoiceManagerConfig:
    """Configuration for unified voice manager"""
    # Mode
    mode: VoiceMode = VoiceMode.LOCAL

    # STT settings
    stt_timeout: int = 5
    stt_phrase_limit: int = 10
    wake_words: list = None

    # TTS settings
    tts_voice: str = "Daniel"  # ElevenLabs voice or platform voice name
    tts_rate: int = 175  # Speaking rate for pyttsx3

    # Privacy
    require_wake_word: bool = False
    identify_speaker: bool = True


class VoiceManager:
    """
    Unified voice manager for Alfred

    Provides a single interface for:
    - Speech-to-Text (STT): VOSK offline -> Google Speech fallback
    - Text-to-Speech (TTS): ElevenLabs premium -> pyttsx3 fallback

    Privacy-first design:
    - LOCAL mode: 100% offline operation
    - HYBRID mode: Prefer offline, use cloud as fallback
    - CLOUD mode: Prefer cloud for best quality
    """

    def __init__(self, config: Optional[VoiceManagerConfig] = None,
                 brain=None, privacy_controller=None):
        """
        Initialize unified voice manager

        Args:
            config: VoiceManagerConfig with settings
            brain: AlfredBrain for memory integration
            privacy_controller: PrivacyController for cloud access
        """
        self.logger = logging.getLogger(__name__)
        self.config = config or VoiceManagerConfig()
        self.brain = brain
        self.privacy_controller = privacy_controller

        # Components
        self.ears = None  # AlfredEarsAdvanced (STT)
        self.voice = None  # AlfredVoice (TTS)

        # State
        self.listening = False
        self.speaking = False

        # Initialize components
        self._initialize_stt()
        self._initialize_tts()

        self.logger.info(f"Voice Manager initialized (mode: {self.config.mode.value})")

    def _initialize_stt(self):
        """Initialize speech-to-text system"""
        try:
            from capabilities.voice.alfred_ears_advanced import (
                AlfredEarsAdvanced,
                create_alfred_ears_advanced
            )

            prefer_offline = self.config.mode in [VoiceMode.LOCAL, VoiceMode.HYBRID]

            self.ears = create_alfred_ears_advanced(
                brain=self.brain,
                prefer_offline=prefer_offline
            )

            # Configure wake words
            if self.config.wake_words:
                self.ears.WAKE_WORDS = self.config.wake_words

            status = self.ears.get_status()
            self.logger.info(f"STT initialized: {status['stt_engines']['active']}")

        except Exception as e:
            self.logger.error(f"Failed to initialize STT: {e}")
            self.ears = None

    def _initialize_tts(self):
        """Initialize text-to-speech system"""
        try:
            from capabilities.voice.alfred_voice import (
                AlfredVoice,
                create_alfred_voice
            )

            privacy_mode = self.config.mode == VoiceMode.LOCAL
            prefer_elevenlabs = self.config.mode == VoiceMode.CLOUD

            self.voice = create_alfred_voice(
                privacy_mode=privacy_mode,
                privacy_controller=self.privacy_controller,
                prefer_elevenlabs=prefer_elevenlabs
            )

            status = self.voice.get_status()
            self.logger.info(f"TTS initialized: {status['tts_engines']['active']}")

        except Exception as e:
            self.logger.error(f"Failed to initialize TTS: {e}")
            self.voice = None

    # ==================== STT Methods ====================

    def listen(self, timeout: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Listen for speech and convert to text

        Args:
            timeout: Override default timeout

        Returns:
            Dict with 'text', 'confidence', 'engine' or None
        """
        if not self.ears:
            self.logger.error("STT not available")
            return None

        timeout = timeout or self.config.stt_timeout
        self.listening = True

        try:
            result = self.ears.listen_once(
                timeout=timeout,
                identify_speaker=self.config.identify_speaker
            )
            return result

        finally:
            self.listening = False

    def listen_continuous(self, callback: Callable[[str], None],
                         stop_phrase: str = "stop listening"):
        """
        Listen continuously and call callback with recognized text

        Args:
            callback: Function to call with recognized text
            stop_phrase: Phrase to stop listening
        """
        if not self.ears:
            self.logger.error("STT not available")
            return

        self.listening = True
        self.logger.info(f"Continuous listening started (say '{stop_phrase}' to stop)")

        try:
            while self.listening:
                result = self.listen()

                if result and result.get('text'):
                    text = result['text']

                    # Check for stop phrase
                    if stop_phrase.lower() in text.lower():
                        self.logger.info("Stop phrase detected")
                        break

                    # Check wake word if required
                    if self.config.require_wake_word:
                        if not result.get('wake_word_detected'):
                            continue  # Skip if no wake word

                    callback(text)

        except KeyboardInterrupt:
            self.logger.info("Listening interrupted")

        finally:
            self.listening = False
            self.logger.info("Continuous listening stopped")

    def listen_for_wake_word(self, callback: Callable[[str], None]):
        """
        Listen for wake word, then process command

        Args:
            callback: Function to call with command after wake word
        """
        if not self.ears:
            self.logger.error("STT not available")
            return

        self.config.require_wake_word = True
        self.listen_continuous(callback)

    def stop_listening(self):
        """Stop listening"""
        self.listening = False
        if self.ears:
            self.ears.stop_listening()

    # ==================== TTS Methods ====================

    def speak(self, text: str, personality: str = "information"):
        """
        Convert text to speech

        Args:
            text: Text to speak
            personality: Personality type (greeting, confirmation, warning, etc.)
        """
        if not self.voice:
            self.logger.error("TTS not available")
            return

        from capabilities.voice.alfred_voice import VoicePersonality

        personality_map = {
            "greeting": VoicePersonality.GREETING,
            "confirmation": VoicePersonality.CONFIRMATION,
            "warning": VoicePersonality.WARNING,
            "suggestion": VoicePersonality.SUGGESTION,
            "sarcasm": VoicePersonality.SARCASM,
            "information": VoicePersonality.INFORMATION,
            "error": VoicePersonality.ERROR
        }

        self.speaking = True
        try:
            self.voice.speak(
                text,
                personality=personality_map.get(personality, VoicePersonality.INFORMATION)
            )
        finally:
            self.speaking = False

    def greet(self):
        """Alfred greets"""
        if self.voice:
            self.voice.greet()

    def confirm(self, action: Optional[str] = None):
        """Confirm an action"""
        if self.voice:
            self.voice.confirm(action)

    def warn(self, warning: str):
        """Warn about something"""
        if self.voice:
            self.voice.warn(warning)

    def error(self, error_msg: str):
        """Report an error"""
        if self.voice:
            self.voice.error(error_msg)

    def stop_speaking(self):
        """Stop speaking"""
        self.speaking = False
        if self.voice:
            self.voice.stop_speaking()

    # ==================== Voice Conversation ====================

    def converse(self, process_input: Callable[[str], str],
                 greeting: str = "Good evening, sir. How may I assist you?",
                 stop_phrase: str = "goodbye alfred"):
        """
        Have a voice conversation

        Args:
            process_input: Function that takes user input and returns response
            greeting: Initial greeting
            stop_phrase: Phrase to end conversation
        """
        self.logger.info("Starting voice conversation")

        # Greet
        self.speak(greeting, "greeting")

        # Conversation loop
        def handle_input(text: str):
            # Get response
            response = process_input(text)

            # Speak response
            if response:
                self.speak(response)

        self.listen_continuous(handle_input, stop_phrase=stop_phrase)

        # Farewell
        self.speak("Very good, sir. Until next time.", "confirmation")

    # ==================== Mode Control ====================

    def set_mode(self, mode: VoiceMode):
        """
        Set operating mode

        Args:
            mode: VoiceMode (LOCAL, HYBRID, CLOUD)
        """
        self.config.mode = mode

        # Update STT
        if self.ears:
            prefer_offline = mode in [VoiceMode.LOCAL, VoiceMode.HYBRID]
            self.ears.set_offline_mode(prefer_offline)

        # Update TTS
        if self.voice:
            privacy_mode = mode == VoiceMode.LOCAL
            self.voice.set_privacy_mode(privacy_mode)

        self.logger.info(f"Voice mode set to: {mode.value}")

    def set_local_mode(self):
        """Enable 100% offline operation"""
        self.set_mode(VoiceMode.LOCAL)

    def set_cloud_mode(self):
        """Enable cloud services for best quality"""
        self.set_mode(VoiceMode.CLOUD)

    # ==================== Status ====================

    def get_status(self) -> dict:
        """Get comprehensive voice system status"""
        stt_status = {}
        if self.ears:
            stt_status = self.ears.get_status()

        tts_status = {}
        if self.voice:
            tts_status = self.voice.get_status()

        return {
            'mode': self.config.mode.value,
            'listening': self.listening,
            'speaking': self.speaking,
            'stt': {
                'available': self.ears is not None,
                'engines': stt_status.get('stt_engines', {}),
                'wake_words': self.config.wake_words or self.ears.WAKE_WORDS if self.ears else []
            },
            'tts': {
                'available': self.voice is not None,
                'engines': tts_status.get('tts_engines', {}),
                'enabled': tts_status.get('enabled', False)
            },
            'privacy_mode': self.config.mode == VoiceMode.LOCAL
        }

    def is_available(self) -> bool:
        """Check if voice system is available"""
        return self.ears is not None or self.voice is not None

    def stt_available(self) -> bool:
        """Check if STT is available"""
        return self.ears is not None

    def tts_available(self) -> bool:
        """Check if TTS is available"""
        return self.voice is not None

    # ==================== Model Management ====================

    def download_vosk_model(self, size: str = "small") -> bool:
        """
        Download VOSK model for offline STT

        Args:
            size: "small" (~50MB), "medium" (~500MB), "large" (~1.8GB)
        """
        if not self.ears:
            self.logger.error("STT not initialized")
            return False

        return self.ears.download_vosk_model(size)


def create_voice_manager(
    mode: str = "local",
    brain=None,
    privacy_controller=None
) -> VoiceManager:
    """
    Factory function to create voice manager

    Args:
        mode: "local", "hybrid", or "cloud"
        brain: AlfredBrain instance
        privacy_controller: PrivacyController instance

    Returns:
        VoiceManager instance
    """
    mode_map = {
        "local": VoiceMode.LOCAL,
        "hybrid": VoiceMode.HYBRID,
        "cloud": VoiceMode.CLOUD
    }

    config = VoiceManagerConfig(mode=mode_map.get(mode, VoiceMode.LOCAL))

    return VoiceManager(
        config=config,
        brain=brain,
        privacy_controller=privacy_controller
    )


# CLI test
if __name__ == "__main__":
    import json
    logging.basicConfig(level=logging.INFO)

    print("Voice Manager Test")
    print("="*40)

    manager = create_voice_manager(mode="local")
    status = manager.get_status()

    print(f"\nStatus:")
    print(json.dumps(status, indent=2))

    if manager.tts_available():
        print("\nTesting TTS...")
        manager.speak("Good evening, sir. The voice system is operational.")

    if manager.stt_available():
        print("\nTesting STT (5 second timeout)...")
        result = manager.listen(timeout=5)
        if result:
            print(f"Heard: {result['text']}")
        else:
            print("No speech detected")
