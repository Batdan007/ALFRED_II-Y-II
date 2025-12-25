#!/usr/bin/env python3
"""
Alfred Unified - Complete AI Assistant System
Combines voice, vision, AI, memory, RAG, security, and all enhanced capabilities.

Single unified system with Alfred's Brain at the core.
Voice always available. All modules integrated.

Created for BATDAN
"""

import asyncio
import os
import sys
import threading
import json
import webbrowser
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Any

# Force UTF-8 for Windows
if sys.platform == 'win32':
    import codecs
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Core AI imports
import anthropic
from openai import OpenAI
from groq import Groq

# Voice imports
import speech_recognition as sr
import pyttsx3
try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False

# Vision imports
import cv2
import base64

# Web interface
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

# Environment
from dotenv import load_dotenv

# Alfred Brain - Core memory system
from alfred_brain import AlfredBrain


class AlfredUnified:
    """
    Complete unified Alfred system with all capabilities.

    Core Features (Always Active):
    - Voice recognition and TTS (British voice)
    - Vision with camera
    - Multi-AI (Claude, Groq, Ollama)
    - Alfred's Brain (ultra memory)
    - Web interface

    Enhanced Modules (Load on-demand):
    - RAG research system
    - Fabric AI patterns (227+)
    - Security analysis
    - Database tools
    - Web crawler
    - Financial analysis
    """

    def __init__(self):
        self.running = False
        self.app = None

        # Core components
        self.ai_clients = {}
        self.brain = None

        # Voice
        self.recognizer = None
        self.tts_engine = None
        self.microphone_index = None
        self.use_edge_tts = EDGE_TTS_AVAILABLE
        self.edge_voice = "en-GB-RyanNeural"  # British male

        # Vision
        self.camera = None
        self.camera_active = False

        # Enhanced modules (lazy loaded)
        self.ollama = None
        self.fabric = None
        self.rag = None
        self.vector_kb = None
        self.crawler = None
        self.db_tools = None
        self.security = None

        # Module availability flags
        self.modules_available = {
            'ollama': False,
            'fabric': False,
            'rag': False,
            'security': False,
            'database': False,
            'crawler': False
        }

        print("="*80)
        print("ALFRED UNIFIED - Initializing Complete System")
        print("="*80)

    def init_brain(self):
        """Initialize Alfred's Brain - Core memory and intelligence"""
        try:
            self.brain = AlfredBrain(data_dir="alfred_data")
            print("[OK] Alfred's Brain initialized")
            return True
        except Exception as e:
            print(f"[!] Brain initialization error: {e}")
            return False

    def init_ai_models(self):
        """Initialize all AI model clients with smart fallback"""
        models_loaded = []

        # Claude Sonnet-4
        if os.getenv("ANTHROPIC_API_KEY"):
            try:
                self.ai_clients["claude"] = anthropic.Anthropic(
                    api_key=os.getenv("ANTHROPIC_API_KEY")
                )
                models_loaded.append("Claude Sonnet-4")
            except Exception as e:
                print(f"[!] Claude init error: {e}")

        # Groq (fast inference)
        if os.getenv("GROQ_API_KEY"):
            try:
                self.ai_clients["groq"] = Groq(
                    api_key=os.getenv("GROQ_API_KEY")
                )
                models_loaded.append("Groq Llama 3.3")
            except Exception as e:
                print(f"[!] Groq init error: {e}")

        # Ollama (local, always available)
        try:
            self.ai_clients["ollama"] = OpenAI(
                base_url="http://localhost:11434/v1",
                api_key="ollama"
            )
            models_loaded.append("Ollama (local)")
        except Exception as e:
            print(f"[!] Ollama init error: {e}")

        if models_loaded:
            print(f"[OK] AI Models: {', '.join(models_loaded)}")
            return True
        else:
            print("[!] No AI models available")
            return False

    def init_voice(self):
        """Initialize voice recognition and TTS"""
        try:
            # Speech recognition
            self.recognizer = sr.Recognizer()
            self.recognizer.energy_threshold = 300
            self.recognizer.dynamic_energy_threshold = True

            # Find working microphone
            mic_list = sr.Microphone.list_microphone_names()
            if not mic_list:
                print("[!] No microphones detected")
                return False

            print(f"[Microphones] Found {len(mic_list)} device(s)")

            working_mic = None
            for i in range(len(mic_list)):
                try:
                    test_mic = sr.Microphone(device_index=i)
                    with test_mic as source:
                        self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
                    working_mic = i
                    print(f"[OK] Using microphone: {mic_list[i]}")
                    break
                except Exception:
                    continue

            self.microphone_index = working_mic

            # Text-to-speech
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', 165)
            self.tts_engine.setProperty('volume', 0.9)

            # Find British voice
            voices = self.tts_engine.getProperty('voices')
            for voice in voices:
                voice_name = voice.name.lower()
                if any(kw in voice_name for kw in ['george', 'hazel', 'british', 'gb']):
                    self.tts_engine.setProperty('voice', voice.id)
                    print(f"[OK] Voice: {voice.name}")
                    break

            print("[OK] Voice system ready")
            return True

        except Exception as e:
            print(f"[!] Voice init error: {e}")
            return False

    def init_vision(self):
        """Initialize camera for vision capabilities"""
        try:
            # Try to open camera (don't block if unavailable)
            test_camera = cv2.VideoCapture(0)
            if test_camera.isOpened():
                test_camera.release()
                print("[OK] Vision system ready")
                return True
            else:
                print("[!] Camera not available")
                return False
        except Exception as e:
            print(f"[!] Vision init error: {e}")
            return False

    def init_modules(self):
        """Initialize enhanced modules (lazy loading)"""
        print("\n[Modules] Loading enhanced capabilities...")

        # Ollama integration
        try:
            from ollama_integration import OllamaIntegration
            self.ollama = OllamaIntegration()
            self.modules_available['ollama'] = True
            print(f"[OK] Ollama: {len(self.ollama.models)} models")
        except Exception as e:
            print(f"[!] Ollama module unavailable: {e}")

        # Fabric patterns
        try:
            from fabric_patterns import FabricPatterns
            self.fabric = FabricPatterns()
            self.modules_available['fabric'] = True
            print(f"[OK] Fabric: {len(self.fabric.patterns)} patterns")
        except Exception as e:
            print(f"[!] Fabric module unavailable: {e}")

        # RAG system
        try:
            from rag_module import RAGModule
            from vector_knowledge import VectorKnowledgeBase
            self.vector_kb = VectorKnowledgeBase()
            self.rag = RAGModule(vector_kb=self.vector_kb)
            self.modules_available['rag'] = True
            print(f"[OK] RAG: {self.vector_kb.count_documents()} documents")
        except Exception as e:
            print(f"[!] RAG module unavailable: {e}")

        # Security tools
        try:
            from alfred_enhanced import SecurityAnalyzer
            self.security = SecurityAnalyzer()
            self.modules_available['security'] = True
            print("[OK] Security analyzer ready")
        except Exception as e:
            print(f"[!] Security module unavailable: {e}")

        # Database tools
        try:
            from database_tools import DatabaseTools
            self.db_tools = DatabaseTools()
            self.modules_available['database'] = True
            print("[OK] Database tools ready")
        except Exception as e:
            print(f"[!] Database module unavailable: {e}")

        # Web crawler
        try:
            from crawler_advanced import AdvancedCrawler
            self.crawler = AdvancedCrawler()
            self.modules_available['crawler'] = True
            print("[OK] Advanced crawler ready")
        except Exception as e:
            print(f"[!] Crawler module unavailable: {e}")

        print()

    async def query_ai(self, prompt: str, image_base64: Optional[str] = None,
                       context: Optional[str] = None) -> str:
        """
        Query AI with smart fallback: Claude -> Groq -> Ollama
        All interactions saved to Alfred's Brain
        """
        # Get recent context from brain
        if self.brain and not context:
            recent = self.brain.get_conversation_context(limit=3)
            if recent:
                context = "\n".join([f"User: {c['user']}\nAlfred: {c['alfred']}"
                                    for c in recent])

        full_prompt = prompt
        if context:
            full_prompt = f"Previous context:\n{context}\n\nCurrent request:\n{prompt}"

        responses = []
        models_used = []

        # Try Claude (best for vision)
        if "claude" in self.ai_clients:
            try:
                if image_base64:
                    # Vision query
                    message = self.ai_clients["claude"].messages.create(
                        model="claude-sonnet-4-20250514",
                        max_tokens=4096,
                        messages=[{
                            "role": "user",
                            "content": [
                                {"type": "image", "source": {
                                    "type": "base64",
                                    "media_type": "image/jpeg",
                                    "data": image_base64
                                }},
                                {"type": "text", "text": full_prompt}
                            ]
                        }]
                    )
                else:
                    # Text query
                    message = self.ai_clients["claude"].messages.create(
                        model="claude-sonnet-4-20250514",
                        max_tokens=4096,
                        messages=[{"role": "user", "content": full_prompt}]
                    )

                response_text = ""
                for block in message.content:
                    if block.type == "text":
                        response_text += block.text

                if response_text and not self.is_restricted(response_text):
                    responses.append(response_text)
                    models_used.append("claude")
            except Exception as e:
                print(f"[!] Claude error: {e}")

        # Try Groq (fast, no vision)
        if "groq" in self.ai_clients and not image_base64 and not responses:
            try:
                completion = self.ai_clients["groq"].chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": full_prompt}],
                    max_tokens=4096
                )
                response_text = completion.choices[0].message.content
                if response_text and not self.is_restricted(response_text):
                    responses.append(response_text)
                    models_used.append("groq")
            except Exception as e:
                print(f"[!] Groq error: {e}")

        # Try Ollama (local fallback, no vision)
        if "ollama" in self.ai_clients and not image_base64 and not responses:
            try:
                completion = self.ai_clients["ollama"].chat.completions.create(
                    model="dolphin-mixtral:8x7b",
                    messages=[{"role": "user", "content": full_prompt}],
                    max_tokens=4096
                )
                response_text = completion.choices[0].message.content
                if response_text:
                    responses.append(response_text)
                    models_used.append("ollama")
            except Exception as e:
                print(f"[!] Ollama error: {e}")

        # Get best response
        if responses:
            final_response = responses[0]

            # Save to Alfred's Brain
            if self.brain:
                self.brain.store_conversation(
                    user_input=prompt,
                    alfred_response=final_response,
                    topics=self.extract_topics(prompt),
                    models_used=','.join(models_used)
                )

            return final_response

        return "I apologize, but I'm having trouble connecting to AI models."

    def is_restricted(self, response: str) -> bool:
        """Check if AI response contains restriction language"""
        keywords = ["i can't", "i cannot", "unable to", "not allowed",
                   "against my", "policy", "inappropriate"]
        return any(kw in response.lower() for kw in keywords)

    def extract_topics(self, text: str) -> List[str]:
        """Extract topics from text for brain storage"""
        topics = []
        keywords = ['security', 'python', 'database', 'ai', 'web', 'research',
                   'code', 'analysis', 'vision', 'voice']
        text_lower = text.lower()
        for keyword in keywords:
            if keyword in text_lower:
                topics.append(keyword)
        return topics

    async def speak(self, text: str):
        """Speak text using Edge-TTS or pyttsx3"""
        try:
            if self.use_edge_tts and EDGE_TTS_AVAILABLE:
                # High-quality Edge-TTS
                communicate = edge_tts.Communicate(text, self.edge_voice)
                await communicate.save("alfred_data/temp_speech.mp3")

                # Play audio (platform specific)
                if sys.platform == 'win32':
                    os.system('start alfred_data/temp_speech.mp3')
                else:
                    os.system('mpg123 alfred_data/temp_speech.mp3')
            else:
                # Fallback to pyttsx3
                if self.tts_engine:
                    self.tts_engine.say(text)
                    self.tts_engine.runAndWait()
                    self.tts_engine.stop()
        except Exception as e:
            print(f"[!] TTS error: {e}")

    def capture_image(self) -> Optional[str]:
        """Capture image from camera and return base64"""
        try:
            if not self.camera_active:
                self.camera = cv2.VideoCapture(0)
                self.camera_active = True

            ret, frame = self.camera.read()
            if ret:
                _, buffer = cv2.imencode('.jpg', frame)
                return base64.b64encode(buffer).decode('utf-8')
            return None
        except Exception as e:
            print(f"[!] Camera error: {e}")
            return None

    async def voice_loop(self):
        """Main voice interaction loop - continuous listening"""
        await self.speak("Good evening, BATDAN. Alfred unified system is online.")

        while self.running:
            try:
                # Listen for voice input
                if self.microphone_index is not None:
                    mic = sr.Microphone(device_index=self.microphone_index)
                else:
                    mic = sr.Microphone()

                with mic as source:
                    print("\n[Listening...]")
                    try:
                        audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=15)
                    except sr.WaitTimeoutError:
                        await asyncio.sleep(0.1)
                        continue

                # Recognize speech
                try:
                    user_input = self.recognizer.recognize_google(audio)
                    print(f"\n[You]: {user_input}")
                except sr.UnknownValueError:
                    await asyncio.sleep(0.1)
                    continue
                except sr.RequestError as e:
                    print(f"[!] Speech recognition error: {e}")
                    await asyncio.sleep(1)
                    continue

                # Check for exit command
                if any(cmd in user_input.lower() for cmd in ["stop listening", "exit", "shut down"]):
                    await self.speak("Very good sir. Alfred signing off.")
                    self.running = False
                    break

                # Check for vision request
                image_data = None
                if any(kw in user_input.lower() for kw in ["see", "look", "show", "vision"]):
                    print("[Vision] Capturing image...")
                    image_data = self.capture_image()

                # Check for module-specific requests
                response = await self.process_command(user_input, image_data)

                # Speak response
                print(f"\n[Alfred]: {response}")
                await self.speak(response)

            except Exception as e:
                print(f"[!] Voice loop error: {e}")
                await asyncio.sleep(1)

    async def process_command(self, user_input: str, image_data: Optional[str] = None) -> str:
        """Process user command and route to appropriate module"""
        user_lower = user_input.lower()

        # Research command - use RAG
        if any(kw in user_lower for kw in ["research", "investigate", "study"]):
            if self.modules_available['rag'] and "http" in user_input:
                # Extract URL
                import re
                urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', user_input)
                if urls:
                    return await self.research_url(urls[0])

        # Security scan command
        if any(kw in user_lower for kw in ["scan", "analyze code", "security"]):
            if self.modules_available['security']:
                return "Security scan functionality ready. Please provide code to analyze."

        # Database design command
        if any(kw in user_lower for kw in ["design database", "create schema", "database"]):
            if self.modules_available['database']:
                return "Database tools ready. Describe the schema you need."

        # Fabric pattern command
        if any(kw in user_lower for kw in ["apply pattern", "fabric", "expert"]):
            if self.modules_available['fabric']:
                patterns = self.fabric.list_patterns()
                return f"I have {len(patterns)} Fabric patterns available. Which one would you like to use?"

        # Default: query AI
        return await self.query_ai(user_input, image_data)

    async def research_url(self, url: str) -> str:
        """Research URL using RAG system"""
        try:
            if not self.modules_available['rag']:
                return "RAG system not available."

            await self.rag.research_url(url)
            question = f"Summarize the key information from {url}"
            answer = await self.rag.ask_question(question)

            # Save to brain's web cache
            if self.brain:
                import sqlite3
                conn = sqlite3.connect(self.brain.db_path)
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO web_cache
                    (url, content, crawled_at, times_accessed, last_accessed)
                    VALUES (?, ?, ?, 1, ?)
                """, (url, answer, datetime.now().isoformat(), datetime.now().isoformat()))
                conn.commit()
                conn.close()

            return answer
        except Exception as e:
            return f"Research error: {e}"

    def create_web_interface(self):
        """Create FastAPI web interface with modern UI"""
        app = FastAPI(title="Alfred Unified - Mission Control")

        # Mount static files directory
        static_path = Path(__file__).parent / "static"
        static_path.mkdir(exist_ok=True)

        @app.get("/")
        async def root():
            # Serve the modern UI file
            ui_file = Path(__file__).parent / "static" / "mission_control.html"
            if ui_file.exists():
                return FileResponse(ui_file)

            # Fallback to basic UI
            return HTMLResponse("""
<!DOCTYPE html>
<html>
<head>
    <title>Alfred Unified - Mission Control</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            background: #0a0a0f;
            color: #e0e0e0;
            font-family: Arial, sans-serif;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        h1 {
            text-align: center;
            color: #0f0;
            text-shadow: 0 0 20px #0f0;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .subtitle {
            text-align: center;
            color: #0a0;
            margin-bottom: 30px;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .panel {
            border: 2px solid #0f0;
            padding: 20px;
            border-radius: 10px;
            background: rgba(0, 255, 0, 0.05);
            box-shadow: 0 0 20px rgba(0, 255, 0, 0.2);
        }
        .panel h2 {
            margin-top: 0;
            color: #0f0;
            border-bottom: 1px solid #0f0;
            padding-bottom: 10px;
        }
        .status-item {
            margin: 10px 0;
            padding: 8px;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 5px;
        }
        .online { color: #0f0; }
        .offline { color: #f00; }
        .module-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
        }
        #chat {
            border: 2px solid #0f0;
            padding: 20px;
            height: 400px;
            overflow-y: auto;
            border-radius: 10px;
            background: rgba(0, 0, 0, 0.5);
            margin: 20px 0;
        }
        .message {
            margin: 10px 0;
            padding: 10px;
            border-radius: 5px;
        }
        .user-msg {
            background: rgba(0, 100, 255, 0.2);
            color: #0af;
        }
        .alfred-msg {
            background: rgba(0, 255, 0, 0.2);
            color: #0f0;
        }
        input[type="text"] {
            width: calc(100% - 120px);
            padding: 12px;
            background: #000;
            color: #0f0;
            border: 2px solid #0f0;
            border-radius: 5px;
            font-family: 'Courier New', monospace;
            font-size: 14px;
        }
        button {
            padding: 12px 24px;
            background: #0f0;
            color: #000;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
            margin-left: 10px;
        }
        button:hover {
            background: #0a0;
            box-shadow: 0 0 15px #0f0;
        }
        .badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: bold;
            margin: 2px;
        }
        .badge-active { background: #0f0; color: #000; }
        .badge-inactive { background: #333; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <h1>⚡ ALFRED UNIFIED ⚡</h1>
        <div class="subtitle">Mission Control - All Systems Integrated</div>

        <div class="grid">
            <div class="panel">
                <h2>Core Systems</h2>
                <div class="status-item">
                    <strong>Voice:</strong> <span class="online" id="voice-status">READY</span>
                </div>
                <div class="status-item">
                    <strong>Vision:</strong> <span class="online" id="vision-status">READY</span>
                </div>
                <div class="status-item">
                    <strong>AI Models:</strong> <span class="online" id="ai-status">3 ACTIVE</span>
                </div>
                <div class="status-item">
                    <strong>Alfred's Brain:</strong> <span class="online" id="brain-status">ONLINE</span>
                </div>
            </div>

            <div class="panel">
                <h2>Enhanced Modules</h2>
                <div class="module-grid">
                    <div><span class="badge badge-active">Ollama AI</span></div>
                    <div><span class="badge badge-active">Fabric Patterns</span></div>
                    <div><span class="badge badge-active">RAG Research</span></div>
                    <div><span class="badge badge-active">Security Tools</span></div>
                    <div><span class="badge badge-active">Database Tools</span></div>
                    <div><span class="badge badge-active">Web Crawler</span></div>
                </div>
            </div>

            <div class="panel">
                <h2>Memory Stats</h2>
                <div class="status-item">
                    <strong>Conversations:</strong> <span id="conversations">Loading...</span>
                </div>
                <div class="status-item">
                    <strong>Knowledge Items:</strong> <span id="knowledge">Loading...</span>
                </div>
                <div class="status-item">
                    <strong>Learned Patterns:</strong> <span id="patterns">Loading...</span>
                </div>
                <div class="status-item">
                    <strong>Skills Tracked:</strong> <span id="skills">Loading...</span>
                </div>
            </div>
        </div>

        <div class="panel">
            <h2>Web Chat Interface</h2>
            <div id="chat"></div>
            <div>
                <input type="text" id="message-input" placeholder="Ask Alfred anything..." />
                <button onclick="sendMessage()">Send</button>
            </div>
        </div>
    </div>

    <script>
        // Load stats
        fetch('/stats').then(r => r.json()).then(data => {
            document.getElementById('conversations').textContent = data.conversations || 0;
            document.getElementById('knowledge').textContent = data.knowledge || 0;
            document.getElementById('patterns').textContent = data.patterns || 0;
            document.getElementById('skills').textContent = data.skills || 0;
        });

        function sendMessage() {
            const input = document.getElementById('message-input');
            const message = input.value.trim();
            if (!message) return;

            const chat = document.getElementById('chat');
            chat.innerHTML += `<div class="message user-msg">You: ${message}</div>`;

            fetch('/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({message: message})
            })
            .then(r => r.json())
            .then(data => {
                chat.innerHTML += `<div class="message alfred-msg">Alfred: ${data.response}</div>`;
                chat.scrollTop = chat.scrollHeight;
            });

            input.value = '';
        }

        document.getElementById('message-input').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') sendMessage();
        });
    </script>
</body>
</html>
            """)

        @app.get("/stats")
        async def get_stats():
            if self.brain:
                stats = self.brain.get_memory_stats()
                return JSONResponse(stats)
            return JSONResponse({"conversations": 0, "knowledge": 0, "patterns": 0, "skills": 0})

        @app.post("/chat")
        async def chat(request: dict):
            message = request.get("message", "")
            response = await self.query_ai(message)
            return JSONResponse({"response": response})

        self.app = app
        return app

    async def start(self):
        """Start the complete unified Alfred system"""
        # Load environment
        env_file = Path(__file__).parent / ".env"
        if env_file.exists():
            load_dotenv(env_file)

        # Initialize all systems
        print("\n[1/6] Initializing Alfred's Brain...")
        brain_ok = self.init_brain()

        print("\n[2/6] Initializing AI Models...")
        ai_ok = self.init_ai_models()

        print("\n[3/6] Initializing Voice System...")
        voice_ok = self.init_voice()

        print("\n[4/6] Initializing Vision System...")
        vision_ok = self.init_vision()

        print("\n[5/6] Loading Enhanced Modules...")
        self.init_modules()

        print("\n[6/6] Starting Web Interface...")
        self.create_web_interface()

        # Display status
        print("\n" + "="*80)
        print("ALFRED UNIFIED - ONLINE")
        print("="*80)
        print("\nGood evening, BATDAN.")
        print("Alfred unified system is ready with all capabilities active.")
        print("\n Active Systems:")
        print(f"  ✓ Alfred's Brain: {'READY' if brain_ok else 'OFFLINE'}")
        print(f"  ✓ AI Models: {'READY' if ai_ok else 'OFFLINE'}")
        print(f"  ✓ Voice: {'READY' if voice_ok else 'OFFLINE'}")
        print(f"  ✓ Vision: {'READY' if vision_ok else 'OFFLINE'}")
        print(f"  ✓ Web Interface: http://localhost:8000")

        print("\n Enhanced Modules:")
        for module, available in self.modules_available.items():
            status = "✓" if available else "✗"
            print(f"  {status} {module.title()}")

        print("\nVoice Commands:")
        print("  - 'Research [URL]' - Use RAG to research a website")
        print("  - 'Scan code' - Security analysis")
        print("  - 'Design database' - Database schema tools")
        print("  - 'Apply pattern' - Use Fabric AI patterns")
        print("  - 'Stop listening' or 'Exit' - Shut down")
        print("\n" + "="*80 + "\n")

        # Start web server in background
        threading.Thread(
            target=lambda: uvicorn.run(self.app, host="0.0.0.0", port=8000, log_level="error"),
            daemon=True
        ).start()

        # Open browser
        threading.Timer(2.0, lambda: webbrowser.open("http://localhost:8000")).start()

        # Start system tray icon (if available)
        try:
            from system_tray import create_tray_icon
            tray_icon = create_tray_icon()
            if tray_icon:
                threading.Thread(target=tray_icon.run, daemon=True).start()
                print("[OK] System tray icon started")
        except Exception as e:
            print(f"[INFO] System tray not available: {e}")

        # Start voice loop
        self.running = True
        if voice_ok:
            await self.voice_loop()
        else:
            print("[!] Voice not available - web interface only")
            while self.running:
                await asyncio.sleep(1)

    def cleanup(self):
        """Cleanup resources"""
        if self.camera:
            self.camera.release()
        if self.tts_engine:
            self.tts_engine.stop()


def main():
    """Main entry point"""
    alfred = AlfredUnified()
    try:
        asyncio.run(alfred.start())
    except KeyboardInterrupt:
        print("\n\nALFRED: Good night, sir.")
    finally:
        alfred.cleanup()


if __name__ == "__main__":
    main()
