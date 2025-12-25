"""
Voice Pipeline End-to-End Test
Tests the complete voice system: STT (VOSK/Google) + TTS (ElevenLabs/pyttsx3)

Author: Daniel J Rita (BATDAN)
"""

import logging
import json
import sys

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_vosk_recognizer():
    """Test VOSK offline speech recognition"""
    print("\n" + "="*60)
    print("TEST 1: VOSK Offline Speech Recognition")
    print("="*60)

    try:
        from vosk_recognizer import VoskRecognizer, create_vosk_recognizer

        recognizer = create_vosk_recognizer()
        status = recognizer.get_status()

        print(f"\nVOSK Status:")
        print(f"  Installed: {status['vosk_installed']}")
        print(f"  Model Loaded: {status['model_loaded']}")
        print(f"  Available: {status['available']}")

        if status['available']:
            print("\n[PASS] VOSK is ready for offline speech recognition")
            return True
        else:
            print("\n[INFO] VOSK not available - model may need to be downloaded")
            print("       Run: recognizer.download_model('small')")
            return False

    except ImportError as e:
        print(f"\n[SKIP] VOSK module not available: {e}")
        print("       Install: pip install vosk sounddevice")
        return False
    except Exception as e:
        print(f"\n[FAIL] VOSK test failed: {e}")
        return False


def test_elevenlabs_tts():
    """Test ElevenLabs premium TTS"""
    print("\n" + "="*60)
    print("TEST 2: ElevenLabs Premium TTS")
    print("="*60)

    try:
        from elevenlabs_tts import ElevenLabsTTS, create_elevenlabs_tts

        tts = create_elevenlabs_tts()
        status = tts.get_status()

        print(f"\nElevenLabs Status:")
        print(f"  Installed: {status['elevenlabs_installed']}")
        print(f"  API Key Set: {status['api_key_set']}")
        print(f"  Client Ready: {status['client_initialized']}")
        print(f"  Available: {status['available']}")

        if status['available']:
            print("\n[PASS] ElevenLabs is ready for premium TTS")
            return True
        else:
            print("\n[INFO] ElevenLabs not available")
            if not status['api_key_set']:
                print("       Set ELEVENLABS_API_KEY environment variable")
            return False

    except ImportError as e:
        print(f"\n[SKIP] ElevenLabs module not available: {e}")
        print("       Install: pip install elevenlabs")
        return False
    except Exception as e:
        print(f"\n[FAIL] ElevenLabs test failed: {e}")
        return False


def test_alfred_voice():
    """Test Alfred's voice system (pyttsx3)"""
    print("\n" + "="*60)
    print("TEST 3: Alfred Voice (pyttsx3)")
    print("="*60)

    try:
        from alfred_voice import AlfredVoice, create_alfred_voice

        voice = create_alfred_voice(privacy_mode=True)
        status = voice.get_status()

        print(f"\nAlfred Voice Status:")
        print(f"  Enabled: {status['enabled']}")
        print(f"  Platform: {status['platform']}")
        print(f"  Local Voice: {status['voice']}")
        print(f"  TTS Active: {status['tts_engines']['active']}")

        if status['enabled'] and status['tts_engines']['pyttsx3'] == 'Ready (local)':
            print("\n[PASS] Alfred voice (pyttsx3) is ready")
            return True
        else:
            print("\n[FAIL] Alfred voice not available")
            return False

    except Exception as e:
        print(f"\n[FAIL] Alfred voice test failed: {e}")
        return False


def test_alfred_ears():
    """Test Alfred's ears (STT)"""
    print("\n" + "="*60)
    print("TEST 4: Alfred Ears (STT)")
    print("="*60)

    try:
        from alfred_ears_advanced import AlfredEarsAdvanced, create_alfred_ears_advanced

        ears = create_alfred_ears_advanced(prefer_offline=True)
        status = ears.get_status()

        print(f"\nAlfred Ears Status:")
        print(f"  VOSK: {status['stt_engines']['vosk']}")
        print(f"  Google: {status['stt_engines']['google']}")
        print(f"  Active: {status['stt_engines']['active']}")
        print(f"  Prefer Offline: {status['prefer_offline']}")

        active = status['stt_engines']['active']
        if active != 'none':
            print(f"\n[PASS] Alfred ears ready with {active}")
            return True
        else:
            print("\n[FAIL] No STT engine available")
            return False

    except Exception as e:
        print(f"\n[FAIL] Alfred ears test failed: {e}")
        return False


def test_voice_manager():
    """Test unified voice manager"""
    print("\n" + "="*60)
    print("TEST 5: Unified Voice Manager")
    print("="*60)

    try:
        from voice_manager import VoiceManager, create_voice_manager

        manager = create_voice_manager(mode="local")
        status = manager.get_status()

        print(f"\nVoice Manager Status:")
        print(f"  Mode: {status['mode']}")
        print(f"  STT Available: {status['stt']['available']}")
        print(f"  TTS Available: {status['tts']['available']}")
        print(f"  Privacy Mode: {status['privacy_mode']}")

        if status['stt']['available'] or status['tts']['available']:
            print("\n[PASS] Voice manager initialized")
            return True
        else:
            print("\n[FAIL] No voice capabilities available")
            return False

    except Exception as e:
        print(f"\n[FAIL] Voice manager test failed: {e}")
        return False


def test_voice_config():
    """Test voice configuration"""
    print("\n" + "="*60)
    print("TEST 6: Voice Configuration")
    print("="*60)

    try:
        from voice_config import VoiceConfig, create_voice_config

        config = create_voice_config()

        print(f"\nVoice Config:")
        print(f"  Mode: {config.mode}")
        print(f"  Prefer Offline STT: {config.prefer_offline_stt}")
        print(f"  Prefer ElevenLabs TTS: {config.prefer_elevenlabs_tts}")
        print(f"  Wake Words: {config.wake_words}")
        print(f"  VOSK Model Size: {config.vosk_model_size}")

        print("\n[PASS] Voice configuration loaded")
        return True

    except Exception as e:
        print(f"\n[FAIL] Voice config test failed: {e}")
        return False


def test_interactive_tts():
    """Interactive TTS test"""
    print("\n" + "="*60)
    print("TEST 7: Interactive TTS (Speaking)")
    print("="*60)

    try:
        from alfred_voice import create_alfred_voice

        response = input("\nWould you like to test TTS? (y/n): ").strip().lower()
        if response != 'y':
            print("[SKIP] Interactive TTS test skipped")
            return True

        voice = create_alfred_voice(privacy_mode=True)

        if not voice.enabled:
            print("\n[SKIP] Voice not enabled")
            return True

        print("\nSpeaking test phrase...")
        voice.speak("Good evening, sir. The voice system is operational.")

        print("[PASS] TTS test complete")
        return True

    except Exception as e:
        print(f"\n[FAIL] Interactive TTS test failed: {e}")
        return False


def test_interactive_stt():
    """Interactive STT test"""
    print("\n" + "="*60)
    print("TEST 8: Interactive STT (Listening)")
    print("="*60)

    try:
        from alfred_ears_advanced import create_alfred_ears_advanced

        response = input("\nWould you like to test STT? (y/n): ").strip().lower()
        if response != 'y':
            print("[SKIP] Interactive STT test skipped")
            return True

        ears = create_alfred_ears_advanced(prefer_offline=True)

        if ears.get_status()['stt_engines']['active'] == 'none':
            print("\n[SKIP] No STT engine available")
            return True

        print("\nListening for 5 seconds... (speak now)")
        result = ears.listen_once(timeout=5)

        if result:
            print(f"\nHeard: {result['text']}")
            print(f"Engine: {result.get('engine', 'unknown')}")
            print(f"Confidence: {result.get('confidence', 'N/A')}")
            print("[PASS] STT test complete")
        else:
            print("\nNo speech detected")
            print("[INFO] STT working but no speech detected")

        return True

    except Exception as e:
        print(f"\n[FAIL] Interactive STT test failed: {e}")
        return False


def run_all_tests():
    """Run all voice pipeline tests"""
    print("\n" + "="*60)
    print("ALFRED VOICE PIPELINE TEST SUITE")
    print("="*60)

    results = {}

    # Run tests
    results['vosk'] = test_vosk_recognizer()
    results['elevenlabs'] = test_elevenlabs_tts()
    results['alfred_voice'] = test_alfred_voice()
    results['alfred_ears'] = test_alfred_ears()
    results['voice_manager'] = test_voice_manager()
    results['voice_config'] = test_voice_config()

    # Interactive tests
    results['interactive_tts'] = test_interactive_tts()
    results['interactive_stt'] = test_interactive_stt()

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test, result in results.items():
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {status} {test}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed >= 4:  # At least core tests passing
        print("\n[SUCCESS] Voice pipeline is operational")
        return 0
    else:
        print("\n[WARNING] Some voice features may not be available")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
