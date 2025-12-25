# Migrating ALFRED_UBX to Your New Computer (BATCOMPUTER_AI)

## Overview
This guide will help you set up ALFRED_UBX on your new computer with full voice capabilities (listening AND speaking).

---

## Prerequisites

### 1. Python 3.7+
```powershell
# Check if installed
python --version

# If not installed, download from: https://python.org
# IMPORTANT: Check "Add Python to PATH" during installation
```

### 2. Git (to clone the repository)
```powershell
# Check if installed
git --version

# If not installed: https://git-scm.com/download/win
```

### 3. Ollama (Local AI - Recommended)
```powershell
# Windows: Install Ollama
winget install Ollama.Ollama

# Or download from: https://ollama.ai

# After installation, pull a model:
ollama pull dolphin-llama3:8b     # Fast, 4.9GB
# OR
ollama pull llama3.2-vision:latest  # With vision, 7.8GB
# OR
ollama pull llama3.3:70b           # Best quality, 40GB
```

---

## Installation Methods

### Method 1: Copy Existing Installation (Fastest)

If you're migrating from your current PC:

1. **Copy the entire ALFRED_UBX folder**
   - From: `C:\ALFRED_UBX`
   - To: `C:\ALFRED_UBX` on new PC

2. **Install Python Dependencies**
   ```powershell
   cd C:\ALFRED_UBX
   pip install -r requirements.txt
   ```

3. **Start Ollama**
   ```powershell
   ollama serve
   # Leave this running in the background
   ```

4. **Test Alfred**
   ```powershell
   python alfred_terminal.py
   ```

### Method 2: Fresh Installation (Clean)

1. **Clone Repository**
   ```powershell
   # Navigate to C:\ drive
   cd C:\

   # Clone (requires GitHub access)
   git clone https://github.com/Batdan007/ALFRED_UBX.git
   cd ALFRED_UBX
   ```

2. **Run Installer**
   ```powershell
   # Windows PowerShell (run as Administrator)
   .\install.ps1
   ```

   The installer will:
   - Install Python dependencies
   - Set up directory structure
   - Create launcher scripts
   - Initialize brain database
   - Optionally install Ollama and models

3. **Manual Installation (if installer fails)**
   ```powershell
   cd C:\ALFRED_UBX
   pip install -r requirements.txt
   python alfred_terminal.py
   ```

---

## Voice Setup (CRITICAL for "Alfred can hear")

### Step 1: Verify Voice Packages

```powershell
# Check if voice packages are installed
pip list | findstr /i "speech audio pyttsx"

# Should see:
# - SpeechRecognition
# - PyAudio
# - pyttsx3
```

### Step 2: Install British Voice (Optional but Recommended)

Alfred sounds best with Ryan (British male) voice:

```powershell
cd C:\ALFRED_UBX

# Option 1: Automatic install (run as Administrator)
powershell -ExecutionPolicy Bypass -File install_british_voice.ps1

# Option 2: Auto-install script
powershell -ExecutionPolicy Bypass -File auto_install_british_voice.ps1

# Option 3: Manual install instructions in:
# INSTALL_RYAN_VOICE.md
```

**If Ryan doesn't install:** Alfred will use Microsoft Hazel (British female voice) - still sounds great!

### Step 3: Test Voice

```powershell
# Test voice output (speaking)
python test_alfred_voice_interactive.py

# Test voice input (listening)
python -c "from capabilities.voice.speech_to_text import AlfredEars; ears = AlfredEars(); print(ears.get_available_microphones())"
```

---

## Running ALFRED

### Terminal Mode (Like Claude Code)

```powershell
cd C:\ALFRED_UBX
python alfred_terminal.py
```

**Available Commands:**
- `/help` - Show all commands
- `/voice` - Toggle voice on/off
- `/memory` - Show brain statistics
- `/privacy` - Check privacy status
- `/cloud` - Request cloud AI access
- `/topics` - Show learned topics
- `/skills` - Show skill proficiency
- `/exit` - Exit Alfred (saves everything)

### Wake Word Mode (Always Listening)

Create a script `alfred_voice_mode.py`:
```python
from alfred_terminal import AlfredTerminal
from capabilities.voice.speech_to_text import AlfredEars

terminal = AlfredTerminal()
ears = AlfredEars()

print("Say 'Alfred' to wake me...")
ears.listen_for_wake_word(lambda cmd: terminal.process_command(cmd))
```

Then run:
```powershell
python alfred_voice_mode.py
```

---

## Configuration

### AI Backends

ALFRED supports multiple AI backends:

**1. Ollama (Default - Local & Free)**
```powershell
# Ensure Ollama is running
ollama serve

# Check available models
ollama list
```

**2. Claude (Cloud - Best Quality)**
```powershell
# Set environment variable
$env:ANTHROPIC_API_KEY="your_key_here"

# Alfred will detect and use automatically
```

**3. OpenAI GPT-4 (Cloud)**
```powershell
# Set environment variable
$env:OPENAI_API_KEY="your_key_here"
```

### Privacy Settings

Alfred respects privacy by default:
- **LOCAL mode**: Only uses Ollama (100% private)
- **AUTO mode**: Uses Ollama first, asks before using cloud AI
- **CLOUD mode**: Cloud AI allowed (requires confirmation)

Edit in: `core/privacy_controller.py` (line 129)

---

## Troubleshooting

### "Ollama connection failed"

```powershell
# Start Ollama manually
ollama serve

# Check if running
curl http://localhost:11434/api/version

# If not installed
winget install Ollama.Ollama
```

### "No module named 'speech_recognition'"

```powershell
cd C:\ALFRED_UBX
pip install -r requirements.txt
# OR
pip install SpeechRecognition PyAudio pyttsx3
```

### "PyAudio install fails"

PyAudio requires Microsoft Visual C++ 14.0+

**Solution:**
```powershell
# Download pre-built wheel from:
# https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio

# Install wheel
pip install PyAudio-0.2.13-cp313-cp313-win_amd64.whl
```

### "Microphone not working"

```powershell
# Check microphone permissions
# Settings > Privacy > Microphone > Allow apps

# List available microphones
python -c "import speech_recognition as sr; print(sr.Microphone.list_microphone_names())"

# Test microphone
python test_voices_simple.py
```

### "Ryan voice not installed"

Alfred will use Microsoft Hazel (British female) as fallback.

To install Ryan:
```powershell
# Run as Administrator
cd C:\ALFRED_UBX
powershell -ExecutionPolicy Bypass -File install_british_voice.ps1
```

### "Brain database error"

```powershell
# Reinitialize brain
cd C:\ALFRED_UBX
python -c "from core.brain import AlfredBrain; brain = AlfredBrain(); print('Brain initialized')"
```

---

## File Transfer Checklist

When copying from old PC to new PC, transfer these:

**Essential:**
- `C:\ALFRED_UBX\` - Entire directory
- `C:\ALFRED_UBX\alfred_data\` - Brain database (memories)
- `requirements.txt` - Dependencies

**Optional but Recommended:**
- `.env` file (if you have API keys)
- `alfred_data.backup.*` - Brain backups
- `logs/` - Historical logs

---

## Verification Steps

After installation, verify everything works:

### 1. Check Python Dependencies
```powershell
cd C:\ALFRED_UBX
pip list | findstr /i "rich prompt anthropic openai pyttsx speech pyaudio"
```

### 2. Test Brain
```powershell
python -c "from core.brain import AlfredBrain; brain = AlfredBrain(); print('Brain: OK')"
```

### 3. Test Voice Output
```powershell
python -c "from capabilities.voice.alfred_voice import AlfredVoice; voice = AlfredVoice(); voice.speak('Good evening sir', voice.GREETINGS); print('Voice Output: OK')"
```

### 4. Test Voice Input
```powershell
python -c "from capabilities.voice.speech_to_text import AlfredEars; ears = AlfredEars(); print('Voice Input:', 'OK' if ears.microphone else 'No microphone')"
```

### 5. Test Ollama
```powershell
curl http://localhost:11434/api/version
```

### 6. Test Full System
```powershell
python alfred_terminal.py
# In Alfred, type: /help
# Then type: /voice
# Then say: "Hello Alfred"
```

---

## Environment Variables (Optional)

Create `.env` file in `C:\ALFRED_UBX\`:

```env
# AI Provider Keys (optional - Ollama works without these)
ANTHROPIC_API_KEY=your_claude_key_here
OPENAI_API_KEY=your_openai_key_here
GROQ_API_KEY=your_groq_key_here

# Privacy Mode (optional)
ALFRED_PRIVACY_MODE=LOCAL  # LOCAL, AUTO, or CLOUD

# Voice Settings (optional)
ALFRED_VOICE_ENABLED=true
ALFRED_WAKE_WORD=alfred

# M5Stack Sync (optional)
ALFRED_SYNC_ENABLED=false
```

---

## Quick Start Commands

```powershell
# Install everything
cd C:\ALFRED_UBX
pip install -r requirements.txt

# Start Ollama (in separate terminal)
ollama serve

# Start Alfred
python alfred_terminal.py

# Enable voice in Alfred
/voice

# Test voice input
# Say: "Alfred, what's the weather?"

# Exit Alfred
/exit
```

---

## Performance Tips

### Faster Startup
- Keep Ollama running in background: `ollama serve`
- Use smaller model: `ollama pull dolphin-llama3:8b`

### Better Quality
- Use larger model: `ollama pull llama3.3:70b`
- Enable Claude fallback (privacy mode: AUTO)

### Lower Resource Usage
- Use `dolphin-llama3:8b` model (4.9GB)
- Disable tools you don't need in `tools/manager.py`

---

## What Works Without Internet

**100% Offline Capable:**
- Voice recognition (SpeechRecognition uses Google API but can work offline with Vosk)
- Voice output (pyttsx3 is fully offline)
- AI responses (via Ollama)
- Brain/Memory system
- Tool mode (file operations, code search)

**Requires Internet:**
- Claude AI (cloud)
- OpenAI GPT-4 (cloud)
- Web search capability
- External API integrations (CAMDAN, etc.)

---

## Support Files

**Documentation:**
- `README.md` - Main documentation
- `INTEGRATION_COMPLETE.md` - Integration guide
- `TOOL_MODE_GUIDE.md` - Tool usage guide
- `PROJECT_SUMMARY.md` - Project overview
- `MCP_SERVERS_COMPLETE.md` - MCP integration

**Testing:**
- `test_alfred_voice_interactive.py` - Test voice
- `test_voices_simple.py` - Test available voices
- `check_voices.py` - List installed voices
- `verify_integration.py` - Full system test

---

## Summary

**Minimum Setup (5 minutes):**
1. Copy `C:\ALFRED_UBX` to new PC
2. `pip install -r requirements.txt`
3. `ollama serve` (in background)
4. `python alfred_terminal.py`

**Full Setup (15 minutes):**
1. Install Python 3.7+
2. Install Ollama
3. Copy/clone ALFRED_UBX
4. Install dependencies
5. Install Ryan voice (optional)
6. Test voice input/output
7. Run Alfred

**ALFRED is ready to serve on your new computer!**

Good evening, Master Wayne. The Batcomputer is online.
