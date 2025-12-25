# ALFRED II-Y-II

<div align="center">

```
    _    _     _____ ____  _____ ____    ___ ___ __   __ ___ ___
   / \  | |   |  ___|  _ \| ____|  _ \  |_ _|_ _|\ \ / /|_ _|_ _|
  / _ \ | |   | |_  | |_) |  _| | | | |  | | | |  \ V /  | | | |
 / ___ \| |___|  _| |  _ <| |___| |_| |  | | | |   | |   | | | |
/_/   \_\_____|_|   |_| \_\_____|____/  |___|___|  |_|  |___|___|
```

**The Ultimate AI Butler - ALFRED_UBX + Alfred_Ultimate Merged**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Proprietary-red.svg)](LICENSE)
[![Patent](https://img.shields.io/badge/patent-pending-orange.svg)](PATENT_TRACKING.md)

*Created by Daniel J. Rita (BATDAN)*

</div>

---

## What Makes This Special

ALFRED II-Y-II combines the best of both worlds:

| Feature | Source | Description |
|---------|--------|-------------|
| **11-Table Brain** | Both | Patent-pending persistent memory |
| **5 MCP Servers** | UBX | 46 tools for Claude Code |
| **243 Fabric Patterns** | Ultimate | Expert AI prompts |
| **Multi-Model Orchestrator** | UBX | 5 AI providers with fallback |
| **ChromaDB RAG** | Ultimate | Semantic vector search |
| **User Recognition** | Ultimate | Voice/face identification |
| **Privacy Controller** | UBX | LOCAL/HYBRID/CLOUD modes |
| **Web UI Dashboard** | Ultimate | Mission Control interface |

---

## Quick Start

```bash
# 1. Clone and enter
git clone https://github.com/Batdan007/ALFRED_II-Y-II.git
cd ALFRED_II-Y-II

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure (GUI wizard)
python setup_wizard.py

# 4. Launch ALFRED
python alfred_terminal.py
```

---

## Architecture

```
ALFRED_II-Y-II/
├── Core Brain (core/)
│   ├── brain.py              # 11-table SQLite memory
│   ├── privacy_controller.py # Privacy-first cloud access
│   └── path_manager.py       # Cross-platform paths
│
├── AI Layer (ai/)
│   ├── multimodel.py         # Ollama->Claude->Gemini->Groq->OpenAI
│   ├── local/                # Ollama integration
│   └── cloud/                # Claude, Gemini, Groq, OpenAI
│
├── Capabilities (capabilities/)
│   ├── voice/                # British butler TTS + STT
│   ├── knowledge/            # Stocks, weather, news, cyber intel
│   ├── rag/                  # ChromaDB + advanced crawling
│   ├── fabric/               # 243 AI patterns
│   └── vision/               # Image analysis
│
├── MCP Servers (mcp/)        # 5 servers, 46 tools
│   ├── alfred-brain/
│   ├── camdan-engineering/
│   ├── strix-security/
│   ├── dontlookup-dvbs2/
│   └── caipe-agents/
│
├── Variants (variants/)      # Specialized entry points
│   ├── alfred_enhanced.py    # Full power mode
│   ├── alfred_unified.py     # Web UI + FastAPI
│   ├── alfred_live.py        # Voice-optimized
│   └── alfred_rag.py         # Research assistant
│
├── Tools (tools/)
│   ├── database_tools.py     # DB migrations, optimization
│   └── upwork_opportunity_finder.py
│
├── User Recognition (user_recognition/)
│   └── BATDAN_PROFILE.md     # Voice/face profile
│
└── Entry Points
    ├── alfred_terminal.py    # Primary CLI
    ├── alfred_api_server.py  # REST API
    └── setup_wizard.py       # GUI setup
```

---

## AI Fallback Chain

```
1. Ollama (local)     Privacy-first, no internet
         ↓
2. Claude (cloud)     High quality, Anthropic
         ↓
3. Gemini (cloud)     Google's AI
         ↓
4. Groq (cloud)       Fast inference
         ↓
5. OpenAI (cloud)     Reliable fallback
```

---

## Commands

| Command | Description |
|---------|-------------|
| `/help` | Show all commands |
| `/memory` | View memory stats |
| `/voice on/off` | Toggle voice output |
| `/privacy` | Show/change privacy mode |
| `/cloud` | Request cloud access |
| `/tools` | Enter tool mode (like Claude Code) |
| `/scan <path>` | Security scan |
| `/exit` | Exit ALFRED |

---

## Variants (from Alfred_Ultimate)

| Variant | Best For | Launch |
|---------|----------|--------|
| **Terminal** | All-around use | `python alfred_terminal.py` |
| **Enhanced** | Full features | `python variants/alfred_enhanced.py` |
| **Unified** | Web interface | `python variants/alfred_unified.py` |
| **Live** | Voice assistant | `python variants/alfred_live.py` |
| **RAG** | Research | `python variants/alfred_rag.py` |

---

## MCP Integration (Claude Code)

Copy `mcp/claude_code_config.json` to your Claude Code config.

**Available Servers:**
- `alfred-brain` - Memory, knowledge, voice
- `camdan-engineering` - Building codes, cost estimation
- `strix-security` - Vulnerability scanning
- `dontlookup-dvbs2` - Satellite signal analysis
- `caipe-agents` - Multi-agent orchestration

---

## Configuration

Create `.env` with your API keys:

```bash
# Cloud AI (optional if using Ollama only)
ANTHROPIC_API_KEY=your_key
OPENAI_API_KEY=your_key
GROQ_API_KEY=your_key
GOOGLE_API_KEY=your_key

# Optional services
POLYGON_API_KEY=your_key      # Stock data
OPEN_WEATHER_KEY=your_key     # Weather
NEWSAPI_KEY=your_key          # News
GITHUB_TOKEN=your_token       # GitHub
```

---

## Patent Status

**USPTO Provisional Patent Filed: November 11, 2025**

11-table brain architecture with:
- Multi-dimensional memory
- Automatic knowledge extraction
- Dual scoring (confidence x importance)
- Pattern learning with success rates
- Mistake-based learning

**Priority Deadline: November 11, 2026**

---

## Origin

This repository merges:
- **ALFRED_UBX** - Core architecture, MCP servers, privacy controller
- **Alfred_Ultimate** - 243 patterns, RAG, user recognition, web UI

---

## Author

**Daniel J. Rita (BATDAN)**
- Email: danieljrita@hotmail.com
- GitHub: [@Batdan007](https://github.com/Batdan007)

---

## License

Proprietary - Patent Pending

---

<div align="center">

*ALFRED: Always Learning, Forever Remembering Every Detail*

</div>
