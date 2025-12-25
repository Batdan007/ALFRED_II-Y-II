# ALFRED Local Terminal Installation Guide

This guide will help you install and run ALFRED's local terminal interface on Linux, macOS, or Windows.

## Quick Installation (Linux/Ubuntu)

```bash
# 1. Install Python dependencies
pip3 install -r requirements.txt

# 2. Install espeak for voice support (Linux only)
sudo apt-get update
sudo apt-get install -y espeak

# 3. Run ALFRED Terminal
python3 alfred_terminal.py
```

## Platform-Specific Installation

### Linux (Ubuntu/Debian)

```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install -y espeak python3 python3-pip

# Install Python dependencies
pip3 install -r requirements.txt

# Run ALFRED
python3 alfred_terminal.py
```

### macOS

```bash
# Install Python dependencies (voice support is built-in)
pip3 install -r requirements.txt

# Run ALFRED
python3 alfred_terminal.py
```

### Windows

```powershell
# Install Python dependencies (voice support is built-in)
pip install -r requirements.txt

# Run ALFRED
python alfred_terminal.py
```

## What Gets Installed

### Core Dependencies
- **pyttsx3** - Text-to-speech (cross-platform)
- **PyYAML** - Configuration files
- **rich** - Beautiful terminal UI with markdown
- **prompt-toolkit** - Advanced input with history

### AI Integration (Optional)
- **anthropic** - Claude API (requires ANTHROPIC_API_KEY)
- **openai** - OpenAI GPT-4 API (requires OPENAI_API_KEY)
- **groq** - Groq API (requires GROQ_API_KEY)

### MCP Integration
- **mcp** - Model Context Protocol for Claude Code

### API Server (Optional)
- **fastapi** - REST API framework
- **uvicorn** - ASGI server
- **pydantic** - Data validation
- **aiohttp** - Async HTTP client

## Data Storage Locations

ALFRED stores data in platform-specific locations:

- **Windows**: `C:/Drive/data/alfred_brain.db`
- **macOS**: `~/Library/Application Support/Alfred/data/alfred_brain.db`
- **Linux**: `~/.alfred/data/alfred_brain.db`

Override with environment variable:
```bash
export ALFRED_HOME="/custom/path"
```

## Terminal Commands

Once ALFRED is running, you can use these commands:

- `/help` - Show available commands
- `/memory` - Show brain statistics
- `/voice` - Toggle voice on/off
- `/tools` - Toggle tool mode (enables file operations, bash commands, code search)
- `/privacy` - Show privacy status
- `/cloud` - Request cloud AI access
- `/clear` - Clear screen (keeps memory)
- `/export` - Export brain to backup
- `/topics` - Show tracked topics
- `/skills` - Show skill proficiency
- `/patterns` - Show learned patterns
- `/scan <target>` - Run security scan (requires Strix)
- `/security` - Show security scan history
- `/exit` - Exit ALFRED

## Optional: Install Ollama (Local AI)

For 100% privacy-first AI, install Ollama for local inference:

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull recommended model
ollama pull dolphin-mixtral:8x7b

# Alternative models
ollama pull llama3.3:70b
ollama pull dolphin-llama3:8b
```

## Optional: Cloud AI Setup

To use cloud AI providers, set environment variables:

```bash
# Claude (Anthropic)
export ANTHROPIC_API_KEY="sk-ant-..."

# OpenAI
export OPENAI_API_KEY="sk-..."

# Groq
export GROQ_API_KEY="gsk_..."
```

**Note:** Cloud AI requires explicit privacy approval via ALFRED's privacy controller.

## Optional: MCP Server Setup (Claude Code Integration)

To enable Claude Code integration with all 5 MCP servers:

### Step 1: Test MCP Servers
```bash
python3 mcp/test_mcp_servers.py
```

You should see: `✓✓✓ ALL TESTS PASSED ✓✓✓`

### Step 2: Copy Config to Claude Code

**Linux:**
```bash
# Create config directory if it doesn't exist
mkdir -p ~/.config/Claude

# Copy the Linux-specific config
cp mcp/claude_code_config_linux.json ~/.config/Claude/claude_desktop_config.json

# Update paths in the config (if your installation is not at /home/user/ALFRED_UBX)
nano ~/.config/Claude/claude_desktop_config.json
```

**macOS:**
```bash
cp mcp/claude_code_config.json ~/Library/Application\ Support/Claude/claude_desktop_config.json
# Edit to update paths
```

**Windows:**
```cmd
copy mcp\claude_code_config.json %APPDATA%\Claude\claude_desktop_config.json
```

### Step 3: Update Config Paths

Edit the config file and change these values to match your installation:

```json
{
  "mcpServers": {
    "alfred-brain": {
      "cwd": "/home/user/ALFRED_UBX",           // ← Your installation path
      "env": {
        "ALFRED_HOME": "/home/user/.alfred",    // ← Your data directory
        "PYTHONPATH": "/home/user/ALFRED_UBX"   // ← Your installation path
      }
    }
  }
}
```

### Step 4: Restart Claude Code

Close and reopen Claude Code.

### Step 5: Test MCP Integration

In Claude Code, try:
```
Use alfred_get_memory_stats to show ALFRED's brain statistics
```

If you see stats about conversations and knowledge, it's working!

## What You Get with MCP Integration

**5 MCP Servers with 46 Total Tools:**

1. **alfred-brain** (16 tools)
   - Memory operations (recall, store knowledge)
   - Voice synthesis (British butler)
   - Privacy controls
   - AI orchestration

2. **camdan-engineering** (8 tools)
   - Building code compliance (all 50 US states)
   - Cost estimation
   - Engineering queries (NIST, EBSCO)
   - Predictive maintenance

3. **strix-security** (8 tools)
   - Security scanning (directories, URLs, GitHub)
   - Vulnerability detection
   - Compliance checking

4. **dontlookup-dvbs2** (6 tools)
   - DVB-S2 satellite communication parsing
   - IP packet extraction
   - Protocol analysis

5. **caipe-agents** (8 tools)
   - Multi-agent orchestration
   - GitHub, ArgoCD, Jira, Slack, PagerDuty integration
   - Platform engineering automation

## Troubleshooting

### Voice Not Working (Linux)

```bash
# Install espeak
sudo apt-get install espeak

# Test espeak
espeak "Hello, this is a test"
```

### ALFRED Brain Database Not Created

Check permissions on the data directory:
```bash
# Linux
ls -la ~/.alfred/data/

# If directory doesn't exist, create it
mkdir -p ~/.alfred/data
```

### Python Module Import Errors

Make sure you're in the ALFRED_UBX directory:
```bash
cd /home/user/ALFRED_UBX
python3 alfred_terminal.py
```

### MCP Servers Not Found in Claude Code

1. Check config file location:
   ```bash
   # Linux
   cat ~/.config/Claude/claude_desktop_config.json

   # macOS
   cat ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```

2. Verify paths in config match your installation
3. Restart Claude Code
4. Check Claude Code logs for errors

### Ollama Connection Refused

Start the Ollama service:
```bash
ollama serve
```

Or install Ollama:
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

## Next Steps

1. **Explore the Terminal**: Run `/help` to see all available commands
2. **Set Up Tool Mode**: Use `/tools on` to enable Claude-like capabilities
3. **Install MCP**: Follow the MCP setup guide above for Claude Code integration
4. **Install Ollama**: For 100% local, privacy-first AI
5. **Read the Docs**: Check `CLAUDE.md` for detailed architecture and usage

## Support

- **Documentation**: See `CLAUDE.md` and `README.md`
- **MCP Guide**: See `mcp/README.md` and `mcp/QUICKSTART.md`
- **Tool Mode**: See `TOOL_MODE_GUIDE.md`
- **Issues**: Report at https://github.com/Batdan007/ALFRED_UBX/issues

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     ALFRED Terminal                         │
│  (Rich UI, Markdown rendering, Command history)            │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┴────────────────┐
        │                                  │
┌───────▼────────┐              ┌─────────▼─────────┐
│  AlfredBrain   │              │  MultiModel AI    │
│  (SQLite 11-   │              │  - Ollama (local) │
│   table arch)  │              │  - Claude         │
│                │              │  - OpenAI         │
│  - Conversations              │  - Groq           │
│  - Knowledge   │              └───────────────────┘
│  - Patterns    │                        │
│  - Skills      │              ┌─────────▼─────────┐
│  - Preferences │              │ PrivacyController │
│  - Topics      │              │  (LOCAL/HYBRID/   │
└────────────────┘              │   CLOUD modes)    │
        │                        └───────────────────┘
        │
┌───────▼────────────────────────────────────────────┐
│               MCP Servers (5)                      │
│  - alfred-brain (16 tools)                        │
│  - camdan-engineering (8 tools)                   │
│  - strix-security (8 tools)                       │
│  - dontlookup-dvbs2 (6 tools)                     │
│  - caipe-agents (8 tools)                         │
└────────────────────────────────────────────────────┘
        │
┌───────▼────────┐
│  Claude Code   │
│  (MCP Client)  │
└────────────────┘
```

## British Butler Personality

ALFRED speaks like a proper British butler:
- "Good evening, sir."
- "The task is complete, sir."
- "I must warn you, sir, this operation cannot be undone."
- "Apologies, sir. An unexpected error has occurred."

Voice is automatically selected based on platform:
- **Windows**: Microsoft Ryan (British English)
- **macOS**: Daniel (British English)
- **Linux**: espeak with British accent

## Privacy-First Design

- **Default Mode**: LOCAL (100% private, no cloud AI)
- **Explicit Consent**: Cloud AI requires user approval
- **No Telemetry**: No data collection or tracking
- **Local Storage**: All data stored on your machine
- **Transparent**: Shows exactly which AI provider is used

Enjoy your British AI butler! 🎩
