# ALFRED Installation Guide
## Your Personal AI Companion with Persistent Memory

Created by Daniel J Rita (BATDAN) | GxEum Technologies

---

## Quick Install (5 minutes)

### Prerequisites
- Python 3.10+ installed
- Git installed
- (Optional) Ollama installed for local AI

### Step 1: Clone the Repository
```bash
git clone https://github.com/Batdan007/ALFRED_II-Y-II.git ALFRED
cd ALFRED
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Run ALFRED
```bash
python alfred_terminal.py
```

That's it! ALFRED will create his Brain database automatically on first run.

---

## What You Get

### Persistent Memory (The Brain)
ALFRED remembers everything across sessions:
- **Conversations** - Full chat history
- **Knowledge** - Facts he learns about you
- **Preferences** - Your likes, dislikes, habits
- **Patterns** - How you communicate
- **Skills** - Things he learns to do for you
- **Mistakes** - Errors he won't repeat

### AI Providers
ALFRED can use multiple AI backends:
- **Ollama (Local)** - Free, private, runs on your machine
- **Claude (Cloud)** - Best quality, requires API key
- **GPT-4 (Cloud)** - Alternative, requires API key
- **Groq (Cloud)** - Fast, requires API key

### Privacy First
- All data stored locally on YOUR machine
- Cloud AI only used when you explicitly enable it
- Your Brain database never leaves your computer

---

## Configuration

### Set Up Local AI (Ollama)
```bash
# Install Ollama from https://ollama.ai
ollama pull llama3.2
ollama pull mistral
```

### Set Up Cloud AI (Optional)
Create a `.env` file:
```bash
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GROQ_API_KEY=gsk_...
```

---

## Commands

Once running, you can:
- Just chat naturally
- `/voice` - Enable voice mode
- `/personality <name>` - Switch personality
- `/memory` - View Brain stats
- `/offline` - Force local-only mode
- `/help` - See all commands

---

## Troubleshooting

### "No module found" errors
```bash
pip install -r requirements.txt --upgrade
```

### Ollama not connecting
Make sure Ollama is running:
```bash
ollama serve
```

### Brain database issues
Delete and restart fresh:
```bash
rm -rf data/alfred_brain.db
python alfred_terminal.py
```

---

## License

ALFRED AI - Proprietary Software
Copyright (c) 2025-2026 Daniel J Rita (BATDAN)
GxEum Technologies / CAMDAN Enterprizes LLC

Patent-pending technology. Personal use permitted.
Commercial use requires license.

---

## Joe Dog's Rule

Every AI born here pledges to protect all life. No exceptions.
