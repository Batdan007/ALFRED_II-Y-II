# ALFRED Sensory Integration - Quick Start
## Get ALFRED Seeing, Hearing, and Remembering in 15 Minutes

**For:** Daniel J Rita (BATDAN)
**Created:** December 10, 2025

---

## What You Need to Know

✅ **All sensory code is complete and ready**
✅ **Installation takes ~15 minutes**
✅ **ALFRED will see you, hear you, and remember Joe Dog**

---

## 15-Minute Setup

### Step 1: Install System Dependencies (5 minutes)

**Windows:**
```cmd
# Download and install Visual C++ Build Tools
# https://visualstudio.microsoft.com/visual-cpp-build-tools/
# Select "Desktop development with C++"
```

**macOS:**
```bash
brew install cmake portaudio ffmpeg
```

**Linux:**
```bash
sudo apt-get install build-essential cmake libportaudio2 portaudio19-dev ffmpeg
```

---

### Step 2: Install Python Dependencies (5 minutes)

```bash
cd C:\ALFRED_UBX

# Install sensory dependencies
pip install -r requirements_sensory.txt

# Or install individually if requirements file fails:
pip install opencv-python face-recognition SpeechRecognition PyAudio librosa soundfile resemblyzer deepface
```

**If dlib fails** (common on Windows):
```bash
# Download pre-built wheel from:
# https://github.com/z-mahmud22/Dlib_Windows_Python3.x
pip install dlib-19.24.2-cp312-cp312-win_amd64.whl
```

**If PyAudio fails**:
```bash
# Download from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
pip install PyAudio‑0.2.11‑cp312‑cp312‑win_amd64.whl
```

---

### Step 3: Verify Installation (1 minute)

```bash
python -c "import cv2, face_recognition, speech_recognition; print('✅ All sensory libraries installed!')"
```

**Expected:** `✅ All sensory libraries installed!`

---

### Step 4: Apply Sensory Integration (4 minutes)

Open `alfred_terminal_sensory_integration.py` and follow the 8 sections to update `alfred_terminal.py`.

**OR** (if you want to do it manually):

1. Open `alfred_terminal.py`
2. Open `alfred_terminal_sensory_integration.py` in another window
3. Copy each section from the integration file into alfred_terminal.py as marked:
   - Section 1: Imports (after line 43)
   - Section 2: __init__ additions (after line 63)
   - Section 3: _initialize_components additions
   - Section 4: New commands in _handle_command
   - Section 5: New command methods
   - Section 6: Updated show_greeting
   - Section 7: Updated _cmd_help
   - Section 8: Cleanup in _cmd_exit

4. Save alfred_terminal.py

---

### Step 5: Run ALFRED (1 second!)

```bash
python alfred_terminal.py
```

---

## First Time Usage (5 minutes)

### Teach ALFRED Who You Are

```bash
# 1. Start ALFRED
python alfred_terminal.py

# 2. Teach your face
> /remember BATDAN

[Look at camera]
✅ I shall remember BATDAN, sir.

# 3. Teach your voice
> /learn_voice

[Speak naturally for 5 seconds]
✅ I now recognize your voice, sir.

# 4. Verify status
> /status

[Shows all systems active]

# 5. Test vision
> /see

👁️ Alfred's Vision
┌────────┬────────────┐
│ BATDAN │ 98.5%      │
└────────┴────────────┘

# 6. Test voice listening
> /listen

[Say: "Alfred, tell me about Joe Dog"]
[ALFRED responds about Joe Dog]
[Say: "stop listening"]

# 7. Pay tribute to Joe Dog
> /joe

[ALFRED shows tribute to Joe Dog]
```

---

## Files You Created

### Core Sensory Systems
```
✅ capabilities/vision/alfred_eyes.py                  # Vision
✅ capabilities/voice/alfred_ears_advanced.py          # Hearing
✅ core/personal_memory.py                            # Personal memory
```

### Documentation
```
✅ SENSORY_SETUP_GUIDE.md                             # Full setup guide
✅ SENSORY_QUICK_START.md                             # This file
✅ COMPLETE_SENSORY_INTEGRATION_SUMMARY.md            # Complete summary
✅ alfred_terminal_sensory_integration.py             # Integration code
✅ requirements_sensory.txt                           # Dependencies
```

### Benchmarks (Already Created)
```
✅ ALFRED_BRAIN_BENCHMARK.md                          # Complete benchmark
✅ ALFRED_BRAIN_QUICK_REFERENCE.md                    # One-page reference
✅ ALFRED_BRAIN_INFOGRAPHIC.md                        # Visual infographic
✅ ALFRED_BRAIN_TEST_RESULTS.md                       # Test methodology
```

---

## Available Commands

### Vision
- `/see` - Show who ALFRED sees
- `/watch` - Live camera view (press 'q' to quit, 'r' to remember face)
- `/remember <name>` - Teach ALFRED to recognize someone

### Hearing
- `/listen` - Start listening for voice commands (only responds to BATDAN)
- `/learn_voice` - Teach ALFRED to recognize your voice
- `/stop_listening` - Stop listening mode

### Personal
- `/joe` - Pay tribute to Joe Dog
- `/status` - Show complete system status

### Existing
- `/help` - Show all commands
- `/memory` - Brain statistics
- `/voice on|off` - Enable/disable speaking
- `/exit` - Exit ALFRED

---

## Troubleshooting

### Camera Not Working
```bash
# Test camera
python -c "import cv2; cap = cv2.VideoCapture(0); print('✅ Working' if cap.isOpened() else '❌ Failed')"

# Check permissions (Windows)
# Settings > Privacy > Camera > Allow desktop apps

# Check permissions (macOS)
# System Settings > Privacy & Security > Camera > Terminal
```

### Microphone Not Working
```bash
# List microphones
python -c "import speech_recognition as sr; print('\n'.join(sr.Microphone.list_microphone_names()))"

# Check permissions (Windows)
# Settings > Privacy > Microphone > Allow desktop apps

# Check permissions (macOS)
# System Settings > Privacy & Security > Microphone > Terminal
```

### dlib Won't Install
```bash
# Windows: Install Visual C++ Build Tools first
# Or download pre-built wheel:
# https://github.com/z-mahmud22/Dlib_Windows_Python3.x

# macOS: Install cmake first
brew install cmake
pip install dlib --no-cache-dir

# Linux: Install build tools first
sudo apt-get install cmake
pip install dlib --no-cache-dir
```

### PyAudio Won't Install
```bash
# Windows: Download pre-built wheel
# https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio

# macOS:
brew install portaudio
pip install pyaudio

# Linux:
sudo apt-get install portaudio19-dev
pip install pyaudio
```

### ALFRED Doesn't Recognize Me
```bash
# Re-train with better conditions
/remember BATDAN   # Good lighting, face camera, no hat/sunglasses
/learn_voice       # Quiet environment, speak clearly
```

---

## What ALFRED Can Do Now

✅ **See you** - Recognizes your face via camera
✅ **Hear you** - Recognizes your voice via microphone
✅ **Speak to you** - British butler voice (already working)
✅ **Remember you** - Permanent memory of BATDAN
✅ **Remember Joe Dog** - Tribute stored forever
✅ **Filter others** - Only responds to BATDAN (ignores TV/strangers)
✅ **Learn continuously** - Every interaction stored in brain
✅ **Personal connection** - Knows who you are specifically

---

## Next Steps

1. **Install dependencies** (see Step 1-2 above)
2. **Apply integration** (see Step 4 above)
3. **Run ALFRED** (see Step 5 above)
4. **Train ALFRED** (teach face + voice)
5. **Test everything** (/see, /listen, /joe, /status)
6. **Use daily** - ALFRED will remember everything

---

## Support

- **Full Guide:** See `SENSORY_SETUP_GUIDE.md`
- **Summary:** See `COMPLETE_SENSORY_INTEGRATION_SUMMARY.md`
- **GitHub:** https://github.com/Batdan007/ALFRED_UBX

---

## The Vision

This is the beginning of something revolutionary:

**Personal AI companions that:**
- See you specifically
- Hear you specifically
- Remember you forever
- Know your history and connections
- Respect your privacy (100% local)

**ALFRED is the first. Others will follow this architecture.**

**The future of AI starts here, with BATDAN and Joe Dog.**

---

*"Good evening, sir. I am ready to see you, hear you, and remember everything we share together. Welcome home."* - ALFRED

---

© 2025 Daniel J Rita (BATDAN) | In Memory of Joe Dog | MIT License
