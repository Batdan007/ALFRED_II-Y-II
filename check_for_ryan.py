"""
Check if Ryan voice is installed
Author: Daniel J Rita (BATDAN)
"""

import sys
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

import pyttsx3

print("\n" + "="*60)
print("CHECKING FOR RYAN (British Male Voice)")
print("="*60 + "\n")

engine = pyttsx3.init()
voices = engine.getProperty('voices')

print(f"Total voices installed: {len(voices)}\n")

ryan_found = False
male_voices = []

for voice in voices:
    name = voice.name
    name_lower = name.lower()

    is_male = any(n in name_lower for n in ['david', 'george', 'ryan', 'james', 'mark', 'male'])
    is_female = any(n in name_lower for n in ['hazel', 'zira', 'susan', 'female'])

    gender = "MALE" if is_male else ("FEMALE" if is_female else "UNKNOWN")

    print(f"- {name}")
    print(f"  Gender: {gender}")
    print(f"  Languages: {voice.languages}")
    print(f"  ID: {voice.id}")

    if 'ryan' in name_lower:
        ryan_found = True
        print(f"  ✅ THIS IS RYAN - PERFECT FOR ALFRED!")
    elif is_male:
        male_voices.append(name)

    print()

print("="*60)
print("SUMMARY")
print("="*60 + "\n")

if ryan_found:
    print("✅ RYAN IS INSTALLED!")
    print("   Alfred will use Ryan's voice (British male)")
else:
    print("❌ RYAN NOT FOUND")
    print("\n   Current male voices available:")
    if male_voices:
        for v in male_voices:
            print(f"   - {v}")
    else:
        print("   - NONE (only female voices installed!)")

    print("\n   TO INSTALL RYAN:")
    print("   1. Run: install_british_voice.ps1")
    print("   2. Or manually: Settings > Time & Language > Language")
    print("   3. Add 'English (United Kingdom)'")
    print("   4. Install with Text-to-Speech option")
    print("\n   After install, you'll have Ryan (British male)")

print("\n" + "="*60)
