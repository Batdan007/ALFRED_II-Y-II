"""
Voice Diagnostic Script
Check which TTS voices are available on this system

Author: Daniel J Rita (BATDAN)
"""

import pyttsx3
import platform

def check_available_voices():
    """List all available voices on the system"""
    print(f"Platform: {platform.system()}\n")

    engine = pyttsx3.init()
    voices = engine.getProperty('voices')

    print(f"Found {len(voices)} voices:\n")

    for i, voice in enumerate(voices):
        print(f"{i+1}. {voice.name}")
        print(f"   ID: {voice.id}")
        print(f"   Languages: {voice.languages}")

        # Check if it's British or male
        is_british = 'gb' in voice.id.lower() or 'british' in voice.name.lower() or 'en-gb' in voice.id.lower()
        is_male = any(name in voice.name.lower() for name in ['david', 'george', 'ryan', 'james', 'mark', 'male'])

        tags = []
        if is_british:
            tags.append("BRITISH")
        if is_male:
            tags.append("MALE")

        if tags:
            print(f"   Tags: {', '.join(tags)}")

        print()

    # Check for specific voices
    ryan_found = any('ryan' in v.name.lower() for v in voices)
    george_found = any('george' in v.name.lower() for v in voices)
    hazel_found = any('hazel' in v.name.lower() for v in voices)
    british_found = any('en-gb' in v.id.lower() or 'gb' in v.id.lower() for v in voices)

    print("\nBritish Voice Status:")
    print(f"  Ryan (British male): {'FOUND' if ryan_found else 'NOT FOUND'}")
    print(f"  George (British gentleman): {'FOUND' if george_found else 'NOT FOUND'}")
    if hazel_found:
        print(f"  Hazel (British female): FOUND (temporary fallback)")

    if not ryan_found and not george_found:
        print("\n" + "="*60)
        print("ISSUE: No British male voices found!")
        print("="*60)
        if hazel_found:
            print("\nHazel (British female) is available and will be used temporarily.")
            print("However, Alfred prefers a British male voice (Ryan or George).")
        else:
            print("\nNo British voices found at all!")
        print("\nTo install Microsoft Ryan (British male voice):")
        print("1. Open Windows Settings")
        print("2. Go to Time & Language > Speech")
        print("3. Click 'Add voices'")
        print("4. Search for 'Ryan' or 'English (United Kingdom)'")
        print("5. Download and install 'Microsoft Ryan Online (Natural) - English (United Kingdom)'")
        print("\nAlternatively, install George or other British English voices.")
        print("\nAfter installation, restart this script to verify.")

if __name__ == "__main__":
    check_available_voices()
