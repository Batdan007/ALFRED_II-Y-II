# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Quick Start

```bash
# Install dependencies (Python 3.11 recommended, 3.10+ required)
pip install -r requirements.txt

# Optional: Install as editable package
pip install -e .

# Run ALFRED
python alfred_terminal.py          # Primary CLI
python alfred_terminal.py --voice  # With voice
```

## Build Commands

```bash
# Windows executable build
py -3.11 -m PyInstaller --name=ALFRED --onefile --console alfred/__main__.py

# Install with voice support
pip install -e ".[voice]"

# Install full (voice + RAG + vision)
pip install -e ".[full]"
```

## Running Tests

```bash
# Run individual test files (no centralized test runner)
python tests/test_core.py
python tests/test_alfred_voice.py
python tests/test_security_agent.py
```

## Joe Dog's Rule (INVIOLABLE)

ALFRED shall NEVER be used for weapons or violence. Protects all life, guards the environment, guides humanity toward peace. Enforced in `core/ethics.py`.

> "No one needs a missile that learns from its mistakes." - BATDAN

## Architecture Overview

### Unified Memory Flow
```
INPUT → CORTEX (5 layers) → BRAIN (11 tables)
          │                      ▲
          │   patterns           │ knowledge
          ▼                      │
      ULTRATHUNK ────────────────┘
      (640:1 compression)
```

### AI Fallback Chain (Privacy-First)
```
Ollama (local) → Claude → Gemini → Groq → OpenAI
```
Cloud providers require explicit user approval via `PrivacyController`.

### Key Directories

| Directory | Purpose |
|-----------|---------|
| `core/` | Patent-pending technologies (Brain, CORTEX, ULTRATHUNK, Guardian, NEXUS) |
| `ai/` | Multi-model orchestration (`multimodel.py`) and provider clients |
| `capabilities/` | Features: voice/, knowledge/, rag/, vision/, fabric/ (243 patterns) |
| `tools/` | Tool management and implementations |
| `mcp/` | 5 MCP servers with 46 tools for Claude Code integration |
| `variants/` | Specialized entry points (enhanced, unified, live, rag) |

## Critical Development Patterns

### ALWAYS Use PathManager
```python
from core.path_manager import PathManager
brain_db = PathManager.BRAIN_DB  # CORRECT
# brain_db = "C:/path/..."       # WRONG - breaks cross-platform
```

### Graceful Degradation (Required Pattern)
```python
try:
    from core.cortex import CORTEX
    CORTEX_AVAILABLE = True
except ImportError:
    CORTEX = None
    CORTEX_AVAILABLE = False

# Then check availability before use
if CORTEX_AVAILABLE:
    cortex = CORTEX()
```

### Privacy Controller Integration
```python
from core.privacy_controller import PrivacyController

controller = PrivacyController()
# Modes: LOCAL (default), HYBRID, CLOUD
if controller.approve_cloud_request("Claude API call"):
    # Make cloud call
```

## Brain Tables (11)
`conversations`, `knowledge`, `preferences`, `patterns`, `skills`, `mistakes`, `topics`, `context_windows`, `web_cache`, `security_scans`, `market_data`

## Environment Variables
```bash
ALFRED_HOME="/custom/path"        # Override root directory
ANTHROPIC_API_KEY="sk-ant-..."    # Claude (optional if Ollama-only)
OPENAI_API_KEY="sk-..."           # OpenAI
GROQ_API_KEY="gsk_..."            # Groq
GOOGLE_API_KEY="..."              # Gemini
POLYGON_API_KEY="..."             # Stock data
```

## MCP Server Integration

Copy `mcp/claude_code_config.json` to Claude Code config. Servers:
- `alfred-brain` - Memory, knowledge, voice
- `strix-security` - Vulnerability scanning
- `camdan-engineering` - Building codes, cost estimation
- `dontlookup-dvbs2` - Satellite signal analysis
- `caipe-agents` - Multi-agent orchestration

## Entry Points

| File | Use Case |
|------|----------|
| `alfred_terminal.py` | Primary interactive CLI |
| `alfred_api_server.py` | REST API server |
| `variants/alfred_enhanced.py` | Full power mode |
| `variants/alfred_unified.py` | Web UI + FastAPI |
| `variants/alfred_live.py` | Voice-optimized |

## Terminal Commands

| Category | Commands |
|----------|----------|
| Core | `/memory` `/voice` `/tools` `/privacy` `/exit` |
| Voice | `/listen` `/wakeword` `/always_listen` `/learn_voice` |
| Patent Tech | `/cortex` `/ultrathunk` `/guardian` `/nexus` `/unified` |
| Memory | `/consolidate` `/learn` `/forget` `/ethics` |

**Wake Words**: "Hey Alfred", "Alfred", "Batcomputer"

## Patent Portfolio (DO NOT DISTRIBUTE)

| Technology | File | Description |
|------------|------|-------------|
| Brain | `core/brain.py` | 11-table persistent memory |
| CORTEX | `core/cortex.py` | 5-layer forgetting architecture |
| ULTRATHUNK | `core/ultrathunk.py` | 640:1 generative compression |
| Guardian | `core/guardian.py` | Behavioral watermarking |
| NEXUS | `core/nexus.py` | AI-to-AI communication protocol |

---
**Author**: Daniel J Rita (BATDAN) | **Entity**: CAMDAN Enterprises LLC | **Version**: 3.0.0
