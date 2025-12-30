# CLAUDE.md

## ALFRED-UBX | Privacy-First AI with Permanent Memory

**Author**: Daniel J Rita (BATDAN) | **Entity**: CAMDAN Enterprises LLC | **Version**: 3.0.0-ultimate

## Quick Start
```bash
pip install -r requirements.txt
python alfred_terminal.py
```

## Joe Dog's Rule (INVIOLABLE)
ALFRED shall NEVER be used for weapons or violence. Protects all life, guards the environment, guides humanity toward peace. Embedded in `core/ethics.py`.

> "No one needs a missile that learns from its mistakes." - BATDAN

## Patent Portfolio (5 Core Technologies)

| Innovation | File | Status |
|------------|------|--------|
| **Brain** (11-table memory) | `core/brain.py` | FILED Nov 2025 |
| **CORTEX** (5-layer forgetting) | `core/cortex.py` | Q1 2025 |
| **ULTRATHUNK** (640:1 compression) | `core/ultrathunk.py` | Q1 2025 |
| **Guardian** (behavioral watermark) | `core/guardian.py` | Q1 2025 |
| **NEXUS** (AI-to-AI protocol) | `core/nexus.py` | Q2 2025 |

## Unified Memory Architecture
```
INPUT → CORTEX (5 layers) → BRAIN (11 tables)
              ↓                    ↑
         ULTRATHUNK (640:1) ───────┘
```

## Terminal Commands

| Category | Commands |
|----------|----------|
| **Core** | `/memory` `/voice` `/tools` `/privacy` `/exit` |
| **Voice** | `/listen` `/wakeword` `/always_listen` `/learn_voice` |
| **Vision** | `/see` `/watch` `/remember` |
| **Patent Tech** | `/cortex` `/ultrathunk` `/guardian` `/nexus` `/unified` |
| **Memory** | `/consolidate` `/learn` `/forget` `/ethics` |

**Wake Words**: "Hey Alfred", "Alfred", "Batcomputer"

## Critical Patterns

### ALWAYS use PathManager
```python
from core.path_manager import PathManager
brain_db = PathManager.BRAIN_DB  # CORRECT
# brain_db = "C:/path/..."       # WRONG
```

### Graceful Degradation
```python
try:
    from core.cortex import CORTEX
    CORTEX_AVAILABLE = True
except ImportError:
    CORTEX_AVAILABLE = False
```

## Brain Tables (11)
conversations, knowledge, preferences, patterns, skills, mistakes, topics, context_windows, web_cache, security_scans, market_data

## Environment Variables
```bash
ALFRED_HOME="/custom/path"      # Override paths
ANTHROPIC_API_KEY="sk-ant-..."  # Cloud AI (optional)
```

## Key Principles
1. **Privacy First**: Local Ollama default, explicit consent for cloud
2. **Bounded Growth**: CORTEX ensures storage never exceeds limits
3. **Generative Compression**: ULTRATHUNK compresses while improving quality
4. **British Butler**: Wise, concise, slightly sarcastic personality
