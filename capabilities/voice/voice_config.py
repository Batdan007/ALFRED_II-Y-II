"""
Voice Configuration Module
Loads and manages voice settings from the config system

Author: Daniel J Rita (BATDAN)
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from enum import Enum

# Default voice configuration
DEFAULT_VOICE_CONFIG = {
    'voice': {
        # Operating mode: local, hybrid, or cloud
        'mode': 'local',

        # STT (Speech-to-Text) settings
        'stt': {
            'prefer_offline': True,  # Prefer VOSK over Google
            'timeout': 5,            # Seconds to wait for speech
            'phrase_limit': 10,      # Max seconds for a phrase
            'wake_words': ['alfred', 'hey alfred', 'computer', 'bat computer'],
            'require_wake_word': False,
            'identify_speaker': True,

            # VOSK settings
            'vosk': {
                'model_size': 'small',  # small, medium, large
                'sample_rate': 16000,
                'model_path': None  # Auto-detect if None
            },

            # Google Speech settings (fallback)
            'google': {
                'energy_threshold': 4000,
                'dynamic_threshold': True
            }
        },

        # TTS (Text-to-Speech) settings
        'tts': {
            'prefer_elevenlabs': False,  # Prefer pyttsx3 by default (privacy)
            'speaking_rate': 175,        # Words per minute for pyttsx3

            # ElevenLabs settings (premium)
            'elevenlabs': {
                'voice': 'Daniel',       # British male voice
                'model': 'eleven_monolingual_v1',
                'stability': 0.5,
                'similarity_boost': 0.75,
                'streaming': True,
                'cache_audio': True
            },

            # pyttsx3 settings (local)
            'pyttsx3': {
                'voice_preference': ['Ryan', 'George', 'Daniel', 'Alex'],
                'volume': 1.0
            }
        },

        # Personality settings
        'personality': {
            'british_butler': True,      # Add "sir" and butler mannerisms
            'add_personality': True,     # Add personality to speech
            'sarcasm_enabled': True      # Enable sarcastic responses
        }
    }
}


class VoiceConfig:
    """
    Voice configuration manager

    Loads settings from the config system or uses defaults.
    """

    def __init__(self, config_loader=None):
        """
        Initialize voice configuration

        Args:
            config_loader: ConfigLoader instance (optional)
        """
        self.logger = logging.getLogger(__name__)
        self.config_loader = config_loader
        self._config = None

        self._load_config()

    def _load_config(self):
        """Load configuration from file or use defaults"""
        if self.config_loader:
            try:
                self._config = self.config_loader.load('voice')
                if self._config:
                    self.logger.info("Voice config loaded from file")
                    return
            except Exception as e:
                self.logger.debug(f"Could not load voice config: {e}")

        # Use defaults
        self._config = DEFAULT_VOICE_CONFIG.get('voice', {})
        self.logger.debug("Using default voice configuration")

    def save_config(self):
        """Save current configuration to file"""
        if self.config_loader:
            try:
                self.config_loader.save('voice', {'voice': self._config})
                self.logger.info("Voice config saved")
            except Exception as e:
                self.logger.error(f"Failed to save voice config: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation

        Args:
            key: Configuration key (e.g., "stt.timeout")
            default: Default value if not found

        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self._config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any):
        """
        Set configuration value using dot notation

        Args:
            key: Configuration key (e.g., "stt.timeout")
            value: Value to set
        """
        keys = key.split('.')
        config = self._config

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value

    # ==================== Convenience Properties ====================

    @property
    def mode(self) -> str:
        """Get voice mode (local/hybrid/cloud)"""
        return self.get('mode', 'local')

    @mode.setter
    def mode(self, value: str):
        self.set('mode', value)

    @property
    def prefer_offline_stt(self) -> bool:
        """Whether to prefer offline STT (VOSK)"""
        return self.get('stt.prefer_offline', True)

    @property
    def prefer_elevenlabs_tts(self) -> bool:
        """Whether to prefer ElevenLabs TTS"""
        return self.get('tts.prefer_elevenlabs', False)

    @property
    def stt_timeout(self) -> int:
        """STT listening timeout in seconds"""
        return self.get('stt.timeout', 5)

    @property
    def wake_words(self) -> list:
        """Wake words for voice activation"""
        return self.get('stt.wake_words', ['alfred', 'hey alfred'])

    @property
    def require_wake_word(self) -> bool:
        """Whether wake word is required"""
        return self.get('stt.require_wake_word', False)

    @property
    def vosk_model_size(self) -> str:
        """VOSK model size (small/medium/large)"""
        return self.get('stt.vosk.model_size', 'small')

    @property
    def elevenlabs_voice(self) -> str:
        """ElevenLabs voice name"""
        return self.get('tts.elevenlabs.voice', 'Daniel')

    @property
    def speaking_rate(self) -> int:
        """pyttsx3 speaking rate"""
        return self.get('tts.speaking_rate', 175)

    @property
    def british_butler_mode(self) -> bool:
        """Whether to use British butler personality"""
        return self.get('personality.british_butler', True)

    # ==================== Factory Methods ====================

    def to_voice_manager_config(self):
        """
        Convert to VoiceManagerConfig

        Returns:
            VoiceManagerConfig instance
        """
        from capabilities.voice.voice_manager import VoiceManagerConfig, VoiceMode

        mode_map = {
            'local': VoiceMode.LOCAL,
            'hybrid': VoiceMode.HYBRID,
            'cloud': VoiceMode.CLOUD
        }

        return VoiceManagerConfig(
            mode=mode_map.get(self.mode, VoiceMode.LOCAL),
            stt_timeout=self.stt_timeout,
            stt_phrase_limit=self.get('stt.phrase_limit', 10),
            wake_words=self.wake_words,
            tts_voice=self.elevenlabs_voice,
            tts_rate=self.speaking_rate,
            require_wake_word=self.require_wake_word,
            identify_speaker=self.get('stt.identify_speaker', True)
        )


def create_voice_config(config_loader=None) -> VoiceConfig:
    """
    Factory function to create voice configuration

    Args:
        config_loader: ConfigLoader instance

    Returns:
        VoiceConfig instance
    """
    return VoiceConfig(config_loader=config_loader)


def create_default_voice_config_file(config_dir: Path) -> Path:
    """
    Create default voice configuration file

    Args:
        config_dir: Directory to create config in

    Returns:
        Path to created config file
    """
    import yaml

    config_dir = Path(config_dir)
    config_dir.mkdir(parents=True, exist_ok=True)

    config_file = config_dir / "voice.yaml"

    with open(config_file, 'w') as f:
        yaml.safe_dump(DEFAULT_VOICE_CONFIG, f, default_flow_style=False, sort_keys=False)

    return config_file


# CLI test
if __name__ == "__main__":
    import json
    logging.basicConfig(level=logging.INFO)

    print("Voice Configuration Test")
    print("="*40)

    config = create_voice_config()

    print(f"\nMode: {config.mode}")
    print(f"Prefer Offline STT: {config.prefer_offline_stt}")
    print(f"Prefer ElevenLabs TTS: {config.prefer_elevenlabs_tts}")
    print(f"STT Timeout: {config.stt_timeout}s")
    print(f"Wake Words: {config.wake_words}")
    print(f"VOSK Model Size: {config.vosk_model_size}")
    print(f"ElevenLabs Voice: {config.elevenlabs_voice}")
    print(f"Speaking Rate: {config.speaking_rate}")

    print("\nDefault config:")
    print(json.dumps(DEFAULT_VOICE_CONFIG, indent=2))
