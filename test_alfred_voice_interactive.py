"""
Interactive Alfred Voice Test
Hear Alfred speak and test different voices
Author: Daniel J Rita (BATDAN)
"""

import sys
import os

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pyttsx3


def list_all_voices():
    """List all available voices on the system"""
    print("\n" + "="*60)
    print("AVAILABLE VOICES ON YOUR SYSTEM")
    print("="*60 + "\n")

    engine = pyttsx3.init()
    voices = engine.getProperty('voices')

    print(f"Found {len(voices)} voices:\n")

    for i, voice in enumerate(voices):
        print(f"{i}. {voice.name}")
        print(f"   ID: {voice.id}")
        print(f"   Languages: {voice.languages}")
        print()

    return voices


def test_voice(voice_id, test_phrases):
    """Test a specific voice"""
    engine = pyttsx3.init()
    engine.setProperty('voice', voice_id)
    engine.setProperty('rate', 175)  # Slightly slower for distinguished effect

    for phrase in test_phrases:
        print(f"\n🎩 Alfred: {phrase}")
        engine.say(phrase)
        engine.runAndWait()


def find_best_alfred_voice(voices):
    """Find the best Alfred voice"""
    print("\n" + "="*60)
    print("SEARCHING FOR BEST ALFRED VOICE")
    print("="*60 + "\n")

    # Priority order
    george = None
    ryan = None
    british = []
    male = []

    for voice in voices:
        name_lower = voice.name.lower()

        if 'george' in name_lower:
            george = voice
            print(f"✅ Found GEORGE: {voice.name}")
        elif 'ryan' in name_lower:
            ryan = voice
            print(f"✅ Found Ryan: {voice.name}")
        elif any(word in name_lower for word in ['british', 'english', 'uk']):
            british.append(voice)
            print(f"✅ Found British voice: {voice.name}")
        elif any(word in name_lower for word in ['male', 'david', 'james', 'mark']):
            male.append(voice)

    print("\n" + "="*60)
    print("RECOMMENDED VOICES (in priority order):")
    print("="*60 + "\n")

    candidates = []

    if george:
        print("1. GEORGE (BEST - Older British gentleman) ⭐⭐⭐")
        print(f"   {george.name}")
        candidates.append(('George', george))

    if ryan:
        print("2. Ryan (Good - British accent) ⭐⭐")
        print(f"   {ryan.name}")
        candidates.append(('Ryan', ryan))

    if british:
        print("3. Other British voices ⭐")
        for v in british[:3]:
            print(f"   {v.name}")
            candidates.append((v.name, v))

    if male and not george and not ryan and not british:
        print("4. Male voices (fallback)")
        for v in male[:3]:
            print(f"   {v.name}")
            candidates.append((v.name, v))

    return candidates


def main():
    print("\n" + "="*60)
    print("ALFRED VOICE INTERACTIVE TEST")
    print("Let's find the perfect voice for Alfred")
    print("="*60)

    # List all voices
    voices = list_all_voices()

    # Find best candidates
    candidates = find_best_alfred_voice(voices)

    if not candidates:
        print("\n❌ No suitable voices found")
        return

    # Test phrases
    test_phrases = [
        "Good evening, sir.",
        "Good evening, Master Rita.",
        "The Batcomputer is online, sir.",
        "Right away, sir.",
        "I must advise caution, sir.",
        "Might I suggest taking a break, sir?",
        "As you wish, sir. Though I suspect you know where this leads.",
        "All systems operational, sir."
    ]

    print("\n" + "="*60)
    print("TESTING EACH VOICE")
    print("="*60)
    print("\nYou will hear each candidate voice speak Alfred's phrases.")
    print("Listen and decide which one sounds best!\n")

    input("Press ENTER to start testing voices...")

    for i, (name, voice) in enumerate(candidates, 1):
        print("\n" + "="*60)
        print(f"TESTING VOICE {i}: {name}")
        print("="*60)
        print(f"Voice: {voice.name}")

        input(f"\nPress ENTER to hear {name}...")

        test_voice(voice.id, test_phrases[:3])  # Test first 3 phrases

        print(f"\n✅ {name} test complete")

        if i < len(candidates):
            choice = input(f"\nContinue to next voice? (y/n): ").lower()
            if choice != 'y':
                break

    print("\n" + "="*60)
    print("VOICE TESTING COMPLETE")
    print("="*60)
    print("\nWhich voice did you like best?")
    print("\nOptions:")
    for i, (name, _) in enumerate(candidates, 1):
        print(f"{i}. {name}")

    try:
        choice = input("\nEnter number (or 'all' to hear all again): ").strip()

        if choice.lower() == 'all':
            print("\nPlaying all voices again...")
            for name, voice in candidates:
                print(f"\n🎩 {name}:")
                test_voice(voice.id, test_phrases[:1])
        elif choice.isdigit() and 1 <= int(choice) <= len(candidates):
            idx = int(choice) - 1
            name, voice = candidates[idx]
            print(f"\n✅ You selected: {name}")
            print(f"   Voice ID: {voice.id}")
            print(f"   This will be Alfred's voice!")
            print(f"\nPlaying full test...")
            test_voice(voice.id, test_phrases)
    except:
        pass

    print("\n" + "="*60)
    print("🎩 Alfred Voice Test Complete")
    print("="*60)
    print("\nNext steps:")
    print("1. If you found the perfect voice, we'll use it")
    print("2. If no voice was good enough, we can install ElevenLabs")
    print("3. Voice configuration will be saved to ALFRED-UBX\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
