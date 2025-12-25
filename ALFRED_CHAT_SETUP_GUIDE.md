# ALFRED Chat - Complete Setup Guide

## Overview

ALFRED Chat is a modern, responsive chat interface for ALFRED with:
- **Local-first privacy** (runs on your device, no data sharing by default)
- **Intelligent agent selection** (automatically chooses best agents for your task)
- **Parallel execution** (multiple agents can work together)
- **Response quality validation** (prevents repeats, checks honesty)
- **Brain integration** (learns from every interaction)

## Quick Start

### Windows
```bash
# Option 1: Double-click desktop shortcut (if installed)
# Option 2: Run from command line
.\launchers\alfred_chat.bat

# Option 3: PowerShell
.\launchers\alfred_chat.ps1

# Option 4: Universal launcher with menu
python launchers/alfred_launcher.py
```

### macOS
```bash
# Option 1: Open ALFRED.app from Applications
# Option 2: Run from terminal
./launchers/alfred_chat.sh

# Option 3: Universal launcher
python launchers/alfred_launcher.py
```

### Linux
```bash
# Option 1: Search for ALFRED Chat in application menu
# Option 2: Run from terminal
./launchers/alfred_chat.sh

# Option 3: Universal launcher
python launchers/alfred_launcher.py
```

### iOS
1. See iOS_SHORTCUT_SETUP.md for detailed instructions
2. Quick: Open Safari and go to `http://<your-mac-ip>:8000`

## Installation & Setup

### Prerequisites
- Python 3.10+
- (Optional but recommended) Ollama for maximum privacy

### Step 1: Install Dependencies
```bash
pip install fastapi uvicorn[standard] aiohttp
```

### Step 2: Verify Setup
```bash
# Check Python
python --version  # Should be 3.10+

# Check Ollama (optional)
curl http://localhost:11434/api/version
```

### Step 3: Create Desktop Shortcuts

**Windows:**
```bash
launchers/setup_windows_shortcuts.bat
```

**macOS:**
```bash
bash launchers/setup_macos_app.sh
```

**Linux:**
```bash
bash launchers/setup_linux_menu.sh
```

## Privacy & Security

### Default Settings
- ✅ **All data stays on your device**
- ✅ **Local Ollama model preferred** (if installed)
- ⚠️ **Cloud AI requires explicit permission**
- ✅ **No telemetry or tracking**

### Privacy Modes

#### LOCAL (Default)
```
User Input → ALFRED Brain → Ollama (local)
└─ All processing on device
└─ Zero cloud access
```

#### HYBRID
```
User Input → ALFRED Brain → Try Ollama → Fallback to Claude
└─ Local preferred, cloud with permission
└─ Requires explicit cloud approval once
```

#### CLOUD
```
User Input → ALFRED Brain → Claude/OpenAI
└─ Uses cloud AI
└─ Requires explicit permission
└─ Only available if user approves
```

### Enable Ollama for Maximum Privacy

1. **Install Ollama**: https://ollama.ai
2. **Pull a model**: `ollama pull llama2`
3. **Start server**: `ollama serve`
4. **Verify**: Open `http://localhost:11434/api/version`

Once Ollama is running:
- ALFRED automatically uses it
- All processing stays on your device
- No internet required
- Complete privacy

## Features

### 1. Task Classification
ALFRED automatically detects your task type:
- **CODE_MODIFICATION** - Creating or modifying code
- **CYBERSECURITY** - Security analysis, penetration testing
- **ARCHITECTURE** - System design decisions
- **RESEARCH** - Information gathering
- **DEBUGGING** - Troubleshooting problems
- **DATA_ANALYSIS** - Processing data
- **CODE_REVIEW** - Analyzing existing code
- **OPTIMIZATION** - Performance improvement
- **DOCUMENTATION** - Writing guides/docs
- **SYSTEM_LEARNING** - Learning from interactions

### 2. Agent Selection
For each task, ALFRED:
- Classifies the task type
- Selects appropriate agents
- Considers historical success rates
- Shows confidence levels
- Can run multiple agents in parallel

**Available Agents:**
- `alfred-engineer` - Best at code modification, debugging
- `alfred-researcher` - Best at research, analysis
- `engineer` - Code and architecture
- `researcher` - Information gathering
- `architect` - System design
- `pentester` - Security analysis
- `designer` - UI/UX design

### 3. Response Quality
Every response is validated:
- ✅ **VERIFIED** - Checked against known facts
- ✅ **LIKELY_ACCURATE** - High confidence but unverified
- ⚠️ **HONEST_LIMITATION** - Acknowledges what it can't do
- ⚠️ **UNVERIFIED** - Needs fact-checking
- ❌ **SUSPICIOUS** - Potential accuracy issue
- ❌ **REPEAT** - Too similar to previous answer
- ❌ **CONTRADICTS** - Conflicts with known facts

### 4. Brain Integration
ALFRED learns from every interaction:
- Stores conversations with importance/confidence scores
- Tracks which agents succeed at which tasks
- Identifies patterns and preferences
- Improves decisions over time

View brain stats:
```
In chat, use:
/memory - Show brain statistics
/patterns - Show learned patterns
/skills - Show agent skill proficiency
```

## Configuration

### Server Settings
Edit `ui/chat_interface.py`:
```python
# Change default host/port
server = AlfredChatServer(host="0.0.0.0", port=8000)
```

### Privacy Settings
Edit `core/privacy_controller.py`:
```python
# Change default privacy mode
privacy = PrivacyController(default_mode="LOCAL")  # LOCAL, HYBRID, or CLOUD
```

### Agent Selection
Edit `core/agent_selector.py`:
```python
# Customize agent specializations and model tiers
# HAIKU (fast), SONNET (balanced), OPUS (powerful)
```

## Troubleshooting

### Server won't start
```bash
# Check if port 8000 is in use
# Windows: netstat -ano | findstr :8000
# macOS/Linux: lsof -i :8000

# Use different port:
python -c "from ui.chat_interface import AlfredChatServer; AlfredChatServer(port=8001).run()"
```

### Can't connect from iOS
```bash
# Make sure:
1. ALFRED server running on Mac/Linux
2. Both devices on same WiFi network
3. Firewall allows port 8000
4. Get Mac's IP: System Preferences > Network
5. On iOS Safari: http://<mac-ip>:8000
```

### Ollama not detected
```bash
# Start Ollama:
ollama serve

# Or install from: https://ollama.ai
# Verify: curl http://localhost:11434/api/version
```

### Response quality issues
ALFRED is designed to prefer honesty over precision:
- If it can't verify something, it will say so
- If information is outdated, it will acknowledge
- If capability is limited, it will be explicit

This is by design and builds trust.

### Cloud access prompts
- ALFRED is LOCAL-FIRST by default
- Cloud models require explicit permission
- Install Ollama to avoid cloud access entirely
- View privacy status: /privacy command

## Advanced Usage

### Parallel Agent Execution
For complex tasks, ALFRED can run multiple agents:
```
Input: "Design a secure microservices architecture and perform security audit"
↓
Task Classification: ARCHITECTURE + CYBERSECURITY (multi-type)
↓
Agents: architect (1.0), alfred-engineer (0.8), pentester (0.9)
↓
Parallel Execution: All three agents work simultaneously
↓
Combined Response: Integrated findings from all agents
```

### Learning Patterns
ALFRED tracks:
- Task patterns you ask about
- Which agents succeed most
- Your preferences and style
- Common pain points

View:
```bash
# In Python
from core.brain import AlfredBrain
brain = AlfredBrain()
stats = brain.get_memory_stats()
print(stats)
```

### Custom Training
Help ALFRED improve:
```
1. Ask questions regularly
2. Verify responses you trust
3. Note where ALFRED was wrong
4. The system learns and improves
```

Over time, ALFRED becomes more specialized to your needs.

## API Reference

### WebSocket Endpoint
```
ws://localhost:8000/ws/chat
```

**Message Format:**
```json
{
  "message": "Your question here"
}
```

**Response Types:**
```json
{
  "type": "task_classification",
  "task_type": "CODE_MODIFICATION",
  "confidence": 0.92,
  "agents": [...]
}
```

```json
{
  "type": "response",
  "message": "Response text here",
  "quality": {
    "level": "verified",
    "is_clean": true,
    "flags": [],
    "confidence": 0.95
  }
}
```

### REST Endpoints

#### Get Privacy Status
```
GET /api/privacy-status

Response:
{
  "mode": "LOCAL",
  "cloud_allowed": false,
  "explanation": "..."
}
```

#### Request Cloud Access
```
POST /api/request-cloud-access?provider=claude

Response:
{
  "approved": false,
  "message": "...",
  "providers": ["claude", "openai", "groq"]
}
```

#### Get Brain Stats
```
GET /api/brain-stats

Response:
{
  "total_conversations": 42,
  "total_knowledge": 156,
  "patterns_learned": 12,
  "skills_tracked": 7,
  "last_consolidated": "2025-12-10T..."
}
```

## Support & Resources

### Documentation
- QUICK_REFERENCE_BRAIN_LEARNING.md - Task types and agents
- IMPLEMENTATION_SUMMARY.md - Architecture overview
- ALFRED_BRAIN_LEARNING_GUIDE.md - Full learning system guide

### Community
- GitHub: https://github.com/Batdan007/ALFRED_UBX
- Issues: Report bugs or request features

### Developer Notes
- All code is open source
- Modify and customize as needed
- MCP integration for Claude Code support
- Full brain access via API

## Updates & Maintenance

### Check for Updates
```bash
git pull origin main
pip install -r requirements.txt
```

### Backup Brain
```bash
# Brain is stored at:
# Windows: C:/Drive/data/alfred_brain.db
# macOS: ~/Library/Application Support/Alfred/data/alfred_brain.db
# Linux: ~/.alfred/data/alfred_brain.db

# Backup regularly:
cp alfred_brain.db alfred_brain.backup.db
```

### Clear Brain (Restart Learning)
```bash
# WARNING: This deletes all learned information
python -c "
from core.brain import AlfredBrain
brain = AlfredBrain()
brain.clear_database()
"
```

---

**Created:** December 10, 2025  
**Author:** Daniel J Rita (BATDAN007)  
**Version:** 1.0.0
