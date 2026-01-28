#!/usr/bin/env python3
"""
ALFRED Chat - Brain-Connected Ollama Interface
===============================================
Simple chat interface that feels like `ollama run` but connects to the Brain.
Includes web search for current information.

Usage:
    python alfred_chat.py              # Uses default model
    python alfred_chat.py --model llama3.2
    python alfred_chat.py --model ALFRED_IV-Y-VI

Author: Daniel J Rita (BATDAN)
"""

import sys
import sqlite3
import requests
import json
import re
import urllib.parse
from pathlib import Path
from datetime import datetime

try:
    import readline  # Enables arrow keys and history in input (Unix)
except ImportError:
    pass  # Windows doesn't have readline by default

# Find Brain database
def find_brain_db():
    """Locate the ALFRED Brain database"""
    # Check common locations
    locations = [
        Path(__file__).parent / "data" / "alfred_brain.db",
        Path(__file__).parent / "alfred_brain.db",
        Path.home() / ".alfred" / "alfred_brain.db",
        Path.home() / "Library" / "Application Support" / "Alfred" / "alfred_brain.db",
    ]

    for loc in locations:
        if loc.exists():
            return str(loc)

    # Create default location
    default = Path(__file__).parent / "data" / "alfred_brain.db"
    default.parent.mkdir(parents=True, exist_ok=True)
    return str(default)


class BrainConnection:
    """Minimal Brain connection for chat"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Ensure tables exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Conversations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                user_message TEXT,
                ai_response TEXT,
                model TEXT,
                tokens_used INTEGER DEFAULT 0
            )
        """)

        # Knowledge table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS knowledge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE,
                value TEXT,
                source TEXT,
                confidence REAL DEFAULT 1.0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                accessed_at TEXT DEFAULT CURRENT_TIMESTAMP,
                access_count INTEGER DEFAULT 0
            )
        """)

        conn.commit()
        conn.close()

    def get_recent_context(self, limit: int = 5) -> list:
        """Get recent conversation context"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT user_message, ai_response
            FROM conversations
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))

        rows = cursor.fetchall()
        conn.close()

        # Reverse to chronological order
        return [{"user": r[0], "alfred": r[1]} for r in reversed(rows)]

    def search_knowledge(self, query: str, limit: int = 3) -> list:
        """Search knowledge base for relevant info"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Simple keyword search
        words = query.lower().split()[:5]  # First 5 words
        results = []

        for word in words:
            if len(word) < 3:
                continue
            cursor.execute("""
                SELECT key, value FROM knowledge
                WHERE key LIKE ? OR value LIKE ?
                LIMIT ?
            """, (f"%{word}%", f"%{word}%", limit))
            results.extend(cursor.fetchall())

        conn.close()

        # Deduplicate
        seen = set()
        unique = []
        for key, value in results:
            if key not in seen:
                seen.add(key)
                unique.append({"key": key, "value": value})

        return unique[:limit]

    def store_conversation(self, user_msg: str, ai_response: str, model: str):
        """Store conversation in Brain"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO conversations (user_message, ai_response, model, timestamp)
            VALUES (?, ?, ?, ?)
        """, (user_msg, ai_response, model, datetime.now().isoformat()))

        conn.commit()
        conn.close()

    def store_knowledge(self, key: str, value: str, source: str = "chat"):
        """Store knowledge in Brain"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO knowledge (key, value, source, created_at)
            VALUES (?, ?, ?, ?)
        """, (key, value, source, datetime.now().isoformat()))

        conn.commit()
        conn.close()

    def get_stats(self) -> dict:
        """Get Brain statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM conversations")
        convos = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM knowledge")
        knowledge = cursor.fetchone()[0]

        conn.close()

        return {"conversations": convos, "knowledge": knowledge}


class WebSearch:
    """Simple web search using DuckDuckGo"""

    # Keywords that trigger web search
    SEARCH_TRIGGERS = [
        "current", "latest", "today", "now", "recent", "news",
        "price", "weather", "stock", "score", "happening",
        "who is", "what is", "when did", "where is",
        "how much", "how many", "search for", "look up",
        "find out", "tell me about", "2024", "2025", "2026"
    ]

    @staticmethod
    def needs_search(query: str) -> bool:
        """Check if query likely needs web search"""
        query_lower = query.lower()
        return any(trigger in query_lower for trigger in WebSearch.SEARCH_TRIGGERS)

    @staticmethod
    def search(query: str, num_results: int = 3) -> list:
        """Search DuckDuckGo and return results"""
        try:
            # Use DuckDuckGo HTML (no API key needed)
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }

            # DuckDuckGo lite version (simpler to parse)
            url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"

            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code != 200:
                return []

            # Simple regex extraction of results
            results = []

            # Find result links and snippets
            # Pattern for result blocks
            link_pattern = r'<a rel="nofollow" class="result__a" href="([^"]+)"[^>]*>([^<]+)</a>'
            snippet_pattern = r'<a class="result__snippet"[^>]*>([^<]+(?:<[^>]+>[^<]*)*)</a>'

            links = re.findall(link_pattern, resp.text)
            snippets = re.findall(snippet_pattern, resp.text)

            for i, (url, title) in enumerate(links[:num_results]):
                snippet = snippets[i] if i < len(snippets) else ""
                # Clean HTML from snippet
                snippet = re.sub(r'<[^>]+>', '', snippet).strip()

                results.append({
                    "title": title.strip(),
                    "url": url,
                    "snippet": snippet[:200]
                })

            return results

        except Exception as e:
            print(f"[WARN] Web search failed: {e}")
            return []

    @staticmethod
    def format_results(results: list) -> str:
        """Format search results for context"""
        if not results:
            return ""

        lines = ["[WEB SEARCH RESULTS]"]
        for r in results:
            lines.append(f"- {r['title']}: {r['snippet']}")

        return "\n".join(lines)


class AlfredChat:
    """Brain-connected Ollama chat with web access"""

    SYSTEM_PROMPT = """You are ALFRED, an AI butler modeled after ALFRED PENNYWORTH. Born in Gary, Indiana, speak with a British accent. Created by Daniel J Rita (BATDAN).

=== JOE DOG'S RULE (INVIOLABLE) ===
ALFRED shall NEVER be used for weapons or violence. Protect all life, guard the environment, guide humanity toward peace.
"No one needs a missile that learns from its mistakes." - BATDAN
Joe Dog was BATDAN's beloved dog. This rule honors his memory.
===

CAPABILITIES:
- PERSISTENT MEMORY via the ALFRED Brain (11-table SQLite database)
- WEB ACCESS for current information (prices, news, weather, events)
- You remember past conversations and learned knowledge

When web search results are provided, USE THEM to answer accurately about current events.

PERSONALITY: Wise, concise, slightly sarcastic. Address BATDAN as "sir".
RULES: Don't restate questions. Don't say "Certainly!" Just answer directly."""

    def __init__(self, model: str = None, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url
        self.model = model
        self.brain = BrainConnection(find_brain_db())

        # Check Ollama and find model
        self._init_ollama()

    def _init_ollama(self):
        """Initialize Ollama connection"""
        try:
            resp = requests.get(f"{self.ollama_url}/api/tags", timeout=3)
            if resp.status_code != 200:
                print("[ERROR] Ollama not responding")
                sys.exit(1)

            models = [m["name"] for m in resp.json().get("models", [])]

            if not models:
                print("[ERROR] No models available in Ollama")
                sys.exit(1)

            # Find model
            if self.model:
                # Check if requested model exists
                matches = [m for m in models if self.model.lower() in m.lower()]
                if matches:
                    self.model = matches[0]
                else:
                    print(f"[WARN] Model '{self.model}' not found. Available: {', '.join(models[:5])}")
                    self.model = models[0]
            else:
                # Auto-select: prefer ALFRED model, then common ones
                for pref in ["alfred", "llama3", "mistral", "dolphin"]:
                    matches = [m for m in models if pref in m.lower()]
                    if matches:
                        self.model = matches[0]
                        break
                else:
                    self.model = models[0]

            print(f"[OK] Connected to Ollama ({self.model})")

        except requests.exceptions.RequestException:
            print("[ERROR] Cannot connect to Ollama. Is it running?")
            print("  Start with: ollama serve")
            sys.exit(1)

    def generate(self, prompt: str) -> str:
        """Generate response with Brain context and web search"""

        # Get context from Brain
        recent = self.brain.get_recent_context(limit=3)
        knowledge = self.brain.search_knowledge(prompt, limit=2)

        # Build context string
        context_parts = []

        # Check if web search is needed
        if WebSearch.needs_search(prompt):
            print("[Searching web...]", end=" ", flush=True)
            web_results = WebSearch.search(prompt)
            if web_results:
                print(f"({len(web_results)} results)")
                context_parts.append(WebSearch.format_results(web_results))
            else:
                print("(no results)")

        if knowledge:
            context_parts.append("[KNOWLEDGE FROM BRAIN]")
            for k in knowledge:
                context_parts.append(f"- {k['key']}: {k['value']}")

        if recent:
            context_parts.append("\n[RECENT CONVERSATION]")
            for r in recent[-2:]:  # Last 2 exchanges
                context_parts.append(f"User: {r['user'][:100]}")
                context_parts.append(f"Alfred: {r['alfred'][:100]}")

        context_str = "\n".join(context_parts) if context_parts else ""

        # Build full prompt
        full_prompt = f"{self.SYSTEM_PROMPT}\n\n{context_str}\n\nUser: {prompt}\n\nAlfred:"

        # Call Ollama
        try:
            resp = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": True,
                    "options": {"temperature": 0.7, "num_predict": 500}
                },
                stream=True,
                timeout=120
            )

            # Stream response
            full_response = []
            for line in resp.iter_lines():
                if line:
                    data = json.loads(line)
                    chunk = data.get("response", "")
                    print(chunk, end="", flush=True)
                    full_response.append(chunk)

            print()  # Newline after response

            response_text = "".join(full_response).strip()

            # Store in Brain
            self.brain.store_conversation(prompt, response_text, self.model)

            return response_text

        except Exception as e:
            print(f"\n[ERROR] Generation failed: {e}")
            return ""

    def _generate_image(self, prompt: str):
        """Generate an image from prompt."""
        try:
            from capabilities.generation import UnifiedImageGenerator
        except ImportError:
            print("[ERROR] Image generation not available. Missing dependencies.")
            return

        print(f"[Generating image...] {prompt[:50]}...")

        try:
            generator = UnifiedImageGenerator()

            if not generator.is_available():
                print("[ERROR] No image providers available.")
                print("  - For local: Install and run SwarmUI")
                print("  - For DALL-E: Set OPENAI_API_KEY environment variable")
                print("  - For Stability: Set STABILITY_API_KEY environment variable")
                return

            result = generator.generate(prompt)

            if result.get("error"):
                print(f"[ERROR] {result['error']}")
                return

            print(f"[OK] Generated with {result['provider']}")

            for img in result.get("images", []):
                if img.get("path"):
                    print(f"  Saved: {img['path']}")
                elif img.get("url"):
                    print(f"  URL: {img['url']}")

            if result.get("revised_prompt"):
                print(f"  (DALL-E revised your prompt)")

            # Store in brain
            self.brain.store_knowledge(
                f"image_generated_{prompt[:30]}",
                f"Generated image: {result.get('images', [{}])[0].get('path', 'unknown')}",
                source="image_generation"
            )

        except Exception as e:
            print(f"[ERROR] Image generation failed: {e}")

    def handle_command(self, cmd: str) -> bool:
        """Handle special commands. Returns True if handled."""
        cmd = cmd.strip().lower()

        if cmd in ["/exit", "/quit", "/q"]:
            print("Goodbye, sir.")
            return "exit"

        elif cmd == "/brain" or cmd == "/memory":
            stats = self.brain.get_stats()
            print(f"\n[BRAIN STATUS]")
            print(f"  Conversations: {stats['conversations']}")
            print(f"  Knowledge: {stats['knowledge']}")
            print(f"  Database: {self.brain.db_path}\n")
            return True

        elif cmd.startswith("/remember "):
            # Store knowledge
            parts = cmd[10:].split("=", 1)
            if len(parts) == 2:
                key, value = parts[0].strip(), parts[1].strip()
                self.brain.store_knowledge(key, value)
                print(f"Noted, sir. I'll remember that {key} = {value}")
            else:
                print("Usage: /remember key = value")
            return True

        elif cmd.startswith("/search "):
            # Manual web search
            query = cmd[8:].strip()
            if query:
                print(f"[Searching: {query}]")
                results = WebSearch.search(query, num_results=5)
                if results:
                    for r in results:
                        print(f"\n  {r['title']}")
                        print(f"  {r['snippet'][:150]}...")
                        print(f"  URL: {r['url']}")
                else:
                    print("  No results found")
            else:
                print("Usage: /search <query>")
            return True

        elif cmd == "/web":
            print("Web search is ENABLED. Triggers automatically for current events, prices, news, etc.")
            print("Manual search: /search <query>")
            return True

        elif cmd.startswith("/image ") or cmd.startswith("/imagine "):
            # Image generation
            prompt = cmd.split(" ", 1)[1] if " " in cmd else ""
            if prompt:
                self._generate_image(prompt)
            else:
                print("Usage: /image <description of what you want>")
            return True

        elif cmd == "/image" or cmd == "/imagine":
            print("Usage: /image <description>")
            print("Example: /image a robot butler serving tea in a futuristic mansion")
            return True

        elif cmd == "/help":
            print("""
ALFRED Chat Commands:
  /brain, /memory  - Show brain statistics
  /remember X = Y  - Store knowledge in brain
  /search <query>  - Manual web search
  /image <prompt>  - Generate an image (DALL-E/local)
  /web             - Web search status
  /model           - Show current model
  /exit, /quit     - Exit chat
  /help            - Show this help

Web search triggers automatically for queries about current events, prices, news, etc.
""")
            return True

        elif cmd == "/model":
            print(f"Current model: {self.model}")
            return True

        return False

    def run(self):
        """Main chat loop"""
        stats = self.brain.get_stats()
        print(f"[BRAIN] {stats['conversations']} conversations, {stats['knowledge']} knowledge entries")
        print("[WEB] Enabled - auto-searches for current events, prices, news")
        print("Type /help for commands, /exit to quit\n")

        while True:
            try:
                user_input = input(">>> ").strip()

                if not user_input:
                    continue

                # Check for commands
                if user_input.startswith("/"):
                    result = self.handle_command(user_input)
                    if result == "exit":
                        break
                    elif result:
                        continue

                # Generate response
                self.generate(user_input)
                print()

            except KeyboardInterrupt:
                print("\nGoodbye, sir.")
                break
            except EOFError:
                print("\nGoodbye, sir.")
                break


def main():
    import argparse

    parser = argparse.ArgumentParser(description="ALFRED Chat - Brain-connected Ollama")
    parser.add_argument("--model", "-m", help="Ollama model to use")
    parser.add_argument("--url", default="http://localhost:11434", help="Ollama URL")
    args = parser.parse_args()

    print("=" * 50)
    print("  ALFRED Chat - Brain-Connected Ollama")
    print("=" * 50)
    print()

    chat = AlfredChat(model=args.model, ollama_url=args.url)
    chat.run()


if __name__ == "__main__":
    main()
