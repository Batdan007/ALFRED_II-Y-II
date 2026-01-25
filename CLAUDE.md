# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Quick Start

```bash
# Install dependencies (Python 3.11 or 3.12 ONLY - 3.13+ breaks faster-whisper)
py -3.11 -m pip install -r requirements.txt

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
| `core/` | Patent-pending technologies (Brain, CORTEX, ULTRATHUNK, Guardian, NEXUS, Agents) |
| `ai/` | Multi-model orchestration (`multimodel.py`) and provider clients |
| `capabilities/` | Features: voice/, knowledge/, rag/, vision/, fabric/ (243 patterns) |
| `tools/` | Tool management and implementations |
| `skills/` | PAI-inspired skill routing with SKILL.md files (USE WHEN triggers) |
| `telos/` | Goal framework: MISSION.md, GOALS.md, BELIEFS.md, LEARNED.md, PROJECTS.md |
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
| `alfred_chat.py` | Simple chat (Ollama-only, no brain overhead) |
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

## PAI-Inspired Features (New)

### Skills System (`skills/`)
Semantic routing based on "USE WHEN" triggers in SKILL.md files:
```python
from skills import create_skill_router
router = create_skill_router()
result = router.route("Scan example.com for vulnerabilities")
# → Matches security skill with triggers: ['vuln', 'scan']
```

Available skills: `security`, `engineering`, `research`, `voice`, `memory`, `coding`

### Named Agents (`core/agents.py`)
Specialized agent personalities for different tasks:
- **Engineer**: TDD, clean code, Python/TypeScript
- **Researcher**: OSINT, fact verification, synthesis
- **Architect**: System design, trade-offs, patterns
- **SecurityExpert**: Pentesting, OWASP, vulnerability assessment
- **Writer**: Documentation, tutorials, clear communication
- **Analyst**: Data analysis, metrics, insights

### TELOS Goal Framework (`telos/`)
Structured goal tracking (inspired by PAI):
- `MISSION.md` - Core purpose and directives
- `GOALS.md` - Active projects and objectives
- `BELIEFS.md` - Core values (Joe Dog's Rule, etc.)
- `LEARNED.md` - Accumulated learnings
- `PROJECTS.md` - Project status tracking

### The 7-Phase Algorithm
Applied at every scale:
```
OBSERVE → THINK → PLAN → BUILD → EXECUTE → VERIFY → LEARN
```

## Key Principles
1. **Privacy First**: Local Ollama default, explicit consent for cloud
2. **Bounded Growth**: CORTEX ensures storage never exceeds limits
3. **Generative Compression**: ULTRATHUNK compresses while improving quality
4. **Scaffolding Over Model**: System design matters more than raw AI capability
5. **Global Butler**: British accent, born in Gary IN, serves humanity worldwide. Wise, concise, slightly sarcastic.

## Instance Status

This is the **Master Development Instance** of ALFRED. Changes here propagate to:
- **GX_TECH** (`../GX_TECH/`) - Commercial Mai-AI platform (extracts core/ technology)
- Deployed client instances

**Location**: `C:\Users\danie\Projects\ALFRED_IV-Y-VI\` (canonical master)

---
**Author**: Daniel J Rita (BATDAN) | **Entity**: GxEum Technologies / CAMDAN Enterprizes | **Version**: 4.0.6
