"""
Alfred Voice System - Privacy-First Voice Interface

Components:
- VoiceManager: Unified voice interface (STT + TTS)
- AlfredVoice: Text-to-Speech (ElevenLabs + pyttsx3)
- AlfredEarsAdvanced: Speech-to-Text (VOSK + Google)
- VoiceConfig: Configuration management

NEW (Upgraded):
- WhisperSTT: High-quality speech recognition (faster-whisper, GPU accelerated)
- EdgeTTSVoice: Natural British voice (Edge TTS, free, no API key)

STT Priority: Whisper (GPU) -> VOSK (offline) -> Google Speech (online)
TTS Priority: Edge TTS (free, natural) -> ElevenLabs (premium) -> pyttsx3 (local)

Author: Daniel J Rita (BATDAN)
"""

from typing import Optional

# Core TTS
from .alfred_voice import AlfredVoice, VoicePersonality, create_alfred_voice

# Core STT
try:
    from .alfred_ears_advanced import AlfredEarsAdvanced, create_alfred_ears_advanced
    EARS_AVAILABLE = True
except ImportError:
    EARS_AVAILABLE = False

# Voice Manager
try:
    from .voice_manager import VoiceManager, VoiceMode, VoiceManagerConfig, create_voice_manager
    VOICE_MANAGER_AVAILABLE = True
except ImportError:
    VOICE_MANAGER_AVAILABLE = False

# Voice Config
try:
    from .voice_config import VoiceConfig, create_voice_config, DEFAULT_VOICE_CONFIG
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False

# VOSK (offline STT)
try:
    from .vosk_recognizer import VoskRecognizer, VoskConfig, VoskModelSize, create_vosk_recognizer
    VOSK_AVAILABLE = True
except ImportError:
    VOSK_AVAILABLE = False

# ElevenLabs (premium TTS)
try:
    from .elevenlabs_tts import ElevenLabsTTS, ElevenLabsConfig, create_elevenlabs_tts
    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False

# Legacy support
try:
    from .speech_to_text import AlfredEars
    LEGACY_EARS_AVAILABLE = True
except ImportError:
    LEGACY_EARS_AVAILABLE = False

# NEW: Whisper STT (GPU accelerated, high quality)
try:
    from .whisper_stt import WhisperSTT, create_whisper_stt
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False

# NEW: Edge TTS (free, natural British voice)
try:
    from .edge_tts_voice import EdgeTTSVoice, create_edge_tts_voice
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False


# Build __all__ dynamically
__all__ = [
    # Core TTS
    'AlfredVoice',
    'VoicePersonality',
    'create_alfred_voice',

    # Availability flags
    'VOSK_AVAILABLE',
    'ELEVENLABS_AVAILABLE',
    'EARS_AVAILABLE',
    'VOICE_MANAGER_AVAILABLE',
]

if EARS_AVAILABLE:
    __all__.extend(['AlfredEarsAdvanced', 'create_alfred_ears_advanced'])

if VOICE_MANAGER_AVAILABLE:
    __all__.extend(['VoiceManager', 'VoiceMode', 'VoiceManagerConfig', 'create_voice_manager'])

if CONFIG_AVAILABLE:
    __all__.extend(['VoiceConfig', 'create_voice_config', 'DEFAULT_VOICE_CONFIG'])

if VOSK_AVAILABLE:
    __all__.extend(['VoskRecognizer', 'VoskConfig', 'VoskModelSize', 'create_vosk_recognizer'])

if ELEVENLABS_AVAILABLE:
    __all__.extend(['ElevenLabsTTS', 'ElevenLabsConfig', 'create_elevenlabs_tts'])

if LEGACY_EARS_AVAILABLE:
    __all__.append('AlfredEars')

if WHISPER_AVAILABLE:
    __all__.extend(['WhisperSTT', 'create_whisper_stt', 'WHISPER_AVAILABLE'])

if EDGE_TTS_AVAILABLE:
    __all__.extend(['EdgeTTSVoice', 'create_edge_tts_voice', 'EDGE_TTS_AVAILABLE'])


def get_voice_system_status() -> dict:
    """
    Get comprehensive status of the voice system

    Returns:
        Dict with availability and status of all components
    """
    return {
        'stt': {
            'whisper': {
                'installed': WHISPER_AVAILABLE,
                'description': 'GPU-accelerated speech recognition (RECOMMENDED)'
            },
            'vosk': {
                'installed': VOSK_AVAILABLE,
                'description': 'Offline speech recognition (privacy-first)'
            },
            'google': {
                'installed': EARS_AVAILABLE,
                'description': 'Online speech recognition (fallback)'
            }
        },
        'tts': {
            'edge_tts': {
                'installed': EDGE_TTS_AVAILABLE,
                'description': 'Natural British voice, free (RECOMMENDED)'
            },
            'elevenlabs': {
                'installed': ELEVENLABS_AVAILABLE,
                'description': 'Premium AI voice (cloud, requires API key)'
            },
            'pyttsx3': {
                'installed': True,  # Always available with AlfredVoice
                'description': 'Local system voice (offline, robotic)'
            }
        },
        'managers': {
            'voice_manager': VOICE_MANAGER_AVAILABLE,
            'voice_config': CONFIG_AVAILABLE
        },
        'install_commands': {
            'recommended': 'pip install faster-whisper edge-tts sounddevice numpy',
            'offline_stt': 'pip install vosk sounddevice',
            'premium_tts': 'pip install elevenlabs && set ELEVENLABS_API_KEY=your_key',
            'full_setup': 'pip install faster-whisper edge-tts vosk sounddevice elevenlabs SpeechRecognition pyaudio'
        }
    }
