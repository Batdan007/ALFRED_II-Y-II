# ALFRED II-Y-II: Money Machine Setup Guide

## Complete Step-by-Step Installation

---

## Prerequisites Checklist

Before starting, ensure you have:

- [ ] Windows 10/11, macOS, or Linux
- [ ] Python 3.10 or higher installed
- [ ] Git installed
- [ ] Internet connection
- [ ] (Optional) Docker Desktop for security scanning

---

## Step 1: Install Python

### Windows
1. Go to: https://www.python.org/downloads/
2. Download Python 3.12 or 3.13
3. Run installer
4. **IMPORTANT**: Check "Add Python to PATH"
5. Click "Install Now"

### Verify Installation
Open PowerShell or Command Prompt:
```bash
python --version
```
Should show: `Python 3.12.x` or higher

---

## Step 2: Install Git

### Windows
1. Go to: https://git-scm.com/download/win
2. Download and run installer
3. Use default options

### Verify Installation
```bash
git --version
```

---

## Step 3: Clone ALFRED II-Y-II

Open PowerShell/Terminal and run:

```bash
# Navigate to where you want ALFRED
cd C:\Users\YourName\Projects

# Clone the repository
git clone https://github.com/Batdan007/ALFRED_II-Y-II.git

# Enter the directory
cd ALFRED_II-Y-II
```

---

## Step 4: Install Dependencies

```bash
# Install all Python packages
pip install -r requirements.txt
```

This installs:
- AI providers (Claude, OpenAI, Groq, Gemini)
- Voice synthesis
- Web crawling
- Security scanning
- And more...

**If you get errors:**
```bash
# Try with --user flag
pip install -r requirements.txt --user

# Or upgrade pip first
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## Step 5: Configure API Keys

### Create your .env file
```bash
# Copy the example
copy .env.example .env

# Open in notepad (Windows)
notepad .env

# Or use VS Code
code .env
```

### Add Your API Keys

Edit `.env` with your keys:

```env
# AI Providers (get at least ONE)
ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
GROQ_API_KEY=your_key_here
GOOGLE_API_KEY=your_key_here

# Bug Bounty
HACKERONE_API_KEY=your_hackerone_key
HACKERONE_USERNAME=your_username
```

### Where to Get API Keys

| Provider | URL | Free Tier? |
|----------|-----|------------|
| Groq | https://console.groq.com/keys | Yes (free) |
| Anthropic | https://console.anthropic.com | $5 credit |
| OpenAI | https://platform.openai.com/api-keys | Pay as you go |
| Google | https://aistudio.google.com/apikey | Yes (free) |
| HackerOne | https://hackerone.com/settings/api_token | Free |

**Tip:** Start with Groq - it's free and fast.

---

## Step 6: (Optional) Install Docker for Security Scanning

For full Strix security scanning:

1. Download: https://www.docker.com/products/docker-desktop/
2. Install and restart computer
3. Open Docker Desktop (let it start)
4. Verify: `docker --version`

---

## Step 7: First Run

```bash
# Make sure you're in the ALFRED directory
cd C:\Users\YourName\Projects\ALFRED_II-Y-II

# Start ALFRED
python alfred_terminal.py
```

You should see ALFRED's interface. Type `/help` for commands.

---

## Step 8: Start Making Money

### Option A: Bug Bounty Hunting

```bash
# Hunt for vulnerabilities
python tools/bug_bounty_hunter.py https://target.com

# With Docker installed, use Strix
strix -t https://target.com -m quick
```

**Platforms to join:**
1. https://hackerone.com - Create account, verify email
2. https://bugcrowd.com - Alternative platform
3. https://immunefi.com - Crypto bounties (high payouts)

### Option B: Use ALFRED for Freelance Work

```bash
# Start ALFRED
python alfred_terminal.py

# Ask for help with tasks:
You: Help me write a Python script to scrape product prices
You: Generate a database migration for a users table
You: Write a proposal for a web scraping job on Upwork
```

### Option C: Web Intelligence Services

```bash
# Start the research-focused version
python variants/alfred_rag.py

# Use for:
# - Competitive research
# - Lead generation
# - Market analysis
```

---

## Quick Commands Reference

| Task | Command |
|------|---------|
| Start ALFRED | `python alfred_terminal.py` |
| Bug hunt | `python tools/bug_bounty_hunter.py <url>` |
| Security scan | `strix -t <url> -m quick` |
| Web UI | `python variants/alfred_unified.py` |
| Research mode | `python variants/alfred_rag.py` |
| Find gigs | `python tools/upwork_opportunity_finder.py` |

---

## Folder Structure After Setup

```
ALFRED_II-Y-II/
├── .env                    ← Your API keys (keep secret!)
├── alfred_terminal.py      ← Main entry point
├── tools/
│   ├── bug_bounty_hunter.py
│   └── upwork_opportunity_finder.py
├── variants/
│   ├── alfred_unified.py   ← Web UI
│   └── alfred_rag.py       ← Research mode
├── bounty_results/         ← Your scan reports
└── MONEY_GUIDE.md          ← Detailed money-making guide
```

---

## Troubleshooting

### "Python not found"
- Reinstall Python, check "Add to PATH"
- Restart terminal after installing

### "Module not found"
```bash
pip install -r requirements.txt --user
```

### "Permission denied"
- Run PowerShell as Administrator
- Or use `--user` flag with pip

### "API key invalid"
- Check for extra spaces in .env file
- Regenerate key from provider's website

### "Docker not running" (for Strix)
- Open Docker Desktop app
- Wait for it to fully start
- Try again

---

## Daily Money-Making Routine

### Morning (30 min)
```bash
# Check for new bounty programs
# Browse HackerOne directory for new targets

# Run quick scans
python tools/bug_bounty_hunter.py https://new-target.com
```

### Work Session (2-4 hours)
```bash
# Start ALFRED
python alfred_terminal.py

# Hunt bugs, do client work, research
```

### Evening
```bash
# Write and submit bug reports
# Check for responses on HackerOne
# Invoice clients
```

---

## Expected Earnings Timeline

| Week | Goal |
|------|------|
| 1 | Setup complete, first scans |
| 2 | First bug submission |
| 3-4 | First payout ($100-500) |
| Month 2+ | $500-2000/month part-time |
| Month 6+ | $2000-5000/month |

---

## Support

- Read: `MONEY_GUIDE.md` for detailed strategies
- Issues: https://github.com/Batdan007/ALFRED_II-Y-II/issues
- Contact: danieljrita@hotmail.com

---

## Quick Start Checklist

- [ ] Python installed
- [ ] Git installed
- [ ] Repository cloned
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file created with API keys
- [ ] ALFRED runs (`python alfred_terminal.py`)
- [ ] HackerOne account created
- [ ] First target scanned
- [ ] Docker installed (optional, for Strix)

---

*ALFRED II-Y-II - Your AI Money Machine*
*Created by Daniel J. Rita (BATDAN)*
