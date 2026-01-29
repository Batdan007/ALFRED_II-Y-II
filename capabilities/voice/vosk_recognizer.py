"""
VOSK Offline Speech Recognition for Alfred
Privacy-first, no internet required speech-to-text

Features:
- 100% offline operation (no data leaves the device)
- Real-time streaming recognition
- Multiple model sizes (small/medium/large)
- Wake word detection support
- Low latency (<300ms)

Author: Daniel J Rita (BATDAN)
"""

import logging
import json
import queue
import threading
from pathlib import Path
from typing import Optional, Callable, Dict, Any
from dataclasses import dataclass
from enum import Enum

# Graceful degradation for VOSK
try:
    import vosk
    VOSK_AVAILABLE = True
except ImportError:
    VOSK_AVAILABLE = False
    vosk = None

# Audio capture
try:
    import sounddevice as sd
    SOUNDDEVICE_AVAILABLE = True
except ImportError:
    SOUNDDEVICE_AVAILABLE = False
    sd = None

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None


class VoskModelSize(Enum):
    """Available VOSK model sizes"""
    SMALL = "small"      # ~50MB, fastest, less accurate
    MEDIUM = "medium"    # ~500MB, balanced
    LARGE = "large"      # ~1.8GB, most accurate, slower


@dataclass
class VoskConfig:
    """Configuration for VOSK recognizer"""
    model_path: Optional[str] = None
    model_size: VoskModelSize = VoskModelSize.SMALL
    sample_rate: int = 16000
    block_size: int = 8000  # Audio block size
    channels: int = 1
    device: Optional[int] = None  # None = default microphone

    # Recognition settings
    words: bool = True  # Include word-level timestamps
    partial: bool = True  # Enable partial results for real-time feedback

    # Wake word settings
    wake_words: list = None
    wake_word_sensitivity: float = 0.5


class VoskRecognizer:
    """
    VOSK-based offline speech recognition

    Privacy-first design:
    - All processing happens locally
    - No internet connection required
    - No data sent to external servers
    - Integrates with Alfred's PrivacyController
    """

    # Model download URLs (for auto-download feature)
    MODEL_URLS = {
        "en-us-small": "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip",
        "en-us-medium": "https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip",
        "en-us-large": "https://alphacephei.com/vosk/models/vosk-model-en-us-0.22-lgraph.zip",
    }

    DEFAULT_WAKE_WORDS = ['alfred', 'hey alfred', 'okay alfred', 'computer', 'bat computer']

    def __init__(self, config: Optional[VoskConfig] = None, brain=None):
        """
        Initialize VOSK recognizer

        Args:
            config: VoskConfig with settings
            brain: AlfredBrain instance for memory integration
        """
        self.logger = logging.getLogger(__name__)
        self.config = config or VoskConfig()
        self.brain = brain

        # State
        self.model = None
        self.recognizer = None
        self.audio_queue = queue.Queue()
        self.listening = False
        self.stream = None

        # Callbacks
        self.on_result: Optional[Callable[[str], None]] = None
        self.on_partial: Optional[Callable[[str], None]] = None
        self.on_wake_word: Optional[Callable[[str], None]] = None

        # Wake words
        self.wake_words = self.config.wake_words or self.DEFAULT_WAKE_WORDS

        # Check availability
        if not self._check_dependencies():
            return

        # Auto-detect real microphone if using default (which might be Stereo Mix)
        if self.config.device is None:
            self._auto_detect_microphone()

        # Initialize model
        self._initialize_model()

    def _check_dependencies(self) -> bool:
        """Check if all required dependencies are available"""
        missing = []

        if not VOSK_AVAILABLE:
            missing.append("vosk")
        if not SOUNDDEVICE_AVAILABLE:
            missing.append("sounddevice")
        if not NUMPY_AVAILABLE:
            missing.append("numpy")

        if missing:
            self.logger.warning(
                f"VOSK dependencies missing. Install: pip install {' '.join(missing)}"
            )
            return False

        return True

    def _auto_detect_microphone(self):
        """Auto-detect a real microphone (not Stereo Mix)"""
        if not SOUNDDEVICE_AVAILABLE:
            return

        try:
            # Get all input devices
            devices = sd.query_devices()

            # Priority: look for actual microphones, avoid Stereo Mix
            microphone_keywords = ['microphone', 'mic array', 'mic input']
            avoid_keywords = ['stereo mix', 'what u hear', 'loopback']

            candidates = []
            for i, dev in enumerate(devices):
                if dev['max_input_channels'] > 0:
                    name_lower = dev['name'].lower()

                    # Skip loopback/stereo mix devices
                    if any(avoid in name_lower for avoid in avoid_keywords):
                        continue

                    # Prefer devices with "microphone" in name
                    is_mic = any(kw in name_lower for kw in microphone_keywords)
                    candidates.append((i, dev['name'], is_mic))

            # Sort: microphones first, then by index
            candidates.sort(key=lambda x: (not x[2], x[0]))

            if candidates:
                device_idx, device_name, _ = candidates[0]
                self.config.device = device_idx
                self.logger.info(f"Auto-selected microphone: {device_name} (device {device_idx})")
            else:
                self.logger.warning("No suitable microphone found, using system default")

        except Exception as e:
            self.logger.debug(f"Auto-detect microphone failed: {e}")

    def _initialize_model(self):
        """Initialize VOSK model"""
        if not VOSK_AVAILABLE:
            return

        try:
            # Determine model path
            model_path = self._get_model_path()

            if not model_path or not Path(model_path).exists():
                self.logger.warning(
                    f"VOSK model not found at {model_path}. "
                    f"Download from: {self.MODEL_URLS.get('en-us-small')}"
                )
                self._show_model_instructions()
                return

            # Suppress VOSK logging
            vosk.SetLogLevel(-1)

            # Load model
            self.logger.info(f"Loading VOSK model from {model_path}...")
            self.model = vosk.Model(str(model_path))

            # Create recognizer
            self.recognizer = vosk.KaldiRecognizer(
                self.model,
                self.config.sample_rate
            )
            self.recognizer.SetWords(self.config.words)
            self.recognizer.SetPartialWords(self.config.partial)

            self.logger.info("VOSK offline speech recognition initialized")

        except Exception as e:
            self.logger.error(f"Failed to initialize VOSK: {e}")
            self.model = None
            self.recognizer = None

    def _get_model_path(self) -> Optional[str]:
        """Get path to VOSK model"""
        # Check if explicitly configured
        if self.config.model_path:
            return self.config.model_path

        # Check standard locations
        try:
            from core.path_manager import PathManager
            models_dir = Path(PathManager.MODELS_DIR) / "vosk"
        except ImportError:
            models_dir = Path.home() / ".alfred" / "models" / "vosk"

        # Look for model by size preference
        size_names = {
            VoskModelSize.SMALL: ["vosk-model-small-en-us-0.15", "vosk-model-small-en-us"],
            VoskModelSize.MEDIUM: ["vosk-model-en-us-0.22", "vosk-model-en-us"],
            VoskModelSize.LARGE: ["vosk-model-en-us-0.22-lgraph", "vosk-model-en-us-lgraph"],
        }

        # Try preferred size first, then fall back to any available
        search_order = [self.config.model_size] + [s for s in VoskModelSize if s != self.config.model_size]

        for size in search_order:
            for name in size_names.get(size, []):
                model_path = models_dir / name
                if model_path.exists():
                    self.logger.info(f"Found VOSK model: {name} ({size.value})")
                    return str(model_path)

        # Check if models_dir exists and has any model
        if models_dir.exists():
            for item in models_dir.iterdir():
                if item.is_dir() and item.name.startswith("vosk-model"):
                    return str(item)

        return None

    def _show_model_instructions(self):
        """Show instructions for downloading VOSK model"""
        try:
            from core.path_manager import PathManager
            models_dir = Path(PathManager.MODELS_DIR) / "vosk"
        except ImportError:
            models_dir = Path.home() / ".alfred" / "models" / "vosk"

        self.logger.info("\n" + "="*60)
        self.logger.info("VOSK MODEL INSTALLATION")
        self.logger.info("="*60)
        self.logger.info(f"\n1. Download the small English model (~50MB):")
        self.logger.info(f"   {self.MODEL_URLS['en-us-small']}")
        self.logger.info(f"\n2. Extract to: {models_dir}")
        self.logger.info(f"\n3. Restart Alfred")
        self.logger.info("\nFor better accuracy, use the medium or large model.")
        self.logger.info("="*60 + "\n")

    def _audio_callback(self, indata, frames, time_info, status):
        """Callback for audio stream"""
        if status:
            self.logger.warning(f"Audio status: {status}")
        self.audio_queue.put(bytes(indata))

    def is_available(self) -> bool:
        """Check if VOSK is ready to use"""
        return self.model is not None and self.recognizer is not None

    def listen_once(self, timeout: float = 5.0) -> Optional[Dict[str, Any]]:
        """
        Listen for a single utterance

        Args:
            timeout: Maximum time to wait for speech

        Returns:
            Dict with 'text', 'confidence', 'words' or None
        """
        if not self.is_available():
            self.logger.error("VOSK not available")
            return None

        if not SOUNDDEVICE_AVAILABLE:
            self.logger.error("sounddevice not available")
            return None

        try:
            # Clear queue
            while not self.audio_queue.empty():
                self.audio_queue.get()

            # Reset recognizer
            self.recognizer.Reset()

            # Start audio stream
            with sd.RawInputStream(
                samplerate=self.config.sample_rate,
                blocksize=self.config.block_size,
                dtype='int16',
                channels=self.config.channels,
                device=self.config.device,
                callback=self._audio_callback
            ):
                # Listening debug message removed - too verbose

                import time
                start_time = time.time()
                speech_detected = False
                silence_count = 0
                max_silence = 10  # Stop after this many silent blocks

                while time.time() - start_time < timeout:
                    try:
                        data = self.audio_queue.get(timeout=0.5)
                    except queue.Empty:
                        continue

                    if self.recognizer.AcceptWaveform(data):
                        # Final result
                        result = json.loads(self.recognizer.Result())
                        if result.get('text'):
                            return self._process_result(result)
                        silence_count += 1
                    else:
                        # Partial result
                        partial = json.loads(self.recognizer.PartialResult())
                        if partial.get('partial'):
                            speech_detected = True
                            silence_count = 0
                            if self.on_partial:
                                self.on_partial(partial['partial'])

                    # Stop if speech was detected then silence
                    if speech_detected and silence_count >= max_silence:
                        break

                # Get final result
                result = json.loads(self.recognizer.FinalResult())
                if result.get('text'):
                    return self._process_result(result)

                return None

        except Exception as e:
            self.logger.error(f"Listen error: {e}")
            return None

    def _process_result(self, result: dict) -> Dict[str, Any]:
        """Process VOSK recognition result"""
        text = result.get('text', '').strip()

        # Calculate confidence from word confidences if available
        confidence = 1.0
        words = result.get('result', [])
        if words:
            confidences = [w.get('conf', 1.0) for w in words]
            confidence = sum(confidences) / len(confidences)

        processed = {
            'text': text,
            'confidence': confidence,
            'words': words,
            'engine': 'vosk'
        }

        # Check for wake word
        text_lower = text.lower()
        for wake_word in self.wake_words:
            if wake_word in text_lower:
                processed['wake_word_detected'] = wake_word
                if self.on_wake_word:
                    self.on_wake_word(wake_word)
                break

        # Call result callback
        if self.on_result:
            self.on_result(text)

        # Store in brain
        if self.brain and text:
            try:
                self.brain.store_conversation(
                    user_input=text,
                    alfred_response="[listening]",
                    success=True,
                    importance=5
                )
            except Exception as e:
                self.logger.debug(f"Could not store in brain: {e}")

        return processed

    def listen_continuous(
        self,
        callback: Callable[[str], None],
        stop_phrase: str = "stop listening",
        wake_word_mode: bool = False
    ):
        """
        Listen continuously and call callback with recognized text

        Args:
            callback: Function to call with recognized text
            stop_phrase: Phrase to stop listening
            wake_word_mode: If True, only trigger callback after wake word
        """
        if not self.is_available():
            self.logger.error("VOSK not available")
            return

        self.listening = True
        waiting_for_command = not wake_word_mode

        self.logger.info(f"Continuous listening started (say '{stop_phrase}' to stop)")
        if wake_word_mode:
            self.logger.info(f"Wake words: {', '.join(self.wake_words)}")

        try:
            while self.listening:
                result = self.listen_once(timeout=10.0)

                if result and result.get('text'):
                    text = result['text']
                    text_lower = text.lower()

                    # Check for stop phrase
                    if stop_phrase.lower() in text_lower:
                        self.logger.info("Stop phrase detected")
                        break

                    # Wake word mode handling
                    if wake_word_mode:
                        if result.get('wake_word_detected'):
                            # Remove wake word from text
                            command = text_lower
                            for wake_word in self.wake_words:
                                command = command.replace(wake_word, '').strip()

                            if command:
                                # Wake word + command in same utterance
                                callback(command)
                            else:
                                # Just wake word, wait for command
                                waiting_for_command = True
                                self.logger.info("Wake word detected, listening for command...")
                        elif waiting_for_command:
                            # Process command after wake word
                            callback(text)
                            waiting_for_command = False
                    else:
                        # Not in wake word mode, process everything
                        callback(text)

        except KeyboardInterrupt:
            self.logger.info("Listening interrupted")
        finally:
            self.listening = False
            self.logger.info("Continuous listening stopped")

    def stop_listening(self):
        """Stop continuous listening"""
        self.listening = False

    def get_available_devices(self) -> list:
        """Get list of available audio input devices"""
        if not SOUNDDEVICE_AVAILABLE:
            return []

        devices = []
        for i, device in enumerate(sd.query_devices()):
            if device['max_input_channels'] > 0:
                devices.append({
                    'index': i,
                    'name': device['name'],
                    'channels': device['max_input_channels'],
                    'sample_rate': device['default_samplerate']
                })
        return devices

    def set_device(self, device_index: int):
        """Set audio input device"""
        self.config.device = device_index
        self.logger.info(f"Audio device set to index {device_index}")

    def get_status(self) -> dict:
        """Get recognizer status"""
        return {
            'available': self.is_available(),
            'vosk_installed': VOSK_AVAILABLE,
            'sounddevice_installed': SOUNDDEVICE_AVAILABLE,
            'model_loaded': self.model is not None,
            'listening': self.listening,
            'sample_rate': self.config.sample_rate,
            'device': self.config.device,
            'wake_words': self.wake_words
        }

    def download_model(self, size: VoskModelSize = VoskModelSize.SMALL) -> bool:
        """
        Download VOSK model automatically

        Args:
            size: Model size to download

        Returns:
            True if download successful
        """
        import urllib.request
        import zipfile
        import tempfile

        url_key = f"en-us-{size.value}"
        url = self.MODEL_URLS.get(url_key)

        if not url:
            self.logger.error(f"No URL for model size: {size.value}")
            return False

        try:
            from core.path_manager import PathManager
            models_dir = Path(PathManager.MODELS_DIR) / "vosk"
        except ImportError:
            models_dir = Path.home() / ".alfred" / "models" / "vosk"

        models_dir.mkdir(parents=True, exist_ok=True)

        self.logger.info(f"Downloading VOSK {size.value} model...")
        self.logger.info(f"URL: {url}")
        self.logger.info("This may take a few minutes...")

        try:
            # Download to temp file
            with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp:
                urllib.request.urlretrieve(url, tmp.name)
                tmp_path = tmp.name

            # Extract
            self.logger.info("Extracting model...")
            with zipfile.ZipFile(tmp_path, 'r') as zip_ref:
                zip_ref.extractall(models_dir)

            # Clean up
            Path(tmp_path).unlink()

            self.logger.info(f"Model downloaded to {models_dir}")

            # Reinitialize
            self._initialize_model()

            return self.is_available()

        except Exception as e:
            self.logger.error(f"Download failed: {e}")
            return False


def create_vosk_recognizer(brain=None, model_size: str = "small") -> VoskRecognizer:
    """
    Factory function to create VOSK recognizer

    Args:
        brain: AlfredBrain instance
        model_size: "small", "medium", or "large"

    Returns:
        VoskRecognizer instance
    """
    size_map = {
        "small": VoskModelSize.SMALL,
        "medium": VoskModelSize.MEDIUM,
        "large": VoskModelSize.LARGE
    }

    config = VoskConfig(model_size=size_map.get(model_size, VoskModelSize.SMALL))
    return VoskRecognizer(config=config, brain=brain)


# CLI test
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("VOSK Speech Recognition Test")
    print("="*40)

    recognizer = create_vosk_recognizer()

    status = recognizer.get_status()
    print(f"\nStatus: {json.dumps(status, indent=2)}")

    if not recognizer.is_available():
        print("\nVOSK not available. Check status above for details.")
        print("\nTo install VOSK:")
        print("  pip install vosk sounddevice")
        print("\nThen download a model from:")
        print("  https://alphacephei.com/vosk/models")
    else:
        print("\nSay something (5 second timeout)...")
        result = recognizer.listen_once(timeout=5.0)

        if result:
            print(f"\nRecognized: {result['text']}")
            print(f"Confidence: {result['confidence']:.2f}")
        else:
            print("\nNo speech detected")
