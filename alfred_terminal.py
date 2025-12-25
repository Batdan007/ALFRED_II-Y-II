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

import sys
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
        file_handler = logging.FileHandler('alfred_terminal.log', encoding='utf-8')
        stream_handler = logging.StreamHandler(sys.stdout)

        logging.basicConfig(
            level=logging.INFO,
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

            self.console.print(f"\n[green]Alfred Brain initialized on {platform_name}[/green]\n")

        except Exception as e:
            self.logger.error(f"Failed to initialize components: {e}")
            self.console.print(f"[red]Initialization failed: {e}[/red]")
            sys.exit(1)

    def show_greeting(self):
        """Show Alfred's greeting with personal recognition"""
        self.console.print()
        self.console.print(Panel(
            "[bold cyan]ALFRED-UBX[/bold cyan] v3.0.0\n"
            "[dim]The Distinguished British Butler AI[/dim]\n"
            "[dim]With Complete Sensory Integration[/dim]",
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
            '/learn_voice': self._cmd_learn_voice,
            '/stop_listening': self._cmd_stop_listening,
            '/joe': self._cmd_joe_dog,
            '/status': self._cmd_status,
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
            # Get conversation context from brain
            context = self.brain.get_conversation_context(limit=5)

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

            # Add knowledge to context if found
            if knowledge_context:
                context_text = "\n\n[ALFRED'S BRAIN KNOWLEDGE - CRITICAL INFORMATION]:\n"
                for k in knowledge_context[:5]:  # Top 5 most relevant
                    context_text += f"- {k['category']}/{k['key']}: {k['value']} (importance: {k['importance']}/10)\n"
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
                # Regular mode - simple generation
                self.console.print("[dim]Alfred is thinking...[/dim]")
                response = self.ai.generate(user_input, context)

                if response:
                    # Store in brain
                    self.brain.store_conversation(
                        user_input=user_input,
                        alfred_response=response,
                        success=True
                    )

                    # Display response
                    self.console.print(f"\n[bold cyan]Alfred:[/bold cyan]")
                    self.console.print(Markdown(response))
                    self.console.print()

                    # Speak if voice enabled
                    self._safe_speak(response, VoicePersonality.INFORMATION)

                else:
                    self.console.print("[red]All AI backends failed. Please check configuration.[/red]")
                    self.console.print("[dim]Suggestion: Install Ollama or set cloud API keys[/dim]")

        except Exception as e:
            self.logger.error(f"Conversation error: {e}")
            self.console.print(f"[red]Error generating response: {e}[/red]")

    def _handle_conversation_with_tools(self, user_input: str, context):
        """Handle conversation with tool use enabled"""
        try:
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

                # Speak if enabled
                self._safe_speak(response, VoicePersonality.INFORMATION)

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
        if not self.ears or not self.ears.microphone:
            self.console.print("[red]Hearing system not available. Microphone may not be connected.[/red]")
            self.console.print("[dim]Install dependencies: pip install SpeechRecognition pyaudio[/dim]")
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
        if not self.ears or not self.ears.microphone:
            self.console.print("[red]Hearing system not available.[/red]")
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

    def _cmd_stop_listening(self, command: str):
        """Stop listening mode"""
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
        table = Table(title="🤖 ALFRED-UBX System Status", box=box.ROUNDED)
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
