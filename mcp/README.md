# ALFRED MCP Servers

Complete Model Context Protocol (MCP) integration for ALFRED-UBX and all integrated systems.

## Overview

This directory contains **5 MCP servers** that expose ALFRED's capabilities to Claude Code:

1. **alfred-brain** - Core memory, voice, privacy, and AI orchestration
2. **camdan-engineering** - Building codes, cost estimation, compliance checking
3. **strix-security** - AI-powered security testing and vulnerability scanning
4. **dontlookup-dvbs2** - Satellite communication analysis (DVB-S2 parser)
5. **caipe-agents** - Multi-agent platform engineering (GitHub, ArgoCD, Jira, etc.)

---

## Installation

### 1. Install MCP Library

```bash
pip install mcp
```

### 2. Install Optional Dependencies

```bash
# For Strix security scanning
pipx install strix-agent

# For CAMDAN engineering (if available)
# Clone and run CAMDAN service at http://localhost:8001

# For DontLookUp satellite analysis
git clone https://github.com/ucsdsysnet/dontlookup.git
cd dontlookup
pip install -r requirements.txt
```

### 3. Configure Claude Code

Copy `claude_code_config.json` to Claude Code's configuration directory:

**Windows:**
```cmd
copy mcp\claude_code_config.json %APPDATA%\Claude\claude_desktop_config.json
```

**macOS:**
```bash
cp mcp/claude_code_config.json ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**Linux:**
```bash
cp mcp/claude_code_config.json ~/.config/Claude/claude_desktop_config.json
```

### 4. Update Paths in Config

Edit the copied `claude_desktop_config.json` and update:
- `cwd`: Change `C:/Alfred_UBX` to your actual ALFRED installation path
- `ALFRED_HOME`: Change `C:/Drive` if you use a custom location
- `PYTHONPATH`: Ensure it points to your ALFRED directory

### 5. Restart Claude Code

MCP servers are loaded when Claude Code starts.

---

## MCP Server Capabilities

### 1. alfred-brain

**Tools (16 total):**

| Tool | Description |
|------|-------------|
| `alfred_recall_knowledge` | Query brain knowledge by category/key |
| `alfred_store_knowledge` | Store new knowledge with importance/confidence |
| `alfred_get_conversation_context` | Get conversation history with importance filtering |
| `alfred_store_mistake` | Record mistakes for learning |
| `alfred_get_skills` | Get skill proficiency levels (0.0-1.0) |
| `alfred_get_topics` | Get tracked topics with frequency |
| `alfred_get_patterns` | Get learned behavioral patterns |
| `alfred_get_memory_stats` | Get brain statistics |
| `alfred_speak` | Make ALFRED speak with British butler voice |
| `alfred_toggle_voice` | Enable/disable voice output |
| `alfred_get_privacy_status` | Get privacy mode and cloud usage |
| `alfred_request_cloud_access` | Request cloud AI access |
| `alfred_set_privacy_mode` | Set LOCAL/HYBRID/CLOUD mode |
| `alfred_get_available_models` | List available AI models |
| `alfred_generate_with_model` | Generate with specific model |
| `alfred_consolidate_memory` | Trigger memory consolidation |

**Example Usage:**

```javascript
// Query ALFRED's knowledge
await alfred_recall_knowledge({
  category: "preferences",
  key: "coding_style"
});

// Store new knowledge
await alfred_store_knowledge({
  category: "project_facts",
  key: "main_language",
  value: "Python 3.13",
  importance: 8,
  confidence: 1.0
});

// Get conversation context (high-importance only)
await alfred_get_conversation_context({
  limit: 5,
  min_importance: 7
});

// Make ALFRED speak
await alfred_speak({
  text: "Good evening, sir. The tests have passed successfully.",
  personality: "CONFIRMATION"
});
```

---

### 2. camdan-engineering

**Tools (8 total):**

| Tool | Description |
|------|-------------|
| `camdan_query_engineering` | Query NIST, EBSCO, building codes |
| `camdan_estimate_cost` | AI-powered construction cost estimation |
| `camdan_check_compliance` | Check building code compliance (all 50 states) |
| `camdan_analyze_plan` | Computer vision analysis of building plans |
| `camdan_predict_maintenance` | Predict component maintenance needs |
| `camdan_get_building_codes` | Get applicable codes for location/type |
| `camdan_search_nist` | Search NIST Standard Reference Data |
| `camdan_search_ebsco` | Search EBSCO Engineering Source |

**Example Usage:**

```javascript
// Estimate construction cost
await camdan_estimate_cost({
  project_description: "5-story office building with parking garage",
  square_footage: 50000,
  building_type: "office",
  location: "Seattle, WA",
  quality_level: "high-end"
});

// Check code compliance
await camdan_check_compliance({
  building_description: "3-story residential apartment building",
  building_type: "residential",
  location: "California",
  specifications: {
    stories: 3,
    occupancy_type: "R-2",
    construction_type: "V-A"
  }
});

// Predict maintenance
await camdan_predict_maintenance({
  component_type: "HVAC",
  installation_date: "2015-03-15",
  current_condition: "good",
  usage_intensity: "moderate"
});
```

---

### 3. strix-security

**Tools (8 total):**

| Tool | Description |
|------|-------------|
| `strix_scan_directory` | Scan local directory for vulnerabilities |
| `strix_scan_url` | Scan web application URL |
| `strix_scan_github` | Scan GitHub repository |
| `strix_get_scan_results` | Get scan results by ID |
| `strix_list_scans` | List recent scans |
| `strix_get_vulnerability_details` | Get vuln details with POC |
| `strix_retest_vulnerability` | Retest to verify fix |
| `strix_get_vulnerability_trends` | Get vulnerability trends |

**Example Usage:**

```javascript
// Scan a web application
await strix_scan_url({
  url: "https://example.com",
  scan_type: "owasp-top-10",
  max_depth: 3,
  include_authenticated: false
});

// Scan GitHub repository
await strix_scan_github({
  repo_url: "https://github.com/user/repo",
  branch: "main",
  scan_secrets: true,
  scan_dependencies: true
});

// Get vulnerability details
await strix_get_vulnerability_details({
  vulnerability_id: "vuln-12345",
  include_remediation: true,
  include_poc: true
});

// List recent scans
await strix_list_scans({
  limit: 10,
  target_type: "url"
});
```

---

### 4. dontlookup-dvbs2

**Tools (6 total):**

| Tool | Description |
|------|-------------|
| `dontlookup_parse_capture` | Parse DVB-S2 capture, extract IP packets |
| `dontlookup_list_parsers` | List 9 parser variants |
| `dontlookup_analyze_stats` | Get capture statistics |
| `dontlookup_extract_protocols` | Extract specific protocols |
| `dontlookup_get_results` | Retrieve parse results from brain |
| `dontlookup_compare_parsers` | Compare parser effectiveness |

**Available Parsers:**
- `dvbs2-ip` - Direct IP (fastest, try first)
- `dvbs2-rev-ip` - Byte-swapped IP
- `dvbs2-mpegts` - Standard MPEG-TS
- `dvbs2-mpegts-crc` - MPEG-TS with Generic CRC
- `dvbs2-mpegts-newtec` - MPEG-TS with Newtec CRC
- `dvbs2-gse-stdlen-split-ip` - GSE standard length, split fragment
- `dvbs2-gse-stdlen-std-ip` - GSE standard length, standard fragment
- `dvbs2-gse-len2-split-ip` - GSE 2-byte header, split fragment
- `dvbs2-gse-len2-std-ip` - GSE 2-byte header, standard fragment

**Example Usage:**

```javascript
// Parse capture with auto-detection
await dontlookup_parse_capture({
  capture_path: "/path/to/capture.dvbs2",
  parser_type: "auto",
  output_path: "/path/to/output.pcap",
  auto_detect: true
});

// Compare parsers
await dontlookup_compare_parsers({
  capture_path: "/path/to/capture.dvbs2",
  parsers: ["dvbs2-ip", "dvbs2-gse-stdlen-split-ip", "dvbs2-mpegts"]
});

// Extract specific protocols
await dontlookup_extract_protocols({
  capture_path: "/path/to/capture.dvbs2",
  protocols: ["TCP", "UDP", "HTTP"],
  parser_type: "dvbs2-ip"
});
```

---

### 5. caipe-agents

**Available Agents:**
- **github** - Repository operations, PRs, issues
- **argocd** - Deployment, sync, GitOps
- **pagerduty** - Incident management, on-call
- **jira** - Issue tracking, sprints
- **slack** - Team communication
- **confluence** - Documentation
- **backstage** - Developer portal
- **komodor** - Kubernetes troubleshooting
- **atlassian** - Atlassian suite integration

**Tools (8 total):**

| Tool | Description |
|------|-------------|
| `caipe_list_agents` | List all agents with capabilities |
| `caipe_get_agent_capabilities` | Get specific agent details |
| `caipe_call_github_agent` | GitHub operations |
| `caipe_call_argocd_agent` | Deployment operations |
| `caipe_call_pagerduty_agent` | Incident management |
| `caipe_call_jira_agent` | Issue tracking |
| `caipe_call_slack_agent` | Team communication |
| `caipe_orchestrate_multi_agent` | Multi-agent workflows |

**Example Usage:**

```javascript
// Create GitHub PR
await caipe_call_github_agent({
  action: "create_pr",
  parameters: {
    repo: "user/repo",
    title: "Add new feature",
    branch: "feature-branch",
    base: "main"
  }
});

// Deploy with ArgoCD
await caipe_call_argocd_agent({
  action: "deploy",
  parameters: {
    application: "my-app",
    environment: "production"
  }
});

// Orchestrate multiple agents
await caipe_orchestrate_multi_agent({
  task: "Deploy new version and notify team",
  agents: ["github", "argocd", "slack"],
  priority: "high"
});
```

---

## Privacy & Security

### Privacy Modes

ALFRED supports 3 privacy modes:
- **LOCAL** (default) - 100% local, no cloud AI
- **HYBRID** - Local first, cloud with approval
- **CLOUD** - Cloud AI allowed

### Security Scanning

Strix security scans require explicit configuration:
```bash
# Use local Ollama (no approval needed)
export STRIX_LLM="ollama/dolphin-mixtral:8x7b"

# Use cloud AI (requires approval)
export STRIX_LLM="openai/gpt-4"
export LLM_API_KEY="your-key"
```

---

## Troubleshooting

### MCP Servers Not Appearing

1. Check Claude Code logs: `%APPDATA%\Claude\logs\` (Windows)
2. Verify Python path: `python --version` (should be 3.11+)
3. Test server directly: `python -m mcp.alfred_mcp_server`
4. Check PYTHONPATH in config matches your installation

### Import Errors

```bash
# Install missing dependencies
pip install mcp
pip install -r requirements.txt
```

### CAMDAN/Strix/DontLookUp Not Available

These are optional. Servers will report unavailability gracefully.

To install:
```bash
# Strix
pipx install strix-agent

# DontLookUp
git clone https://github.com/ucsdsysnet/dontlookup.git
cd dontlookup && pip install -r requirements.txt

# CAMDAN - Requires separate installation at C:/CAMDAN
```

### Permission Errors

Run Claude Code as administrator (Windows) or check file permissions.

---

## Advanced Usage

### Combining Multiple MCP Servers

Claude Code can call tools from all servers simultaneously:

```javascript
// Store task in ALFRED brain
await alfred_store_knowledge({
  category: "current_task",
  key: "deployment",
  value: "Deploying v2.0 to production"
});

// Check security
await strix_scan_github({
  repo_url: "https://github.com/user/repo",
  branch: "release-v2.0"
});

// Deploy with ArgoCD
await caipe_call_argocd_agent({
  action: "deploy",
  parameters: { app: "my-app", version: "v2.0" }
});

// Notify team
await caipe_call_slack_agent({
  action: "send_message",
  parameters: {
    channel: "#deployments",
    text: "v2.0 deployed to production"
  }
});

// Store completion
await alfred_store_knowledge({
  category: "deployments",
  key: "v2.0",
  value: "Deployed successfully on 2025-11-25",
  importance: 8
});
```

### Building Custom Workflows

Use ALFRED brain to coordinate complex workflows:

1. Store workflow state in brain
2. Query brain before each step
3. Record successes/failures
4. Learn from mistakes

---

## Development

### Creating New MCP Servers

1. Copy template from `alfred_mcp_server.py`
2. Implement `list_tools()` handler
3. Implement `call_tool()` handler
4. Add to `claude_code_config.json`
5. Restart Claude Code

### Testing MCP Servers

```bash
# Test individual server
python -m mcp.alfred_mcp_server

# Check MCP protocol compliance
# (MCP Inspector tool: https://github.com/modelcontextprotocol/inspector)
```

---

## Resources

- **MCP Documentation**: https://modelcontextprotocol.io
- **MCP Python SDK**: https://github.com/modelcontextprotocol/python-sdk
- **ALFRED Documentation**: ../README.md
- **CAIPE Documentation**: ../.claude/CLAUDE.md

---

## Support

Issues or questions? Create an issue at:
https://github.com/anthropics/claude-code/issues

Include:
- MCP server name
- Error message
- `claude_desktop_config.json` (redact sensitive info)
- Python version
- Operating system
