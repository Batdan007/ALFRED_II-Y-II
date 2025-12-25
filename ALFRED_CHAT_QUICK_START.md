# ALFRED Chat - Quick Start Reference

## Start ALFRED Now

### Windows
```bash
# Desktop shortcut (if installed)
# Double-click "ALFRED Chat" on desktop

# Or from command line:
.\launchers\alfred_chat.bat

# Or PowerShell:
.\launchers\alfred_chat.ps1

# Or universal launcher:
python launchers/alfred_launcher.py
```

### macOS
```bash
# Finder: Applications > ALFRED.app
# Or terminal:
./launchers/alfred_chat.sh

# Or universal launcher:
python launchers/alfred_launcher.py
```

### Linux
```bash
# Application menu: Search "ALFRED Chat"
# Or terminal:
./launchers/alfred_chat.sh

# Or universal launcher:
python launchers/alfred_launcher.py
```

### iOS
```
Open Safari → http://192.168.1.X:8000
(Replace X with your Mac's IP)
```

---

## Setup Desktop Shortcut (First Time Only)

### Windows
```bash
.\launchers\setup_windows_shortcuts.bat
```
Creates shortcuts on Desktop, Start Menu, Quick Launch

### macOS
```bash
bash launchers/setup_macos_app.sh
```
Creates ALFRED.app in Applications folder

### Linux
```bash
bash launchers/setup_linux_menu.sh
```
Adds ALFRED to Application menu

---

## Privacy - Local-First by Default

| Feature | Status |
|---------|--------|
| Data stays on device | ✅ YES |
| Cloud AI | ⚠️ Requires permission |
| Local Ollama | ✅ Preferred (install from ollama.ai) |
| Telemetry | ❌ NONE |
| Tracking | ❌ NONE |

**To enable maximum privacy:**
```bash
# Install Ollama: https://ollama.ai
ollama serve
# ALFRED automatically uses it - all data stays local
```

---

## Chat Commands

In the ALFRED Chat interface:

| Command | What it does |
|---------|-------------|
| Type message | Send to ALFRED |
| Click agent badge | See which agent is processing |
| Quality badge | Shows response validation status |
| Brain stats | Shows memory and learning |

---

## How ALFRED Works

```
1. You ask a question
   ↓
2. ALFRED classifies the task type
   (code, security, research, etc.)
   ↓
3. ALFRED selects best agents
   (engineer, researcher, pentester, etc.)
   ↓
4. Agents process in parallel
   (multiple can work at once)
   ↓
5. Response quality validated
   (verified, honest, or flagged)
   ↓
6. ALFRED learns from interaction
   (brain stores for future improvement)
   ↓
7. You get the response
```

---

## Task Types ALFRED Recognizes

| Type | When to use | Best Agent |
|------|-----------|-----------|
| **CODE_MODIFICATION** | Create/edit code | alfred-engineer |
| **CODE_REVIEW** | Analyze code | engineer |
| **CYBERSECURITY** | Security analysis | pentester |
| **ARCHITECTURE** | System design | architect |
| **RESEARCH** | Information gathering | alfred-researcher |
| **OPTIMIZATION** | Performance tuning | alfred-engineer |
| **DEBUGGING** | Fix problems | engineer |
| **DATA_ANALYSIS** | Process data | researcher |
| **DOCUMENTATION** | Write guides | alfred-researcher |
| **SYSTEM_LEARNING** | Learn from mistakes | (system) |

---

## Response Quality Levels

| Level | Meaning | Trust |
|-------|---------|-------|
| ✅ **VERIFIED** | Fact-checked against brain | 95% |
| ✅ **LIKELY_ACCURATE** | High confidence | 75% |
| ✅ **HONEST_LIMITATION** | Admits what it can't do | 85% |
| ⚠️ **UNVERIFIED** | Not yet confirmed | ~50% |
| ❌ **SUSPICIOUS** | Potential issue | 10% |
| ❌ **REPEAT** | Similar to previous | Review |
| ❌ **CONTRADICTS** | Conflicts with known facts | 5% |

---

## Common Questions

**Q: Does ALFRED send data to cloud?**
A: No, it's LOCAL-FIRST by default. Cloud AI only with explicit permission.

**Q: What if Ollama isn't installed?**
A: ALFRED still works, but will ask about cloud models. Install Ollama for privacy.

**Q: Can I access ALFRED from my phone?**
A: Yes! See iOS_SHORTCUT_SETUP.md for instructions.

**Q: Does ALFRED learn from my questions?**
A: Yes! Every interaction improves ALFRED's future responses.

**Q: Can I trust ALFRED's answers?**
A: ALFRED validates responses. It's honest about limitations instead of making things up.

**Q: Where is my data stored?**
A: In alfred_brain.db on your device. Backup: `cp alfred_brain.db alfred_brain.backup.db`

---

## Need Help?

- **Setup issues:** ALFRED_CHAT_SETUP_GUIDE.md
- **Learning system:** ALFRED_BRAIN_LEARNING_GUIDE.md
- **Task types:** QUICK_REFERENCE_BRAIN_LEARNING.md
- **Architecture:** IMPLEMENTATION_SUMMARY.md
- **iOS access:** iOS_SHORTCUT_SETUP.md

---

## Settings to Know

### Privacy Mode (in core/privacy_controller.py)
```python
# Options: "LOCAL", "HYBRID", "CLOUD"
# LOCAL = only local Ollama (most private)
# HYBRID = try local, ask before cloud
# CLOUD = use cloud models (least private)
```

### Server Port (in ui/chat_interface.py)
```python
# Default is 8000
# Access at: http://localhost:8000
```

### Agent Models (in core/agent_selector.py)
```python
# HAIKU = fast (3.5 Sonnet level)
# SONNET = balanced (Claude Sonnet)
# OPUS = powerful (Claude Opus)
```

---

## Troubleshooting

**Server won't start:**
```bash
# Check port 8000 is free
# Windows: netstat -ano | findstr :8000
# Mac/Linux: lsof -i :8000

# Use different port:
python -c "from ui.chat_interface import AlfredChatServer; AlfredChatServer(port=8001).run()"
```

**Can't access from iOS:**
1. Verify ALFRED running on Mac
2. Get Mac IP: System Preferences > Network
3. Both devices on same WiFi
4. Try `http://192.168.1.X:8000` in Safari

**Ollama not detected:**
```bash
# Start it:
ollama serve

# Or install from: https://ollama.ai
```

**Response quality warnings:**
- This is GOOD - ALFRED is being honest
- Prefer honesty over perfection
- Marks responses it can't verify

---

## Files You Need to Know

| File | Purpose |
|------|---------|
| `ui/chat_interface.py` | Main web UI server |
| `launchers/alfred_chat.bat` | Windows launcher |
| `launchers/alfred_chat.sh` | macOS/Linux launcher |
| `launchers/alfred_launcher.py` | Universal launcher menu |
| `core/brain.py` | Persistent memory system |
| `core/task_classifier.py` | Task type detection |
| `core/agent_selector.py` | Agent routing |
| `core/response_quality_checker.py` | Response validation |

---

## Performance Tips

1. **Use Ollama** for best speed (no internet delay)
2. **Close other apps** to free memory
3. **Use same WiFi** for iOS access (faster than tunnels)
4. **Save important responses** (bookmark in Safari)
5. **Regular backups** of alfred_brain.db

---

## Privacy Guarantees

✅ **ALFRED guarantees:**
- Your data stays on your device by default
- No cloud access without permission
- No tracking or telemetry
- No data sharing with third parties
- Complete transparency about capabilities

---

**Last Updated:** December 10, 2025
**Version:** 1.0.0
**Creator:** Daniel J Rita (BATDAN007)
