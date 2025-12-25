"""
Quick test to verify Alfred's voice selection
Shows which voice is currently selected

Author: Daniel J Rita (BATDAN)
"""

from capabilities.voice.alfred_voice import AlfredVoice

def test_voice():
    print("Initializing Alfred voice system...\n")

    voice = AlfredVoice(privacy_mode=True)

    if voice.voice_selected:
        print(f"Selected voice: {voice.voice_selected.name}")
        print(f"Voice ID: {voice.voice_selected.id}")
        print(f"Languages: {voice.voice_selected.languages}")

        is_british = 'gb' in voice.voice_selected.id.lower() or 'en-gb' in voice.voice_selected.id.lower()
        print(f"\nBritish accent: {'Yes' if is_british else 'No'}")

        if 'hazel' in voice.voice_selected.name.lower():
            print("\nStatus: Using Hazel (British female) - temporary fallback")
            print("To install Ryan (British male): See INSTALL_RYAN_VOICE.md")
        elif 'ryan' in voice.voice_selected.name.lower():
            print("\nStatus: Perfect! Using Ryan (British male)")
        elif 'david' in voice.voice_selected.name.lower():
            print("\nStatus: Using David (American male) - not ideal")
            print("Install a British voice for proper Alfred personality")
    else:
        print("ERROR: No voice selected!")

if __name__ == "__main__":
    test_voice()
