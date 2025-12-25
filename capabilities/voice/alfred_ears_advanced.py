"""
Alfred's Advanced Ears - Speech Recognition with Speaker Identification
Can distinguish BATDAN's voice from others, TV, and background noise
Learns voice patterns for personalized recognition

STT Priority Chain:
1. VOSK (offline, privacy-first, no internet required)
2. Google Speech Recognition (online fallback)

Author: Daniel J Rita (BATDAN)
"""

import logging
import numpy as np
from pathlib import Path
from typing import Optional, Callable, Dict, Tuple
from datetime import datetime
import pickle


# VOSK offline speech recognition (preferred - privacy-first)
try:
    from capabilities.voice.vosk_recognizer import VoskRecognizer, VoskConfig, create_vosk_recognizer
    VOSK_AVAILABLE = True
except ImportError:
    VOSK_AVAILABLE = False
    VoskRecognizer = None

# Graceful degradation for optional speech recognition (fallback)
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False
    sr = None

try:
    import librosa
    import soundfile as sf
    AUDIO_ANALYSIS_AVAILABLE = True
except ImportError:
    AUDIO_ANALYSIS_AVAILABLE = False

try:
    from resemblyzer import VoiceEncoder, preprocess_wav
    SPEAKER_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEAKER_RECOGNITION_AVAILABLE = False


class AlfredEarsAdvanced:
    """
    Alfred's advanced listening system - knows BATDAN's voice

    Features:
    - Continuous listening with wake word detection
    - Speaker identification (recognizes BATDAN specifically)
    - Filters out TV, other people, background noise
    - Voice pattern learning
    - Integration with AlfredBrain for voice memory
    - Can be interrupted
    """

    WAKE_WORDS = ['alfred', 'hey alfred', 'okay alfred', 'computer', 'bat computer']

    def __init__(self, brain=None, listen_timeout: int = 5, phrase_time_limit: int = 10,
                 prefer_offline: bool = True):
        """
        Initialize Alfred's advanced ears

        Args:
            brain: AlfredBrain instance for voice memory
            listen_timeout: Seconds to wait for speech to start
            phrase_time_limit: Max seconds for a phrase
            prefer_offline: If True, prefer VOSK offline recognition (privacy-first)
        """
        self.logger = logging.getLogger(__name__)
        self.brain = brain
        self.prefer_offline = prefer_offline

        # VOSK offline recognizer (primary - privacy-first)
        self.vosk_recognizer = None
        self._initialize_vosk()

        # Google Speech Recognition (fallback)
        self.recognizer = None
        self.microphone = None

        if not VOSK_AVAILABLE and not SPEECH_RECOGNITION_AVAILABLE:
            self.logger.warning("⚠️ No speech recognition available.")
            self.logger.warning("   For offline: pip install vosk sounddevice")
            self.logger.warning("   For online:  pip install SpeechRecognition pyaudio")
            self.listen_timeout = listen_timeout
            self.phrase_time_limit = phrase_time_limit
            self.listening = False
            self.wake_word_mode = False
            return

        # Initialize Google Speech Recognition as fallback
        if SPEECH_RECOGNITION_AVAILABLE:
            self.recognizer = sr.Recognizer()

        self.listen_timeout = listen_timeout
        self.phrase_time_limit = phrase_time_limit
        self.listening = False
        self.wake_word_mode = False

        # Speaker identification
        self.voice_encoder = None
        self.known_voices = {}  # name -> voice embedding
        self.voice_memory_path = None
        self.batdan_voice_threshold = 0.75  # Similarity threshold for BATDAN's voice

        # Noise filtering
        self.energy_threshold = 4000  # Adjust based on environment
        self.dynamic_energy_threshold = True

        # Check capabilities
        self._check_capabilities()

        # Initialize microphone (for Google Speech fallback)
        self._initialize_microphone()

    def _initialize_vosk(self):
        """Initialize VOSK offline speech recognition"""
        if not VOSK_AVAILABLE:
            self.logger.info("VOSK not installed. Install: pip install vosk sounddevice")
            return

        try:
            self.vosk_recognizer = create_vosk_recognizer(brain=self.brain)

            if self.vosk_recognizer.is_available():
                self.logger.info("VOSK offline speech recognition initialized (privacy-first)")
            else:
                self.logger.warning("VOSK installed but model not found. See vosk_recognizer.py for download instructions.")
        except Exception as e:
            self.logger.error(f"Failed to initialize VOSK: {e}")
            self.vosk_recognizer = None

    def use_vosk(self) -> bool:
        """Check if VOSK should be used for recognition"""
        return (
            self.prefer_offline and
            self.vosk_recognizer is not None and
            self.vosk_recognizer.is_available()
        )

    def _check_capabilities(self):
        """Check what audio capabilities are available"""
        # VOSK status
        if VOSK_AVAILABLE:
            if self.vosk_recognizer and self.vosk_recognizer.is_available():
                self.logger.info("✅ VOSK offline STT: Ready (privacy-first)")
            else:
                self.logger.warning("⚠️ VOSK installed but model not loaded. Download model for offline STT.")
        else:
            self.logger.info("ℹ️ VOSK not installed. Install: pip install vosk sounddevice")

        # Google Speech status
        if SPEECH_RECOGNITION_AVAILABLE:
            self.logger.info("✅ Google Speech Recognition: Available (online fallback)")
        else:
            self.logger.info("ℹ️ Google Speech not installed. Install: pip install SpeechRecognition pyaudio")

        if not AUDIO_ANALYSIS_AVAILABLE:
            self.logger.warning("⚠️ librosa not available. Install: pip install librosa soundfile")

        if not SPEAKER_RECOGNITION_AVAILABLE:
            self.logger.warning("⚠️ resemblyzer not available. Install: pip install resemblyzer")
            self.logger.info("💡 Speaker recognition will use basic audio fingerprinting instead")

    def _initialize_microphone(self):
        """Initialize the microphone with optimized settings (for Google Speech fallback)"""
        if not SPEECH_RECOGNITION_AVAILABLE or not self.recognizer:
            self.logger.debug("Skipping microphone init - using VOSK or no Google Speech")
            return

        try:
            self.microphone = sr.Microphone()

            # Adjust for ambient noise with multiple samples
            with self.microphone as source:
                self.logger.info("🎤 Calibrating for ambient noise (Google Speech fallback)...")
                self.recognizer.adjust_for_ambient_noise(source, duration=2)

                # Set energy threshold for better noise filtering
                if self.dynamic_energy_threshold:
                    self.recognizer.dynamic_energy_threshold = True
                else:
                    self.recognizer.energy_threshold = self.energy_threshold

            self.logger.info("✅ Google Speech microphone initialized")

        except Exception as e:
            self.logger.error(f"❌ Failed to initialize microphone: {e}")
            self.microphone = None

        # Initialize speaker recognition
        self._initialize_speaker_recognition()

        # Load known voices
        self._load_known_voices()

    def _initialize_speaker_recognition(self):
        """Initialize speaker recognition system"""
        if not SPEAKER_RECOGNITION_AVAILABLE:
            self.logger.info("📢 Using basic speaker recognition (install resemblyzer for advanced)")
            return

        try:
            self.voice_encoder = VoiceEncoder()
            self.logger.info("✅ Advanced speaker recognition initialized")
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize speaker recognition: {e}")
            self.voice_encoder = None

    def _load_known_voices(self):
        """Load known voice patterns from storage"""
        try:
            # Set voice memory path
            if self.brain:
                from core.path_manager import PathManager
                voice_dir = Path(PathManager.DATA_DIR) / "voices"
                voice_dir.mkdir(exist_ok=True)
                self.voice_memory_path = voice_dir
            else:
                self.voice_memory_path = Path("alfred_data/voices")
                self.voice_memory_path.mkdir(parents=True, exist_ok=True)

            # Load BATDAN's voice if it exists
            batdan_voice_path = self.voice_memory_path / "batdan_voice.pkl"
            if batdan_voice_path.exists():
                with open(batdan_voice_path, 'rb') as f:
                    self.known_voices['BATDAN'] = pickle.load(f)
                self.logger.info("✅ BATDAN's voice loaded from memory")
            else:
                self.logger.info("👤 BATDAN's voice not learned yet. Use /learn_voice to train Alfred")

            # Load other known voices
            for voice_file in self.voice_memory_path.glob("*_voice.pkl"):
                if voice_file.stem == 'batdan_voice':
                    continue  # Already loaded

                name = voice_file.stem.replace('_voice', '').upper()
                with open(voice_file, 'rb') as f:
                    self.known_voices[name] = pickle.load(f)
                self.logger.info(f"✅ {name}'s voice loaded from memory")

            if self.known_voices:
                self.logger.info(f"🎤 Alfred recognizes {len(self.known_voices)} voices")

        except Exception as e:
            self.logger.error(f"❌ Failed to load known voices: {e}")

    def learn_voice(self, name: str = "BATDAN", duration: int = 5) -> bool:
        """
        Learn BATDAN's voice pattern for speaker identification

        Args:
            name: Person's name (default: BATDAN)
            duration: Seconds to record voice sample

        Returns:
            True if voice learned successfully
        """
        if not self.microphone:
            self.logger.error("❌ No microphone available")
            return False

        try:
            self.logger.info(f"🎤 Learning {name}'s voice...")
            self.logger.info(f"📢 Please speak naturally for {duration} seconds...")

            with self.microphone as source:
                # Record audio sample
                audio = self.recognizer.listen(source, timeout=duration, phrase_time_limit=duration)

            # Convert to numpy array for analysis
            audio_data = np.frombuffer(audio.get_raw_data(), dtype=np.int16).astype(np.float32)
            audio_data = audio_data / 32768.0  # Normalize to [-1, 1]

            # Create voice embedding
            if self.voice_encoder and SPEAKER_RECOGNITION_AVAILABLE:
                # Advanced: Use deep learning voice encoder
                voice_embedding = self.voice_encoder.embed_utterance(audio_data)
            else:
                # Basic: Use audio features (MFCCs if librosa available)
                if AUDIO_ANALYSIS_AVAILABLE:
                    import librosa
                    mfcc = librosa.feature.mfcc(y=audio_data, sr=audio.sample_rate, n_mfcc=13)
                    voice_embedding = np.mean(mfcc, axis=1)  # Average MFCCs
                else:
                    # Fallback: Basic audio statistics
                    voice_embedding = np.array([
                        np.mean(audio_data),
                        np.std(audio_data),
                        np.max(audio_data),
                        np.min(audio_data)
                    ])

            # Store voice embedding
            name_key = name.upper()
            self.known_voices[name_key] = voice_embedding

            # Save to disk
            if self.voice_memory_path:
                voice_file = self.voice_memory_path / f"{name.lower()}_voice.pkl"
                with open(voice_file, 'wb') as f:
                    pickle.dump(voice_embedding, f)
                self.logger.info(f"💾 {name}'s voice saved to {voice_file}")

            # Store in AlfredBrain
            if self.brain:
                self.brain.store_knowledge(
                    category='people',
                    key=f'{name_key}_voice',
                    value=f'Voice learned on {datetime.now().isoformat()}',
                    importance=10,  # Max importance
                    confidence=1.0
                )

            self.logger.info(f"✅ Alfred now recognizes {name}'s voice")
            return True

        except Exception as e:
            self.logger.error(f"❌ Failed to learn voice: {e}")
            return False

    def identify_speaker(self, audio) -> Tuple[str, float]:
        """
        Identify who is speaking

        Args:
            audio: Audio data from speech_recognition

        Returns:
            (speaker_name, confidence)
        """
        if not self.known_voices:
            return ("Unknown", 0.0)

        try:
            # Convert audio to numpy array
            audio_data = np.frombuffer(audio.get_raw_data(), dtype=np.int16).astype(np.float32)
            audio_data = audio_data / 32768.0  # Normalize

            # Create embedding for current audio
            if self.voice_encoder and SPEAKER_RECOGNITION_AVAILABLE:
                current_embedding = self.voice_encoder.embed_utterance(audio_data)
            else:
                if AUDIO_ANALYSIS_AVAILABLE:
                    import librosa
                    mfcc = librosa.feature.mfcc(y=audio_data, sr=audio.sample_rate, n_mfcc=13)
                    current_embedding = np.mean(mfcc, axis=1)
                else:
                    current_embedding = np.array([
                        np.mean(audio_data),
                        np.std(audio_data),
                        np.max(audio_data),
                        np.min(audio_data)
                    ])

            # Compare with known voices
            best_match = None
            best_similarity = 0.0

            for name, known_embedding in self.known_voices.items():
                # Calculate cosine similarity
                similarity = np.dot(current_embedding, known_embedding) / (
                    np.linalg.norm(current_embedding) * np.linalg.norm(known_embedding)
                )

                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = name

            # Check if similarity exceeds threshold
            if best_match == 'BATDAN' and best_similarity >= self.batdan_voice_threshold:
                return (best_match, best_similarity)
            elif best_similarity >= 0.6:  # Lower threshold for other known people
                return (best_match, best_similarity)
            else:
                return ("Unknown", best_similarity)

        except Exception as e:
            self.logger.error(f"❌ Speaker identification error: {e}")
            return ("Unknown", 0.0)

    def listen_once(self, timeout: Optional[int] = None, identify_speaker: bool = True) -> Optional[Dict]:
        """
        Listen for a single command with speaker identification

        Uses VOSK (offline, privacy-first) as primary, Google Speech as fallback.

        Args:
            timeout: Override default timeout
            identify_speaker: If True, identify who is speaking

        Returns:
            Dict with 'text', 'speaker', 'confidence', 'engine' or None
        """
        timeout = timeout or self.listen_timeout

        # Try VOSK first (offline, privacy-first)
        if self.use_vosk():
            result = self._listen_vosk(timeout)
            if result:
                # Add speaker identification if available
                if identify_speaker:
                    result['speaker'] = "Unknown"
                    result['speaker_confidence'] = 0.0
                return result
            # VOSK failed, try fallback
            self.logger.debug("VOSK returned no result, trying Google Speech fallback...")

        # Fallback to Google Speech Recognition (online)
        if self.microphone and self.recognizer:
            return self._listen_google(timeout, identify_speaker)

        self.logger.error("No speech recognition available (VOSK or Google)")
        return None

    def _listen_vosk(self, timeout: float) -> Optional[Dict]:
        """Listen using VOSK offline recognition"""
        if not self.vosk_recognizer:
            return None

        try:
            self.logger.info("👂 Listening (VOSK offline)...")
            result = self.vosk_recognizer.listen_once(timeout=timeout)

            if result and result.get('text'):
                self.logger.info(f"✅ Heard (VOSK): '{result['text']}'")

                # Store in brain
                if self.brain:
                    self.brain.store_conversation(
                        user_input=result['text'],
                        alfred_response="[listening]",
                        success=True,
                        importance=5
                    )

                return {
                    'text': result['text'],
                    'confidence': result.get('confidence', 1.0),
                    'engine': 'vosk',
                    'words': result.get('words', []),
                    'wake_word_detected': result.get('wake_word_detected'),
                    'timestamp': datetime.now().isoformat()
                }

            return None

        except Exception as e:
            self.logger.error(f"VOSK listen error: {e}")
            return None

    def _listen_google(self, timeout: int, identify_speaker: bool) -> Optional[Dict]:
        """Listen using Google Speech Recognition (online fallback)"""
        if not self.microphone:
            self.logger.error("No microphone available for Google Speech")
            return None

        try:
            self.logger.info("👂 Listening (Google Speech - online)...")

            with self.microphone as source:
                # Listen
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=self.phrase_time_limit
                )

            # Identify speaker first
            speaker = "Unknown"
            speaker_confidence = 0.0

            if identify_speaker and self.known_voices:
                speaker, speaker_confidence = self.identify_speaker(audio)
                self.logger.info(f"🎤 Speaker: {speaker} (confidence: {speaker_confidence:.2f})")

            # Only process if speaker is BATDAN or unknown (to allow initial training)
            if speaker != "BATDAN" and speaker != "Unknown" and self.known_voices.get('BATDAN'):
                self.logger.info(f"🚫 Ignoring speech from {speaker} (not BATDAN)")
                return None

            # Recognize speech
            self.logger.info("🔄 Processing speech (Google)...")
            text = self.recognizer.recognize_google(audio)

            self.logger.info(f"✅ Heard (Google): '{text}'")

            # Store in brain if from BATDAN
            if speaker == "BATDAN" and self.brain:
                self.brain.store_conversation(
                    user_input=text,
                    alfred_response="[listening]",
                    success=True,
                    importance=7
                )

            return {
                'text': text,
                'speaker': speaker,
                'speaker_confidence': speaker_confidence,
                'confidence': 1.0,  # Google doesn't provide confidence
                'engine': 'google',
                'timestamp': datetime.now().isoformat()
            }

        except sr.WaitTimeoutError:
            self.logger.debug("Listening timeout (no speech detected)")
            return None

        except sr.UnknownValueError:
            self.logger.debug("Could not understand audio")
            return None

        except sr.RequestError as e:
            self.logger.error(f"Google Speech request error: {e}")
            return None

        except Exception as e:
            self.logger.error(f"Listening error: {e}")
            return None

    def listen_for_batdan(self, callback: Callable[[str], None],
                         stop_phrase: str = "stop listening"):
        """
        Listen continuously but ONLY respond to BATDAN's voice

        Args:
            callback: Function to call with recognized text (only for BATDAN)
            stop_phrase: Phrase to stop listening
        """
        if not self.microphone:
            self.logger.error("❌ No microphone available")
            return

        if 'BATDAN' not in self.known_voices:
            self.logger.error("❌ BATDAN's voice not learned. Use /learn_voice first")
            return

        self.listening = True
        self.logger.info("👂 Listening for BATDAN only (others ignored)")
        self.logger.info(f"💡 Say '{stop_phrase}' to stop")

        try:
            while self.listening:
                result = self.listen_once(identify_speaker=True)

                if result and result['speaker'] == 'BATDAN':
                    text = result['text']

                    # Check for stop phrase
                    if stop_phrase.lower() in text.lower():
                        self.logger.info("🛑 Stop phrase detected")
                        break

                    # Call callback with BATDAN's command
                    callback(text)

        except KeyboardInterrupt:
            self.logger.info("🛑 Listening interrupted by user")

        finally:
            self.listening = False
            self.logger.info("👂 Stopped listening for BATDAN")

    def listen_for_wake_word(self, callback: Callable[[str], None]):
        """
        Listen for wake word from BATDAN only, then process command

        Args:
            callback: Function to call when BATDAN says wake word + command
        """
        if not self.microphone:
            self.logger.error("❌ No microphone available")
            return

        self.wake_word_mode = True
        self.logger.info(f"👂 Listening for wake word from BATDAN: {self.WAKE_WORDS}")

        try:
            while self.wake_word_mode:
                result = self.listen_once(timeout=None, identify_speaker=True)

                if result:
                    # Only respond to BATDAN (or Unknown during initial setup)
                    if result['speaker'] == 'BATDAN' or (result['speaker'] == 'Unknown' and 'BATDAN' not in self.known_voices):
                        text = result['text']
                        text_lower = text.lower()

                        # Check for wake word
                        if any(wake_word in text_lower for wake_word in self.WAKE_WORDS):
                            self.logger.info(f"✅ Wake word detected from BATDAN: '{text}'")

                            # Remove wake word from text
                            for wake_word in self.WAKE_WORDS:
                                text = text_lower.replace(wake_word, '').strip()

                            # If there's a command after the wake word, process it
                            if text:
                                callback(text)
                            else:
                                # Just wake word, listen for command
                                command_result = self.listen_once(identify_speaker=True)
                                if command_result and command_result['speaker'] == 'BATDAN':
                                    callback(command_result['text'])

        except KeyboardInterrupt:
            self.logger.info("🛑 Wake word listening interrupted")

        finally:
            self.wake_word_mode = False
            self.logger.info("👂 Wake word listening stopped")

    def is_batdan_speaking(self) -> Optional[bool]:
        """
        Quick check: Is BATDAN currently speaking?

        Returns:
            True if BATDAN is speaking, False if someone else, None if no speech
        """
        result = self.listen_once(timeout=1, identify_speaker=True)

        if result:
            return result['speaker'] == 'BATDAN'
        return None

    def stop_listening(self):
        """Stop all listening modes"""
        self.listening = False
        self.wake_word_mode = False
        self.logger.info("🛑 Listening stopped")

    def get_available_microphones(self) -> list:
        """Get list of available microphones"""
        if not SPEECH_RECOGNITION_AVAILABLE:
            return []

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
        """Get listening status with STT engine info"""
        vosk_status = "Not installed"
        if VOSK_AVAILABLE:
            if self.vosk_recognizer and self.vosk_recognizer.is_available():
                vosk_status = "Ready (primary)"
            else:
                vosk_status = "Installed, model not loaded"

        google_status = "Not installed"
        if SPEECH_RECOGNITION_AVAILABLE:
            if self.microphone:
                google_status = "Ready (fallback)"
            else:
                google_status = "Installed, no microphone"

        return {
            'listening': self.listening,
            'wake_word_mode': self.wake_word_mode,
            'prefer_offline': self.prefer_offline,
            # STT Engines
            'stt_engines': {
                'vosk': vosk_status,
                'google': google_status,
                'active': 'vosk' if self.use_vosk() else ('google' if self.microphone else 'none')
            },
            # Legacy fields
            'microphone': 'Available' if self.microphone else 'Not available',
            'speaker_recognition': SPEAKER_RECOGNITION_AVAILABLE,
            'known_voices': list(self.known_voices.keys()),
            'batdan_voice_learned': 'BATDAN' in self.known_voices,
            'timeout': self.listen_timeout,
            'phrase_limit': self.phrase_time_limit
        }

    def download_vosk_model(self, size: str = "small") -> bool:
        """
        Download VOSK model for offline speech recognition

        Args:
            size: "small" (~50MB), "medium" (~500MB), or "large" (~1.8GB)

        Returns:
            True if download successful
        """
        if not VOSK_AVAILABLE:
            self.logger.error("VOSK not installed. Run: pip install vosk sounddevice")
            return False

        if not self.vosk_recognizer:
            self._initialize_vosk()

        if self.vosk_recognizer:
            from capabilities.voice.vosk_recognizer import VoskModelSize
            size_map = {
                "small": VoskModelSize.SMALL,
                "medium": VoskModelSize.MEDIUM,
                "large": VoskModelSize.LARGE
            }
            return self.vosk_recognizer.download_model(size_map.get(size, VoskModelSize.SMALL))

        return False

    def set_offline_mode(self, enabled: bool = True):
        """
        Enable/disable offline-first mode

        Args:
            enabled: If True, prefer VOSK offline recognition
        """
        self.prefer_offline = enabled
        if enabled:
            self.logger.info("Offline mode enabled - using VOSK (privacy-first)")
        else:
            self.logger.info("Online mode enabled - using Google Speech")


# Convenience function
def create_alfred_ears_advanced(brain=None, prefer_offline: bool = True) -> AlfredEarsAdvanced:
    """
    Create Alfred's advanced listening system

    Args:
        brain: AlfredBrain instance for memory integration
        prefer_offline: If True, prefer VOSK offline recognition (privacy-first)

    Returns:
        AlfredEarsAdvanced instance
    """
    return AlfredEarsAdvanced(brain=brain, prefer_offline=prefer_offline)
