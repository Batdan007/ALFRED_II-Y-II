"""
ALFRED Voice - Unified Module
==============================
Single file containing everything needed for voice.
No external dependencies on other voice modules.

Components:
- WhisperSTT: Speech-to-text (faster-whisper, GPU)
- EdgeTTS: Text-to-speech (edge-tts, British voice)
- VoiceInterface: Combined STT + TTS

Usage:
    from capabilities.voice.alfred_voice_unified import VoiceInterface
    voice = VoiceInterface()
    voice.speak("Hello, Master Batdan")
    text = voice.listen()

Author: Daniel J Rita (BATDAN)
"""

import os
import sys
import asyncio
import tempfile
import subprocess
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass

import numpy as np
import sounddevice as sd

# ============================================================
# Configuration
# ============================================================

@dataclass
class VoiceConfig:
    """Voice system configuration"""
    # Whisper
    whisper_model: str = "base.en"
    whisper_device: str = "cuda"

    # TTS
    tts_voice: str = "en-GB-RyanNeural"  # British male
    tts_rate: str = "+0%"

    # Audio
    sample_rate: int = 16000
    silence_threshold: float = 500
    silence_duration: float = 1.5
    max_record_duration: float = 30


# ============================================================
# Speech-to-Text (Whisper)
# ============================================================

class WhisperSTT:
    """High-quality speech recognition using faster-whisper"""

    def __init__(self, config: VoiceConfig):
        self.config = config
        self.model = None
        self.device = config.whisper_device
        self.logger = logging.getLogger(__name__)
        self._load_model()

    def _load_model(self):
        """Load Whisper model"""
        try:
            from faster_whisper import WhisperModel

            # Try GPU
            try:
                self.model = WhisperModel(
                    self.config.whisper_model,
                    device="cuda",
                    compute_type="float16"
                )
                self.device = "cuda"
            except:
                # Fall back to CPU
                self.model = WhisperModel(
                    self.config.whisper_model,
                    device="cpu",
                    compute_type="float32"
                )
                self.device = "cpu"

            self.logger.info(f"Whisper loaded on {self.device.upper()}")

        except ImportError:
            self.logger.debug("faster-whisper not installed")
        except Exception as e:
            self.logger.error(f"Failed to load Whisper: {e}")

    @property
    def available(self) -> bool:
        return self.model is not None

    def record(self) -> Optional[np.ndarray]:
        """Record audio until silence"""
        recording = []
        silent_chunks = 0
        chunk_duration = 0.1
        chunks_for_silence = int(self.config.silence_duration / chunk_duration)
        max_chunks = int(self.config.max_record_duration / chunk_duration)

        def callback(indata, frames, time, status):
            recording.append(indata.copy())

        try:
            with sd.InputStream(
                samplerate=self.config.sample_rate,
                channels=1,
                callback=callback,
                blocksize=int(self.config.sample_rate * chunk_duration)
            ):
                for _ in range(max_chunks):
                    sd.sleep(int(chunk_duration * 1000))

                    if recording:
                        volume = np.abs(recording[-1]).mean() * 32768
                        if volume < self.config.silence_threshold:
                            silent_chunks += 1
                        else:
                            silent_chunks = 0

                        if silent_chunks >= chunks_for_silence and len(recording) > 10:
                            break

        except Exception as e:
            self.logger.error(f"Recording error: {e}")
            return None

        if not recording:
            return None

        return np.concatenate(recording, axis=0).flatten()

    def transcribe(self, audio: np.ndarray) -> str:
        """Transcribe audio to text"""
        if not self.available:
            return ""

        try:
            segments, _ = self.model.transcribe(
                audio,
                language="en",
                beam_size=5,
                vad_filter=True
            )
            return " ".join(s.text.strip() for s in segments)

        except Exception as e:
            self.logger.error(f"Transcription error: {e}")
            return ""

    def listen(self) -> str:
        """Record and transcribe"""
        audio = self.record()
        if audio is None or len(audio) < self.config.sample_rate * 0.5:
            return ""
        return self.transcribe(audio)


# ============================================================
# Text-to-Speech (Edge TTS)
# ============================================================

class EdgeTTS:
    """Natural TTS using Microsoft Edge voices"""

    VOICES = {
        'ryan': 'en-GB-RyanNeural',
        'sonia': 'en-GB-SoniaNeural',
        'thomas': 'en-GB-ThomasNeural',
    }

    def __init__(self, config: VoiceConfig):
        self.config = config
        self.voice = config.tts_voice
        self.rate = config.tts_rate
        self.logger = logging.getLogger(__name__)
        self._available = self._check_available()

    def _check_available(self) -> bool:
        """Check if edge-tts and ffmpeg are available"""
        try:
            import edge_tts
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
            return True
        except:
            return False

    @property
    def available(self) -> bool:
        return self._available

    async def _generate(self, text: str) -> Optional[str]:
        """Generate audio file"""
        import edge_tts

        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            temp_mp3 = f.name

        try:
            comm = edge_tts.Communicate(text, voice=self.voice, rate=self.rate)
            await comm.save(temp_mp3)
            return temp_mp3
        except Exception as e:
            self.logger.error(f"TTS error: {e}")
            if os.path.exists(temp_mp3):
                os.unlink(temp_mp3)
            return None

    def _convert_and_play(self, mp3_path: str):
        """Convert to WAV and play"""
        wav_path = mp3_path.replace(".mp3", ".wav")

        try:
            # Convert
            subprocess.run(
                ['ffmpeg', '-y', '-i', mp3_path, '-ar', '22050', '-ac', '1', wav_path],
                capture_output=True,
                timeout=30
            )

            # Play
            import wave
            with wave.open(wav_path, 'rb') as wf:
                data = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16)
                sd.play(data.astype(np.float32) / 32768.0, 22050)
                sd.wait()

        finally:
            # Cleanup
            for f in [mp3_path, wav_path]:
                try:
                    if os.path.exists(f):
                        os.unlink(f)
                except:
                    pass

    def speak(self, text: str):
        """Speak text aloud"""
        if not self.available:
            self.logger.warning("TTS not available")
            return

        try:
            mp3_path = asyncio.run(self._generate(text))
            if mp3_path:
                self._convert_and_play(mp3_path)
        except Exception as e:
            self.logger.error(f"Speak error: {e}")


# ============================================================
# Unified Voice Interface
# ============================================================

class VoiceInterface:
    """
    Combined STT + TTS interface for ALFRED

    Usage:
        voice = VoiceInterface()
        voice.speak("Hello")
        text = voice.listen()
    """

    def __init__(self, config: VoiceConfig = None):
        self.config = config or VoiceConfig()
        self.logger = logging.getLogger(__name__)

        # Initialize components
        self.stt = WhisperSTT(self.config)
        self.tts = EdgeTTS(self.config)

    @property
    def stt_available(self) -> bool:
        return self.stt.available

    @property
    def tts_available(self) -> bool:
        return self.tts.available

    def listen(self) -> str:
        """Listen for speech and return text"""
        return self.stt.listen()

    def speak(self, text: str):
        """Speak text aloud"""
        self.tts.speak(text)

    def greet(self):
        """ALFRED's greeting"""
        self.speak("Good day, Master Batdan. How may I be of service?")

    def farewell(self):
        """ALFRED's farewell"""
        self.speak("Very good, sir. I shall be here if you need me.")

    def confirm(self, action: str = None):
        """Confirm an action"""
        if action:
            self.speak(f"Very good, sir. {action}")
        else:
            self.speak("Very good, sir.")

    def get_status(self) -> Dict[str, Any]:
        """Get voice system status"""
        return {
            'stt': {
                'available': self.stt_available,
                'engine': 'whisper',
                'model': self.config.whisper_model,
                'device': self.stt.device if self.stt_available else None
            },
            'tts': {
                'available': self.tts_available,
                'engine': 'edge-tts',
                'voice': self.config.tts_voice
            }
        }


# ============================================================
# Factory Functions
# ============================================================

def create_voice_interface(
    whisper_model: str = "base.en",
    tts_voice: str = "ryan"
) -> VoiceInterface:
    """
    Create a voice interface

    Args:
        whisper_model: tiny.en, base.en, small.en, medium.en
        tts_voice: ryan, sonia, thomas (British voices)
    """
    # Map short voice names
    voice_map = {
        'ryan': 'en-GB-RyanNeural',
        'sonia': 'en-GB-SoniaNeural',
        'thomas': 'en-GB-ThomasNeural',
    }

    config = VoiceConfig(
        whisper_model=whisper_model,
        tts_voice=voice_map.get(tts_voice, tts_voice)
    )

    return VoiceInterface(config)


# ============================================================
# CLI Test
# ============================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("ALFRED Voice - Unified Module Test")
    print("=" * 40)

    voice = create_voice_interface()
    status = voice.get_status()

    print(f"\nSTT: {status['stt']}")
    print(f"TTS: {status['tts']}")

    if voice.tts_available:
        print("\nTesting TTS...")
        voice.greet()

    if voice.stt_available:
        print("\nTesting STT (speak now)...")
        text = voice.listen()
        print(f"You said: {text}")
