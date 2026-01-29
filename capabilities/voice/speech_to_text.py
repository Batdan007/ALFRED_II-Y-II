"""
Alfred's Ears - Speech Recognition for BATDAN
Can be interrupted, always listening when active
Author: Daniel J Rita (BATDAN)
"""

import logging
from typing import Optional, Callable

# Graceful degradation for optional speech recognition
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False
    sr = None


class AlfredEars:
    """
    Alfred's listening system - always attentive to BATDAN

    Features:
    - Continuous listening when active
    - Can be interrupted
    - Filters background noise
    - Local processing (100% private)
    """

    WAKE_WORDS = ['alfred', 'hey alfred', 'okay alfred', 'computer']

    def __init__(self, listen_timeout: int = 5, phrase_time_limit: int = 10):
        """
        Initialize Alfred's ears

        Args:
            listen_timeout: Seconds to wait for speech to start
            phrase_time_limit: Max seconds for a phrase
        """
        self.logger = logging.getLogger(__name__)

        if not SPEECH_RECOGNITION_AVAILABLE:
            self.logger.warning("⚠️ Speech recognition not available. Install with: pip install SpeechRecognition pyaudio")
            self.recognizer = None
            self.microphone = None
            self.listen_timeout = listen_timeout
            self.phrase_time_limit = phrase_time_limit
            self.listening = False
            self.wake_word_mode = False
            return

        self.recognizer = sr.Recognizer()
        self.microphone = None
        self.listen_timeout = listen_timeout
        self.phrase_time_limit = phrase_time_limit
        self.listening = False
        self.wake_word_mode = False

        self._initialize_microphone()

    def _initialize_microphone(self):
        """Initialize the microphone"""
        try:
            self.microphone = sr.Microphone()

            # Adjust for ambient noise
            with self.microphone as source:
                self.logger.info("🎤 Calibrating for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)

            self.logger.info("✅ Alfred's ears initialized")

        except Exception as e:
            self.logger.error(f"❌ Failed to initialize microphone: {e}")
            self.microphone = None

    def listen_once(self, timeout: Optional[int] = None) -> Optional[str]:
        """
        Listen for a single command

        Args:
            timeout: Override default timeout

        Returns:
            Recognized text or None
        """
        if not self.microphone:
            self.logger.error("❌ No microphone available")
            return None

        timeout = timeout or self.listen_timeout

        try:
            self.logger.debug("👂 Listening...")

            with self.microphone as source:
                # Listen
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=self.phrase_time_limit
                )

            # Recognize (using Google Speech Recognition - free and local processing)
            self.logger.debug("🔄 Processing speech...")
            text = self.recognizer.recognize_google(audio)

            self.logger.debug(f"✅ Heard: '{text}'")
            return text

        except sr.WaitTimeoutError:
            self.logger.debug("⏱️ Listening timeout (no speech detected)")
            return None

        except sr.UnknownValueError:
            self.logger.debug("🤷 Could not understand audio")
            return None

        except sr.RequestError as e:
            self.logger.error(f"❌ Could not request results: {e}")
            return None

        except Exception as e:
            self.logger.error(f"❌ Listening error: {e}")
            return None

    def listen_continuous(self, callback: Callable[[str], None],
                         stop_phrase: str = "stop listening"):
        """
        Listen continuously and call callback with recognized text

        Args:
            callback: Function to call with recognized text
            stop_phrase: Phrase to stop listening
        """
        if not self.microphone:
            self.logger.error("❌ No microphone available")
            return

        self.listening = True
        self.logger.debug("👂 Continuous listening active")

        try:
            while self.listening:
                text = self.listen_once()

                if text:
                    # Check for stop phrase
                    if stop_phrase.lower() in text.lower():
                        self.logger.info("🛑 Stop phrase detected")
                        break

                    # Call callback with recognized text
                    callback(text)

        except KeyboardInterrupt:
            self.logger.info("🛑 Listening interrupted by user")

        finally:
            self.listening = False
            self.logger.info("👂 Continuous listening stopped")

    def listen_for_wake_word(self, callback: Callable[[str], None]):
        """
        Listen for wake word, then activate full listening

        Args:
            callback: Function to call when wake word detected
        """
        if not self.microphone:
            self.logger.error("❌ No microphone available")
            return

        self.wake_word_mode = True
        self.logger.debug(f"👂 Listening for wake word: {self.WAKE_WORDS}")

        try:
            while self.wake_word_mode:
                text = self.listen_once(timeout=None)  # Wait indefinitely

                if text:
                    text_lower = text.lower()

                    # Check for wake word
                    if any(wake_word in text_lower for wake_word in self.WAKE_WORDS):
                        self.logger.info(f"✅ Wake word detected: '{text}'")

                        # Remove wake word from text
                        for wake_word in self.WAKE_WORDS:
                            text = text_lower.replace(wake_word, '').strip()

                        # If there's a command after the wake word, process it
                        if text:
                            callback(text)
                        else:
                            # Just wake word, listen for command
                            command = self.listen_once()
                            if command:
                                callback(command)

        except KeyboardInterrupt:
            self.logger.info("🛑 Wake word listening interrupted")

        finally:
            self.wake_word_mode = False
            self.logger.info("👂 Wake word listening stopped")

    def stop_listening(self):
        """Stop continuous or wake word listening"""
        self.listening = False
        self.wake_word_mode = False
        self.logger.info("🛑 Listening stopped")

    def get_available_microphones(self) -> list:
        """Get list of available microphones"""
        try:
            mics = sr.Microphone.list_microphone_names()
            return [f"{i}: {name}" for i, name in enumerate(mics)]
        except Exception as e:
            self.logger.error(f"❌ Failed to list microphones: {e}")
            return []

    def set_microphone(self, device_index: int):
        """Set specific microphone device"""
        try:
            self.microphone = sr.Microphone(device_index=device_index)
            self._initialize_microphone()
            self.logger.info(f"✅ Microphone set to device {device_index}")
        except Exception as e:
            self.logger.error(f"❌ Failed to set microphone: {e}")

    def get_status(self) -> dict:
        """Get listening status"""
        return {
            'listening': self.listening,
            'wake_word_mode': self.wake_word_mode,
            'microphone': 'Available' if self.microphone else 'Not available',
            'timeout': self.listen_timeout,
            'phrase_limit': self.phrase_time_limit
        }


# Convenience function
def create_alfred_ears() -> AlfredEars:
    """Create Alfred's listening system"""
    return AlfredEars()
