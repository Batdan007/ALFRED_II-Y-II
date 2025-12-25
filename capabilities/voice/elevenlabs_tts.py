"""
ElevenLabs Premium Text-to-Speech for Alfred
High-quality, natural-sounding British butler voice

Features:
- Premium quality AI voices
- Streaming support for low latency
- Voice cloning capability
- Multiple voice options (British male voices)
- Fallback to local TTS when API unavailable

Author: Daniel J Rita (BATDAN)
"""

import logging
import os
import tempfile
import threading
from pathlib import Path
from typing import Optional, Callable
from dataclasses import dataclass
from enum import Enum

# Graceful degradation
try:
    from elevenlabs import ElevenLabs, Voice, VoiceSettings
    from elevenlabs.client import ElevenLabs as ElevenLabsClient
    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False
    ElevenLabs = None

# Audio playback
try:
    import sounddevice as sd
    import soundfile as sf
    AUDIO_PLAYBACK_AVAILABLE = True
except ImportError:
    AUDIO_PLAYBACK_AVAILABLE = False

try:
    from pydub import AudioSegment
    from pydub.playback import play as pydub_play
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False


class ElevenLabsVoice(Enum):
    """Pre-configured ElevenLabs voices suitable for Alfred"""
    # British male voices (Alfred-like)
    DANIEL = "Daniel"           # British, mature, professional
    JAMES = "James"             # British, distinguished
    CHARLIE = "Charlie"         # British, warm
    GEORGE = "George"           # British, authoritative
    CLYDE = "Clyde"             # British, butler-like
    ETHAN = "Ethan"             # British, calm

    # Custom voice IDs (if you've cloned a voice)
    CUSTOM = "custom"


@dataclass
class ElevenLabsConfig:
    """Configuration for ElevenLabs TTS"""
    api_key: Optional[str] = None
    voice_id: Optional[str] = None
    voice_name: str = "Daniel"  # Default to Daniel (British male)
    model_id: str = "eleven_monolingual_v1"  # Fast model
    stability: float = 0.5
    similarity_boost: float = 0.75
    style: float = 0.0
    use_speaker_boost: bool = True

    # Streaming settings
    enable_streaming: bool = True
    output_format: str = "mp3_44100_128"

    # Cache settings
    cache_audio: bool = True
    cache_dir: Optional[str] = None


class ElevenLabsTTS:
    """
    ElevenLabs premium text-to-speech

    Provides high-quality, natural-sounding voices for Alfred.
    Requires API key from https://elevenlabs.io
    """

    # Voice ID mapping for well-known voices
    VOICE_IDS = {
        "Daniel": "CYw3kZ02Hs0563khs1Fj",
        "James": "ZQe5CZNOzWyzPSCn5a3c",
        "Charlie": "IKne3meq5aSn9XLyUdCD",
        "George": "JBFqnCBsd6RMkjVDRZzb",
        "Clyde": "2EiwWnXFnvU5JabPnv8n",
        "Ethan": "g5CIjZEefAph4nQFvHAz",
    }

    def __init__(self, config: Optional[ElevenLabsConfig] = None, privacy_controller=None):
        """
        Initialize ElevenLabs TTS

        Args:
            config: ElevenLabsConfig with settings
            privacy_controller: PrivacyController for cloud access approval
        """
        self.logger = logging.getLogger(__name__)
        self.config = config or ElevenLabsConfig()
        self.privacy_controller = privacy_controller

        self.client = None
        self.speaking = False
        self.enabled = True

        # Cache for audio files
        self.cache_dir = None
        self.audio_cache = {}

        # Check availability
        if not self._check_dependencies():
            return

        # Initialize client
        self._initialize_client()

        # Setup cache
        self._setup_cache()

    def _check_dependencies(self) -> bool:
        """Check if all required dependencies are available"""
        if not ELEVENLABS_AVAILABLE:
            self.logger.warning(
                "ElevenLabs not installed. Install: pip install elevenlabs"
            )
            return False

        if not AUDIO_PLAYBACK_AVAILABLE and not PYDUB_AVAILABLE:
            self.logger.warning(
                "No audio playback available. Install: pip install sounddevice soundfile pydub"
            )
            return False

        return True

    def _initialize_client(self):
        """Initialize ElevenLabs client"""
        # Get API key from config or environment
        api_key = self.config.api_key or os.environ.get("ELEVENLABS_API_KEY")

        if not api_key:
            self.logger.warning(
                "ElevenLabs API key not found. Set ELEVENLABS_API_KEY environment variable "
                "or pass api_key in config."
            )
            return

        try:
            self.client = ElevenLabsClient(api_key=api_key)
            self.logger.info("ElevenLabs TTS initialized")

            # Verify API key by listing voices
            try:
                voices = self.client.voices.get_all()
                self.logger.info(f"ElevenLabs connected. {len(voices.voices)} voices available.")
            except Exception as e:
                self.logger.warning(f"Could not verify ElevenLabs API key: {e}")

        except Exception as e:
            self.logger.error(f"Failed to initialize ElevenLabs: {e}")
            self.client = None

    def _setup_cache(self):
        """Setup audio cache directory"""
        if not self.config.cache_audio:
            return

        if self.config.cache_dir:
            self.cache_dir = Path(self.config.cache_dir)
        else:
            try:
                from core.path_manager import PathManager
                self.cache_dir = Path(PathManager.CACHE_DIR) / "elevenlabs"
            except ImportError:
                self.cache_dir = Path(tempfile.gettempdir()) / "alfred_elevenlabs"

        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.logger.debug(f"ElevenLabs cache: {self.cache_dir}")

    def is_available(self) -> bool:
        """Check if ElevenLabs is ready to use"""
        return self.client is not None

    def _check_privacy_approval(self) -> bool:
        """Check if cloud TTS is approved (privacy mode)"""
        if not self.privacy_controller:
            return True  # No controller, allow by default

        try:
            from core.privacy_controller import PrivacyMode, CloudProvider

            # In LOCAL mode, don't use cloud TTS
            if self.privacy_controller.mode == PrivacyMode.LOCAL:
                self.logger.debug("Privacy mode is LOCAL - ElevenLabs disabled")
                return False

            # In HYBRID/CLOUD mode, check if cloud is approved
            return self.privacy_controller.is_cloud_approved(CloudProvider.OPENAI)  # Use generic cloud check

        except ImportError:
            return True  # No privacy controller available

    def get_voice_id(self) -> str:
        """Get the voice ID to use"""
        # Custom voice ID takes priority
        if self.config.voice_id:
            return self.config.voice_id

        # Look up voice by name
        return self.VOICE_IDS.get(self.config.voice_name, self.VOICE_IDS["Daniel"])

    def speak(self, text: str, blocking: bool = True) -> bool:
        """
        Speak text using ElevenLabs

        Args:
            text: Text to speak
            blocking: If True, wait for speech to complete

        Returns:
            True if speech successful
        """
        if not self.is_available():
            self.logger.warning("ElevenLabs not available")
            return False

        if not self._check_privacy_approval():
            self.logger.debug("ElevenLabs blocked by privacy mode")
            return False

        if not text or not text.strip():
            return False

        self.speaking = True

        try:
            # Check cache first
            cache_key = self._get_cache_key(text)
            cached_path = self._get_cached_audio(cache_key)

            if cached_path:
                self.logger.debug(f"Playing cached audio: {cached_path}")
                return self._play_audio(cached_path, blocking)

            # Generate new audio
            self.logger.info(f"ElevenLabs TTS: {text[:50]}...")

            audio = self.client.generate(
                text=text,
                voice=self.get_voice_id(),
                model=self.config.model_id,
                voice_settings=VoiceSettings(
                    stability=self.config.stability,
                    similarity_boost=self.config.similarity_boost,
                    style=self.config.style,
                    use_speaker_boost=self.config.use_speaker_boost
                ) if hasattr(VoiceSettings, 'style') else VoiceSettings(
                    stability=self.config.stability,
                    similarity_boost=self.config.similarity_boost
                )
            )

            # Save to temp file
            audio_path = self._save_audio(audio, cache_key)

            # Play audio
            return self._play_audio(audio_path, blocking)

        except Exception as e:
            self.logger.error(f"ElevenLabs speak error: {e}")
            return False

        finally:
            self.speaking = False

    def speak_stream(self, text: str, on_chunk: Optional[Callable[[bytes], None]] = None) -> bool:
        """
        Stream audio for lower latency

        Args:
            text: Text to speak
            on_chunk: Callback for each audio chunk

        Returns:
            True if streaming successful
        """
        if not self.is_available():
            return False

        if not self._check_privacy_approval():
            return False

        if not self.config.enable_streaming:
            return self.speak(text)

        self.speaking = True

        try:
            self.logger.info(f"ElevenLabs streaming: {text[:50]}...")

            # Use streaming API
            audio_stream = self.client.generate(
                text=text,
                voice=self.get_voice_id(),
                model=self.config.model_id,
                stream=True,
                output_format=self.config.output_format
            )

            # Collect chunks and play
            audio_data = b""
            for chunk in audio_stream:
                audio_data += chunk
                if on_chunk:
                    on_chunk(chunk)

            # Save and play complete audio
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                f.write(audio_data)
                audio_path = f.name

            return self._play_audio(audio_path, blocking=True)

        except Exception as e:
            self.logger.error(f"ElevenLabs streaming error: {e}")
            return False

        finally:
            self.speaking = False

    def _get_cache_key(self, text: str) -> str:
        """Generate cache key for text"""
        import hashlib
        voice_id = self.get_voice_id()
        return hashlib.md5(f"{voice_id}:{text}".encode()).hexdigest()

    def _get_cached_audio(self, cache_key: str) -> Optional[Path]:
        """Get cached audio file if exists"""
        if not self.config.cache_audio or not self.cache_dir:
            return None

        cache_path = self.cache_dir / f"{cache_key}.mp3"
        if cache_path.exists():
            return cache_path

        return None

    def _save_audio(self, audio, cache_key: str) -> Path:
        """Save audio to cache"""
        if self.config.cache_audio and self.cache_dir:
            audio_path = self.cache_dir / f"{cache_key}.mp3"
        else:
            audio_path = Path(tempfile.gettempdir()) / f"alfred_{cache_key}.mp3"

        # Handle generator or bytes
        if hasattr(audio, '__iter__') and not isinstance(audio, bytes):
            audio_data = b"".join(audio)
        else:
            audio_data = audio

        with open(audio_path, 'wb') as f:
            f.write(audio_data)

        return audio_path

    def _play_audio(self, audio_path: Path, blocking: bool = True) -> bool:
        """Play audio file"""
        try:
            if AUDIO_PLAYBACK_AVAILABLE:
                return self._play_with_sounddevice(audio_path, blocking)
            elif PYDUB_AVAILABLE:
                return self._play_with_pydub(audio_path, blocking)
            else:
                self.logger.error("No audio playback method available")
                return False

        except Exception as e:
            self.logger.error(f"Audio playback error: {e}")
            return False

    def _play_with_sounddevice(self, audio_path: Path, blocking: bool) -> bool:
        """Play using sounddevice"""
        try:
            data, samplerate = sf.read(str(audio_path))
            if blocking:
                sd.play(data, samplerate)
                sd.wait()
            else:
                sd.play(data, samplerate)
            return True
        except Exception as e:
            self.logger.error(f"sounddevice playback error: {e}")
            return False

    def _play_with_pydub(self, audio_path: Path, blocking: bool) -> bool:
        """Play using pydub"""
        try:
            audio = AudioSegment.from_mp3(str(audio_path))
            if blocking:
                pydub_play(audio)
            else:
                # Non-blocking with pydub
                thread = threading.Thread(target=pydub_play, args=(audio,))
                thread.daemon = True
                thread.start()
            return True
        except Exception as e:
            self.logger.error(f"pydub playback error: {e}")
            return False

    def stop_speaking(self):
        """Stop current speech"""
        self.speaking = False
        if AUDIO_PLAYBACK_AVAILABLE:
            try:
                sd.stop()
            except:
                pass

    def list_voices(self) -> list:
        """List available ElevenLabs voices"""
        if not self.client:
            return list(self.VOICE_IDS.keys())

        try:
            response = self.client.voices.get_all()
            return [
                {
                    'name': v.name,
                    'voice_id': v.voice_id,
                    'labels': v.labels
                }
                for v in response.voices
            ]
        except Exception as e:
            self.logger.error(f"Failed to list voices: {e}")
            return list(self.VOICE_IDS.keys())

    def set_voice(self, voice_name: str = None, voice_id: str = None):
        """Set voice by name or ID"""
        if voice_id:
            self.config.voice_id = voice_id
        elif voice_name:
            self.config.voice_name = voice_name
            self.config.voice_id = None

        self.logger.info(f"Voice set to: {voice_name or voice_id}")

    def get_status(self) -> dict:
        """Get TTS status"""
        return {
            'available': self.is_available(),
            'elevenlabs_installed': ELEVENLABS_AVAILABLE,
            'api_key_set': bool(self.config.api_key or os.environ.get("ELEVENLABS_API_KEY")),
            'client_initialized': self.client is not None,
            'speaking': self.speaking,
            'voice': self.config.voice_name,
            'voice_id': self.get_voice_id(),
            'streaming_enabled': self.config.enable_streaming,
            'cache_enabled': self.config.cache_audio,
            'audio_playback': 'sounddevice' if AUDIO_PLAYBACK_AVAILABLE else ('pydub' if PYDUB_AVAILABLE else 'none')
        }

    def clear_cache(self):
        """Clear audio cache"""
        if not self.cache_dir:
            return

        try:
            for f in self.cache_dir.glob("*.mp3"):
                f.unlink()
            self.logger.info("ElevenLabs cache cleared")
        except Exception as e:
            self.logger.error(f"Failed to clear cache: {e}")


def create_elevenlabs_tts(
    api_key: Optional[str] = None,
    voice: str = "Daniel",
    privacy_controller=None
) -> ElevenLabsTTS:
    """
    Factory function to create ElevenLabs TTS

    Args:
        api_key: ElevenLabs API key (or set ELEVENLABS_API_KEY env var)
        voice: Voice name ("Daniel", "James", "Charlie", etc.)
        privacy_controller: PrivacyController for cloud access approval

    Returns:
        ElevenLabsTTS instance
    """
    config = ElevenLabsConfig(
        api_key=api_key,
        voice_name=voice
    )
    return ElevenLabsTTS(config=config, privacy_controller=privacy_controller)


# CLI test
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("ElevenLabs TTS Test")
    print("="*40)

    tts = create_elevenlabs_tts()
    status = tts.get_status()

    print(f"\nStatus:")
    for key, value in status.items():
        print(f"  {key}: {value}")

    if tts.is_available():
        print("\nSpeaking test phrase...")
        tts.speak("Good evening, sir. The Batcomputer is online and ready for your command.")
    else:
        print("\nElevenLabs not available. Set ELEVENLABS_API_KEY environment variable.")
