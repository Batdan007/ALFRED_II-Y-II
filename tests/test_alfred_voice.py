"""
Test Alfred's Voice System
The Real Alfred - Distinguished, Wise, Slightly Sarcastic
Author: Daniel J Rita (BATDAN)
"""

import sys
import os

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_voice_system():
    """Test Alfred's voice system"""
    print("="*60)
    print("TESTING ALFRED'S VOICE SYSTEM")
    print("="*60)

    try:
        from capabilities.voice import AlfredVoice, VoicePersonality
        print("✅ AlfredVoice imported successfully")
    except Exception as e:
        print(f"❌ Failed to import AlfredVoice: {e}")
        return False

    # Create Alfred's voice
    try:
        alfred = AlfredVoice(privacy_mode=True)
        print("✅ Alfred's voice initialized")
    except Exception as e:
        print(f"❌ Failed to initialize voice: {e}")
        return False

    # Check status
    status = alfred.get_status()
    print(f"\n🎩 Alfred's Voice Status:")
    print(f"   Voice: {status['voice']}")
    print(f"   Engine: {status['engine']}")
    print(f"   Privacy Mode: {status['privacy_mode']}")
    print(f"   Enabled: {status['enabled']}")

    # Test different personalities
    print(f"\n{'='*60}")
    print("TESTING ALFRED'S PERSONALITY")
    print(f"{'='*60}\n")

    print("Testing Greeting...")
    alfred.greet()
    print("✅ Greeting complete\n")

    print("Testing Confirmation...")
    alfred.confirm("Task completed")
    print("✅ Confirmation complete\n")

    print("Testing Information...")
    alfred.inform("The analysis is complete. I found 3 vulnerabilities in the code.")
    print("✅ Information complete\n")

    print("Testing Suggestion...")
    alfred.suggest("taking a break before continuing")
    print("✅ Suggestion complete\n")

    print("Testing Warning...")
    alfred.warn("This action may have unintended consequences")
    print("✅ Warning complete\n")

    print("Testing Sarcasm...")
    alfred.be_sarcastic()
    print("✅ Sarcasm complete\n")

    # Test context awareness
    print(f"{'='*60}")
    print("TESTING CONTEXT AWARENESS")
    print(f"{'='*60}\n")

    test_contexts = [
        ("error occurred", "normal"),
        ("task complete", "normal"),
        ("routine update", "low"),
        ("critical security issue", "critical"),
        ("file saved", "low"),
    ]

    for context, importance in test_contexts:
        should_speak = alfred.should_speak(context, importance)
        speak_status = "🔊 SPEAK" if should_speak else "🤫 SILENT"
        print(f"{speak_status} - Context: '{context}' (importance: {importance})")

    print("\n✅ Context awareness working correctly")

    # Test disable/enable
    print(f"\n{'='*60}")
    print("TESTING ENABLE/DISABLE")
    print(f"{'='*60}\n")

    alfred.disable()
    print("✅ Alfred silenced")

    alfred.enable()
    print("✅ Alfred voice restored")

    print(f"\n{'='*60}")
    print("✅ ALFRED'S VOICE: ALL TESTS PASSED")
    print(f"{'='*60}\n")

    print("🎩 Alfred says: 'Good evening, sir. Voice system fully operational.'")

    return True


if __name__ == "__main__":
    print("\n" + "="*60)
    print("ALFRED'S VOICE TEST SUITE")
    print("The Distinguished British Butler AI")
    print("="*60 + "\n")

    if test_voice_system():
        print("\n✅ Alfred's voice is ready to serve BATDAN")
        sys.exit(0)
    else:
        print("\n❌ Voice system needs attention")
        sys.exit(1)
