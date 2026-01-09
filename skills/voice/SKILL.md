# Voice Skill

## Identity
**Name**: Alfred Voice System
**Personality**: Distinguished British butler, can be interrupted

## USE WHEN
User mentions any of:
- "voice", "speak", "say", "tell me"
- "listen", "hear", "microphone"
- "wake word", "hey alfred", "batcomputer"
- "learn voice", "recognize me"
- "silent", "mute", "quiet"

## CAPABILITIES
- Text-to-speech (Edge TTS Ryan, ElevenLabs, pyttsx3)
- Speech-to-text (VOSK offline, Google fallback)
- Speaker recognition (BATDAN identification)
- Wake word detection
- Interruptible playback (Escape key)

## COMMANDS
- `/voice`: Toggle voice on/off
- `/listen`: Listen for single command
- `/learn_voice`: Train speaker recognition
- `/always_listen`: Continuous listening mode
- `/wakeword`: Wake word detection mode

## WORKFLOW
1. OBSERVE: Detect audio input
2. THINK: Identify speaker (BATDAN vs others)
3. PLAN: Route to appropriate handler
4. BUILD: Process speech to text
5. EXECUTE: Respond with voice if enabled
6. VERIFY: Confirm understanding
7. LEARN: Improve voice recognition over time

## EXAMPLES
```
User: "Enable voice"
Action: voice.enable()

User: "Learn my voice"
Action: ears.learn_voice(name="BATDAN", duration=5)

User: "Listen for commands"
Action: ears.listen_for_wake_word(callback=process_command)
```

## TTS PRIORITY
1. Edge TTS (Microsoft Ryan Neural) - Primary on Windows
2. ElevenLabs (Cloud, premium quality)
3. pyttsx3 (Local fallback)

## STT PRIORITY
1. VOSK (Offline, privacy-first)
2. Google Speech (Online fallback)
