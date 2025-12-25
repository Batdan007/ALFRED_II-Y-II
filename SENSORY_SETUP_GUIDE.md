# ALFRED-UBX Complete Sensory Setup Guide
## Vision, Voice, and Hearing Integration

**Author:** Daniel J Rita (BATDAN)
**Date:** December 10, 2025
**Version:** 3.0.0

---

## Table of Contents

1. [Overview](#overview)
2. [System Requirements](#system-requirements)
3. [Quick Start (Experienced Users)](#quick-start)
4. [Detailed Installation](#detailed-installation)
5. [Configuration](#configuration)
6. [Usage Guide](#usage-guide)
7. [Troubleshooting](#troubleshooting)
8. [Privacy & Security](#privacy--security)

---

## Overview

ALFRED-UBX now has **complete sensory integration**:

✅ **👁️ VISION** - Sees through camera, recognizes faces (especially BATDAN)
✅ **👂 HEARING** - Listens via microphone, recognizes voices (filters out TV/others)
✅ **🗣️ VOICE** - Speaks with British butler personality (already working)
✅ **💭 PERSONAL MEMORY** - Remembers BATDAN, Joe Dog, and all personal connections

### Key Features

- **Face Recognition**: ALFRED recognizes BATDAN and other people you teach him
- **Speaker Identification**: ALFRED only responds to BATDAN's voice (ignores TV/others)
- **Personal Memories**: ALFRED knows about Joe Dog and your personal history
- **Privacy-First**: All processing happens locally (no cloud required for sensory)

---

## System Requirements

### Hardware

- **Camera**: Webcam (built-in or USB, 720p or higher recommended)
- **Microphone**: Built-in or external microphone
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 2GB free space for libraries

### Software

- **Python**: 3.10 or higher (3.12 recommended)
- **OS**: Windows 10/11, macOS 12+, or Linux (Ubuntu 20.04+)
- **Build Tools**: Required for some dependencies (see below)

---

## Quick Start (Experienced Users)

```bash
# 1. Install system dependencies
# Windows: Install Visual C++ Build Tools and CMake
# macOS: brew install cmake portaudio ffmpeg
# Linux: sudo apt-get install build-essential cmake libportaudio2 portaudio19-dev ffmpeg

# 2. Install Python dependencies
pip install -r requirements.txt
pip install -r requirements_sensory.txt

# 3. Apply sensory integration to alfred_terminal.py
# (See SENSORY_INTEGRATION.md for manual steps)

# 4. Run ALFRED
python alfred_terminal.py

# 5. Teach ALFRED who you are
/remember BATDAN  # Teach your face
/learn_voice      # Teach your voice
```

---

## Detailed Installation

### Step 1: Install System Dependencies

#### Windows

1. **Install Visual C++ Build Tools**:
   - Download: https://visualstudio.microsoft.com/visual-cpp-build-tools/
   - Run installer
   - Select "Desktop development with C++"
   - Install

2. **Install CMake** (for dlib):
   - Download: https://cmake.org/download/
   - Install and add to PATH

3. **Verify Installation**:
   ```cmd
   cmake --version
   ```

#### macOS

```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install build tools
brew install cmake

# Install audio libraries
brew install portaudio ffmpeg

# Verify installation
cmake --version
```

#### Linux (Ubuntu/Debian)

```bash
# Install build tools
sudo apt-get update
sudo apt-get install build-essential cmake

# Install audio libraries
sudo apt-get install libportaudio2 portaudio19-dev python3-pyaudio

# Install multimedia libraries
sudo apt-get install ffmpeg

# Verify installation
cmake --version
```

---

### Step 2: Install Python Dependencies

```bash
# Navigate to ALFRED-UBX directory
cd C:\ALFRED_UBX  # Windows
# cd ~/ALFRED_UBX  # macOS/Linux

# Install core dependencies (if not already installed)
pip install -r requirements.txt

# Install sensory dependencies
pip install -r requirements_sensory.txt
```

**Expected Output:**
```
Successfully installed opencv-python-4.8.1.78
Successfully installed face-recognition-1.3.0
Successfully installed dlib-19.24.2
Successfully installed SpeechRecognition-3.10.1
Successfully installed PyAudio-0.2.14
Successfully installed librosa-0.10.1
Successfully installed resemblyzer-0.1.1.dev0
...
```

---

### Step 3: Verify Installation

Run this test to verify all libraries are installed:

```bash
python -c "import cv2; import face_recognition; import speech_recognition; print('✅ All sensory libraries installed successfully!')"
```

**Expected Output:**
```
✅ All sensory libraries installed successfully!
```

---

### Step 4: Apply Sensory Integration

**Option A: Manual Integration** (Recommended for existing alfred_terminal.py)

1. Open `alfred_terminal_sensory_integration.py`
2. Copy each section into `alfred_terminal.py` as indicated
3. Save alfred_terminal.py

**Option B: Automatic Integration** (Coming soon)

```bash
python install_sensory_integration.py
```

---

### Step 5: Test Camera and Microphone

#### Test Camera

```bash
python -c "import cv2; cap = cv2.VideoCapture(0); ret, frame = cap.read(); print('✅ Camera working' if ret else '❌ Camera not detected'); cap.release()"
```

#### Test Microphone

```bash
python -c "import speech_recognition as sr; r = sr.Recognizer(); m = sr.Microphone(); print(f'✅ Microphone working: {m}' if m else '❌ Microphone not detected')"
```

#### List Available Devices

```python
# List microphones
python -c "import speech_recognition as sr; print('\n'.join([f'{i}: {name}' for i, name in enumerate(sr.Microphone.list_microphone_names())]))"

# List cameras
python -c "import cv2; print('Testing cameras...'); [print(f'Camera {i}: {'✅ Working' if cv2.VideoCapture(i).isOpened() else '❌ Not available'}') for i in range(5)]"
```

---

## Configuration

### Camera Configuration

If you have multiple cameras, specify which one to use:

```python
# In alfred_terminal.py or when creating AlfredEyes
self.eyes = AlfredEyes(brain=self.brain, camera_index=0)  # 0 = default camera
# camera_index=1 for second camera, etc.
```

### Microphone Configuration

If you have multiple microphones, specify which one:

```python
# In alfred_terminal.py
/stop_listening  # First, stop listening if active
# Then in Python:
self.ears.set_microphone(device_index=1)  # 1 = second microphone
```

### Voice Recognition Sensitivity

Adjust speaker identification threshold:

```python
# In alfred_ears_advanced.py
self.batdan_voice_threshold = 0.75  # Default
# Higher = more strict (fewer false positives)
# Lower = more lenient (may accept similar voices)
```

### Noise Filtering

Adjust microphone sensitivity for noisy environments:

```python
# In alfred_ears_advanced.py
self.energy_threshold = 4000  # Default
# Higher = less sensitive (filters more noise)
# Lower = more sensitive (picks up quieter sounds)
```

---

## Usage Guide

### Initial Setup (First Time)

1. **Start ALFRED**:
   ```bash
   python alfred_terminal.py
   ```

2. **Teach Your Face**:
   ```
   /remember BATDAN
   ```
   - Look directly at camera
   - Good lighting helps
   - Remove sunglasses/hats

3. **Teach Your Voice**:
   ```
   /learn_voice
   ```
   - Speak naturally for 5 seconds
   - Use your normal speaking voice
   - Quiet environment recommended

4. **Verify Status**:
   ```
   /status
   ```

---

### Daily Usage

#### Vision Commands

```bash
# See who is in view
/see

# Live camera view with face detection
/watch
# Press 'q' to quit, 'r' to remember current face

# Teach ALFRED to recognize someone else
/remember Alice
```

#### Hearing Commands

```bash
# Start listening for voice commands
/listen
# Say "stop listening" to stop, or press Ctrl+C

# Re-train voice recognition
/learn_voice

# Stop listening mode
/stop_listening
```

#### Voice Commands

```bash
# Enable/disable ALFRED's voice
/voice on
/voice off
```

#### Personal Memory

```bash
# Pay tribute to Joe Dog
/joe

# View all system status
/status
```

---

### Example Workflow

**Morning Routine:**

1. Start ALFRED: `python alfred_terminal.py`
2. ALFRED sees you via camera and greets: *"Welcome back, sir. Good to see you again."*
3. Enable voice: `/voice on`
4. Start listening: `/listen`
5. Speak naturally: "Alfred, what's on my agenda today?"
6. ALFRED responds (voice + text)

**Teaching ALFRED:**

- First person: `/remember BATDAN`
- Family member: `/remember Alice`
- Friend: `/remember Bob`
- Re-train voice: `/learn_voice`

---

## Troubleshooting

### Common Issues

#### 1. Camera Not Detected

**Problem:** `❌ Camera not available - vision disabled`

**Solutions:**

```bash
# Test camera access
python -c "import cv2; cap = cv2.VideoCapture(0); print('Working' if cap.isOpened() else 'Failed'); cap.release()"

# Windows: Check camera permissions
# Settings > Privacy > Camera > Allow desktop apps

# macOS: Check camera permissions
# System Settings > Privacy & Security > Camera > Terminal (or your IDE)

# Linux: Check video devices
ls -l /dev/video*
# Add user to video group if needed
sudo usermod -a -G video $USER
```

#### 2. Microphone Not Detected

**Problem:** `❌ Microphone not available - hearing disabled`

**Solutions:**

```bash
# List available microphones
python -c "import speech_recognition as sr; print('\n'.join(sr.Microphone.list_microphone_names()))"

# Windows: Check microphone permissions
# Settings > Privacy > Microphone > Allow desktop apps

# macOS: Check microphone permissions
# System Settings > Privacy & Security > Microphone > Terminal

# Linux: Check audio devices
arecord -l
# Test recording
arecord -d 5 test.wav && aplay test.wav
```

#### 3. dlib Installation Fails

**Problem:** `error: Microsoft Visual C++ 14.0 or greater is required`

**Solutions:**

**Windows:**
```cmd
# Install Visual C++ Build Tools
# https://visualstudio.microsoft.com/visual-cpp-build-tools/

# Or download pre-built dlib wheel
# https://github.com/z-mahmud22/Dlib_Windows_Python3.x
pip install dlib-19.24.2-cp312-cp312-win_amd64.whl
```

**macOS/Linux:**
```bash
# Install cmake first
brew install cmake  # macOS
sudo apt-get install cmake  # Linux

# Then install dlib
pip install dlib --no-cache-dir
```

#### 4. PyAudio Installation Fails

**Problem:** `error: portaudio.h: No such file or directory`

**Solutions:**

**Windows:**
```cmd
# Download pre-built wheel
# https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
pip install PyAudio‑0.2.11‑cp312‑cp312‑win_amd64.whl
```

**macOS:**
```bash
brew install portaudio
pip install pyaudio
```

**Linux:**
```bash
sudo apt-get install portaudio19-dev
pip install pyaudio
```

#### 5. Face Recognition Not Working

**Problem:** ALFRED doesn't recognize faces

**Checklist:**

- ✅ Good lighting (not backlit)
- ✅ Face clearly visible (no hats/sunglasses)
- ✅ Camera at eye level
- ✅ 2-4 feet from camera
- ✅ `/remember` completed successfully

**Re-train:**
```bash
/remember BATDAN  # Re-learn face with better conditions
```

#### 6. Voice Recognition Not Working

**Problem:** ALFRED doesn't recognize voice or responds to TV

**Solutions:**

```bash
# Re-train with better audio quality
/learn_voice

# Adjust sensitivity in alfred_ears_advanced.py:
self.batdan_voice_threshold = 0.85  # More strict (less false positives)

# Test in quiet environment first
# Move microphone closer
# Reduce background noise
```

#### 7. ALFRED Responds to TV/Other People

**Problem:** ALFRED reacts to voices on TV or other people

**Solution:**

```bash
# Ensure BATDAN's voice is learned
/learn_voice

# Increase voice recognition threshold
# Edit alfred_ears_advanced.py:
self.batdan_voice_threshold = 0.85  # More strict

# Use wake word
/listen  # Will only respond to BATDAN after wake word "Alfred"
```

---

## Privacy & Security

### Data Storage

**All sensory data is stored locally:**

- **Face Encodings**: `C:/Drive/data/faces/batdan.npy` (or ~/.alfred/data/faces/)
- **Voice Patterns**: `C:/Drive/data/voices/batdan_voice.pkl`
- **Personal Memories**: `C:/Drive/data/alfred_brain.db` (SQLite)

**No cloud storage** - Everything stays on your computer.

### Permissions Required

**Camera:**
- Windows: Settings > Privacy > Camera
- macOS: System Settings > Privacy & Security > Camera
- Linux: User must be in `video` group

**Microphone:**
- Windows: Settings > Privacy > Microphone
- macOS: System Settings > Privacy & Security > Microphone
- Linux: User must be in `audio` group

### Disabling Sensory Features

If you want to disable specific features:

```python
# In alfred_terminal.py

# Disable vision
self.eyes = None

# Disable hearing
self.ears = None

# Disable voice
self.voice_enabled = False
```

Or simply don't install the sensory dependencies:
```bash
pip install -r requirements.txt  # Core only, no sensory
```

---

## Advanced Configuration

### Using External AI Vision

Integrate GPT-4 Vision or Claude Vision for scene analysis:

```python
# In alfred_eyes.py, implement analyze_scene_with_ai():
def analyze_scene_with_ai(self, prompt: str = "Describe what you see"):
    frame = self.capture_frame()

    # Convert to base64
    import base64
    _, buffer = cv2.imencode('.jpg', frame)
    image_base64 = base64.b64encode(buffer).decode('utf-8')

    # Call GPT-4 Vision or Claude Vision
    # (Implementation depends on your AI client)
    response = your_ai_client.vision_analyze(image_base64, prompt)

    return response
```

### Multi-Camera Setup

Use multiple cameras for different angles:

```python
# In alfred_terminal.py
self.eyes_front = AlfredEyes(brain=self.brain, camera_index=0)
self.eyes_side = AlfredEyes(brain=self.brain, camera_index=1)
```

### Voice Commands Integration

Create custom voice commands:

```python
# In alfred_ears_advanced.py
CUSTOM_COMMANDS = {
    'lights on': lambda: control_lights(True),
    'lights off': lambda: control_lights(False),
    'play music': lambda: start_music(),
}
```

---

## Testing Checklist

Use this checklist to verify everything works:

```
□ ALFRED starts without errors
□ Camera is detected (/status shows vision active)
□ Microphone is detected (/status shows hearing active)
□ Voice works (/voice on, ALFRED speaks)
□ Face recognition works (/remember BATDAN)
□ ALFRED sees me (/see shows "BATDAN")
□ Live camera view works (/watch, press 'q')
□ Voice recognition works (/learn_voice)
□ ALFRED hears me (/listen, speak naturally)
□ ALFRED ignores TV/others (only responds to me)
□ Personal memory works (/joe shows tribute)
□ Status shows all systems active (/status)
```

---

## Minimum vs Recommended Setup

### Minimum Setup (Works without build tools)

```bash
# If you can't install dlib/face_recognition due to build errors
pip install pyttsx3 SpeechRecognition PyAudio opencv-python

# ALFRED will work but:
# - No face recognition (generic face detection only)
# - No speaker identification (listens to everyone)
# - Voice and basic vision still work
```

### Recommended Setup (Full capabilities)

```bash
# Full installation with all features
pip install -r requirements_sensory.txt

# ALFRED will have:
# ✅ Face recognition (knows BATDAN specifically)
# ✅ Speaker identification (filters out TV/others)
# ✅ Voice, vision, hearing all integrated
```

---

## Support & Feedback

**GitHub:** https://github.com/Batdan007/ALFRED_UBX
**Issues:** https://github.com/Batdan007/ALFRED_UBX/issues
**Email:** daniel@alfred-ubx.com

---

## What's Next?

Once sensory integration is working:

1. **Train ALFRED**: Teach him to recognize your face and voice
2. **Add family/friends**: Use `/remember <name>` for each person
3. **Use voice mode**: `/listen` for hands-free interaction
4. **Explore AI vision**: Implement scene analysis with GPT-4 Vision
5. **Build custom commands**: Add voice-activated automations

---

**Welcome to the future of AI - where ALFRED truly sees, hears, and remembers you.**

---

© 2025 Daniel J Rita (BATDAN) | Patent Pending | MIT License
