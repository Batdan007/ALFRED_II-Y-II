"""
Test script to check all sensory integration imports and dependencies
"""

import sys
import traceback

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

print("=" * 80)
print("ALFRED-UBX Sensory Integration - Dependency Check")
print("=" * 80)

errors = []
warnings = []

# Test 1: Core imports
print("\n[1] Testing core imports...")
try:
    from core.path_manager import PathManager
    print("  ✅ PathManager imported")
except Exception as e:
    errors.append(f"PathManager import failed: {e}")
    print(f"  ❌ PathManager import failed: {e}")

try:
    from core.brain import AlfredBrain
    print("  ✅ AlfredBrain imported")
except Exception as e:
    errors.append(f"AlfredBrain import failed: {e}")
    print(f"  ❌ AlfredBrain import failed: {e}")

# Test 2: Vision imports
print("\n[2] Testing vision imports...")
try:
    from capabilities.vision.alfred_eyes import AlfredEyes
    print("  ✅ AlfredEyes imported")
except Exception as e:
    errors.append(f"AlfredEyes import failed: {e}")
    print(f"  ❌ AlfredEyes import failed: {e}")
    traceback.print_exc()

# Test 3: Hearing imports
print("\n[3] Testing hearing imports...")
try:
    from capabilities.voice.alfred_ears_advanced import AlfredEarsAdvanced
    print("  ✅ AlfredEarsAdvanced imported")
except Exception as e:
    errors.append(f"AlfredEarsAdvanced import failed: {e}")
    print(f"  ❌ AlfredEarsAdvanced import failed: {e}")
    traceback.print_exc()

# Test 4: Personal memory imports
print("\n[4] Testing personal memory imports...")
try:
    from core.personal_memory import PersonalMemory
    print("  ✅ PersonalMemory imported")
except Exception as e:
    errors.append(f"PersonalMemory import failed: {e}")
    print(f"  ❌ PersonalMemory import failed: {e}")
    traceback.print_exc()

# Test 5: Check brain methods
print("\n[5] Checking AlfredBrain methods...")
try:
    from core.brain import AlfredBrain
    brain = AlfredBrain()

    # Check for get_knowledge_by_category method
    if hasattr(brain, 'get_knowledge_by_category'):
        print("  ✅ get_knowledge_by_category method exists")
    else:
        errors.append("AlfredBrain missing method: get_knowledge_by_category")
        print("  ❌ get_knowledge_by_category method NOT FOUND")

except Exception as e:
    errors.append(f"Brain method check failed: {e}")
    print(f"  ❌ Brain method check failed: {e}")

# Test 6: Optional dependencies
print("\n[6] Testing optional dependencies...")

try:
    import cv2
    print("  ✅ OpenCV (cv2) available")
except ImportError:
    warnings.append("OpenCV not installed - vision features disabled")
    print("  ⚠️  OpenCV not installed")

try:
    import face_recognition
    print("  ✅ face_recognition available")
except ImportError:
    warnings.append("face_recognition not installed - face detection disabled")
    print("  ⚠️  face_recognition not installed")

try:
    import speech_recognition
    print("  ✅ SpeechRecognition available")
except ImportError:
    warnings.append("SpeechRecognition not installed - hearing disabled")
    print("  ⚠️  SpeechRecognition not installed")

try:
    import pyaudio
    print("  ✅ PyAudio available")
except ImportError:
    warnings.append("PyAudio not installed - microphone disabled")
    print("  ⚠️  PyAudio not installed")

try:
    import librosa
    print("  ✅ librosa available")
except ImportError:
    warnings.append("librosa not installed - advanced audio analysis disabled")
    print("  ⚠️  librosa not installed")

# Summary
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

if not errors:
    print("✅ All critical imports successful!")
else:
    print(f"❌ {len(errors)} ERRORS FOUND:")
    for i, error in enumerate(errors, 1):
        print(f"  {i}. {error}")

if warnings:
    print(f"\n⚠️  {len(warnings)} WARNINGS:")
    for i, warning in enumerate(warnings, 1):
        print(f"  {i}. {warning}")

print("\n" + "=" * 80)
sys.exit(len(errors))
