"""
Edge TTS Voice for ALFRED
=========================
Natural British voice using Microsoft Edge TTS.
Free, no API key needed, sounds way better than pyttsx3.

Author: Daniel J Rita (BATDAN)
"""

import os
import asyncio
import tempfile
import subprocess
import logging
from typing import Optional
from pathlib import Path

import numpy as np
import sounddevice as sd

try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False


class EdgeTTSVoice:
    """
    Natural TTS using Microsoft Edge voices.
    Free, high quality, British voices available.
    """

    # British voice options
    VOICES = {
        'ryan': 'en-GB-RyanNeural',      # British male (recommended for Alfred)
        'sonia': 'en-GB-SoniaNeural',    # British female
        'thomas': 'en-GB-ThomasNeural',  # British male (older)
        'libby': 'en-GB-LibbyNeural',    # British female
        'mia': 'en-GB-MiaNeural',        # British female (child)
    }

    DEFAULT_VOICE = 'ryan'  # en-GB-RyanNeural - perfect for Alfred

    def __init__(self, voice: str = None, rate: str = "+0%"):
        """
        Initialize Edge TTS

        Args:
            voice: Voice name (ryan, sonia, thomas) or full voice ID
            rate: Speech rate (-50% to +50%)
        """
        self.logger = logging.getLogger(__name__)

        # Set voice
        if voice in self.VOICES:
            self.voice = self.VOICES[voice]
        elif voice and voice.startswith('en-'):
            self.voice = voice
        else:
            self.voice = self.VOICES[self.DEFAULT_VOICE]

        self.rate = rate
        self.speaking = False

        # Check ffmpeg
        self.ffmpeg_available = self._check_ffmpeg()

        if not EDGE_TTS_AVAILABLE:
            self.logger.error("edge-tts not installed. Run: pip install edge-tts")

        self.logger.info(f"Edge TTS initialized with voice: {self.voice}")

    def _check_ffmpeg(self) -> bool:
        """Check if ffmpeg is available"""
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True)
            return True
        except:
            self.logger.warning("ffmpeg not found - TTS may not work")
            return False

    @property
    def available(self) -> bool:
        """Check if TTS is available"""
        return EDGE_TTS_AVAILABLE and self.ffmpeg_available

    async def _generate_audio(self, text: str) -> Optional[str]:
        """Generate audio file from text"""
        if not EDGE_TTS_AVAILABLE:
            return None

        # Create temp file
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            temp_mp3 = f.name

        try:
            communicate = edge_tts.Communicate(
                text,
                voice=self.voice,
                rate=self.rate
            )
            await communicate.save(temp_mp3)
            return temp_mp3

        except Exception as e:
            self.logger.error(f"TTS generation error: {e}")
            if os.path.exists(temp_mp3):
                os.unlink(temp_mp3)
            return None

    def _convert_to_wav(self, mp3_path: str) -> Optional[str]:
        """Convert MP3 to WAV for playback"""
        wav_path = mp3_path.replace(".mp3", ".wav")

        try:
            result = subprocess.run(
                ['ffmpeg', '-y', '-i', mp3_path, '-ar', '22050', '-ac', '1', wav_path],
                capture_output=True,
                timeout=30
            )
            if result.returncode == 0:
                return wav_path
        except Exception as e:
            self.logger.error(f"ffmpeg conversion error: {e}")

        return None

    def _play_audio(self, wav_path: str):
        """Play WAV file through speakers"""
        try:
            import wave
            with wave.open(wav_path, 'rb') as wf:
                data = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16)
                sample_rate = wf.getframerate()

            sd.play(data.astype(np.float32) / 32768.0, sample_rate)
            sd.wait()

        except Exception as e:
            self.logger.error(f"Audio playback error: {e}")

    def speak(self, text: str):
        """
        Speak text aloud

        Args:
            text: Text to speak
        """
        if not self.available:
            self.logger.warning("TTS not available")
            print(f"[ALFRED would say]: {text}")
            return

        self.speaking = True
        temp_files = []

        try:
            # Generate audio
            mp3_path = asyncio.run(self._generate_audio(text))
            if not mp3_path:
                return
            temp_files.append(mp3_path)

            # Convert to WAV
            wav_path = self._convert_to_wav(mp3_path)
            if not wav_path:
                return
            temp_files.append(wav_path)

            # Play
            self._play_audio(wav_path)

        finally:
            # Cleanup temp files
            for f in temp_files:
                try:
                    if os.path.exists(f):
                        os.unlink(f)
                except:
                    pass
            self.speaking = False

    def greet(self):
        """Alfred's greeting"""
        self.speak("Good day, Master Batdan. How may I be of service?")

    def confirm(self, action: str = None):
        """Confirm an action"""
        if action:
            self.speak(f"Very good, sir. {action}")
        else:
            self.speak("Very good, sir.")

    def farewell(self):
        """Alfred's farewell"""
        self.speak("Very good, sir. I shall be here if you need me.")

    def error(self, message: str):
        """Report an error"""
        self.speak(f"I apologize, sir, but {message}")

    def set_voice(self, voice: str):
        """Change voice"""
        if voice in self.VOICES:
            self.voice = self.VOICES[voice]
        elif voice.startswith('en-'):
            self.voice = voice
        self.logger.info(f"Voice changed to: {self.voice}")

    def set_rate(self, rate: str):
        """Change speech rate (e.g., '+10%', '-20%')"""
        self.rate = rate

    def get_status(self) -> dict:
        """Get TTS status"""
        return {
            'available': self.available,
            'engine': 'edge-tts',
            'voice': self.voice,
            'rate': self.rate,
            'ffmpeg': self.ffmpeg_available,
            'speaking': self.speaking
        }

    @classmethod
    def list_voices(cls) -> dict:
        """List available British voices"""
        return cls.VOICES.copy()


def create_edge_tts_voice(voice: str = "ryan", rate: str = "+0%") -> EdgeTTSVoice:
    """
    Factory function to create Edge TTS voice

    Args:
        voice: ryan, sonia, thomas, libby, or mia
        rate: Speech rate (-50% to +50%)

    Returns:
        EdgeTTSVoice instance
    """
    return EdgeTTSVoice(voice=voice, rate=rate)


# Test
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("Edge TTS Voice Test")
    print("=" * 40)
    print(f"Available voices: {EdgeTTSVoice.list_voices()}")

    voice = create_edge_tts_voice()
    print(f"Status: {voice.get_status()}")

    if voice.available:
        print("\nTesting voice...")
        voice.greet()
        voice.speak("The weather in Gary, Indiana is rather dreary today, sir.")
        voice.farewell()
    else:
        print("TTS not available. Install: pip install edge-tts")
        print("Also ensure ffmpeg is installed: winget install ffmpeg")
