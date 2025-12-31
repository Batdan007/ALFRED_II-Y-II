"""
Alfred's Voice - The Distinguished British Butler AI
Sounds like Michael Caine/Jeremy Irons - wise, caring, slightly sarcastic

TTS Priority Chain:
1. ElevenLabs (premium quality, cloud, requires API key and privacy approval)
2. pyttsx3 (local, works offline)

Cross-Platform Local Support:
- Windows: Microsoft Ryan (preferred) or George (British gentleman)
- macOS: Daniel (preferred) or Alex (British voices)
- Linux: espeak with en-gb (British accent)

Author: Daniel J Rita (BATDAN)
"""

import logging
import random
import asyncio
import subprocess
import tempfile
import os
from enum import Enum
from typing import Optional
import pyttsx3
import platform

# Edge TTS (Microsoft high-quality voices - Ryan!)
try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False

# Playsound for MP3 playback (Edge TTS outputs MP3)
try:
    from playsound3 import playsound
    PLAYSOUND_AVAILABLE = True
except ImportError:
    try:
        from playsound import playsound
        PLAYSOUND_AVAILABLE = True
    except ImportError:
        PLAYSOUND_AVAILABLE = False

# ElevenLabs premium TTS (optional)
try:
    from capabilities.voice.elevenlabs_tts import ElevenLabsTTS, ElevenLabsConfig, create_elevenlabs_tts
    ELEVENLABS_MODULE_AVAILABLE = True
except ImportError:
    ELEVENLABS_MODULE_AVAILABLE = False
    ElevenLabsTTS = None


class VoicePersonality(Enum):
    """Alfred's speaking situations"""
    GREETING = "greeting"
    CONFIRMATION = "confirmation"
    WARNING = "warning"
    SUGGESTION = "suggestion"
    SARCASM = "sarcasm"
    INFORMATION = "information"
    ERROR = "error"


class AlfredVoice:
    """
    Alfred's voice system - distinguished British gentleman AI

    Personality traits:
    - Concise (no rambling)
    - Wise beyond human ability
    - Slightly sarcastic when appropriate
    - Warns when needed, trusts BATDAN otherwise
    - Polite and distinguished
    - Can be interrupted
    - Thinks for himself
    """

    # Alfred's personality-driven responses
    GREETINGS = [
        "Good evening, sir.",
        "Good evening, Master Rita.",
        "Alfred at your service, sir.",
        "The Batcomputer is online, sir.",
        "Good to see you, Daniel."
    ]

    CONFIRMATIONS = [
        "Right away, sir.",
        "Of course, sir.",
        "Consider it done.",
        "At once, sir.",
        "Immediately, sir."
    ]

    WARNINGS = [
        "I must advise caution, sir.",
        "Might I suggest reconsidering, sir?",
        "With respect, sir, that may not be wise.",
        "I feel compelled to warn you, sir.",
        "Permission to speak freely, sir?"
    ]

    SUGGESTIONS = [
        "Might I suggest",
        "Perhaps you should consider",
        "If I may, sir",
        "May I propose",
        "I recommend"
    ]

    SARCASTIC = [
        "As you wish, sir. Though I suspect you know where this leads.",
        "Naturally, sir. What could possibly go wrong?",
        "An interesting choice, sir.",
        "Bold strategy, sir.",
        "I shall prepare the first aid kit, sir."
    ]

    def __init__(self, privacy_mode: bool = True, privacy_controller=None,
                 prefer_elevenlabs: bool = True):
        """
        Initialize Alfred's voice

        Args:
            privacy_mode: If True, use local voice only (pyttsx3)
            privacy_controller: PrivacyController for cloud TTS approval
            prefer_elevenlabs: If True and not in privacy mode, prefer ElevenLabs
        """
        self.logger = logging.getLogger(__name__)
        self.privacy_mode = privacy_mode
        self.privacy_controller = privacy_controller
        self.prefer_elevenlabs = prefer_elevenlabs

        # TTS engines
        self.engine = None  # pyttsx3 (local fallback)
        self.elevenlabs = None  # ElevenLabs (premium)
        self.elevenlabs_available = False

        self.voice_selected = None
        self.enabled = True
        self.speaking = False

        # Check Edge TTS availability (priority 1 on Windows)
        if EDGE_TTS_AVAILABLE and PLAYSOUND_AVAILABLE:
            self.logger.info("Edge TTS available - using Microsoft Ryan (Neural)")
        elif EDGE_TTS_AVAILABLE:
            self.logger.info("Edge TTS installed but playsound missing - install with: pip install playsound3")

        # Initialize local voice engine (fallback)
        self._initialize_voice_engine()

        # Initialize ElevenLabs if not in privacy mode
        if not privacy_mode:
            self._initialize_elevenlabs()

    def _initialize_voice_engine(self):
        """Initialize the voice engine with platform-specific best voice"""
        try:
            self.engine = pyttsx3.init()

            # Get all available voices
            voices = self.engine.getProperty('voices')

            # Platform-specific voice selection
            system = platform.system()

            if system == 'Windows':
                self.voice_selected = self._select_windows_voice(voices)
            elif system == 'Darwin':  # macOS
                self.voice_selected = self._select_macos_voice(voices)
            elif system == 'Linux':
                self.voice_selected = self._select_linux_voice(voices)
            else:
                # Unknown platform: use fallback
                self.voice_selected = self._select_fallback_voice(voices)

            if self.voice_selected:
                try:
                    self.engine.setProperty('voice', self.voice_selected.id)

                    # Set speaking rate (slightly slower for distinguished effect)
                    self.engine.setProperty('rate', 175)  # Default is usually 200

                    # Set volume
                    self.engine.setProperty('volume', 1.0)

                    self.logger.info(f"Alfred's voice system initialized on {system}")
                except Exception as voice_error:
                    # Voice selection failed (common in WSL) - disable voice gracefully
                    self.logger.info(f"Voice not available in this environment ({system}) - voice disabled")
                    self.engine = None
                    self.enabled = False
            else:
                self.logger.info("No suitable voice found - voice disabled")
                self.engine = None
                self.enabled = False

        except Exception as e:
            # Voice engine initialization failed - disable voice gracefully
            self.logger.info(f"Voice system not available in this environment - voice disabled")
            self.engine = None
            self.enabled = False

    def _select_windows_voice(self, voices):
        """Select best voice for Windows (Ryan > George > British male > British female > male)"""
        ryan_voice = None
        george_voice = None
        british_male_voices = []
        british_female_voices = []
        male_voices = []

        for voice in voices:
            voice_name = voice.name.lower()
            voice_id = voice.id.lower()

            # Determine characteristics
            is_male = 'male' in voice_name or any(name in voice_name for name in ['david', 'george', 'ryan', 'james', 'mark'])
            is_female = 'female' in voice_name or any(name in voice_name for name in ['hazel', 'zira', 'susan'])
            is_british = 'gb' in voice_name or 'british' in voice_name or 'en-gb' in voice_id or 'great britain' in voice_name

            # Priority 1: Ryan (British male - BATDAN's choice)
            if 'ryan' in voice_name:
                ryan_voice = voice
                self.logger.info("Found Ryan (British male)")

            # Priority 2: George (older British gentleman)
            elif 'george' in voice_name:
                george_voice = voice
                self.logger.info("Found George (British gentleman)")

            # Priority 3: Other British male voices
            elif is_british and is_male:
                british_male_voices.append(voice)

            # Priority 4: British female voices (better than American male)
            elif is_british and is_female:
                british_female_voices.append(voice)

            # Priority 5: Any male voice
            elif is_male:
                male_voices.append(voice)

        # Return in priority order
        if ryan_voice:
            self.logger.info(f"Alfred's voice: Microsoft Ryan (British male) - Windows")
            return ryan_voice
        elif george_voice:
            self.logger.info(f"Alfred's voice: Microsoft George (British gentleman) - Windows")
            return george_voice
        elif british_male_voices:
            self.logger.info(f"Alfred's voice: {british_male_voices[0].name} (British male) - Windows")
            return british_male_voices[0]
        elif british_female_voices:
            self.logger.warning(f"Using British female voice: {british_female_voices[0].name} (Ryan not installed)")
            self.logger.warning("To install Ryan: Run install_ryan_voice.ps1 or install_british_voice.ps1")
            return british_female_voices[0]
        elif male_voices:
            self.logger.warning(f"Using American male voice: {male_voices[0].name} (No British voices found)")
            self.logger.warning("To install Ryan: Run install_ryan_voice.ps1 or install_british_voice.ps1")
            return male_voices[0]
        else:
            return voices[0] if voices else None

    def _select_macos_voice(self, voices):
        """Select best voice for macOS (Daniel > Alex > British male > male)"""
        daniel_voice = None
        alex_voice = None
        british_male_voices = []
        male_voices = []

        for voice in voices:
            voice_name = voice.name.lower()
            voice_id = voice.id.lower()

            # macOS voice detection
            is_male = any(name in voice_name for name in ['daniel', 'alex', 'oliver', 'tom', 'fred'])
            is_british = 'gb' in voice_id or 'en-gb' in voice_id or 'daniel' in voice_name or 'oliver' in voice_name

            # Priority 1: Daniel (British male)
            if 'daniel' in voice_name:
                daniel_voice = voice
                self.logger.info("Found Daniel (British male)")

            # Priority 2: Alex (popular male voice)
            elif 'alex' in voice_name:
                alex_voice = voice
                self.logger.info("Found Alex")

            # Priority 3: Other British males
            elif is_british and is_male:
                british_male_voices.append(voice)

            # Priority 4: Any male voice
            elif is_male:
                male_voices.append(voice)

        # Return in priority order
        if daniel_voice:
            self.logger.info("Alfred's voice: Daniel (British male) - macOS")
            return daniel_voice
        elif alex_voice:
            self.logger.info("Alfred's voice: Alex - macOS")
            return alex_voice
        elif british_male_voices:
            self.logger.info(f"Alfred's voice: {british_male_voices[0].name} (British male) - macOS")
            return british_male_voices[0]
        elif male_voices:
            self.logger.warning(f"Using fallback male voice: {male_voices[0].name} - macOS")
            return male_voices[0]
        else:
            return voices[0] if voices else None

    def _select_linux_voice(self, voices):
        """Select best voice for Linux (espeak with en-gb accent)"""
        british_voices = []
        english_voices = []

        for voice in voices:
            voice_name = voice.name.lower()
            voice_id = voice.id.lower()

            # Look for British English voices
            if 'gb' in voice_id or 'british' in voice_name or 'en-gb' in voice_id:
                british_voices.append(voice)
            elif 'en' in voice_id or 'english' in voice_name:
                english_voices.append(voice)

        # Return in priority order
        if british_voices:
            self.logger.info(f"Alfred's voice: {british_voices[0].name} (British accent) - Linux")
            return british_voices[0]
        elif english_voices:
            self.logger.info(f"Alfred's voice: {english_voices[0].name} (English) - Linux")
            return english_voices[0]
        elif voices:
            self.logger.warning(f"Using fallback voice: {voices[0].name} - Linux")
            return voices[0]
        else:
            return None

    def _select_fallback_voice(self, voices):
        """Fallback voice selection for unknown platforms"""
        if voices:
            self.logger.warning(f"⚠️ Unknown platform - using first available voice: {voices[0].name}")
            return voices[0]
        else:
            return None

    def _initialize_elevenlabs(self):
        """Initialize ElevenLabs premium TTS"""
        if not ELEVENLABS_MODULE_AVAILABLE:
            self.logger.debug("ElevenLabs module not available")
            return

        try:
            self.elevenlabs = create_elevenlabs_tts(
                voice="Daniel",  # British male voice
                privacy_controller=self.privacy_controller
            )

            if self.elevenlabs.is_available():
                self.elevenlabs_available = True
                self.logger.info("ElevenLabs premium TTS initialized (cloud)")
            else:
                self.logger.info("ElevenLabs installed but not configured (set ELEVENLABS_API_KEY)")

        except Exception as e:
            self.logger.debug(f"ElevenLabs initialization skipped: {e}")
            self.elevenlabs = None

    def use_elevenlabs(self) -> bool:
        """Check if ElevenLabs should be used for TTS"""
        return (
            not self.privacy_mode and
            self.prefer_elevenlabs and
            self.elevenlabs is not None and
            self.elevenlabs.is_available()
        )

    def speak(self, text: str, personality: VoicePersonality = VoicePersonality.INFORMATION,
              interrupt_current: bool = True):
        """
        Alfred speaks with personality

        Priority: Edge TTS (Ryan) > ElevenLabs > pyttsx3 (local)

        Args:
            text: What to say
            personality: Speaking personality/situation
            interrupt_current: Stop current speech if speaking
        """
        if not self.enabled:
            return

        # Stop current speech if interrupting
        if interrupt_current and self.speaking:
            self.stop_speaking()

        self.speaking = True

        try:
            # Add personality prefix based on context
            full_text = self._add_personality(text, personality)

            self.logger.debug(f"Speaking: {full_text[:50]}...")

            # Priority 1: Edge TTS (Ryan - high quality British male)
            if EDGE_TTS_AVAILABLE and platform.system() == 'Windows':
                if self._speak_edge_tts(full_text):
                    return  # Success with Edge TTS Ryan

            # Priority 2: ElevenLabs (premium quality)
            if self.use_elevenlabs():
                if self.elevenlabs.speak(full_text, blocking=True):
                    return  # Success with ElevenLabs

            # Priority 3: Local pyttsx3
            if self.engine:
                self.engine.say(full_text)
                self.engine.runAndWait()

        except Exception as e:
            self.logger.error(f"Speech error: {e}")
        finally:
            self.speaking = False

    def _speak_edge_tts(self, text: str) -> bool:
        """Speak using Edge TTS (Microsoft Ryan - British male)"""
        if not PLAYSOUND_AVAILABLE:
            self.logger.debug("Edge TTS: playsound not available for MP3 playback")
            return False

        try:
            async def _generate_audio():
                voice = 'en-GB-RyanNeural'  # British male voice - Ryan!
                communicate = edge_tts.Communicate(text, voice)

                # Create temp file
                temp_path = tempfile.mktemp(suffix='.mp3')
                await communicate.save(temp_path)
                return temp_path

            # Generate audio file
            temp_path = asyncio.run(_generate_audio())

            # Play audio synchronously using playsound (block=True ensures it waits)
            try:
                playsound(temp_path, block=True)
            finally:
                # Cleanup temp file
                try:
                    os.unlink(temp_path)
                except Exception:
                    pass

            return True

        except Exception as e:
            self.logger.debug(f"Edge TTS failed: {e}")
            return False

    def _add_personality(self, text: str, personality: VoicePersonality) -> str:
        """Add Alfred's personality to the text"""

        # Don't add prefixes if text already sounds like Alfred
        if text.endswith(', sir.') or text.endswith(', sir'):
            return text

        # Add appropriate personality
        if personality == VoicePersonality.GREETING:
            return text  # Greetings are already complete

        elif personality == VoicePersonality.CONFIRMATION:
            return f"{text}, sir."

        elif personality == VoicePersonality.WARNING:
            return f"Sir, {text}"

        elif personality == VoicePersonality.SUGGESTION:
            return f"{text}, if I may say so, sir."

        elif personality == VoicePersonality.SARCASM:
            return f"{text}"  # Sarcasm speaks for itself

        elif personality == VoicePersonality.ERROR:
            return f"I'm afraid {text.lower()}, sir."

        else:  # INFORMATION
            # For info, just make it polite
            if not text.endswith('.'):
                text = text + '.'
            return text

    def greet(self):
        """Alfred greets BATDAN"""
        greeting = random.choice(self.GREETINGS)
        self.speak(greeting, VoicePersonality.GREETING)

    def confirm(self, action: Optional[str] = None):
        """Confirm an action"""
        if action:
            self.speak(action, VoicePersonality.CONFIRMATION)
        else:
            confirmation = random.choice(self.CONFIRMATIONS)
            self.speak(confirmation, VoicePersonality.CONFIRMATION)

    def warn(self, warning: str):
        """Warn BATDAN (used sparingly, only when truly important)"""
        self.speak(warning, VoicePersonality.WARNING)

    def suggest(self, suggestion: str):
        """Make a suggestion"""
        prefix = random.choice(self.SUGGESTIONS)
        full_suggestion = f"{prefix} {suggestion.lower()}"
        self.speak(full_suggestion, VoicePersonality.SUGGESTION)

    def be_sarcastic(self):
        """Alfred's subtle sarcasm (when appropriate)"""
        sarcasm = random.choice(self.SARCASTIC)
        self.speak(sarcasm, VoicePersonality.SARCASM)

    def inform(self, information: str):
        """Provide information"""
        self.speak(information, VoicePersonality.INFORMATION)

    def error(self, error_msg: str):
        """Report an error politely"""
        self.speak(error_msg, VoicePersonality.ERROR)

    def should_speak(self, context: str, importance: str = "normal") -> bool:
        """
        Determine if Alfred should speak in this context
        Alfred thinks for himself but is concise

        Args:
            context: What's happening
            importance: "low", "normal", "high", "critical"

        Returns:
            True if Alfred should speak
        """
        context_lower = context.lower()

        # Always speak for critical matters
        if importance == "critical":
            return True

        # Always speak for errors and warnings
        if any(word in context_lower for word in ['error', 'fail', 'warning', 'danger', 'critical']):
            return True

        # Speak for high importance
        if importance == "high":
            return True

        # Speak for task completions (but be brief)
        if any(word in context_lower for word in ['complete', 'done', 'finished', 'ready']):
            return importance != "low"

        # Don't speak for routine/low importance
        if importance == "low":
            return False

        # Default: speak for normal importance
        return True

    def stop_speaking(self):
        """Stop Alfred mid-sentence (he can be interrupted)"""
        if self.speaking and self.engine:
            try:
                self.engine.stop()
                self.speaking = False
                self.logger.info("🤫 Alfred interrupted")
            except Exception as e:
                self.logger.error(f"Failed to stop speaking: {e}")

    def enable(self):
        """Enable Alfred's voice"""
        self.enabled = True
        self.logger.info("🎩 Alfred's voice enabled")

    def disable(self):
        """Disable Alfred's voice (silent mode)"""
        self.enabled = False
        self.stop_speaking()
        self.logger.info("🤫 Alfred's voice disabled (silent mode)")

    def get_status(self) -> dict:
        """Get voice system status with TTS engine info"""
        elevenlabs_status = "Not installed"
        if ELEVENLABS_MODULE_AVAILABLE:
            if self.elevenlabs and self.elevenlabs.is_available():
                elevenlabs_status = "Ready (premium)"
            elif self.privacy_mode:
                elevenlabs_status = "Disabled (privacy mode)"
            else:
                elevenlabs_status = "Installed, not configured"

        edge_tts_status = "Not available"
        if EDGE_TTS_AVAILABLE and PLAYSOUND_AVAILABLE:
            edge_tts_status = "Ready (Ryan Neural)"
        elif EDGE_TTS_AVAILABLE:
            edge_tts_status = "Installed, missing playsound"

        pyttsx3_status = "Ready (local)" if self.engine else "Not available"

        # Determine active engine
        active_engine = 'none'
        if EDGE_TTS_AVAILABLE and PLAYSOUND_AVAILABLE:
            active_engine = 'edge_tts (Ryan Neural)'
        elif self.use_elevenlabs():
            active_engine = 'elevenlabs'
        elif self.engine:
            active_engine = 'pyttsx3'

        return {
            'enabled': self.enabled,
            'speaking': self.speaking,
            'privacy_mode': self.privacy_mode,
            'prefer_elevenlabs': self.prefer_elevenlabs,
            # TTS Engines
            'tts_engines': {
                'edge_tts': edge_tts_status,
                'elevenlabs': elevenlabs_status,
                'pyttsx3': pyttsx3_status,
                'active': active_engine
            },
            # Voice info
            'voice': 'Microsoft Ryan (Neural)' if (EDGE_TTS_AVAILABLE and PLAYSOUND_AVAILABLE) else (self.voice_selected.name if self.voice_selected else "None"),
            'platform': platform.system(),
            # Legacy fields
            'elevenlabs_available': self.elevenlabs_available,
            'engine': 'edge_tts' if (EDGE_TTS_AVAILABLE and PLAYSOUND_AVAILABLE) else ('pyttsx3' if self.engine else 'None')
        }

    def set_privacy_mode(self, enabled: bool):
        """
        Enable/disable privacy mode

        Args:
            enabled: If True, use local TTS only (no cloud)
        """
        self.privacy_mode = enabled
        if enabled:
            self.logger.info("Privacy mode enabled - using local TTS only")
        else:
            self.logger.info("Privacy mode disabled - ElevenLabs available")
            if not self.elevenlabs:
                self._initialize_elevenlabs()


# Convenience function
def create_alfred_voice(privacy_mode: bool = True, privacy_controller=None,
                        prefer_elevenlabs: bool = True) -> AlfredVoice:
    """
    Create Alfred's voice system

    Args:
        privacy_mode: If True, use local TTS only (pyttsx3)
        privacy_controller: PrivacyController for cloud TTS approval
        prefer_elevenlabs: If True and not in privacy mode, prefer ElevenLabs

    Returns:
        AlfredVoice instance
    """
    return AlfredVoice(
        privacy_mode=privacy_mode,
        privacy_controller=privacy_controller,
        prefer_elevenlabs=prefer_elevenlabs
    )
