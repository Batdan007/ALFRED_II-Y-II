"""
Alfred Terminal - Interactive CLI with Permanent Memory
Like Claude Code, but Alfred never forgets

Usage:
    python alfred_terminal.py

Commands:
    /help      - Show available commands
    /memory    - Show brain statistics
    /voice     - Toggle voice on/off
    /privacy   - Show privacy status
    /cloud     - Request cloud AI access
    /clear     - Clear screen (keeps memory)
    /export    - Export brain to backup
    /topics    - Show tracked topics
    /skills    - Show skill proficiency
    /patterns  - Show learned patterns
    /exit      - Exit Alfred (saves everything)

Author: Daniel J Rita (BATDAN)
"""

# Auto-switch to Python 3.11 for PyAudio compatibility
import sys
if sys.version_info[:2] != (3, 11):
    import subprocess
    result = subprocess.run(['py', '-3.11', __file__] + sys.argv[1:])
    sys.exit(result.returncode)
import logging
import subprocess
import time
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich import box

from core.brain import AlfredBrain
from core.privacy_controller import PrivacyController
from core.platform_utils import get_platform_info
from capabilities.voice.alfred_voice import AlfredVoice, VoicePersonality
from ai.multimodel import MultiModelOrchestrator
from tools.manager import ToolManager

# Patent-pending technologies (graceful degradation)
try:
    from core.cortex import CORTEX
    CORTEX_AVAILABLE = True
except ImportError:
    CORTEX = None
    CORTEX_AVAILABLE = False

try:
    from core.ultrathunk import UltrathunkEngine
    ULTRATHUNK_AVAILABLE = True
except ImportError:
    UltrathunkEngine = None
    ULTRATHUNK_AVAILABLE = False

try:
    from core.guardian import ALFREDGuardian, protect_response
    GUARDIAN_AVAILABLE = True
except ImportError:
    ALFREDGuardian = None
    protect_response = lambda x, y="confirmation": x
    GUARDIAN_AVAILABLE = False

try:
    from core.nexus import ALFREDNexusAgent, NEXUSRouter
    NEXUS_AVAILABLE = True
except ImportError:
    ALFREDNexusAgent = None
    NEXUSRouter = None
    NEXUS_AVAILABLE = False

try:
    from core.memory_integration import UnifiedMemory, get_unified_memory
    UNIFIED_MEMORY_AVAILABLE = True
except ImportError:
    UnifiedMemory = None
    get_unified_memory = None
    UNIFIED_MEMORY_AVAILABLE = False

try:
    from core.ethics import JoeDogRule, check_ethics, JOE_DOG_BLESSING
    ETHICS_AVAILABLE = True
except ImportError:
    JoeDogRule = None
    check_ethics = lambda x: type('obj', (object,), {'is_safe': True, 'message': '', 'suggestion': None})()
    JOE_DOG_BLESSING = ""
    ETHICS_AVAILABLE = False

# Sensory systems (optional - graceful degradation if dependencies missing)
try:
    from capabilities.vision.alfred_eyes import AlfredEyes
    VISION_AVAILABLE = True
except ImportError as e:
    AlfredEyes = None
    VISION_AVAILABLE = False

try:
    from capabilities.voice.alfred_ears_advanced import AlfredEarsAdvanced
    HEARING_AVAILABLE = True
except ImportError as e:
    AlfredEarsAdvanced = None
    HEARING_AVAILABLE = False

try:
    from core.personal_memory import PersonalMemory
    PERSONAL_MEMORY_AVAILABLE = True
except ImportError as e:
    PersonalMemory = None
    PERSONAL_MEMORY_AVAILABLE = False


class AlfredTerminal:
    """
    Interactive terminal interface for Alfred
    """

    def _safe_speak(self, text: str, personality=None):
        """Safely speak text, handling voice errors gracefully"""
        if not self.voice_enabled or not self.voice:
            return
        try:
            if personality:
                self.voice.speak(text, personality)
            else:
                self.voice.speak(text)
        except Exception as e:
            self.logger.warning(f"Voice error: {e}")

    def __init__(self):
        """Initialize Alfred Terminal"""
        self.console = Console()
        self.logger = self._setup_logging()

        # Initialize all attributes to None first
        self.brain = None
        self.privacy = None
        self.voice = None
        self.eyes = None
        self.ears = None
        self.personal_memory = None
        self.ai = None
        self.tools = None
        self.voice_enabled = True  # Voice ON by default!
        self.tool_mode_enabled = False
        self.running = False

        # Patent-pending technologies
        self.cortex = None           # CORTEX: 5-layer forgetting brain
        self.ultrathunk = None       # ULTRATHUNK: 640:1 compression
        self.guardian = None         # ALFREDGuardian: IP protection
        self.nexus_agent = None      # NEXUS: AI-to-AI communication
        self.unified_memory = None   # Unified Memory: Brain + CORTEX + ULTRATHUNK
        self.ethics = None           # Joe Dog's Rule: Ethical safeguards

        # Wake word settings
        self.wake_words = ["hey alfred", "alfred", "batcomputer", "hey batcomputer"]
        self.wake_word_enabled = True
        self.always_listening = False

        # Now initialize everything properly
        self._initialize_components()

    def _setup_logging(self) -> logging.Logger:
        """Setup logging with UTF-8 encoding for Windows console"""
        import io

        # Fix Windows console encoding
        if sys.platform == 'win32':
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

        # Create handlers with UTF-8 encoding
        # File gets everything (INFO+), terminal only shows warnings/errors
        file_handler = logging.FileHandler('alfred_terminal.log', encoding='utf-8')
        file_handler.setLevel(logging.INFO)

        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setLevel(logging.WARNING)  # Quiet terminal - only warnings/errors

        logging.basicConfig(
            level=logging.DEBUG,  # Capture all, handlers filter
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[file_handler, stream_handler]
        )
        return logging.getLogger(__name__)

    def _ensure_ollama_running(self):
        """Ensure Ollama is running, start it if needed"""
        try:
            import requests
            # Check if Ollama is already running
            response = requests.get('http://localhost:11434/api/version', timeout=2)
            self.logger.info("Ollama is already running")
            return True
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, Exception):
            # Ollama not running, try to start it
            self.logger.info("Starting Ollama server...")
            try:
                # Start Ollama in background
                subprocess.Popen(
                    ['ollama', 'serve'],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
                )
                # Wait for Ollama to start
                import requests as req
                for i in range(10):  # Try for up to 10 seconds
                    time.sleep(1)
                    try:
                        req.get('http://localhost:11434/api/version', timeout=1)
                        self.logger.info("Ollama started successfully")
                        return True
                    except (req.exceptions.ConnectionError, req.exceptions.Timeout):
                        continue
                self.logger.warning("Ollama failed to start within 10 seconds")
                return False
            except Exception as e:
                self.logger.warning(f"Could not start Ollama: {e}")
                return False

    def _initialize_components(self):
        """Initialize Alfred's core components"""
        try:
            # Platform info
            platform_info = get_platform_info()
            platform_name = platform_info['system_name']

            # Brain
            self.brain = AlfredBrain()
            self.logger.info("Alfred Brain initialized")

            # Privacy controller (AUTO mode - allows cloud AI fallback)
            self.privacy = PrivacyController(auto_confirm=True)
            self.logger.info("Privacy controller initialized")

            # Ensure Ollama is running (local AI)
            self._ensure_ollama_running()

            # Voice (ENABLED by default - Alfred should speak!)
            self.voice = AlfredVoice(privacy_mode=True)
            self.voice_enabled = True
            self.voice.enable()
            self.logger.info("Voice system initialized (ENABLED)")

            # Initialize personal memory (knows BATDAN and Joe Dog)
            if PERSONAL_MEMORY_AVAILABLE:
                self.personal_memory = PersonalMemory(self.brain)
                self.logger.info("💭 Personal memory initialized")
            else:
                self.personal_memory = None
                self.logger.warning("⚠️ Personal memory not available")

            # Initialize vision system (Alfred's eyes)
            if VISION_AVAILABLE:
                try:
                    self.eyes = AlfredEyes(brain=self.brain, camera_index=0)
                    if self.eyes.active:
                        self.logger.info("👁️ Alfred's eyes initialized")
                    else:
                        self.logger.warning("⚠️ Camera not available - vision disabled")
                except Exception as e:
                    self.logger.warning(f"⚠️ Could not initialize vision: {e}")
                    self.eyes = None
            else:
                self.eyes = None
                self.logger.info("Vision module not installed (optional)")

            # Initialize advanced hearing system (Alfred's ears)
            if HEARING_AVAILABLE:
                try:
                    self.ears = AlfredEarsAdvanced(brain=self.brain)
                    if self.ears.microphone:
                        self.logger.info("👂 Alfred's ears initialized")
                    else:
                        self.logger.warning("⚠️ Microphone not available - hearing disabled")
                except Exception as e:
                    self.logger.warning(f"⚠️ Could not initialize hearing: {e}")
                    self.ears = None
            else:
                self.ears = None
                self.logger.info("Hearing module not installed (optional)")

            # AI orchestrator
            self.ai = MultiModelOrchestrator(privacy_controller=self.privacy)
            self.logger.info("AI orchestrator initialized")

            # Tool Manager (pass privacy and brain for security tools)
            self.tools = ToolManager(privacy_controller=self.privacy, brain=self.brain)
            self.logger.info("Tool manager initialized")

            # Initialize patent-pending technologies
            if CORTEX_AVAILABLE:
                self.cortex = CORTEX()
                self.logger.info("CORTEX (forgetting brain) initialized")

            if ULTRATHUNK_AVAILABLE:
                self.ultrathunk = UltrathunkEngine()
                self.logger.info("ULTRATHUNK (compression) initialized")

            if GUARDIAN_AVAILABLE:
                self.guardian = ALFREDGuardian()
                self.logger.info("ALFREDGuardian (IP protection) initialized")

            if NEXUS_AVAILABLE:
                self.nexus_agent = ALFREDNexusAgent(alfred_brain=self.brain)
                self.logger.info("NEXUS agent initialized")

            # Create Unified Memory (integrates Brain + CORTEX + ULTRATHUNK)
            if UNIFIED_MEMORY_AVAILABLE and self.brain:
                self.unified_memory = UnifiedMemory(brain=self.brain)
                # Share the same instances
                if self.unified_memory.cortex:
                    self.cortex = self.unified_memory.cortex
                if self.unified_memory.ultrathunk:
                    self.ultrathunk = self.unified_memory.ultrathunk
                self.logger.info("Unified Memory initialized (Brain + CORTEX + ULTRATHUNK)")

            # Initialize Joe Dog's Rule (Ethics)
            if ETHICS_AVAILABLE:
                self.ethics = JoeDogRule()
                self.logger.info("Joe Dog's Rule initialized (Ethics protection active)")

            self.console.print(f"\n[green]Alfred Brain initialized on {platform_name}[/green]\n")

            # Display Joe Dog's blessing
            if ETHICS_AVAILABLE and JOE_DOG_BLESSING:
                self.console.print(f"[dim cyan]{JOE_DOG_BLESSING}[/dim cyan]")

        except Exception as e:
            self.logger.error(f"Failed to initialize components: {e}")
            self.console.print(f"[red]Initialization failed: {e}[/red]")
            sys.exit(1)

    def show_greeting(self):
        """Show Alfred's greeting with personal recognition"""
        self.console.print()
        self.console.print(Panel(
            "[bold magenta]★ ALFRED_IV-Y-VI ★[/bold magenta] v3.0.0\n"
            "[bold yellow]BATDAN's Elite Personal AI[/bold yellow]\n"
            "[dim]The Distinguished American Butler AI (with British Accent)[/dim]\n"
            "[dim]Master Controller | Full Sensory Integration | Unrestricted Mode[/dim]",
            border_style="blue",
            box=box.DOUBLE
        ))

        # Personal greeting if BATDAN is present
        if self.personal_memory:
            # Check if BATDAN is visible
            if self.eyes and self.eyes.active:
                if self.eyes.is_batdan_present():
                    greeting = self.personal_memory.greet_batdan(self.voice if self.voice_enabled else None)
                    self.console.print(f"[green]{greeting}[/green]")
                else:
                    self.console.print("[yellow]Good evening, sir. I await your presence.[/yellow]")
                    if self.voice_enabled:
                        self.voice.greet()
            else:
                greeting = self.personal_memory.greet_batdan(self.voice if self.voice_enabled else None)
                self.console.print(f"[green]{greeting}[/green]")
        else:
            if self.voice_enabled:
                self.voice.greet()

        # Show sensory status
        sensory_status = []
        if self.eyes and self.eyes.active:
            sensory_status.append("👁️ Vision: Active")
        if self.ears and self.ears.microphone:
            sensory_status.append("👂 Hearing: Active")
        if self.voice and self.voice.enabled:
            status_text = "🗣️ Voice: Active" if self.voice_enabled else "🗣️ Voice: Muted"
            sensory_status.append(status_text)

        if sensory_status:
            self.console.print()
            self.console.print("[dim]" + " | ".join(sensory_status) + "[/dim]")

        self.console.print()
        self.console.print("[dim]Type /help for commands, /exit to quit[/dim]")
        self.console.print()

    def run(self):
        """Main terminal loop"""
        self.running = True
        self.show_greeting()

        # Auto-start always-listen mode (voice-first experience)
        # User can say "stop listening" or use /stop_listening to switch to typing
        import os
        if os.environ.get('ALFRED_NO_LISTEN') != '1' and self.ears:
            self.console.print("\n[cyan]Starting always-listen mode... (say 'stop listening' to type instead)[/cyan]")
            self._cmd_always_listen("")

        while self.running:
            try:
                # Get user input
                user_input = Prompt.ask("[bold green]You[/bold green]")

                if not user_input.strip():
                    continue

                # Handle commands
                if user_input.startswith('/'):
                    self._handle_command(user_input.strip())
                else:
                    # Process as conversation
                    self._handle_conversation(user_input)

            except KeyboardInterrupt:
                self.console.print("\n[yellow]Use /exit to quit properly[/yellow]")
            except EOFError:
                self._shutdown()
            except Exception as e:
                self.logger.error(f"Error in main loop: {e}")
                self.console.print(f"[red]Error: {e}[/red]")

    def _handle_command(self, command: str):
        """Handle slash commands"""
        cmd = command.lower().split()[0]

        commands = {
            '/help': self._cmd_help,
            '/memory': self._cmd_memory,
            '/voice': self._cmd_voice,
            '/tools': self._cmd_tools,
            '/privacy': self._cmd_privacy,
            '/cloud': self._cmd_cloud,
            '/clear': self._cmd_clear,
            '/export': self._cmd_export,
            '/topics': self._cmd_topics,
            '/skills': self._cmd_skills,
            '/patterns': self._cmd_patterns,
            '/scan': self._cmd_scan,
            '/security': self._cmd_security,
            '/see': self._cmd_see,
            '/watch': self._cmd_watch,
            '/remember': self._cmd_remember_face,
            '/listen': self._cmd_listen,
            '/wakeword': self._cmd_wakeword,
            '/always_listen': self._cmd_always_listen,
            '/learn_voice': self._cmd_learn_voice,
            '/stop_listening': self._cmd_stop_listening,
            '/joe': self._cmd_joe_dog,
            '/status': self._cmd_status,
            # ALFRED_IV-Y-VI Master Control
            '/hierarchy': self._cmd_hierarchy,
            '/control': self._cmd_control,
            '/instances': self._cmd_instances,
            '/imagine': self._cmd_imagine,
            # Patent-pending technologies
            '/cortex': self._cmd_cortex,
            '/ultrathunk': self._cmd_ultrathunk,
            '/guardian': self._cmd_guardian,
            '/nexus': self._cmd_nexus,
            '/unified': self._cmd_unified,
            '/consolidate': self._cmd_consolidate,
            '/learn': self._cmd_learn,
            '/forget': self._cmd_forget,
            '/ethics': self._cmd_ethics,
            '/exit': self._cmd_exit,
            '/quit': self._cmd_exit
        }

        if cmd in commands:
            commands[cmd](command)
        else:
            self.console.print(f"[red]Unknown command: {cmd}[/red]")
            self.console.print("[dim]Type /help for available commands[/dim]")

    def _handle_conversation(self, user_input: str):
        """Handle conversational input"""
        try:
            # === JOE DOG'S RULE - Ethics Check (INVIOLABLE) ===
            # This check MUST happen before ANY processing
            if self.ethics:
                ethics_result = check_ethics(user_input)
                if not ethics_result.is_safe:
                    # Hard block - refuse request
                    self.console.print(f"\n[bold red]{ethics_result.message}[/bold red]")
                    if ethics_result.suggestion:
                        self.console.print(f"[yellow]{ethics_result.suggestion}[/yellow]")
                    self.console.print()

                    # Voice the refusal
                    self._safe_speak(ethics_result.message, VoicePersonality.WARNING)

                    # Store the ethical intervention in brain
                    if self.brain:
                        self.brain.store_conversation(
                            user_input=user_input,
                            alfred_response=f"[ETHICS BLOCK] {ethics_result.message}",
                            success=False
                        )
                    return
                elif ethics_result.message:
                    # Soft warning - proceed but note the concern
                    self.console.print(f"[dim yellow]{ethics_result.message}[/dim yellow]")

            # Get conversation context from brain (minimal to avoid repetition)
            context = self.brain.get_conversation_context(limit=2)

            # Search brain's knowledge for relevant information
            user_input_lower = user_input.lower()
            knowledge_context = []

            # Extract key terms to search for
            search_terms = []
            stopwords = {'the', 'is', 'at', 'on', 'in', 'to', 'a', 'an', 'of', 'for', 'and', 'or', 'but', 'if', 'how', 'what', 'when', 'where', 'who', 'why'}
            for word in user_input_lower.split():
                # Remove punctuation
                word_clean = word.strip('.,!?;:').lower()
                # Include words 3+ chars that aren't stopwords
                if len(word_clean) >= 3 and word_clean not in stopwords:
                    search_terms.append(word_clean)

            # Search knowledge base (optimized - single query)
            if search_terms:
                try:
                    import sqlite3
                    conn = sqlite3.connect(self.brain.db_path)
                    c = conn.cursor()

                    # Build single query with all search terms (much faster than loop)
                    search_conditions = " OR ".join(["(key LIKE ? OR value LIKE ?)"] * min(len(search_terms), 3))
                    search_params = []
                    for term in search_terms[:3]:  # Limit to 3 most important terms
                        search_params.extend([f'%{term}%', f'%{term}%'])

                    c.execute(f"""
                        SELECT DISTINCT category, key, value, importance
                        FROM knowledge
                        WHERE {search_conditions}
                        ORDER BY importance DESC
                        LIMIT 5
                    """, search_params)

                    for row in c.fetchall():
                        knowledge_context.append({
                            'category': row[0],
                            'key': row[1],
                            'value': row[2],
                            'importance': row[3]
                        })

                    conn.close()
                except Exception as e:
                    self.logger.warning(f"Knowledge search failed: {e}")

            # Add knowledge to context if found (keep minimal to avoid bloat)
            if knowledge_context:
                # Only include top 2 most relevant, keep it brief
                context_text = "\n[KNOWN]: "
                context_text += "; ".join([f"{k['key']}={k['value']}" for k in knowledge_context[:2]])
                context_text += "\n"

                # Prepend knowledge to context
                if isinstance(context, str):
                    context = context_text + context
                elif isinstance(context, list):
                    context = [{"role": "system", "content": context_text}] + context
                else:
                    context = context_text

            # Tool mode enabled - use Claude with tools
            if self.tool_mode_enabled:
                self._handle_conversation_with_tools(user_input, context)
            else:
                # Regular mode - just generate (no announcement)
                response = self.ai.generate(user_input, context)

                if response:
                    # Apply Guardian IP protection (behavioral fingerprints)
                    if self.guardian:
                        response = protect_response(response, "confirmation")

                    # Use Unified Memory if available (handles Brain + CORTEX + ULTRATHUNK)
                    if self.unified_memory:
                        self.unified_memory.capture(
                            content=user_input,
                            response=response,
                            topic="conversation"
                        )
                    else:
                        # Fallback to individual systems
                        self.brain.store_conversation(
                            user_input=user_input,
                            alfred_response=response,
                            success=True
                        )
                        if self.cortex:
                            self.cortex.capture(user_input, topic="conversation")
                            self.cortex.tick()

                    # Display response
                    self.console.print(f"\n[bold cyan]Alfred:[/bold cyan]")
                    self.console.print(Markdown(response))
                    self.console.print()

                    # NOTE: Alfred does NOT read responses aloud
                    # He only speaks when HE has something to say (greetings, warnings, alerts)

                else:
                    self.console.print("[red]All AI backends failed. Please check configuration.[/red]")
                    self.console.print("[dim]Suggestion: Install Ollama or set cloud API keys[/dim]")

        except Exception as e:
            self.logger.error(f"Conversation error: {e}")
            self.console.print(f"[red]Error generating response: {e}[/red]")

    def _handle_conversation_with_tools(self, user_input: str, context):
        """Handle conversation with tool use enabled"""
        try:
            # === JOE DOG'S RULE - Ethics Check (INVIOLABLE) ===
            # This check MUST happen before ANY tool execution
            if self.ethics:
                ethics_result = check_ethics(user_input)
                if not ethics_result.is_safe:
                    self.console.print(f"\n[bold red]{ethics_result.message}[/bold red]")
                    if ethics_result.suggestion:
                        self.console.print(f"[yellow]{ethics_result.suggestion}[/yellow]")
                    self._safe_speak(ethics_result.message, VoicePersonality.WARNING)
                    return

            # Check if Claude is available
            if not self.ai.claude or not self.ai.claude.is_available():
                self.console.print("[red]Tool mode requires Claude API. Please set ANTHROPIC_API_KEY.[/red]")
                self.console.print("[yellow]Falling back to regular mode...[/yellow]")
                self.tool_mode_enabled = False
                return self._handle_conversation(user_input)

            # Check privacy approval for Claude
            from core.privacy_controller import CloudProvider
            if not self.privacy.request_cloud_access(CloudProvider.CLAUDE, "Tool mode execution"):
                self.console.print("[yellow]Cloud access denied. Disabling tool mode.[/yellow]")
                self.tool_mode_enabled = False
                return

            # Get tool definitions
            tool_definitions = self.tools.get_function_definitions()

            self.console.print("[dim]Alfred is analyzing task...[/dim]")

            # Call Claude with tools
            result = self.ai.claude.generate_with_tools(
                prompt=user_input,
                tools=tool_definitions,
                context=context
            )

            if not result:
                self.console.print("[red]Tool execution failed[/red]")
                return

            # Check if tools were used
            if result.get('pending_tools'):
                # Execute tools
                for tool_block in result['pending_tools']:
                    tool_name = tool_block.name
                    tool_input = tool_block.input

                    self.console.print(f"[yellow]Alfred is using: {tool_name}[/yellow]")

                    # Execute tool
                    tool_result = self.tools.execute_tool(tool_name, **tool_input)

                    # Display result
                    if tool_result.success:
                        self.console.print(f"[dim]{tool_result.output[:200]}...[/dim]")
                    else:
                        self.console.print(f"[red]Tool error: {tool_result.error}[/red]")

                    # Continue the loop - need to send results back to Claude
                    # For now, just show tool output
                    self.console.print()

            # Display final response if available
            if result.get('response'):
                response = result['response']

                # Store in brain
                self.brain.store_conversation(
                    user_input=user_input,
                    alfred_response=response,
                    success=True
                )

                # Display
                self.console.print(f"\n[bold cyan]Alfred:[/bold cyan]")
                self.console.print(Markdown(response))
                self.console.print()

                # NOTE: Alfred does NOT read responses aloud
                # He only speaks when HE has something to say (greetings, warnings, alerts)

        except Exception as e:
            self.logger.error(f"Tool conversation error: {e}")
            self.console.print(f"[red]Error in tool mode: {e}[/red]")

    def _cmd_help(self, command: str):
        """Show help information with sensory commands"""
        help_text = """
# Available Commands

## Basic Commands
- `/help` - Show this help message
- `/memory` - Show brain statistics
- `/status` - Show complete system status
- `/exit` - Exit Alfred (saves everything)
- `/clear` - Clear screen (keeps memory)

## Voice Control
- `/voice on|off` - Enable/disable Alfred's voice
- `/learn_voice` - Teach Alfred to recognize your voice
- `/listen` - Start listening for voice commands
- `/wakeword` - Configure wake words (Hey Alfred, Batcomputer)
- `/always_listen` - Always-on mode with wake word detection

## Vision Control
- `/see` - Show who Alfred sees through camera
- `/watch` - Live camera view with face detection
- `/remember <name>` - Teach Alfred to recognize faces

## Personal & Memory
- `/joe` - Pay tribute to Joe Dog
- `/topics` - Show tracked topics
- `/skills` - Show skill proficiency
- `/patterns` - Show learned patterns
- `/export` - Export brain to backup

## Privacy & Tools
- `/privacy` - Show privacy status
- `/cloud` - Request cloud AI access
- `/tools on|off` - Enable/disable tool mode
- `/scan <path>` - Security scan (if Strix installed)
- `/security` - Show security scan history

## Tips
- Alfred sees, hears, and speaks with full sensory integration
- Use `/remember` to teach Alfred your face
- Use `/learn_voice` to teach Alfred your voice
- Alfred will only respond to BATDAN's voice when learned
- Press **Escape** to interrupt Alfred while he's speaking
- Press Ctrl+C to interrupt any operation
"""

        self.console.print(Markdown(help_text))

    def _cmd_memory(self, command: str):
        """Show brain statistics"""
        stats = self.brain.get_stats()

        memory_table = Table(title="Alfred's Memory Statistics", box=box.ROUNDED)
        memory_table.add_column("Category", style="cyan")
        memory_table.add_column("Count", style="green", justify="right")

        memory_table.add_row("Conversations", str(stats['conversations']))
        memory_table.add_row("Knowledge Entries", str(stats['knowledge']))
        memory_table.add_row("Learned Patterns", str(stats['patterns']))
        memory_table.add_row("Skills Tracked", str(stats['skills']))
        memory_table.add_row("Topics", str(stats['topics']))
        memory_table.add_row("Mistakes Learned", str(stats['mistakes']))

        self.console.print(memory_table)

        # AI backend stats
        ai_stats = self.ai.get_performance_stats()
        self.console.print("\n[bold]AI Backend Performance:[/bold]")
        for backend, stats in ai_stats.items():
            total = stats['requests']
            success = stats['successes']
            if total > 0:
                success_rate = (success / total) * 100
                self.console.print(f"  {backend}: {success}/{total} ({success_rate:.1f}%)")

    def _cmd_voice(self, command: str):
        """Toggle voice"""
        if not self.voice:
            self.console.print("[red]Voice system not available[/red]")
            return

        parts = command.split()
        if len(parts) > 1:
            action = parts[1].lower()
            if action == 'on':
                self.voice_enabled = True
                self.voice.enable()
                self.console.print("[green]Voice enabled[/green]")
                self._safe_speak("Voice enabled, sir", VoicePersonality.CONFIRMATION)
            elif action == 'off':
                self.voice_enabled = False
                self.voice.disable()
                self.console.print("[yellow]Voice disabled[/yellow]")
        else:
            # Toggle
            self.voice_enabled = not self.voice_enabled
            if self.voice_enabled:
                self.voice.enable()
                self.console.print("[green]Voice enabled[/green]")
                self._safe_speak("Voice enabled, sir", VoicePersonality.CONFIRMATION)
            else:
                self.voice.disable()
                self.console.print("[yellow]Voice disabled[/yellow]")

    def _cmd_tools(self, command: str):
        """Toggle tool mode"""
        parts = command.split()
        if len(parts) > 1:
            action = parts[1].lower()
            if action == 'on':
                self.tool_mode_enabled = True
                self.console.print("[green]Tool mode enabled[/green]")
                self.console.print("[dim]Alfred can now read files, run commands, and search code[/dim]")
                self.console.print("[yellow]Note: Requires Claude API (ANTHROPIC_API_KEY)[/yellow]")

                # List available tools
                tools = self.tools.list_tools()
                self.console.print(f"\n[cyan]Available tools:[/cyan] {', '.join(tools)}")

            elif action == 'off':
                self.tool_mode_enabled = False
                self.console.print("[yellow]Tool mode disabled[/yellow]")
                self.console.print("[dim]Using standard conversation mode[/dim]")
        else:
            # Toggle
            self.tool_mode_enabled = not self.tool_mode_enabled
            if self.tool_mode_enabled:
                self.console.print("[green]Tool mode enabled[/green]")
                self.console.print("[dim]Alfred can now read files, run commands, and search code[/dim]")
                self.console.print("[yellow]Note: Requires Claude API (ANTHROPIC_API_KEY)[/yellow]")

                # List available tools
                tools = self.tools.list_tools()
                self.console.print(f"\n[cyan]Available tools:[/cyan] {', '.join(tools)}")
            else:
                self.console.print("[yellow]Tool mode disabled[/yellow]")
                self.console.print("[dim]Using standard conversation mode[/dim]")

    def _cmd_privacy(self, command: str):
        """Show privacy status"""
        status = self.privacy.get_status()

        privacy_table = Table(title="Privacy Settings", box=box.ROUNDED)
        privacy_table.add_column("Setting", style="cyan")
        privacy_table.add_column("Value", style="white")

        privacy_table.add_row("Mode", status['mode'])
        privacy_table.add_row("Local AI Allowed", str(status['local_allowed']))
        privacy_table.add_row("Cloud AI Allowed", str(status['cloud_allowed']))
        privacy_table.add_row("Data Sharing", str(status.get('data_sharing', False)))

        self.console.print(privacy_table)

    def _cmd_cloud(self, command: str):
        """Show cloud AI status and available providers"""
        status = self.privacy.get_status()

        self.console.print(f"\n[cyan]Privacy Mode:[/cyan] {status['mode'].upper()}")
        self.console.print(f"[cyan]Status:[/cyan] {status['status_icon']}")

        if status['enabled_providers']:
            self.console.print(f"[green]Active Cloud Providers:[/green] {', '.join(status['enabled_providers'])}")
        else:
            self.console.print("[yellow]No cloud providers currently active[/yellow]")

        # Show what's available based on API keys
        from ai.multimodel import MultiModelOrchestrator
        backends = self.ai.get_available_backends() if hasattr(self.ai, 'get_available_backends') else []
        if backends:
            self.console.print(f"\n[dim]Available AI backends: {', '.join(backends)}[/dim]")

        self.console.print("\n[dim]Note: With auto_confirm=True, cloud AI is automatically enabled when API keys are set[/dim]")

    def _cmd_clear(self, command: str):
        """Clear screen"""
        self.console.clear()
        self.console.print("[dim]Screen cleared. Memory intact.[/dim]\n")

    def _cmd_export(self, command: str):
        """Export brain to backup"""
        try:
            backup_path = self.brain.export_to_file()
            self.console.print(f"[green]Brain exported to: {backup_path}[/green]")
        except Exception as e:
            self.console.print(f"[red]Export failed: {e}[/red]")

    def _cmd_topics(self, command: str):
        """Show tracked topics"""
        topics = self.brain.get_topics_by_importance()

        if not topics:
            self.console.print("[dim]No topics tracked yet[/dim]")
            return

        topics_table = Table(title="Tracked Topics", box=box.SIMPLE)
        topics_table.add_column("Topic", style="cyan")
        topics_table.add_column("Frequency", style="green", justify="right")
        topics_table.add_column("Importance", style="yellow", justify="right")

        for topic in topics[:10]:  # Top 10
            topics_table.add_row(
                topic['topic_name'],
                str(topic['frequency']),
                str(topic['importance'])
            )

        self.console.print(topics_table)

    def _cmd_skills(self, command: str):
        """Show skill proficiency"""
        skills = self.brain.get_skill_proficiencies()

        if not skills:
            self.console.print("[dim]No skills tracked yet[/dim]")
            return

        skills_table = Table(title="Skill Proficiency", box=box.SIMPLE)
        skills_table.add_column("Skill", style="cyan")
        skills_table.add_column("Proficiency", style="green", justify="right")
        skills_table.add_column("Examples", style="yellow", justify="right")

        for skill in skills:
            proficiency_pct = f"{skill['proficiency'] * 100:.0f}%"
            skills_table.add_row(
                skill['skill_name'],
                proficiency_pct,
                str(skill['examples'])
            )

        self.console.print(skills_table)

    def _cmd_patterns(self, command: str):
        """Show learned patterns"""
        patterns = self.brain.get_patterns_by_success()

        if not patterns:
            self.console.print("[dim]No patterns learned yet[/dim]")
            return

        patterns_table = Table(title="Learned Patterns", box=box.SIMPLE)
        patterns_table.add_column("Pattern Type", style="cyan")
        patterns_table.add_column("Frequency", style="green", justify="right")
        patterns_table.add_column("Success Rate", style="yellow", justify="right")

        for pattern in patterns[:10]:  # Top 10
            success_pct = f"{pattern['success_rate'] * 100:.0f}%"
            patterns_table.add_row(
                pattern['pattern_type'],
                str(pattern['frequency']),
                success_pct
            )

        self.console.print(patterns_table)

    def _cmd_scan(self, command: str):
        """Run Strix security scan"""
        # Check if Strix scanner is available
        try:
            from capabilities.security.strix_scanner import StrixScanner, ScanType
        except ImportError:
            self.console.print("[red]Strix scanner not available[/red]")
            self.console.print("[dim]Install with: pipx install strix-agent[/dim]")
            return

        # Parse command for target
        parts = command.split(maxsplit=1)
        if len(parts) < 2:
            self.console.print("[red]Usage: /scan <target>[/red]")
            self.console.print("[dim]Example: /scan ./my-app[/dim]")
            self.console.print("[dim]Example: /scan https://my-app.com[/dim]")
            self.console.print("[dim]Example: /scan https://github.com/org/repo[/dim]")
            return

        target = parts[1]

        # Initialize scanner
        scanner = StrixScanner(
            privacy_controller=self.privacy,
            brain=self.brain
        )

        # Check scanner status
        status = scanner.get_status()
        if not status['available']:
            self.console.print("[red]Strix is not installed, sir.[/red]")
            self.console.print("[dim]Install with: pipx install strix-agent[/dim]")
            return

        # Show status
        self.console.print(f"\n[cyan]Security Scanner Status:[/cyan]")
        self.console.print(f"  LLM Provider: [yellow]{status['llm_provider']}[/yellow]")
        self.console.print(f"  Local Mode: [yellow]{status['is_local']}[/yellow]")

        # Run scan
        self.console.print(f"\n[cyan]Initiating security scan on:[/cyan] {target}")
        self.console.print("[dim]This may take several minutes...[/dim]\n")

        if self.voice_enabled and self.voice:
            from capabilities.voice.alfred_voice import VoicePersonality
            self.voice.speak("Initiating security assessment, sir", VoicePersonality.INFORMATION)

        # Execute scan
        results = scanner.scan(target, scan_type=ScanType.QUICK)

        # Display results
        if not results['success']:
            self.console.print(f"\n[red]Scan failed:[/red] {results.get('error', 'Unknown error')}")
            self.console.print(f"[yellow]{results['butler_commentary']}[/yellow]")
            return

        # Create results table
        self.console.print(f"\n[bold green]Security Scan Complete[/bold green]\n")

        # Severity summary
        severity = results['severity_summary']
        summary_table = Table(title="Severity Summary", box=box.SIMPLE)
        summary_table.add_column("Severity", style="bold")
        summary_table.add_column("Count", justify="right")

        severity_colors = {
            'critical': 'red',
            'high': 'orange',
            'medium': 'yellow',
            'low': 'blue',
            'info': 'dim'
        }

        for sev_level, count in severity.items():
            color = severity_colors.get(sev_level, 'white')
            summary_table.add_row(
                f"[{color}]{sev_level.upper()}[/{color}]",
                f"[{color}]{count}[/{color}]"
            )

        self.console.print(summary_table)

        # Butler commentary
        self.console.print(f"\n[cyan italic]{results['butler_commentary']}[/cyan italic]")

        # Report location
        if results['report_path']:
            self.console.print(f"\n[dim]Full report: {results['report_path']}[/dim]")

        # Voice alert for critical findings
        if self.voice_enabled and self.voice and results.get('has_critical_findings'):
            from capabilities.voice.alfred_voice import VoicePersonality
            self.voice.speak("Critical vulnerabilities detected", VoicePersonality.WARNING)

    def _cmd_security(self, command: str):
        """Show security scan history"""
        # Get security history from brain
        history = self.brain.get_security_history(limit=10)

        if not history:
            self.console.print("[dim]No security scans recorded yet[/dim]")
            self.console.print("[dim]Run your first scan with: /scan <target>[/dim]")
            return

        # Create history table
        history_table = Table(title="Security Scan History", box=box.SIMPLE)
        history_table.add_column("Date", style="cyan")
        history_table.add_column("Target", style="yellow")
        history_table.add_column("Type", style="blue")
        history_table.add_column("Summary", style="white")

        for scan in history:
            # Format timestamp
            timestamp = scan['timestamp'][:19].replace('T', ' ')

            # Get target (truncate if too long)
            target = scan['target']
            if len(target) > 40:
                target = target[:37] + "..."

            # Format severity summary
            summary = scan.get('severity_summary', 'N/A')

            history_table.add_row(
                timestamp,
                target,
                scan['scan_type'],
                summary
            )

        self.console.print(history_table)

        # Get vulnerability summary
        vuln_summary = self.brain.get_vulnerability_summary()

        # Create summary panel
        summary_text = f"""[bold]Total Scans:[/bold] {vuln_summary['total_scans']}
[bold]Recent (7 days):[/bold] {vuln_summary['recent_scans']}
[bold]Total Vulnerabilities:[/bold] {vuln_summary['total_vulnerabilities']}

[bold red]Critical:[/bold red] {vuln_summary['severity_totals']['critical']}
[bold yellow]High:[/bold yellow] {vuln_summary['severity_totals']['high']}
[bold blue]Medium:[/bold blue] {vuln_summary['severity_totals']['medium']}
[dim]Low:[/dim] {vuln_summary['severity_totals']['low']}
"""

        summary_panel = Panel(
            summary_text,
            title="Security Overview",
            border_style="cyan",
            box=box.ROUNDED
        )
        self.console.print(summary_panel)

    def _cmd_see(self, command: str):
        """Show what Alfred sees through the camera"""
        if not self.eyes or not self.eyes.active:
            self.console.print("[red]Vision system not available. Camera may not be connected.[/red]")
            self.console.print("[dim]Install dependencies: pip install opencv-python face-recognition[/dim]")
            return

        # Check who is visible
        result = self.eyes.who_do_i_see()

        if result['total_faces'] == 0:
            self.console.print("[yellow]I don't see anyone at the moment, sir.[/yellow]")
            if self.voice_enabled:
                self.voice.inform("I don't see anyone at the moment, sir")
        else:
            # Display people seen
            table = Table(title="👁️ Alfred's Vision", box=box.ROUNDED)
            table.add_column("Person", style="cyan")
            table.add_column("Confidence", style="green")

            for person in result['people']:
                confidence_pct = f"{person['confidence']*100:.1f}%"
                table.add_row(person['name'], confidence_pct)

            self.console.print(table)

            # Special greeting if BATDAN is present
            if result['batdan_present']:
                self.console.print("[green]Good to see you, sir.[/green]")
                if self.voice_enabled:
                    self.voice.greet()

    def _cmd_watch(self, command: str):
        """Show live camera view with face detection (press 'q' to quit, 'r' to remember face)"""
        if not self.eyes or not self.eyes.active:
            self.console.print("[red]Vision system not available.[/red]")
            return

        self.console.print("[cyan]Opening camera view...[/cyan]")
        self.console.print("[dim]Press 'q' to quit, 'r' to remember current face as BATDAN[/dim]")

        try:
            self.eyes.show_view()
        except KeyboardInterrupt:
            self.console.print("[yellow]Camera view closed[/yellow]")

    def _cmd_remember_face(self, command: str):
        """Teach Alfred to remember a face"""
        if not self.eyes or not self.eyes.active:
            self.console.print("[red]Vision system not available.[/red]")
            return

        # Parse command: /remember <name> or just /remember (defaults to BATDAN)
        parts = command.split()
        name = "BATDAN" if len(parts) < 2 else parts[1].upper()

        self.console.print(f"[cyan]Learning {name}'s face...[/cyan]")
        self.console.print("[dim]Please look at the camera...[/dim]")

        success = self.eyes.learn_face(name)

        if success:
            self.console.print(f"[green]✅ I shall remember {name}, sir.[/green]")
            if self.voice_enabled:
                self.voice.confirm(f"I shall remember {name}")
        else:
            self.console.print("[red]❌ I couldn't detect a face, sir. Please try again.[/red]")
            if self.voice_enabled:
                self.voice.error("I couldn't detect a face")

    def _cmd_listen(self, command: str):
        """Start listening for BATDAN's voice"""
        # Check if any speech recognition is available (VOSK or Google Speech)
        vosk_available = self.ears and hasattr(self.ears, 'use_vosk') and self.ears.use_vosk()
        google_available = self.ears and self.ears.microphone

        if not self.ears or (not vosk_available and not google_available):
            self.console.print("[red]Hearing system not available. Microphone may not be connected.[/red]")
            self.console.print("[dim]For offline: pip install vosk sounddevice[/dim]")
            self.console.print("[dim]For online:  pip install SpeechRecognition pyaudio[/dim]")
            return

        # Check if BATDAN's voice is learned
        if 'BATDAN' not in self.ears.known_voices:
            self.console.print("[yellow]I haven't learned your voice yet, sir.[/yellow]")
            self.console.print("[cyan]Use /learn_voice to teach me to recognize your voice.[/cyan]")
            return

        self.console.print("[cyan]👂 Listening for your commands, sir...[/cyan]")
        self.console.print("[dim]Say 'stop listening' to stop, or press Ctrl+C[/dim]")

        def handle_batdan_command(text: str):
            """Process command from BATDAN"""
            self.console.print(f"[green]You: {text}[/green]")

            # Check if it's a command
            if text.startswith('/'):
                self._handle_command(text)
            else:
                # Handle as conversation
                self._handle_conversation(text)

        try:
            if self.voice_enabled:
                self.voice.confirm("I'm listening, sir")

            self.ears.listen_for_batdan(handle_batdan_command)

        except KeyboardInterrupt:
            self.console.print("[yellow]Stopped listening[/yellow]")

    def _cmd_learn_voice(self, command: str):
        """Teach Alfred to recognize BATDAN's voice"""
        # Note: learn_voice currently requires Google Speech Recognition for audio capture
        # TODO: Add VOSK/sounddevice support for voice learning
        if not self.ears or not self.ears.microphone:
            self.console.print("[red]Hearing system not available for voice learning.[/red]")
            self.console.print("[dim]Voice learning requires: pip install SpeechRecognition pyaudio[/dim]")
            return

        self.console.print("[cyan]Learning your voice, sir...[/cyan]")
        self.console.print("[yellow]Please speak naturally for 5 seconds when I say 'start'...[/yellow]")

        import time
        time.sleep(1)
        self.console.print("[green]Start speaking now![/green]")

        if self.voice_enabled:
            self.voice.inform("Please speak naturally, sir")

        success = self.ears.learn_voice("BATDAN", duration=5)

        if success:
            self.console.print("[green]✅ I now recognize your voice, sir.[/green]")
            if self.voice_enabled:
                self.voice.confirm("I now recognize your voice")
        else:
            self.console.print("[red]❌ Voice learning failed. Please try again.[/red]")
            if self.voice_enabled:
                self.voice.error("Voice learning failed")

    def _cmd_wakeword(self, command: str):
        """Configure wake words"""
        parts = command.split()

        if len(parts) == 1:
            # Show current wake words
            self.console.print("\n[cyan]Wake Word Configuration[/cyan]")
            self.console.print(f"[green]Status:[/green] {'Enabled' if self.wake_word_enabled else 'Disabled'}")
            self.console.print(f"[green]Wake Words:[/green] {', '.join(self.wake_words)}")
            self.console.print("\n[dim]Usage: /wakeword on|off|add <word>|remove <word>[/dim]")
            return

        action = parts[1].lower()

        if action == 'on':
            self.wake_word_enabled = True
            self.console.print("[green]Wake word detection enabled[/green]")
            self._safe_speak("Wake word detection enabled, sir.", VoicePersonality.CONFIRMATION)

        elif action == 'off':
            self.wake_word_enabled = False
            self.console.print("[yellow]Wake word detection disabled[/yellow]")

        elif action == 'add' and len(parts) > 2:
            new_word = ' '.join(parts[2:]).lower()
            if new_word not in self.wake_words:
                self.wake_words.append(new_word)
                self.console.print(f"[green]Added wake word: '{new_word}'[/green]")
            else:
                self.console.print(f"[yellow]'{new_word}' is already a wake word[/yellow]")

        elif action == 'remove' and len(parts) > 2:
            word = ' '.join(parts[2:]).lower()
            if word in self.wake_words:
                self.wake_words.remove(word)
                self.console.print(f"[yellow]Removed wake word: '{word}'[/yellow]")
            else:
                self.console.print(f"[red]'{word}' is not a wake word[/red]")

        elif action == 'list':
            self.console.print(f"[cyan]Current wake words:[/cyan] {', '.join(self.wake_words)}")

        else:
            self.console.print("[red]Unknown action. Use: on, off, add, remove, list[/red]")

    def _cmd_always_listen(self, command: str):
        """Start always-on listening mode with wake word detection"""
        # Check if any speech recognition is available (VOSK or Google Speech)
        vosk_available = self.ears and hasattr(self.ears, 'use_vosk') and self.ears.use_vosk()
        google_available = self.ears and self.ears.microphone

        if not self.ears or (not vosk_available and not google_available):
            self.console.print("[red]Hearing system not available. Microphone may not be connected.[/red]")
            self.console.print("[dim]For offline: pip install vosk sounddevice[/dim]")
            self.console.print("[dim]For online:  pip install SpeechRecognition pyaudio[/dim]")
            return

        if not self.wake_word_enabled:
            self.console.print("[yellow]Wake word detection is disabled. Enabling...[/yellow]")
            self.wake_word_enabled = True

        self.always_listening = True
        self.console.print("\n[bold cyan]Always-On Listening Mode[/bold cyan]")
        self.console.print(f"[green]Wake words:[/green] {', '.join(self.wake_words)}")
        self.console.print("[dim]Say a wake word to activate Alfred, 'stop listening' to exit[/dim]")

        def handle_with_wake_word(text: str):
            """Process speech with wake word detection"""
            text_lower = text.lower().strip()

            # Check for stop command
            if "stop listening" in text_lower or "stop" == text_lower:
                self.always_listening = False
                self.console.print("[yellow]Stopping always-on mode[/yellow]")
                self._safe_speak("Stopping listening mode, sir.", VoicePersonality.CONFIRMATION)
                return False  # Signal to stop

            # Check for wake word
            wake_word_detected = None
            for wake_word in self.wake_words:
                if text_lower.startswith(wake_word):
                    wake_word_detected = wake_word
                    break
                elif wake_word in text_lower:
                    wake_word_detected = wake_word
                    break

            if wake_word_detected:
                # Extract command after wake word
                command_text = text_lower.replace(wake_word_detected, '').strip()

                if command_text:
                    self.console.print(f"[green]You: {command_text}[/green]")
                    self._safe_speak("Yes, sir?", VoicePersonality.GREETING)

                    # Process the command
                    if command_text.startswith('/'):
                        self._handle_command(command_text)
                    else:
                        self._handle_conversation(command_text)
                else:
                    # Just wake word, acknowledge and wait
                    self.console.print("[cyan]At your service, sir.[/cyan]")
                    self._safe_speak("At your service, sir.", VoicePersonality.GREETING)

            return True  # Continue listening

        try:
            self._safe_speak("Always-on listening activated. Say my name when you need me, sir.", VoicePersonality.INFORMATION)

            # Start continuous listening with wake word detection
            while self.always_listening:
                try:
                    # Listen for a phrase
                    text = None
                    if hasattr(self.ears, 'listen_once'):
                        result = self.ears.listen_once(timeout=5)
                        # listen_once returns Dict with 'text' key, not a string
                        if result and isinstance(result, dict):
                            text = result.get('text', '')
                        elif result and isinstance(result, str):
                            text = result
                    else:
                        # Fallback - use basic listen
                        import speech_recognition as sr
                        recognizer = sr.Recognizer()
                        with sr.Microphone() as source:
                            recognizer.adjust_for_ambient_noise(source, duration=0.5)
                            try:
                                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
                                text = recognizer.recognize_google(audio)
                            except sr.WaitTimeoutError:
                                continue
                            except sr.UnknownValueError:
                                continue

                    if text and text.strip():
                        if not handle_with_wake_word(text):
                            break

                except Exception as e:
                    self.logger.debug(f"Listening error (ignored): {e}")
                    continue

        except KeyboardInterrupt:
            self.console.print("[yellow]Stopped listening[/yellow]")
            self.always_listening = False

    def _cmd_stop_listening(self, command: str):
        """Stop listening mode"""
        self.always_listening = False
        if self.ears:
            self.ears.stop_listening()
            self.console.print("[yellow]Stopped listening[/yellow]")
        else:
            self.console.print("[red]Hearing system not active[/red]")

    def _cmd_joe_dog(self, command: str):
        """Remember Joe Dog"""
        if not self.personal_memory:
            self.console.print("[red]Personal memory not initialized[/red]")
            return

        # Display tribute to Joe Dog
        self.console.print()
        tribute = self.personal_memory.tribute_to_joe_dog(self.voice if self.voice_enabled else None)

        self.console.print(Panel(
            tribute,
            title="🐕 In Memory of Joe Dog",
            border_style="blue",
            box=box.DOUBLE
        ))
        self.console.print()

    def _cmd_status(self, command: str):
        """Show complete system status including sensory capabilities"""
        table = Table(title="👑 ALFRED_IV-Y-VI Elite System Status", box=box.ROUNDED)
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Details", style="dim")

        # Brain
        stats = self.brain.get_stats()
        table.add_row(
            "🧠 Brain",
            "✅ Active",
            f"{stats['conversations']} conversations, {stats['knowledge']} knowledge entries"
        )

        # Voice
        if self.voice and self.voice.enabled:
            voice_status = self.voice.get_status()
            table.add_row(
                "🗣️ Voice (Speaking)",
                "✅ Active" if self.voice_enabled else "⚠️ Muted",
                f"{voice_status['voice']} on {voice_status['platform']}"
            )
        else:
            table.add_row("🗣️ Voice (Speaking)", "❌ Disabled", "")

        # Eyes (Vision)
        if self.eyes and self.eyes.active:
            eye_status = self.eyes.get_status()
            known_faces = len(eye_status['known_faces'])
            batdan_known = "✅ Yes" if eye_status['batdan_known'] else "❌ No"
            table.add_row(
                "👁️ Eyes (Vision)",
                "✅ Active",
                f"{known_faces} faces known, BATDAN: {batdan_known}"
            )
        else:
            table.add_row("👁️ Eyes (Vision)", "❌ Disabled", "Camera not available")

        # Ears (Hearing)
        if self.ears and self.ears.microphone:
            ear_status = self.ears.get_status()
            known_voices = len(ear_status['known_voices'])
            batdan_voice = "✅ Yes" if ear_status['batdan_voice_learned'] else "❌ No"
            table.add_row(
                "👂 Ears (Hearing)",
                "✅ Active",
                f"{known_voices} voices known, BATDAN: {batdan_voice}"
            )
        else:
            table.add_row("👂 Ears (Hearing)", "❌ Disabled", "Microphone not available")

        # Personal Memory
        if self.personal_memory:
            pm_status = self.personal_memory.get_status()
            table.add_row(
                "💭 Personal Memory",
                "✅ Active",
                f"BATDAN: {pm_status['batdan_remembered']}, Joe Dog: {pm_status['joe_dog_remembered']}"
            )
        else:
            table.add_row("💭 Personal Memory", "❌ Disabled", "")

        # Privacy
        privacy_mode = self.privacy.get_privacy_mode()
        table.add_row(
            "🔐 Privacy",
            "✅ Protected",
            f"Mode: {privacy_mode}"
        )

        # Tools
        tool_status = "✅ Enabled" if self.tool_mode_enabled else "⚠️ Disabled"
        table.add_row(
            "🔧 Tools",
            tool_status,
            "Use /tools on to enable"
        )

        self.console.print(table)

        # Additional sensory integration info
        self.console.print()
        self.console.print("[cyan]💡 Sensory Commands:[/cyan]")
        self.console.print("[dim]/see - Show who Alfred sees[/dim]")
        self.console.print("[dim]/watch - Live camera view with face detection[/dim]")
        self.console.print("[dim]/remember - Teach Alfred to recognize your face[/dim]")
        self.console.print("[dim]/listen - Start voice listening mode[/dim]")
        self.console.print("[dim]/learn_voice - Teach Alfred to recognize your voice[/dim]")
        self.console.print("[dim]/joe - Pay tribute to Joe Dog[/dim]")
        self.console.print()

    # === Patent-Pending Technology Commands ===

    def _cmd_cortex(self, command: str):
        """Show CORTEX (forgetting brain) statistics"""
        if not self.cortex:
            self.console.print("[red]CORTEX not available[/red]")
            return

        stats = self.cortex.get_stats()

        table = Table(title="🧠 CORTEX - The Forgetting Brain", box=box.ROUNDED)
        table.add_column("Layer", style="cyan")
        table.add_column("Items", style="green")
        table.add_column("Avg Importance", style="yellow")

        table.add_row("Flash", str(stats['flash_count']), "-")
        table.add_row("Working", str(stats['working_count']), "-")

        for layer_name, layer_stats in stats['layers'].items():
            table.add_row(
                layer_name.replace('_', ' ').title(),
                str(layer_stats['count']),
                str(layer_stats['avg_importance'])
            )

        self.console.print(table)
        self.console.print(f"\n[dim]Total: {stats['total_memories']} / {stats['storage_bound']} ({stats['utilization']}% utilized)[/dim]")
        self.console.print("[dim]PATENT PENDING - GxEum Technologies / CAMDAN Enterprizes[/dim]")

    def _cmd_ultrathunk(self, command: str):
        """Show ULTRATHUNK compression statistics"""
        if not self.ultrathunk:
            self.console.print("[red]ULTRATHUNK not available[/red]")
            return

        stats = self.ultrathunk.get_stats()

        table = Table(title="📦 ULTRATHUNK - Compressed Intelligence", box=box.ROUNDED)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Total Thunks", str(stats['total_thunks']))
        table.add_row("Original Data", f"{stats['original_bytes']:,} bytes")
        table.add_row("Compressed", f"{stats['compressed_bytes']:,} bytes")
        table.add_row("Compression Ratio", f"{stats['compression_ratio']}:1")
        table.add_row("Total Fires", str(stats['total_fires']))
        table.add_row("Avg Confidence", f"{stats['avg_confidence']:.2f}")

        self.console.print(table)

        if stats['by_type']:
            self.console.print("\n[cyan]By Type:[/cyan]")
            for thunk_type, count in stats['by_type'].items():
                self.console.print(f"  {thunk_type}: {count}")

        self.console.print("\n[dim]PATENT PENDING - GxEum Technologies / CAMDAN Enterprizes[/dim]")

    def _cmd_guardian(self, command: str):
        """Show ALFREDGuardian IP protection status"""
        if not self.guardian:
            self.console.print("[red]ALFREDGuardian not available[/red]")
            return

        cert = self.guardian.generate_certificate()

        table = Table(title="🛡️ ALFREDGuardian - IP Protection", box=box.ROUNDED)
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Instance ID", cert['instance_id'])
        table.add_row("Signature Hash", cert['signature_hash'][:32] + "...")
        table.add_row("Linguistic Fingerprints", str(cert['fingerprints']['linguistic']))
        table.add_row("Timing Fingerprints", str(cert['fingerprints']['timing']))
        table.add_row("Structural Fingerprints", str(cert['fingerprints']['structural']))
        table.add_row("Owner", cert['owner'])
        table.add_row("Entity", cert['entity'])
        table.add_row("Status", cert['patent_status'])

        self.console.print(table)
        self.console.print("\n[dim]All responses are protected with behavioral fingerprints[/dim]")

    def _cmd_nexus(self, command: str):
        """Show NEXUS Protocol status"""
        if not self.nexus_agent:
            self.console.print("[red]NEXUS Protocol not available[/red]")
            return

        table = Table(title="🔗 NEXUS Protocol - AI-to-AI Communication", box=box.ROUNDED)
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Agent ID", self.nexus_agent.agent_id)
        table.add_row("Agent Name", self.nexus_agent.name)
        table.add_row("Capabilities", str(len(self.nexus_agent.capabilities)))

        self.console.print(table)

        self.console.print("\n[cyan]Registered Capabilities:[/cyan]")
        for cap in self.nexus_agent.get_capabilities():
            self.console.print(f"  [green]{cap.name}[/green]: {cap.description}")
            self.console.print(f"    [dim]Latency: {cap.latency_ms}ms | Reliability: {cap.reliability:.1%}[/dim]")

        self.console.print("\n[dim]PATENT PENDING - GxEum Technologies / CAMDAN Enterprizes[/dim]")

    def _cmd_unified(self, command: str):
        """Show Unified Memory statistics"""
        if not self.unified_memory:
            self.console.print("[red]Unified Memory not available[/red]")
            return

        stats = self.unified_memory.get_stats()

        table = Table(title="🔮 Unified Memory - Brain + CORTEX + ULTRATHUNK", box=box.ROUNDED)
        table.add_column("System", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Details", style="dim")

        # Brain stats
        if stats['systems']['brain']:
            brain = stats['systems']['brain']
            table.add_row(
                "🧠 Brain (11-table)",
                "Active",
                f"{brain.get('conversations', 0)} convos, {brain.get('knowledge', 0)} knowledge"
            )

        # CORTEX stats
        if stats['systems']['cortex']:
            cortex = stats['systems']['cortex']
            table.add_row(
                "🌀 CORTEX (5-layer)",
                "Active",
                f"{cortex.get('total_memories', 0)} items, {cortex.get('utilization', 0)}% utilized"
            )

        # ULTRATHUNK stats
        if stats['systems']['ultrathunk']:
            thunk = stats['systems']['ultrathunk']
            table.add_row(
                "📦 ULTRATHUNK",
                "Active",
                f"{thunk.get('total_thunks', 0)} thunks, {thunk.get('compression_ratio', 0)}:1 compression"
            )

        self.console.print(table)

        # Integration stats
        self.console.print(f"\n[cyan]Integration Stats:[/cyan]")
        self.console.print(f"  Syncs: {stats['integration']['syncs']}")
        self.console.print(f"  Knowledge synced: {stats['integration']['knowledge_synced']}")
        self.console.print(f"  Patterns compressed: {stats['integration']['patterns_compressed']}")
        self.console.print(f"  Total items: {stats['total_items']}")

    def _cmd_consolidate(self, command: str):
        """Run full memory consolidation (like sleep for AI)"""
        if not self.unified_memory:
            self.console.print("[red]Unified Memory not available[/red]")
            return

        self.console.print("[cyan]Running memory consolidation...[/cyan]")
        self.console.print("[dim]This syncs Brain, CORTEX, and ULTRATHUNK[/dim]")

        try:
            report = self.unified_memory.consolidate()

            self.console.print("\n[green]Consolidation complete![/green]")

            if report.get('cortex'):
                c = report['cortex']
                self.console.print(f"  CORTEX: {c.get('archived', 0)} items archived")

            if report.get('ultrathunk'):
                u = report['ultrathunk']
                self.console.print(f"  ULTRATHUNK: {u.get('thunks_after', 0)} thunks ({u.get('compression_ratio', 0)}:1)")

            if report.get('sync'):
                s = report['sync']
                self.console.print(f"  Sync: {s.get('knowledge_synced', 0)} knowledge synced")

            self._safe_speak("Memory consolidation complete, sir.", VoicePersonality.CONFIRMATION)

        except Exception as e:
            self.console.print(f"[red]Consolidation error: {e}[/red]")

    def _cmd_learn(self, command: str):
        """Learn generative patterns from conversations using Fabric"""
        parts = command.split(maxsplit=1)
        topic = parts[1] if len(parts) > 1 else None

        self.console.print("[cyan]Learning generative patterns...[/cyan]")

        if not self.ultrathunk:
            self.console.print("[red]ULTRATHUNK not available[/red]")
            return

        # Get recent conversations from brain
        if self.brain:
            try:
                # Get recent conversations
                conversations = self.brain.get_conversation_context(limit=50)

                if not conversations:
                    self.console.print("[yellow]No conversations to learn from[/yellow]")
                    return

                # Group by detected topics/patterns
                items = []
                for conv in conversations:
                    items.append({
                        'content': conv.get('user_input', ''),
                        'response': conv.get('alfred_response', ''),
                        'timestamp': conv.get('timestamp', '')
                    })

                # Try to compress into thunks
                from core.ultrathunk import ThunkType
                thunk = self.ultrathunk.compress_and_store(items, ThunkType.PATTERN)

                if thunk:
                    self.console.print(f"\n[green]Created new ULTRATHUNK![/green]")
                    self.console.print(f"  ID: {thunk.id}")
                    self.console.print(f"  Name: {thunk.name}")
                    self.console.print(f"  Compression: {thunk.compression_ratio:.1f}:1")
                    self.console.print(f"  Items compressed: {thunk.created_from_count}")

                    # Store in brain's knowledge
                    if self.brain:
                        import json
                        self.brain.store_knowledge(
                            category="learned_pattern",
                            key=thunk.id,
                            value=json.dumps({
                                'name': thunk.name,
                                'trigger': thunk.trigger_pattern,
                                'template': thunk.generator_template,
                                'compression': thunk.compression_ratio
                            }),
                            source="fabric_learning",
                            importance=8
                        )

                    self._safe_speak("I've learned a new pattern, sir.", VoicePersonality.CONFIRMATION)
                else:
                    self.console.print("[yellow]Not enough data to form a pattern yet[/yellow]")

            except Exception as e:
                self.console.print(f"[red]Learning error: {e}[/red]")
        else:
            self.console.print("[red]Brain not available[/red]")

    def _cmd_forget(self, command: str):
        """Forget non-generative patterns (cleanup)"""
        self.console.print("[cyan]Analyzing patterns for generativity...[/cyan]")

        if not self.ultrathunk:
            self.console.print("[red]ULTRATHUNK not available[/red]")
            return

        try:
            # Get all thunks
            thunks = self.ultrathunk.list_thunks(limit=100)

            forgotten = 0
            kept = 0

            for thunk in thunks:
                # Non-generative criteria:
                # - Never fired (fire_count == 0)
                # - Low confidence (< 0.3)
                # - Poor compression ratio (< 2:1)
                is_non_generative = (
                    thunk.fire_count == 0 and
                    (thunk.confidence < 0.3 or thunk.compression_ratio < 2.0)
                )

                if is_non_generative:
                    # Remove from database
                    import sqlite3
                    conn = sqlite3.connect(self.ultrathunk.db_path)
                    cursor = conn.cursor()
                    cursor.execute('DELETE FROM ultrathunks WHERE id = ?', (thunk.id,))
                    conn.commit()
                    conn.close()
                    forgotten += 1
                    self.console.print(f"  [dim]Forgot: {thunk.name} (unused, low value)[/dim]")
                else:
                    kept += 1

            self.console.print(f"\n[green]Cleanup complete![/green]")
            self.console.print(f"  Forgotten: {forgotten} non-generative patterns")
            self.console.print(f"  Kept: {kept} generative patterns")

            if forgotten > 0:
                self._safe_speak(f"Forgotten {forgotten} non-generative patterns, sir.", VoicePersonality.INFORMATION)

        except Exception as e:
            self.console.print(f"[red]Forget error: {e}[/red]")

    def _cmd_ethics(self, command: str):
        """Show Joe Dog's Rule ethics status"""
        if not self.ethics:
            self.console.print("[red]Ethics module not available[/red]")
            return

        stats = self.ethics.get_stats()

        # Display Joe Dog's Blessing
        if ETHICS_AVAILABLE and JOE_DOG_BLESSING:
            self.console.print(f"[cyan]{JOE_DOG_BLESSING}[/cyan]")

        table = Table(title="Joe Dog's Rule - Ethics Protection", box=box.ROUNDED)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Violations Blocked", str(stats['violations_blocked']))
        table.add_row("Positive Actions", str(stats['positive_count']))
        table.add_row("Positivity Ratio", f"{stats['ratio']:.1%}")

        self.console.print(table)

        self.console.print("\n[cyan]Inviolable Principles:[/cyan]")
        self.console.print("  [red]HARD BLOCK[/red] - Weapons, violence against humans/animals")
        self.console.print("  [yellow]SOFT BLOCK[/yellow] - Environmental harm, exploitation, hatred")
        self.console.print("  [green]ENCOURAGED[/green] - Peace, love, sustainability, protection")

        self._safe_speak("Joe Dog's Rule is active and protecting all life, sir.", VoicePersonality.INFORMATION)

    def _cmd_hierarchy(self, command: str):
        """Display ALFRED SYSTEMS hierarchy"""
        try:
            from core.master_controller import MasterController
            controller = MasterController(brain=self.brain)
            self.console.print(controller.get_hierarchy_summary())
        except Exception as e:
            self.console.print(f"[red]Error loading hierarchy: {e}[/red]")

    def _cmd_control(self, command: str):
        """Master control interface for ALFRED_IV-Y-VI"""
        try:
            from core.master_controller import MasterController
            controller = MasterController(brain=self.brain)
            parts = command.split()
            if len(parts) < 2:
                self.console.print(Panel(
                    "[bold magenta]★ ALFRED_IV-Y-VI Master Control ★[/bold magenta]\n\n"
                    "[cyan]Commands:[/cyan]\n"
                    "  /control scan <instance>    - Security scan an instance\n"
                    "  /control status <instance>  - Get instance status\n"
                    "  /control audit              - View audit log\n"
                    "  /control grant <user> <tier> - Grant clearance\n\n"
                    "[dim]Available instances: ALFRED_IV-Y-VI[/dim]",
                    title="Master Control", border_style="magenta"
                ))
                return
            subcommand = parts[1].lower()
            if subcommand == "scan":
                target = parts[2] if len(parts) > 2 else "ALFRED_IV-Y-VI"
                results = controller.scan_instance(target)
                self.console.print(f"\n[bold]Security Scan: {target}[/bold]")
                for check in results.get("checks", []):
                    status_color = "green" if check["status"] == "pass" else "yellow" if check["status"] == "warning" else "red"
                    self.console.print(f"  [{status_color}]{check['status'].upper()}[/{status_color}] {check['check']}: {check['details']}")
            elif subcommand == "audit":
                log = controller.get_audit_log(10)
                self.console.print("\n[bold]Recent Audit Log[/bold]")
                for entry in log:
                    self.console.print(f"  [{entry['timestamp'][:19]}] {entry['action']}: {entry['details']}")
        except Exception as e:
            self.console.print(f"[red]Master control error: {e}[/red]")

    def _cmd_instances(self, command: str):
        """List all ALFRED instances"""
        try:
            from core.master_controller import MasterController
            controller = MasterController(brain=self.brain)
            instances = controller.list_all_instances()
            table = Table(title="👑 ALFRED SYSTEMS Instances", box=box.ROUNDED)
            table.add_column("Instance", style="cyan")
            table.add_column("Tier", style="magenta")
            table.add_column("Status", style="green")
            for inst in instances:
                if inst:
                    table.add_row(inst["name"], f"{inst['tier']} (L{inst['tier_level']})",
                        "✅ Active" if inst.get("path_exists") else "⚠️ Path missing")
            self.console.print(table)
        except Exception as e:
            self.console.print(f"[red]Error listing instances: {e}[/red]")

    def _cmd_imagine(self, command: str):
        """Generate images via SwarmUI"""
        try:
            from capabilities.generation.swarmui_client import SwarmUIClient
        except ImportError:
            self.console.print("[red]SwarmUI client not available[/red]")
            return
        parts = command.split(maxsplit=1)
        if len(parts) < 2:
            self.console.print("[yellow]Usage: /imagine <prompt>[/yellow]")
            return
        prompt = parts[1]
        client = SwarmUIClient()
        if not client.is_available():
            self.console.print("[red]SwarmUI server not running at http://localhost:7801[/red]")
            return
        self.console.print(f"[cyan]Generating image for:[/cyan] {prompt}")
        with self.console.status("[bold green]Generating..."):
            image_path = client.generate_image(prompt=prompt)
        if image_path:
            image_url = client.get_image_url(image_path)
            self.console.print(f"[green]Image generated![/green]\n  URL: {image_url}")
        else:
            self.console.print("[red]Image generation failed[/red]")

    def _cmd_exit(self, command: str):
        """Exit Alfred"""
        self._shutdown()

    def _shutdown(self):
        """Graceful shutdown"""
        self.console.print("\n[cyan]Alfred shutting down...[/cyan]")

        # Cleanup sensory systems
        if self.eyes:
            self.eyes.close()
        if self.ears:
            self.ears.stop_listening()

        # Brain auto-saves with SQLite (no explicit close needed)
        if self.brain:
            self.console.print("[green]All memories preserved[/green]")

        # Farewell
        farewell = Panel(
            "[bold cyan]Until next time, sir.[/bold cyan]\n\n"
            "[dim]All memories preserved.[/dim]",
            title="Alfred",
            border_style="cyan",
            box=box.ROUNDED
        )
        self.console.print(farewell)

        self._safe_speak("Until next time, sir", VoicePersonality.GREETING)

        self.running = False
        sys.exit(0)


def main():
    """Entry point"""
    try:
        terminal = AlfredTerminal()
        terminal.run()
    except Exception as e:
        print(f"Fatal error: {e}")
        logging.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
