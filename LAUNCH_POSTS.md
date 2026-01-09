# ALFRED Launch Posts

Ready-to-use posts for launching ALFRED.

---

## Hacker News (Show HN)

**Title:** Show HN: ALFRED - Privacy-first AI butler with persistent memory (runs locally)

**Post:**

I built an AI assistant that actually remembers you between sessions.

The problem: Every AI has amnesia. You explain your context, preferences, projects - next session? Gone. You're a stranger again. Plus, all your data lives on someone else's servers.

ALFRED fixes both:

**Persistent Memory**: 11-table SQLite brain stores conversations, preferences, patterns, knowledge. Tell it something once, it remembers forever.

**Privacy First**: Runs on Ollama by default. Your data never leaves your machine. Cloud AI (Claude, Gemini, etc.) available but requires explicit consent.

**Bounded Growth**: Most memory systems grow until they break. ALFRED has CORTEX - a 5-layer forgetting architecture that keeps memory bounded while preserving what matters.

**Multi-Modal**: British butler voice (TTS + offline STT), speaker recognition (knows who's talking), wake words ("Hey Alfred").

**Works Offline**: No internet required with Ollama.

Tech: Python, SQLite, Ollama, Edge TTS, VOSK

I've been using it daily for months. It knows my projects, my preferences, my deadlines - without me re-explaining every session.

GitHub: https://github.com/Batdan007/ALFRED_II-Y-II

Feedback welcome. What memory/privacy features would you want in an AI assistant?

---

## Twitter/X Thread

**Tweet 1 (Hook):**
I built an AI butler that actually remembers me.

Not per-session memory. Forever memory.

Privacy-first. Runs locally. Open source.

Meet ALFRED. 🧵

**Tweet 2:**
The problem with ChatGPT, Claude, etc:

- Session amnesia (explain yourself every time)
- Your data on their servers
- Can't work offline
- $20+/month

ALFRED fixes all of these.

**Tweet 3:**
How it works:

11-table SQLite brain stores:
- Conversations
- Preferences
- Patterns (what works for you)
- Knowledge
- Mistakes (what to avoid)

Tell it once. It remembers forever.

**Tweet 4:**
Privacy-first architecture:

- Ollama (local) by default
- Cloud AI requires explicit consent
- Your data stays on your disk
- Works completely offline

Your AI. Your data. Your rules.

**Tweet 5:**
Bonus: It speaks.

British butler voice (Microsoft Ryan)
Offline speech recognition (VOSK)
Speaker ID (knows your voice vs TV)
Wake words: "Hey Alfred", "Batcomputer"

**Tweet 6:**
The secret sauce: CORTEX

Most AI memory grows forever until it breaks.

CORTEX is a 5-layer forgetting system:
- Keeps important stuff
- Forgets noise
- Bounded storage
- Never overflows

Patent pending.

**Tweet 7:**
Try it:

```
git clone github.com/Batdan007/ALFRED_II-Y-II
pip install -r requirements.txt
ollama pull llama3.2
alfred
```

Star if useful. Issues/PRs welcome.

github.com/Batdan007/ALFRED_II-Y-II

---

## LinkedIn

**Post:**

Just open-sourced ALFRED - a privacy-first AI assistant with persistent memory.

**The problem I was solving:**

Every AI assistant has amnesia. You explain your preferences, your projects, your context - and next session, you're a stranger again. Plus, all your conversations live on someone else's servers.

**The solution:**

ALFRED runs locally (Ollama) by default and stores everything in an 11-table SQLite database on YOUR machine:
- Conversations and context
- Your preferences and patterns
- What worked and what didn't
- Knowledge you've shared

Tell it something once. It remembers forever.

**Key features:**
- Privacy-first (local by default, cloud optional)
- Persistent memory (11-table brain)
- Bounded growth (CORTEX forgetting architecture)
- Voice enabled (British butler TTS + offline STT)
- Works completely offline

**Why I built this:**

I was tired of re-explaining my context every session. I wanted an AI that actually knew me - my projects, my preferences, my deadlines - without sending everything to the cloud.

Now I have one. And you can too.

GitHub: https://github.com/Batdan007/ALFRED_II-Y-II

Would love feedback from the community. What memory/privacy features matter most to you in an AI assistant?

#AI #OpenSource #Privacy #LocalAI #LLM

---

## Reddit (r/LocalLLaMA)

**Title:** ALFRED - Privacy-first AI assistant with persistent 11-table memory (Ollama-first)

**Post:**

Hey r/LocalLLaMA!

I've been lurking here for a while and finally shipping something I've been building: ALFRED, an AI assistant designed around local-first principles.

**The core idea:** AI assistants shouldn't have amnesia, and your data shouldn't live on someone else's servers.

**What it does:**

1. **Persistent Memory** - 11-table SQLite brain stores conversations, preferences, patterns, knowledge. Survives restarts.

2. **Ollama-first** - Local by default. Claude/Gemini/Groq/OpenAI available but requires explicit opt-in.

3. **Bounded Growth** - CORTEX (5-layer forgetting) keeps memory from growing forever

4. **Voice** - British butler TTS (Edge TTS Ryan) + VOSK for offline STT + speaker recognition

5. **Offline capable** - Works without internet

**Tech stack:**
- Python 3.11
- SQLite for brain
- Ollama for local LLM
- Edge TTS / VOSK for voice
- Multi-model fallback chain

**Quick start:**
```bash
git clone https://github.com/Batdan007/ALFRED_II-Y-II.git
pip install -r requirements.txt
pip install -e .
ollama pull llama3.2
alfred
```

I've been daily-driving this for months. Happy to answer questions about the architecture or take feature requests.

GitHub: https://github.com/Batdan007/ALFRED_II-Y-II

What would you want in a local AI assistant with persistent memory?

---

## Reddit (r/selfhosted)

**Title:** ALFRED - Self-hosted AI butler with persistent memory and privacy-first design

**Post:**

Built a self-hosted AI assistant that actually remembers you between sessions.

**Why I built it:**

Cloud AI services have two problems:
1. Session amnesia - you re-explain everything every time
2. Your data lives on their servers

ALFRED solves both by running locally with persistent SQLite storage.

**Features:**
- 11-table brain (conversations, preferences, patterns, knowledge, etc.)
- Ollama for local LLM (privacy-first)
- Optional cloud AI with explicit consent
- British butler voice (TTS + offline STT)
- Speaker recognition
- Works completely offline

**Stack:**
- Python 3.11
- SQLite
- Ollama
- Edge TTS / VOSK

**Runs on:** Any machine with 8GB+ RAM. GPU optional but helpful.

**Getting started:**
```bash
git clone https://github.com/Batdan007/ALFRED_II-Y-II.git
pip install -r requirements.txt
ollama pull llama3.2
alfred
```

GitHub: https://github.com/Batdan007/ALFRED_II-Y-II

Feedback welcome!

---

## Product Hunt (Tagline Options)

**Taglines:**
- "Your AI butler that actually remembers you"
- "Privacy-first AI assistant with persistent memory"
- "ChatGPT alternative that runs locally and never forgets"
- "The AI assistant that keeps your data on your machine"

**One-liner:**
ALFRED is a privacy-first AI assistant with persistent memory that runs locally, never forgets what matters, and keeps your data on your machine.

---

## Quick Copy-Paste Links

```
GitHub: https://github.com/Batdan007/ALFRED_II-Y-II
```

---

## Hashtags

```
#AI #OpenSource #Privacy #LocalLLM #Ollama #Python #AIAssistant #SelfHosted #PrivacyFirst #LLM
```
