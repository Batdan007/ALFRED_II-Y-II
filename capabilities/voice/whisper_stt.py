"""
Whisper Speech-to-Text for ALFRED
=================================
High-quality speech recognition using faster-whisper.
Replaces VOSK for much better accuracy.

Author: Daniel J Rita (BATDAN)
"""

import logging
import numpy as np
import sounddevice as sd
from typing import Optional, Dict, Any

try:
    from faster_whisper import WhisperModel
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    WhisperModel = None


class WhisperSTT:
    """
    Whisper-based Speech-to-Text for ALFRED

    Much more accurate than VOSK, runs on GPU for speed.
    """

    # Configuration
    DEFAULT_MODEL = "base.en"  # Options: tiny.en, base.en, small.en, medium.en
    DEFAULT_DEVICE = "cuda"    # cuda or cpu
    SAMPLE_RATE = 16000

    def __init__(self,
                 model_size: str = None,
                 device: str = None,
                 compute_type: str = None):
        """
        Initialize Whisper STT

        Args:
            model_size: Whisper model (tiny.en, base.en, small.en, medium.en)
            device: cuda or cpu
            compute_type: float16 (GPU) or float32 (CPU)
        """
        self.logger = logging.getLogger(__name__)
        self.model = None
        self.model_size = model_size or self.DEFAULT_MODEL
        self.device = device or self.DEFAULT_DEVICE

        # Auto-select compute type
        if compute_type:
            self.compute_type = compute_type
        else:
            self.compute_type = "float16" if self.device == "cuda" else "float32"

        self._initialize()

    def _initialize(self):
        """Load Whisper model"""
        if not WHISPER_AVAILABLE:
            self.logger.debug("faster-whisper not installed")
            return

        self.logger.info(f"Loading Whisper model '{self.model_size}'...")

        try:
            self.model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type
            )
            self.logger.info(f"Whisper ready on {self.device.upper()}")
        except Exception as e:
            self.logger.warning(f"CUDA failed, falling back to CPU: {e}")
            try:
                self.model = WhisperModel(
                    self.model_size,
                    device="cpu",
                    compute_type="float32"
                )
                self.device = "cpu"
                self.logger.info("Whisper ready on CPU")
            except Exception as e2:
                self.logger.error(f"Failed to load Whisper: {e2}")

    @property
    def available(self) -> bool:
        """Check if Whisper is available"""
        return self.model is not None

    def record_audio(self,
                     duration: float = None,
                     silence_threshold: float = 500,
                     silence_duration: float = 1.5,
                     max_duration: float = 30) -> Optional[np.ndarray]:
        """
        Record audio until silence or max duration

        Args:
            duration: Fixed duration (overrides silence detection)
            silence_threshold: Volume threshold for silence
            silence_duration: Seconds of silence to stop
            max_duration: Maximum recording length

        Returns:
            Audio as numpy array or None
        """
        self.logger.debug("Recording audio...")

        recording = []
        silent_chunks = 0
        chunk_duration = 0.1  # 100ms chunks
        chunks_for_silence = int(silence_duration / chunk_duration)
        max_chunks = int(max_duration / chunk_duration)

        def callback(indata, frames, time, status):
            recording.append(indata.copy())

        try:
            with sd.InputStream(samplerate=self.SAMPLE_RATE, channels=1,
                              callback=callback, blocksize=int(self.SAMPLE_RATE * chunk_duration)):

                if duration:
                    # Fixed duration recording
                    sd.sleep(int(duration * 1000))
                else:
                    # Silence-based recording
                    for i in range(max_chunks):
                        sd.sleep(int(chunk_duration * 1000))

                        if len(recording) > 0:
                            volume = np.abs(recording[-1]).mean() * 32768

                            if volume < silence_threshold:
                                silent_chunks += 1
                            else:
                                silent_chunks = 0

                            # Stop after enough silence (but record at least 1 second)
                            if silent_chunks >= chunks_for_silence and len(recording) > 10:
                                break

        except Exception as e:
            self.logger.error(f"Recording error: {e}")
            return None

        if not recording:
            return None

        audio = np.concatenate(recording, axis=0).flatten()
        self.logger.debug(f"Recorded {len(audio)/self.SAMPLE_RATE:.1f}s")
        return audio

    def transcribe(self, audio: np.ndarray) -> Dict[str, Any]:
        """
        Transcribe audio to text

        Args:
            audio: Audio as numpy array

        Returns:
            Dict with 'text', 'confidence', 'language', 'segments'
        """
        if not self.available:
            return {'text': '', 'confidence': 0, 'error': 'Whisper not available'}

        try:
            segments, info = self.model.transcribe(
                audio,
                language="en",
                beam_size=5,
                vad_filter=True
            )

            # Collect segments
            segment_list = []
            full_text = []

            for segment in segments:
                segment_list.append({
                    'start': segment.start,
                    'end': segment.end,
                    'text': segment.text.strip()
                })
                full_text.append(segment.text.strip())

            text = " ".join(full_text)

            return {
                'text': text,
                'confidence': 0.9,  # Whisper doesn't provide per-segment confidence
                'language': info.language,
                'segments': segment_list,
                'engine': 'whisper'
            }

        except Exception as e:
            self.logger.error(f"Transcription error: {e}")
            return {'text': '', 'confidence': 0, 'error': str(e)}

    def listen_once(self, timeout: float = None) -> Dict[str, Any]:
        """
        Listen for speech and transcribe

        Args:
            timeout: Max recording duration (uses silence detection if None)

        Returns:
            Dict with 'text', 'confidence', etc.
        """
        audio = self.record_audio(duration=timeout)

        if audio is None or len(audio) < self.SAMPLE_RATE * 0.5:
            return {'text': '', 'confidence': 0, 'error': 'No speech detected'}

        return self.transcribe(audio)

    def get_status(self) -> Dict[str, Any]:
        """Get STT status"""
        return {
            'available': self.available,
            'engine': 'whisper',
            'model': self.model_size,
            'device': self.device,
            'compute_type': self.compute_type
        }


def create_whisper_stt(model_size: str = "base.en",
                       device: str = "cuda") -> WhisperSTT:
    """
    Factory function to create WhisperSTT

    Args:
        model_size: tiny.en, base.en, small.en, medium.en
        device: cuda or cpu

    Returns:
        WhisperSTT instance
    """
    return WhisperSTT(model_size=model_size, device=device)


# Test
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("Whisper STT Test")
    print("=" * 40)

    stt = create_whisper_stt()
    print(f"Status: {stt.get_status()}")

    if stt.available:
        print("\nSpeak now (will stop on silence)...")
        result = stt.listen_once()
        print(f"Result: {result}")
