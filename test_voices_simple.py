"""
Simple Alfred Voice Test - Automatic playback
Author: Daniel J Rita (BATDAN)
"""

import sys
import os
import time

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pyttsx3


def test_voice(voice_id, voice_name):
    """Test a voice with Alfred's phrases"""
    print(f"\n{'='*60}")
    print(f"TESTING: {voice_name}")
    print(f"{'='*60}\n")

    engine = pyttsx3.init()
    engine.setProperty('voice', voice_id)
    engine.setProperty('rate', 175)

    phrases = [
        "Good evening, sir.",
        "Good evening, Master Rita.",
        "The Batcomputer is online, sir.",
        "Right away, sir.",
        "I must advise caution, sir.",
        "As you wish, sir. Though I suspect you know where this leads."
    ]

    for phrase in phrases:
        print(f"🎩 Alfred: {phrase}")
        engine.say(phrase)
        engine.runAndWait()
        time.sleep(0.5)

    print(f"\n✅ {voice_name} test complete")


def main():
    print("\n" + "="*60)
    print("ALFRED VOICE AUTOMATIC TEST")
    print("="*60)

    engine = pyttsx3.init()
    voices = engine.getProperty('voices')

    print(f"\nFound {len(voices)} voices on your system:\n")

    # Find Hazel (British GB voice)
    hazel = None
    david = None

    for voice in voices:
        print(f"- {voice.name} ({voice.languages})")
        if 'hazel' in voice.name.lower():
            hazel = voice
        elif 'david' in voice.name.lower():
            david = voice

    print("\n" + "="*60)
    print("RECOMMENDED FOR ALFRED:")
    print("="*60)

    if hazel:
        print("✅ Microsoft Hazel (British - Great Britain accent)")
        print("   This is the BEST choice for Alfred!")
        print("   Real British accent, distinguished sound")
    else:
        print("⚠️ No British voice found")

    print("\nNow you'll hear each voice say Alfred's phrases...")
    print("Listen and pick your favorite!\n")

    time.sleep(2)

    # Test Hazel first (best option)
    if hazel:
        print("\n" + "🎩"*30)
        print("VOICE 1: HAZEL (RECOMMENDED)")
        print("🎩"*30)
        test_voice(hazel.id, "Microsoft Hazel - British (GB)")
        time.sleep(2)

    # Test David (fallback)
    if david:
        print("\n" + "🎩"*30)
        print("VOICE 2: DAVID (US Accent - Fallback)")
        print("🎩"*30)
        test_voice(david.id, "Microsoft David - US")

    print("\n" + "="*60)
    print("VOICE TEST COMPLETE")
    print("="*60)

    print("\n🎯 RECOMMENDATION:")
    if hazel:
        print("   Use HAZEL for Alfred's voice")
        print("   Real British Great Britain accent")
        print("   Distinguished and proper")
    else:
        print("   Use David (best available)")

    print("\n✅ Voice system working perfectly")
    print("   Alfred is ready to speak!\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
