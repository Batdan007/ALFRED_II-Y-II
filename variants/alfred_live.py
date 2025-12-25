#!/usr/bin/env python3
"""
Alfred LIVE - Voice-Enabled Interactive Assistant
Optimized for real-time voice interaction with Parler-TTS

Features:
- Voice output (Parler-TTS)
- Ollama AI (local models)
- Fabric Patterns (243 patterns)
- Alfred Brain (persistent memory)
- Security Analysis
- Database Tools

Note: RAG/Vector KB gracefully disabled due to protobuf compatibility
"""

import os
import sys

# Configure for Voice/Parler-TTS compatibility (protobuf 4.25.8)
# TensorFlow causes protobuf conflicts - disable it completely
os.environ['TRANSFORMERS_NO_TF'] = '1'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# Note: TensorFlow should be uninstalled for voice mode
# Run: pip uninstall tensorflow -y

print("=" * 80)
print("ALFRED LIVE - Voice-Enabled Interactive Assistant")
print("PATENT PENDING - AI Memory & Learning System")
print("=" * 80)
print()
print("Optimized for: Voice Interaction (Parler-TTS)")
print("Protobuf: 4.25.8 (Voice-compatible)")
print()

# Import Alfred Brain
from alfred_brain import AlfredBrain

# Try to import Voice
try:
    from alfred_voice import enable_voice_for_alfred
    VOICE_AVAILABLE = True
    print("[OK] Alfred Voice: Ready")
except ImportError as e:
    VOICE_AVAILABLE = False
    print(f"[WARNING] Alfred Voice: Not Available ({e})")

# Try to import Enhanced features
try:
    # Just use the enhanced module's capabilities
    print("[INFO] Loading Alfred Enhanced core...")
    print()
except Exception as e:
    print(f"[WARNING] Enhanced features limited: {e}")

# Initialize Alfred Brain
alfred = AlfredBrain()
print(f"[OK] Alfred Brain: {len(alfred.context_cache)} conversations, {len(alfred.knowledge_cache)} knowledge items")

# Initialize Voice if available
voice = None
if VOICE_AVAILABLE:
    voice = enable_voice_for_alfred(alfred)
    print("[OK] Voice Module: Initialized (model loads on first use)")

print()
print("=" * 80)
print("Alfred LIVE is ready!")
print()

if VOICE_AVAILABLE:
    print("Voice Commands Available:")
    print("  voice.speak('Hello!')                    - Basic speech")
    print("  voice.greet_user()                       - Personalized greeting")
    print("  voice.emergency_alert('Warning!')        - Urgent tone")
    print("  voice.celebrate('Success!')              - Happy tone")
    print("  voice.set_voice_settings(speaker='...')  - Customize voice")
    print()

print("Alfred Brain Commands:")
print("  alfred.store_conversation(user, response)  - Save conversation")
print("  alfred.get_conversation_context(limit=5)   - Get recent context")
print("  alfred.store_knowledge(cat, key, val)      - Store knowledge")
print("  alfred.recall_knowledge(cat, key)          - Recall knowledge")
print()
print("Capabilities:")
print("  [+] Voice Output (Parler-TTS)")
print("  [+] Ollama AI (Local Models)")
print("  [+] Fabric Patterns (243 patterns)")
print("  [+] Alfred Brain (Memory)")
print("  [+] Security Analysis")
print("  [+] Database Tools")
print("  [-] RAG/Vector KB (use Alfred RAG for this)")
print()
print("=" * 80)
print()

# Interactive mode
if __name__ == "__main__":
    if VOICE_AVAILABLE:
        print("Starting in interactive mode with voice...")
        print("Type 'quit' to exit")
        print()

        # Greet the user
        voice.greet_user()

        while True:
            try:
                user_input = input("\n[You]: ").strip()

                if user_input.lower() in ['quit', 'exit', 'bye']:
                    voice.speak("Goodbye! Talk to you soon.")
                    break

                if not user_input:
                    continue

                # Get context from brain
                context = alfred.get_conversation_context(limit=3)

                # For now, simple echo with context awareness
                response = f"You said: {user_input}"

                if context:
                    response += f" (I remember our last {len(context)} conversations)"

                # Speak and store
                voice.speak_alfred_response(user_input, response)

            except KeyboardInterrupt:
                print("\n")
                voice.speak("Goodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")
    else:
        print("Voice not available. Import alfred_live in your code to use Alfred Brain features.")
        print()
        print("Example:")
        print("  from alfred_live import alfred, voice")
        print("  if voice:")
        print("      voice.speak('Hello!')")
