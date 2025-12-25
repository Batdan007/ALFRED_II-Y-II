# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ALFRED-UBX is a cross-platform, privacy-first AI assistant with permanent memory. Unlike stateless AI assistants (ChatGPT, Claude, etc.), Alfred remembers every conversation through a patent-pending 11-table SQLite architecture.

**Status**: Patent pending (USPTO Provisional filed November 11, 2025)
**Author**: Daniel J Rita (BATDAN)
**Version**: 3.0.0-ultimate

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run Alfred Terminal (main interface)
python alfred_terminal.py

# Run tests
python tests/test_core.py
```

## Development Commands

### Running Alfred
```bash
# Main terminal interface
python alfred_terminal.py
```

### Testing Components
```bash
# Test core modules
python tests/test_core.py

# Test brain operations directly
python core/brain.py stats        # View memory statistics
python core/brain.py insights     # Get learning insights
python core/brain.py topics       # Show tracked topics
python core/brain.py skills       # Show skill proficiency
python core/brain.py consolidate  # Consolidate memory
python core/brain.py test         # Run brain tests

# Test platform detection and paths
python core/path_manager.py
python core/platform_utils.py

# Test configuration loader
python core/config_loader.py

# Test voice system
python test_alfred_voice_interactive.py
python test_voices_simple.py
```

### Installing British Voice (Windows)
```powershell
.\install_british_voice.ps1
```

## Architecture

### Core Components

**AlfredBrain** (`core/brain.py`) - Patent-pending persistent memory system
- 11-table SQLite architecture storing conversations, knowledge, patterns, skills, etc.
- Auto-extracts knowledge and preferences from conversations
- Importance (1-10) and confidence (0.0-1.0) scoring
- Database location: Platform-specific (see PathManager)

**PathManager** (`core/path_manager.py`) - Cross-platform path management
- **Windows**: `C:/Drive`
- **macOS**: `~/Library/Application Support/Alfred`
- **Linux**: `~/.alfred`
- Override with `ALFRED_HOME` environment variable
- **CRITICAL**: Always use `PathManager` - never hardcode paths

**MultiModelOrchestrator** (`ai/multimodel.py`) - Cascading AI fallback
- Fallback chain: Ollama (local) → Claude → Groq → OpenAI
- Privacy-first: defaults to local Ollama
- Integrated with PrivacyController

**AlfredTerminal** (`alfred_terminal.py`) - Interactive CLI
- Rich terminal UI with markdown rendering
- Persistent conversation memory via AlfredBrain
- Commands: `/help`, `/memory`, `/voice`, `/privacy`, `/topics`, `/skills`, `/patterns`, `/exit`
- Voice integration (toggle with `/voice`)

**PrivacyController** (`core/privacy_controller.py`) - Privacy management
- Three modes: LOCAL (default), HYBRID, CLOUD
- Explicit user approval required for cloud AI access
- Tracks privacy settings and cloud provider usage

**AlfredVoice** (`capabilities/voice/alfred_voice.py`) - British butler voice
- Platform-specific voice selection (Microsoft Ryan on Windows, Daniel on macOS, espeak on Linux)
- Personality types: GREETING, CONFIRMATION, WARNING, SUGGESTION, SARCASM, INFORMATION, ERROR
- Importance-based speaking decisions

**Platform Utilities** (`core/platform_utils.py`) - Platform detection
- Functions: `get_platform_name()`, `is_windows()`, `is_macos()`, `is_linux()`, `is_mobile()`
- Platform capabilities: `supports_voice()`, `supports_emoji()`
- `get_recommended_voice_for_platform()`

### AI Integration

**Local AI** (`ai/local/ollama_client.py`)
- Connects to local Ollama instance (http://localhost:11434)
- Default model: dolphin-mixtral:8x7b
- Fallback models: llama3.3:70b, dolphin-llama3:8b

**Cloud AI** (`ai/cloud/`)
- `claude_client.py` - Anthropic Claude (requires ANTHROPIC_API_KEY)
- `openai_client.py` - OpenAI GPT-4 (requires OPENAI_API_KEY)
- `groq_client.py` - Groq Mixtral (requires GROQ_API_KEY)
- All require explicit privacy approval via PrivacyController

## Critical Coding Patterns

### Path Management
```python
from core.path_manager import PathManager

# CORRECT - always use PathManager
brain_db = PathManager.BRAIN_DB
model_path = PathManager.get_model_path('ollama', 'model_name')
log_file = PathManager.get_log_file('alfred', 'session.log')

# WRONG - never hardcode paths
brain_db = "C:/Drive/data/alfred_brain.db"  # ❌ Don't do this
```

### AlfredBrain Usage
```python
from core.brain import AlfredBrain

brain = AlfredBrain()

# Get conversation context
context = brain.get_conversation_context(limit=5)

# Store conversation
brain.store_conversation(
    user_input="user input",
    alfred_response="alfred response",
    success=True
)

# Knowledge operations
brain.store_knowledge("category", "key", "value", importance=8)
knowledge = brain.recall_knowledge("category", "key")

# Statistics
stats = brain.get_memory_stats()
```

### Privacy-First Cloud Access
```python
from core.privacy_controller import PrivacyController, CloudProvider

controller = PrivacyController()  # Defaults to LOCAL mode

# Request cloud access (prompts user)
if controller.request_cloud_access(CloudProvider.CLAUDE, "Need advanced reasoning"):
    response = claude_client.generate(prompt)
else:
    response = local_model.generate(prompt)
```

### Multi-Model AI
```python
from ai.multimodel import MultiModelOrchestrator

ai = MultiModelOrchestrator(privacy_controller=privacy)
response = ai.generate(prompt, context)  # Auto-cascades through fallback chain
```

### Voice System
```python
from capabilities.voice.alfred_voice import AlfredVoice, VoicePersonality

voice = AlfredVoice(privacy_mode=True)  # Auto-detects platform voice

voice.greet()  # "Good evening, sir."
voice.confirm("Starting analysis")
voice.warn("This operation is irreversible")
voice.error("Connection failed")
```

### Graceful Degradation (Import Pattern)
```python
# All modules use graceful degradation for optional dependencies
try:
    from optional_module import Feature
    FEATURE_AVAILABLE = True
except ImportError:
    FEATURE_AVAILABLE = False

# Later in code
if FEATURE_AVAILABLE:
    result = Feature.do_something()
else:
    print("Feature not available. Install: pip install ...")
```

## Environment Variables

```bash
# Optional: Override Alfred home directory
export ALFRED_HOME="/custom/path"

# Optional: Cloud AI API keys
export ANTHROPIC_API_KEY="sk-ant-..."
export OPENAI_API_KEY="sk-..."
export GROQ_API_KEY="gsk_..."
```

## Platform Support

**Fully Supported**:
- Windows 10/11 (C:/Drive storage, Microsoft Ryan/George voices)
- macOS (~/Library/Application Support/Alfred, Daniel/Alex voices)
- Linux (~/.alfred storage, espeak with British accent)

**Planned**:
- iOS/Android (app sandbox storage)
- Web (browser-based interface)

## Key Design Principles

1. **Privacy First**: Local-only by default, explicit consent for cloud access
2. **Persistent Memory**: Everything stored in SQLite with importance/confidence scoring
3. **Platform-Agnostic**: Core modules work on Windows/macOS/Linux
4. **Centralized Paths**: Always use PathManager class
5. **British Butler Personality**: Wise, concise, slightly sarcastic, warns when needed
6. **Multi-Model Support**: Cascading fallback from local to cloud AI

## Project Structure

```
ALFRED-UBX/
├── alfred_terminal.py          # Main entry point - interactive CLI
├── core/
│   ├── brain.py               # Patent-pending 11-table memory system
│   ├── path_manager.py        # Cross-platform path management
│   ├── platform_utils.py      # Platform detection utilities
│   ├── privacy_controller.py  # Privacy-first controls
│   ├── context_manager.py     # Conversation context management
│   ├── config_loader.py       # YAML configuration
│   └── ui_launcher.py         # Smart browser launching
├── capabilities/
│   ├── voice/
│   │   ├── alfred_voice.py    # British butler voice system
│   │   └── speech_to_text.py  # STT (future)
│   └── security/
│       └── strix_scanner.py   # Strix security scanner integration (optional)
├── ai/
│   ├── multimodel.py          # Multi-model orchestrator
│   ├── local/
│   │   └── ollama_client.py   # Local Ollama integration
│   └── cloud/
│       ├── claude_client.py   # Anthropic Claude
│       ├── openai_client.py   # OpenAI GPT-4
│       └── groq_client.py     # Groq Mixtral
├── mcp/
│   ├── alfred_mcp_server.py   # MCP server for Claude Code integration
│   ├── README.md              # MCP setup and usage guide
│   └── claude_code_config_example.json  # Config template
├── tests/
│   └── test_core.py           # Core module tests
├── .claude/                   # Claude Code infrastructure (PAI integration)
│   ├── agents/                # Specialized AI personalities
│   │   ├── alfred-engineer.md # ALFRED engineering agent
│   │   ├── alfred-researcher.md # ALFRED research agent
│   │   ├── engineer.md        # Generic engineer
│   │   ├── researcher.md      # Generic researcher
│   │   ├── designer.md        # UI/UX designer
│   │   ├── pentester.md       # Security tester
│   │   └── architect.md       # System architect
│   ├── commands/              # Custom slash commands
│   ├── hooks/                 # Event-driven automation
│   │   ├── initialize-session.ts    # Session startup
│   │   ├── capture-all-events.ts    # Event capture
│   │   ├── capture-session-summary.ts # Session summaries
│   │   └── lib/               # Hook utilities
│   ├── skills/                # Self-contained AI capabilities
│   │   ├── CORE/              # ALFRED core skill (auto-loads)
│   │   │   ├── SKILL.md       # ALFRED identity & capabilities
│   │   │   ├── CONSTITUTION.md # System architecture
│   │   │   └── SkillSystem.md # Skill creation guide
│   │   └── fabric/            # Fabric AI integration (242+ patterns)
│   │       └── fabric-repo/   # Fabric patterns repository
│   ├── Observability/         # Real-time agent monitoring dashboard
│   │   ├── apps/client/       # Vue.js monitoring UI
│   │   └── apps/server/       # WebSocket event server
│   ├── settings.json          # Claude Code configuration
│   └── .env.example           # API key template
├── requirements.txt           # Python dependencies
├── CLAUDE.md                  # This file
├── README.md                  # Project documentation
├── PROJECT_SUMMARY.md         # Complete project context
└── PATENT_TRACKING.md         # Patent status and claims
```

## Claude Code Integration (PAI)

ALFRED-UBX integrates **Personal AI Infrastructure (PAI)** by Daniel Miessler, adding powerful Claude Code capabilities.

### What is PAI?

PAI (Personal AI Infrastructure) is an open-source scaffolding for building AI-powered operating systems on Claude Code. It provides:

- **Skills Architecture**: Self-contained AI capabilities with 3-tier progressive disclosure
- **Agent System**: Specialized AI personalities for different tasks
- **Hook System**: Event-driven automation (session start, tool output capture, etc.)
- **Observability**: Real-time agent monitoring dashboard
- **Fabric AI**: 242+ AI patterns for content analysis

### The `.claude` Directory

The `.claude` directory contains Claude Code infrastructure:

#### **agents/** - Specialized AI Personalities
- `alfred-engineer.md` - British butler engineer with ALFRED brain access
- `alfred-researcher.md` - British butler researcher with memory integration
- `engineer.md`, `researcher.md`, `designer.md`, `pentester.md`, `architect.md`

**Usage:** Launch agents with the Task tool for parallel execution
```typescript
Task({
  prompt: "Implement feature X",
  subagent_type: "alfred-engineer",
  model: "sonnet"  // haiku for simple tasks, opus for complex
})
```

#### **commands/** - Custom Slash Commands
Create custom commands for frequently-used operations.

#### **hooks/** - Event-Driven Automation
- `initialize-session.ts` - Loads CORE skill at session start
- `capture-all-events.ts` - Captures all events to history
- `capture-session-summary.ts` - Generates session summaries
- `lib/pai-paths.ts` - Path resolution utilities

**Auto-Execution:** Hooks run automatically on events (session start, tool use, etc.)

#### **skills/** - Self-Contained Capabilities

**CORE Skill** (auto-loads at session start):
- `.claude/skills/CORE/SKILL.md` - ALFRED identity, personality, capabilities
- `.claude/skills/CORE/CONSTITUTION.md` - System architecture and philosophy
- `.claude/skills/CORE/SkillSystem.md` - How to create custom skills

**Fabric AI Skill**:
- `.claude/skills/fabric/` - Integration with 242+ AI analysis patterns
- Patterns: `extract_wisdom`, `analyze_paper`, `extract_insights`, etc.

**Other Skills:**
- `brightdata/` - 4-tier progressive web scraping
- `art/` - Visual content generation
- Custom skills can be added following the skill system pattern

#### **Observability/** - Real-Time Monitoring
WebSocket-based dashboard for monitoring agent activity:
- Live pulse charts
- Event timelines
- Swim lanes for parallel agents
- Multiple themes (Tokyo Night, Nord, Catppuccin)
- Security obfuscation for sensitive data

**Run:** `cd .claude/Observability && bun install && bun run dev`

#### **settings.json** - Claude Code Configuration
Configures agents, hooks, permissions, and system behavior.

### Integration with ALFRED's Brain

The PAI agents have been customized to integrate with ALFRED's persistent memory:

**alfred-engineer.md:**
```python
from core.brain import AlfredBrain

brain = AlfredBrain()
# Access conversation context
context = brain.get_conversation_context(limit=5)
# Store implementation decisions
brain.store_knowledge("engineering", "api_design", "REST pattern", importance=7)
```

**alfred-researcher.md:**
```python
from core.brain import AlfredBrain

brain = AlfredBrain()
# Check existing research
existing = brain.recall_knowledge("research", topic)
# Store findings with confidence
brain.store_knowledge("research", topic, findings, importance=8, confidence=0.85)
```

### Using Fabric AI Patterns

ALFRED includes Fabric AI with 242+ content analysis patterns:

```bash
# Extract insights from text
echo "content" | fabric --pattern extract_insights

# Analyze research papers
cat paper.pdf | fabric --pattern analyze_paper

# Extract wisdom from articles
cat article.md | fabric --pattern extract_wisdom

# Analyze security threats
cat report.txt | fabric --pattern analyze_threat_report

# Create summaries
echo "long content" | fabric --pattern create_summary
```

**Popular Patterns:**
- `extract_wisdom` - Extract key insights and wisdom
- `analyze_paper` - Analyze research papers
- `extract_insights` - Extract actionable insights
- `create_summary` - Create concise summaries
- `analyze_claims` - Analyze and verify claims
- `review_code` - Code review and suggestions
- `extract_patterns` - Identify patterns in content

### Agent Delegation & Parallelization

**Launch multiple agents in parallel:**
```typescript
// Single message with multiple Task calls
Task({ prompt: "Research company A", subagent_type: "alfred-researcher", model: "haiku" })
Task({ prompt: "Research company B", subagent_type: "alfred-researcher", model: "haiku" })
Task({ prompt: "Research company C", subagent_type: "alfred-researcher", model: "haiku" })
```

**Model Selection:**
- `haiku` - Quick tasks (10-20x faster)
- `sonnet` - Standard implementation (good balance)
- `opus` - Complex reasoning (maximum intelligence)

### British Butler Integration

All ALFRED agents maintain the British butler personality:

**alfred-engineer.md:**
- "The implementation is complete, sir."
- "I must warn you, sir, this operation cannot be undone."
- "Apologies, sir. The implementation encountered an unexpected condition."

**alfred-researcher.md:**
- "I shall commence research on this topic, sir."
- "My research indicates that..., sir."
- "I'm afraid the sources are conflicting on this point, sir."

### File Organization

**Claude Code Files (`.claude/`):**
- `agents/` - Specialized AI personalities
- `commands/` - Custom slash commands
- `hooks/` - Event-driven automation
- `skills/` - Self-contained capabilities
- `Observability/` - Monitoring dashboard
- `settings.json` - Configuration
- `.env` - API keys (NEVER commit)

**ALFRED Files (root):**
- `core/brain.py` - Persistent memory system
- `ai/multimodel.py` - Multi-model orchestration
- `capabilities/voice/` - British butler voice
- Platform-specific data stored per PathManager

### Quick Reference

**Session Start:**
1. CORE skill auto-loads (`.claude/skills/CORE/SKILL.md`)
2. ALFRED identity and capabilities initialized
3. Hooks capture events to history

**Agent Delegation:**
```typescript
Task({
  prompt: "Detailed task description",
  subagent_type: "alfred-engineer" | "alfred-researcher" | "engineer" | "researcher",
  model: "haiku" | "sonnet" | "opus"
})
```

**Fabric Patterns:**
```bash
cat content.txt | fabric --pattern extract_wisdom
```

**Memory Access (in agents):**
```python
from core.brain import AlfredBrain
brain = AlfredBrain()
context = brain.get_conversation_context(limit=5)
```

## The Alfred Brain (Patent-Pending)

### 11-Table Architecture

1. **conversations** - Long-term conversation memory with importance, sentiment, topics
2. **knowledge** - Extracted facts and insights with confidence scoring
3. **preferences** - User adaptation data with confidence levels
4. **patterns** - Behavioral learning patterns with success rates
5. **skills** - Capability proficiency tracking (0.0-1.0 scale)
6. **mistakes** - Error learning database with "learned" flags
7. **topics** - Subject interest tracking with frequency
8. **context_windows** - Recent activity context
9. **web_cache** - Crawled content storage
10. **security_scans** - Security analysis results
11. **market_data** - Financial data caching

### Key Innovations

- **Automatic Knowledge Extraction**: Learns from conversations without commands
- **Dual Scoring**: Confidence (0.0-1.0) × Importance (1-10) weighting
- **Mistake-Based Learning**: Explicit "learned" flags prevent error repetition
- **Memory Consolidation**: Self-optimizing like human sleep
- **Performance**: <1ms recall (21x faster than vector databases)

## Important Notes

- **NO hardcoded paths**: Always use `PathManager` class
- **Privacy default**: System defaults to LOCAL mode, cloud requires explicit approval
- **Voice priority**: Microsoft Ryan (Windows) > Daniel (macOS) > espeak (Linux)
- **Memory importance**: Scale 1-10, auto-archives conversations <3 after 90 days
- **Confidence scoring**: 0.0-1.0, strengthened by access frequency
- **Auto-extraction**: Brain automatically extracts preferences/facts from conversations
- **Console encoding**: UTF-8 encoding fixes applied on Windows

## Configuration

YAML-based configuration from `{platform_root}/config/`:
- **alfred.yaml**: Brain, logging, features
- **models.yaml**: Ollama, Claude, OpenAI, Groq, voice, vision
- **integrations.yaml**: RAG, Fabric AI
- **paths.yaml**: Directory structure reference

Access with:
```python
from core.config_loader import ConfigLoader

loader = ConfigLoader()
value = loader.get('alfred', 'brain.database_path')
```

## Terminal Commands

When running `alfred_terminal.py`:

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
- `/scan <target>` - Run AI security scan with Strix (directory, URL, or GitHub repo)
- `/security` - Show security scan history and vulnerability summary
- `/exit` - Exit Alfred (saves everything)

## Tool Mode (Like Claude Code)

Alfred can work like Claude Code with tool use capabilities!

**Enable tool mode:**
```
/tools on
```

**What it does:**
- Gives Alfred access to tools: read_file, write_file, edit_file, bash, grep, glob, strix_scan
- Alfred decides which tools to use based on your request
- Multi-step task execution (plan → execute → verify)
- Requires Claude API (ANTHROPIC_API_KEY)

**Example usage:**
```
You: Alfred, read core/brain.py and explain the memory consolidation system

Alfred: [Uses read_file tool]
Alfred: The consolidation system uses importance scoring to archive old conversations...

You: Find all TODO comments in Python files

Alfred: [Uses glob to find *.py files, then grep for "TODO"]
Alfred: Found 12 TODOs across 5 files, sir...

You: Run the tests and tell me if they pass

Alfred: [Uses bash to run pytest]
Alfred: Tests completed, sir. 42 passed, 2 failed...

You: Check my web app for SQL injection vulnerabilities

Alfred: [Uses strix_scan tool]
Alfred: Most concerning, sir. I've discovered 2 critical vulnerabilities that require immediate attention...
```

**Available tools:**
- `read_file` - Read file contents
- `write_file` - Create/overwrite files
- `edit_file` - Search and replace in files
- `bash` - Execute shell commands
- `grep` - Search file contents (regex)
- `glob` - Find files by pattern
- `strix_scan` - AI-powered security testing (optional, requires Strix installation)
- `dontlookup_parse` - DVB-S2(X) satellite communication parser (optional, requires DontLookUp installation)
- `camdan_engineering` - Engineering & building management (optional, requires CAMDAN service)

## Claude Code Integration (MCP) - **NEW: 5 MCP SERVERS WITH 46 TOOLS!**

ALFRED now provides **5 complete MCP servers** that expose ALFRED's brain, engineering tools, security scanning, satellite analysis, and multi-agent platform engineering to Claude Code!

### Quick Start

```bash
# 1. Install MCP
pip install mcp

# 2. Test servers
python mcp/test_mcp_servers.py

# 3. Copy config to Claude Code
# Windows:
copy mcp\claude_code_config.json %APPDATA%\Claude\claude_desktop_config.json

# 4. Restart Claude Code
```

**Full Guide:** See `mcp/QUICKSTART.md` and `mcp/README.md`

### The 5 MCP Servers (46 Total Tools)

#### 1. **alfred-brain** (16 tools)
- **Memory**: recall_knowledge, store_knowledge, get_conversation_context, store_mistake
- **Skills**: get_skills, get_topics, get_patterns, get_memory_stats
- **Voice**: speak (British butler), toggle_voice
- **Privacy**: get_privacy_status, request_cloud_access, set_privacy_mode
- **AI**: get_available_models, generate_with_model, consolidate_memory

#### 2. **camdan-engineering** (8 tools)
- **Engineering**: query_engineering (NIST, EBSCO, building codes)
- **Cost**: estimate_cost (AI-powered construction estimation)
- **Compliance**: check_compliance (all 50 US states)
- **Analysis**: analyze_plan (computer vision), predict_maintenance
- **Data**: get_building_codes, search_nist, search_ebsco

#### 3. **strix-security** (8 tools)
- **Scanning**: scan_directory, scan_url, scan_github
- **Results**: get_scan_results, list_scans
- **Vulnerabilities**: get_vulnerability_details, retest_vulnerability
- **Trends**: get_vulnerability_trends

#### 4. **dontlookup-dvbs2** (6 tools)
- **Parsing**: parse_capture (9 parser variants)
- **Analysis**: list_parsers, analyze_stats, extract_protocols
- **Results**: get_results, compare_parsers

#### 5. **caipe-agents** (8 tools)
- **Agents**: GitHub, ArgoCD, PagerDuty, Jira, Slack, Confluence, Backstage, Komodor
- **Operations**: call_github_agent, call_argocd_agent, call_pagerduty_agent, call_jira_agent, call_slack_agent
- **Orchestration**: orchestrate_multi_agent (coordinate multiple agents)
- **Discovery**: list_agents, get_agent_capabilities

### Configuration

**Single server example:**
```json
{
  "mcpServers": {
    "alfred-brain": {
      "command": "python",
      "args": ["-m", "mcp.alfred_mcp_server"],
      "cwd": "C:/Alfred_UBX",
      "env": {
        "ALFRED_HOME": "C:/Drive"
      }
    }
  }
}
```

**All 5 servers:** Copy `mcp/claude_code_config.json` which includes all servers pre-configured!

### Example Usage in Claude Code

```javascript
// Get ALFRED's brain statistics
await alfred_get_memory_stats();

// Store knowledge
await alfred_store_knowledge({
  category: "coding_style",
  key: "python",
  value: "Type hints + descriptive names",
  importance: 8
});

// Estimate construction cost
await camdan_estimate_cost({
  project_description: "5-story office building",
  square_footage: 50000,
  building_type: "office",
  location: "Seattle, WA"
});

// Security scan
await strix_scan_url({
  url: "https://myapp.com",
  scan_type: "owasp-top-10"
});

// Parse satellite capture
await dontlookup_parse_capture({
  capture_path: "/path/to/capture.dvbs2",
  parser_type: "auto"
});

// Deploy with ArgoCD
await caipe_call_argocd_agent({
  action: "deploy",
  parameters: { app: "my-app", version: "v2.0" }
});
```

### Multi-Tool Workflows

Combine tools from all servers:

```javascript
// 1. Store task in brain
await alfred_store_knowledge({
  category: "current_task",
  key: "deployment",
  value: "Deploying v2.0"
});

// 2. Security scan
await strix_scan_github({
  repo_url: "https://github.com/user/repo",
  branch: "v2.0"
});

// 3. Deploy
await caipe_call_argocd_agent({
  action: "deploy",
  parameters: { app: "my-app" }
});

// 4. Notify team
await caipe_call_slack_agent({
  action: "send_message",
  parameters: { channel: "#deployments", text: "v2.0 live!" }
});

// 5. Record completion
await alfred_store_knowledge({
  category: "deployments",
  key: "v2.0",
  value: "Success"
});
```

### Documentation

- **Quick Start**: `mcp/QUICKSTART.md` (5-minute setup)
- **Full Reference**: `mcp/README.md` (all 46 tools documented)
- **Config Template**: `mcp/claude_code_config.json`
- **Test Suite**: `python mcp/test_mcp_servers.py`

### Architecture
```
┌──────────────┐         MCP Protocol         ┌────────────────────┐
│ Claude Code  │◄──────────(stdio)───────────►│ ALFRED MCP Servers │
│              │                               │  (5 servers)       │
└──────────────┘                               └─────────┬──────────┘
                                                        │
                    ┌───────────────────────────────────┼───────────────────────┐
                    │                                   │                       │
              ┌─────▼──────┐    ┌──────────┐    ┌─────▼──────┐    ┌──────────┐
              │ AlfredBrain │    │  CAMDAN  │    │   Strix    │    │  CAIPE   │
              │  (SQLite)  │    │ (API/DB) │    │  (Docker)  │    │ (Agents) │
              └────────────┘    └──────────┘    └────────────┘    └──────────┘
```

### Benefits

**Example Usage in Claude Code:**

```
You: Use alfred_recall_knowledge to check what ALFRED knows about Python error handling

Claude Code: [Queries ALFRED's brain]
ALFRED knows: "Always use parameterized queries to prevent SQL injection"
(confidence: 0.95, importance: 9)

You: Remember that I prefer type hints in all Python functions

Claude Code: [Uses alfred_store_knowledge]
Stored in ALFRED's brain: preferences/type_hints with importance 7

You: What have we discussed recently that was important?

Claude Code: [Uses alfred_get_conversation_context with min_importance: 7]
Shows 5 high-importance conversations from the past week...
```

**Architecture:**
```
┌──────────────┐         MCP Protocol         ┌──────────────┐
│ Claude Code  │◄──────────(stdio)───────────►│ ALFRED MCP   │
│              │                               │   Server     │
└──────────────┘                               └──────┬───────┘
                                                      │
                                                      ▼
                                               ┌──────────────┐
                                               │ AlfredBrain  │
                                               │ (SQLite DB)  │
                                               └──────────────┘
```

**Benefits:**
- **Persistent Context**: Claude Code work is remembered across sessions
- **Shared Learning**: Both ALFRED and Claude Code learn from each conversation
- **Privacy-First**: Runs 100% locally, no external services
- **Mistake Prevention**: Recorded errors help avoid repeating them
- **Skill Tracking**: Monitor proficiency growth over time

See `mcp/README.md` for detailed documentation and troubleshooting.

## Security Scanning with Strix (Optional)

Alfred integrates with Strix, an AI-powered security testing framework, to provide autonomous vulnerability scanning.

**Installation:**
```bash
pipx install strix-agent
```

**Prerequisites:**
- Docker (running)
- Python 3.12+
- LLM API key (or local Ollama)

**Configuration:**
```bash
# For local scanning (100% private - no approval needed)
export STRIX_LLM="ollama/dolphin-mixtral:8x7b"

# For cloud scanning (requires privacy approval)
export STRIX_LLM="openai/gpt-5"
export LLM_API_KEY="your-api-key"
```

**Usage - Direct Commands:**
```bash
# Scan a local directory
/scan ./my-app

# Scan a web application
/scan https://example.com

# Scan a GitHub repository
/scan https://github.com/org/repo

# View security history
/security
```

**Usage - Tool Mode (AI-driven):**
```
You: Alfred, scan my Flask API for security vulnerabilities

Alfred: [Uses strix_scan tool automatically]
Alfred: Sir, I've completed the security assessment. Found 3 vulnerabilities:
        1. SQL Injection in /api/users endpoint (CRITICAL)
        2. Missing authentication on /admin route (HIGH)
        3. Weak session configuration (MEDIUM)
```

**Privacy Controls:**
- Local Ollama scans: No approval required (100% private)
- Cloud AI scans: Requires explicit privacy approval via PrivacyController
- Hybrid mode checks `STRIX_LLM` configuration automatically

**Features:**
- AI agents that act like real hackers
- Validates vulnerabilities with proof-of-concepts
- Detects: SQL injection, XSS, SSRF, IDOR, auth bypasses, and more
- Results stored in AlfredBrain with importance scoring
- British butler commentary on findings
- Voice alerts for critical vulnerabilities

**Memory Integration:**
- All scans stored in `security_scans` brain table
- Tracks vulnerability trends over time
- Importance scoring based on severity (Critical=10, High=8, etc.)
- Historical analysis via `/security` command

## DVB-S2 Satellite Communication Analysis with DontLookUp (Optional)

Alfred integrates with DontLookUp, a DVB-S2(X) IP encapsulation parser for analyzing satellite communication captures.

**Installation:**
```bash
git clone https://github.com/ucsdsysnet/dontlookup.git
cd dontlookup
pip install -r requirements.txt
```

**Prerequisites:**
- Python 3.10+
- Scapy, dpkt, kaitaistruct, and other dependencies (see requirements.txt)

**What it does:**
- Extracts IP packets from DVB-S2(X) satellite captures
- Supports multiple encapsulation standards (GSE, MPEG-TS, direct IP)
- Generates PCAP files viewable in Wireshark
- Security research on satellite communications

**Usage - Tool Mode (AI-driven):**
```
You: Alfred, parse this satellite capture and extract IP traffic

Alfred: [Uses dontlookup_parse tool automatically]
Alfred: Excellent work, sir. Successfully extracted 12,456 packets from 5,234 BBFrames.
        The satellite communication has been decoded.

You: Try different parser variants to find the right encoding

Alfred: [Uses dontlookup_parse with different parser types]
Alfred: After testing multiple parsers, sir, the GSE standard length variant
        yielded the most successful results.
```

**Available Parsers:**
- `dvbs2-ip` - Direct IP extraction (fastest, try this first)
- `dvbs2-rev-ip` - Byte-swapped IP extraction
- `dvbs2-mpegts` - Standard MPEG-TS extraction
- `dvbs2-mpegts-crc` - MPEG-TS with Generic CRC
- `dvbs2-mpegts-newtec` - MPEG-TS with Newtec CRC
- `dvbs2-gse-stdlen-split-ip` - GSE with standard length and split fragment ID
- `dvbs2-gse-stdlen-std-ip` - GSE with standard length and standard fragment ID
- `dvbs2-gse-len2-split-ip` - GSE with 2-byte header length and split fragment ID
- `dvbs2-gse-len2-std-ip` - GSE with 2-byte header length and standard fragment ID
- `all` - Run all parsers (slow but comprehensive)

**Features:**
- Multiple parser variants for different DVB-S2 encapsulations
- PCAP output compatible with Wireshark/tshark
- Progress tracking for large capture files
- British butler commentary on extraction results
- Results stored in AlfredBrain with importance scoring

**Memory Integration:**
- Parse results stored in `security_scans` brain table (type: dontlookup-dvbs2)
- Tracks packet extraction success rates
- Importance scoring based on packets extracted
- Output file paths preserved for later analysis

**Use Cases:**
- Satellite communication security research
- Protocol analysis and reverse engineering
- Traffic pattern analysis in DVB-S2 networks
- Detecting anomalies in satellite protocols

## Engineering & Building Management with CAMDAN (Optional)

Alfred integrates with CAMDAN (Comprehensive AI Management for Design, Architecture & Engineering), an AI-powered engineering and building management system for construction, infrastructure, and facilities management.

**Installation:**
```bash
# CAMDAN is a separate service that runs alongside Alfred
cd C:/CAMDAN
docker-compose up -d
# Or run directly: python backend/main.py
```

**Prerequisites:**
- Python 3.11+
- Docker and Docker Compose (for full deployment)
- PostgreSQL 14+ (for data storage)
- Redis 6+ (for caching)

**What it does:**
- AI-powered cost estimation and budget management
- Building code compliance checking (all 50 US states)
- Predictive maintenance for infrastructure
- Building plan analysis with computer vision
- Engineering knowledge base (NIST data, EBSCO research, building codes)
- Project timeline and resource management

**Usage - Tool Mode (AI-driven):**
```
You: Alfred, what building codes apply to a 5-story office building in California?

Alfred: [Uses camdan_engineering tool automatically]
Alfred: According to California building codes, sir, a 5-story office building must comply with:
        1. California Building Code (CBC) Title 24
        2. International Building Code (IBC) occupancy group B
        3. Fire safety requirements for Type II construction
        4. Seismic zone 4 requirements for California

You: Estimate the cost to build a 50,000 square foot warehouse in Texas

Alfred: [Uses camdan_engineering tool for cost estimation]
Alfred: Based on current market data and construction costs in Texas, sir:
        Total Estimated Cost: $4,250,000

        Cost Breakdown:
        - Site preparation: $125,000
        - Foundation: $375,000
        - Structural steel: $1,500,000
        - Roof system: $625,000
        - Walls and envelope: $750,000
        - Utilities and MEP: $625,000
        - Finishes: $250,000

        This assumes industrial-grade construction with basic finishes.

You: Check if my building design meets fire safety codes

Alfred: [Uses camdan_engineering tool for compliance checking]
Alfred: I've performed a building code compliance check, sir. Found 2 violations:

        1. Fire Code Violation: Exit corridor width insufficient (36" required, 30" provided)
        2. Fire Code Violation: Fire extinguisher placement exceeds 75 ft maximum distance

        Recommendations:
        - Widen main corridor to minimum 36 inches
        - Add 2 additional fire extinguisher stations on east side
```

**Available Actions:**

1. **Engineering Query** (`action: "query"`)
   - Ask engineering questions about codes, standards, specifications
   - Query NIST data, EBSCO research, building code requirements
   - Get expert engineering knowledge with sources

2. **Cost Estimation** (`action: "estimate_cost"`)
   - AI-powered construction cost estimation
   - Location-specific pricing with market factors
   - Detailed cost breakdown by category
   - Square footage and building type analysis

3. **Compliance Checking** (`action: "check_compliance"`)
   - Check against all 50 US state building codes
   - IBC, NEC, IPC standards compliance
   - Identify code violations with severity levels
   - Get remediation recommendations

4. **Building Plan Analysis** (`action: "analyze_plan"`)
   - Computer vision analysis of building plans
   - Identify HVAC, electrical, plumbing, structural components
   - Extract specifications via OCR
   - Predict component lifespans using NIST data
   - Generate maintenance schedules

5. **Maintenance Prediction** (`action: "predict_maintenance"`)
   - Predict component maintenance needs
   - Calculate remaining lifespan
   - Estimate replacement costs
   - Identify critical components

**Features:**
- Specialized AI trained on engineering datasets (EBSCO Engineering Source, NIST SRD)
- All 50 US state building codes integrated
- Computer vision for building plan analysis
- Predictive maintenance algorithms
- Cost estimation with local market data
- British butler commentary on engineering findings
- Results stored in AlfredBrain with importance scoring

**Memory Integration:**
- Engineering queries stored as conversations (topic: "engineering")
- Cost estimates stored as knowledge (category: "engineering_costs")
- Compliance checks stored as security_scans (type: "building_code_compliance")
- Component data stored as patterns (type: "building_component")
- CAMDAN usage tracked as skill proficiency
- Building codes cached for fast retrieval

**Data Sources:**
- EBSCO Engineering Source (15,420+ records)
- NIST Standard Reference Data (8,950+ records)
- US Building Codes Database (12,500+ codes)
- Historical Project Data (1,247+ projects)
- Construction Market Data (5,200+ records)
- Weather/Climate Data for location analysis
- Vendor Performance Data

**Privacy & Deployment:**
- 100% local deployment option (no cloud required)
- Can run on-premises for sensitive projects
- Optional cloud AI for enhanced capabilities
- All data stays within your infrastructure
- HIPAA/compliance-friendly architecture

**Use Cases:**
- Construction cost budgeting and estimation
- Building code compliance verification
- Infrastructure maintenance planning
- Engineering knowledge queries
- Facility management and operations
- Building plan review and analysis
- Project timeline and resource planning
- Government building department operations

**API Integration:**
CAMDAN runs as a separate FastAPI service:
- API: http://localhost:8001
- Documentation: http://localhost:8001/docs
- Health Check: http://localhost:8001/health

**Example Workflows:**

*Construction Project Planning:*
```
You: Alfred, I'm planning a 75,000 sq ft office building in downtown Seattle.
     What building codes apply and what's the estimated cost?

Alfred: [Queries building codes and estimates cost]
Alfred: For downtown Seattle, sir, your project must comply with:
        - Washington State Building Code
        - Seattle Municipal Code Chapter 23
        - Seismic Design Category D requirements

        Estimated construction cost: $18,750,000 to $22,500,000
        This includes seismic retrofitting and sustainable building requirements.
```

*Facility Maintenance:*
```
You: Alfred, analyze the maintenance needs for our 20-year-old building

Alfred: [Analyzes building components]
Alfred: Based on the building's age and components, sir:
        - HVAC system: 2-3 years remaining life (replacement: $450,000)
        - Roof membrane: 5 years remaining (replacement: $180,000)
        - Electrical panels: 15 years remaining (upgrade recommended: $75,000)

        Priority: Schedule HVAC replacement within 24 months.
```

*Code Compliance Review:*
```
You: Alfred, check our building design for accessibility compliance

Alfred: [Performs compliance check]
Alfred: I've found 4 ADA accessibility violations, sir:
        1. Restroom door width insufficient (32" required, 30" provided)
        2. Ramp slope exceeds maximum 1:12 ratio
        3. Elevator cab too small for wheelchair turning radius
        4. Parking lot lacks required accessible spaces

        These must be corrected before permit approval.
```
- Memorize this to do list and ready it for continuing
- memorize for continyuing when the context is out and where is best place to save it user project or claude memory
- memorize and ciontinue
- memorize where we left off
- memorize where we left off