# ALFRED

<div align="center">

<img src="https://img.shields.io/badge/AI-Privacy%20First-green?style=for-the-badge" alt="Privacy First"/>
<img src="https://img.shields.io/badge/Memory-Persistent-blue?style=for-the-badge" alt="Persistent Memory"/>
<img src="https://img.shields.io/badge/Voice-Enabled-purple?style=for-the-badge" alt="Voice Enabled"/>
<img src="https://img.shields.io/badge/Patent-Pending-orange?style=for-the-badge" alt="Patent Pending"/>

### Your AI butler that actually remembers you.

**Privacy-first. Runs locally. Never forgets what matters.**

[Quick Start](#quick-start) | [Features](#what-makes-alfred-different) | [Demo](#demo) | [Documentation](CLAUDE.md)

</div>

---

## The Problem

Every AI assistant has amnesia. You explain your preferences, your projects, your context - and next session? Gone. You're a stranger again.

Cloud AI services store your data on their servers. You have no control, no privacy, no ownership.

**ALFRED fixes both.**

---

## What Makes ALFRED Different

### 1. Persistent Memory (Patent-Pending)
ALFRED has an 11-table brain that remembers:
- Your conversations and context
- Your preferences and patterns
- What worked and what didn't
- Knowledge you've shared

```
"Remember that I prefer dark mode and hate verbose responses"
→ Stored forever. Never ask again.
```

### 2. Privacy First
- **Local by default** - Runs on Ollama, your machine, your data
- **Cloud optional** - Claude, Gemini, Groq, OpenAI available with explicit consent
- **Your data stays yours** - SQLite database on your disk

### 3. Bounded Growth
Most AI memory systems grow forever until they break. ALFRED has **CORTEX** - a 5-layer forgetting system that keeps memory bounded while preserving what matters.

### 4. Multi-Modal
- **Voice** - British butler TTS (Microsoft Ryan) + offline speech recognition
- **Vision** - Camera integration with face recognition
- **Speaker ID** - Knows who's talking, ignores the TV

### 5. Works Offline
No internet? No problem. ALFRED runs entirely local with Ollama.

---

## Quick Start

```bash
# Clone
git clone https://github.com/Batdan007/ALFRED_II-Y-II.git
cd ALFRED_II-Y-II

# Install (Python 3.11)
pip install -r requirements.txt
pip install -e .

# Start Ollama (one-time)
ollama serve
ollama pull llama3.2

# Run ALFRED
alfred                  # Text mode
alfred --voice          # Voice mode
```

**First run**: ALFRED creates a brain at `C:\Drive\data\alfred_brain.db` (Windows) or `~/.alfred/brain.db` (Mac/Linux).

---

## Demo

```
You: Remember that my project deadline is January 15th

ALFRED: Noted, sir. I've stored that your project deadline is
January 15th with high importance.

--- Next day, new session ---

You: What's my deadline?

ALFRED: Your project deadline is January 15th, sir.
```

**Voice Demo:**
```
You: "Hey Alfred, what's the weather?"

ALFRED: *speaks in British accent* "Currently 42°F in Gary,
Indiana, sir. I'd recommend a coat."
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         ALFRED                               │
├─────────────────────────────────────────────────────────────┤
│  BRAIN (11 tables)     │  CORTEX (5 layers)                 │
│  - conversations       │  - Sensory (immediate)             │
│  - knowledge           │  - Short-term (session)            │
│  - preferences         │  - Working (active)                │
│  - patterns            │  - Long-term (persistent)          │
│  - skills              │  - Archival (compressed)           │
│  - mistakes            │                                     │
├─────────────────────────────────────────────────────────────┤
│  AI CHAIN: Ollama → Claude → Gemini → Groq → OpenAI        │
├─────────────────────────────────────────────────────────────┤
│  VOICE: Edge TTS (Ryan) │ VOSK (offline STT) │ Speaker ID  │
├─────────────────────────────────────────────────────────────┤
│  SKILLS: security │ engineering │ research │ coding │ ...  │
└─────────────────────────────────────────────────────────────┘
```

---

## Core Technologies (Patent-Pending)

| Technology | What It Does |
|------------|--------------|
| **Brain** | 11-table SQLite memory with importance/confidence scoring |
| **CORTEX** | 5-layer forgetting architecture - memory never overflows |
| **ULTRATHUNK** | 640:1 generative compression - compress while improving quality |
| **Guardian** | Behavioral watermarking for IP protection |
| **NEXUS** | AI-to-AI communication protocol |

---

## Commands

| Command | Description |
|---------|-------------|
| `/memory` | View what ALFRED remembers |
| `/voice` | Toggle voice on/off |
| `/listen` | Listen for voice command |
| `/privacy` | Check/change privacy mode |
| `/learn` | Teach ALFRED something new |
| `/forget <topic>` | Remove from memory |
| `/tools` | Enter tool mode |
| `/exit` | Exit |

**Wake words**: "Hey Alfred", "Alfred", "Batcomputer"

---

## Privacy Modes

| Mode | Behavior |
|------|----------|
| **LOCAL** (default) | Ollama only - nothing leaves your machine |
| **HYBRID** | Local first, cloud with permission |
| **CLOUD** | Full cloud access enabled |

---

## Requirements

- **Python 3.11** (3.10+ works, not 3.13+)
- **Ollama** for local AI ([ollama.com](https://ollama.com))
- **8GB RAM** minimum (16GB recommended)
- **FFmpeg** for voice features

---

## Why Not Just Use ChatGPT/Claude?

| Feature | ChatGPT/Claude | ALFRED |
|---------|----------------|--------|
| Remembers you | Per-session only | Forever |
| Your data | On their servers | On your disk |
| Works offline | No | Yes |
| Voice I/O | Limited | Full (TTS + STT + Speaker ID) |
| Custom personality | No | Yes (British butler) |
| Open source | No | Yes |
| Free | $20+/mo | Free (with Ollama) |

---

## Roadmap

- [x] Persistent 11-table memory
- [x] Privacy-first architecture
- [x] Multi-model AI chain
- [x] Voice (TTS + STT)
- [x] Speaker recognition
- [x] Skills system
- [ ] Web UI dashboard
- [ ] Mobile app
- [ ] Multi-user support
- [ ] Plugin marketplace

---

## Joe Dog's Rule

ALFRED follows an inviolable ethical core:

> *"ALFRED shall NEVER be used for weapons or violence. Protects all life, guards the environment, guides humanity toward peace."*

> *"No one needs a missile that learns from its mistakes."* - BATDAN

---

## Contributing

Issues and PRs welcome. See [CLAUDE.md](CLAUDE.md) for development guidelines.

---

## License

Proprietary - Patent Pending (USPTO Provisional Filed November 11, 2025)

Core technologies (Brain, CORTEX, ULTRATHUNK, Guardian, NEXUS) are patent-protected.

---

## Author

**Daniel J. Rita (BATDAN)**
GxEum Technologies / CAMDAN Enterprizes

---

<div align="center">

**ALFRED** - *Artificial Lifeform For Refined Executive Decisions*

*Your AI butler. Remembers everything. Judges nothing.*

</div>
