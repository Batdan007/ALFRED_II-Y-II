# ALFRED MCP Servers - Quick Start Guide

Get ALFRED's 5 MCP servers running with Claude Code in 5 minutes.

## What You Get

**5 MCP Servers** with **46 total tools**:

1. **alfred-brain** (16 tools) - Memory, voice, privacy, AI orchestration
2. **camdan-engineering** (8 tools) - Building codes, cost estimation
3. **strix-security** (8 tools) - Security scanning, vulnerability testing
4. **dontlookup-dvbs2** (6 tools) - Satellite communication analysis
5. **caipe-agents** (8 tools) - Multi-agent platform engineering

## Installation Steps

### Step 1: Install MCP Library

```bash
pip install mcp
```

### Step 2: Test MCP Servers

```bash
python mcp/test_mcp_servers.py
```

You should see:
```
✓✓✓ ALL TESTS PASSED ✓✓✓
MCP servers are ready to use with Claude Code!
```

### Step 3: Configure Claude Code

**Windows:**
```cmd
copy C:\Alfred_UBX\mcp\claude_code_config.json %APPDATA%\Claude\claude_desktop_config.json
```

**macOS:**
```bash
cp /path/to/Alfred_UBX/mcp/claude_code_config.json ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**Linux:**
```bash
cp /path/to/Alfred_UBX/mcp/claude_code_config.json ~/.config/Claude/claude_desktop_config.json
```

### Step 4: Update Paths

Edit the config file you just copied and change:

```json
{
  "mcpServers": {
    "alfred-brain": {
      "cwd": "C:/Alfred_UBX",     // ← Change to your installation path
      "env": {
        "ALFRED_HOME": "C:/Drive"  // ← Change if you use custom location
      }
    }
  }
}
```

### Step 5: Restart Claude Code

Close and reopen Claude Code.

### Step 6: Test It!

In Claude Code, try:

```
Use alfred_get_memory_stats to show ALFRED's brain statistics
```

If you see stats about conversations, knowledge, etc., **it's working!**

## Quick Examples

### Get Memory Stats
```
Use alfred_get_memory_stats
```

### Store Knowledge
```
Use alfred_store_knowledge to remember that my preferred coding style is "Python with type hints and descriptive variable names" (importance: 8)
```

### Query Knowledge
```
Use alfred_recall_knowledge to get my coding preferences
```

### Make ALFRED Speak
```
Use alfred_speak to say "Good evening, sir. All systems operational." with personality GREETING
```

### Estimate Construction Cost
```
Use camdan_estimate_cost for a 10,000 sq ft warehouse in Texas
```

### Security Scan
```
Use strix_scan_url to scan https://example.com for vulnerabilities
```

### List CAIPE Agents
```
Use caipe_list_agents to see all available platform engineering agents
```

## Troubleshooting

### "MCP server not found"

1. Check config path is correct
2. Verify Python version: `python --version` (need 3.11+)
3. Check logs: `%APPDATA%\Claude\logs\` (Windows)

### "Import errors"

```bash
pip install mcp
pip install -r requirements.txt
```

### "Path not found"

Update `cwd` in `claude_desktop_config.json` to your actual ALFRED installation path.

## What's Next?

**Full Documentation:** See `mcp/README.md` for:
- Complete tool reference (all 46 tools)
- Advanced usage examples
- Optional integrations (Strix, CAMDAN, DontLookUp)
- Privacy configuration
- Development guide

**Example Workflows:** See `mcp/README.md` for multi-tool workflows combining brain, security, engineering, and agents.

---

**Need Help?**

- Full docs: `mcp/README.md`
- Test servers: `python mcp/test_mcp_servers.py`
- Issues: https://github.com/anthropics/claude-code/issues
