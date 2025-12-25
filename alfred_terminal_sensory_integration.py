"""
Alfred Terminal - SENSORY INTEGRATION MODULE
This module adds vision, hearing, and personal memory to alfred_terminal.py

⚠️ WARNING: THIS IS NOT AN EXECUTABLE PYTHON FILE! ⚠️

This file contains CODE SNIPPETS that must be manually copied into alfred_terminal.py.
DO NOT try to import or run this file directly - it will fail with IndentationError.

USAGE:
1. Open alfred_terminal.py
2. Open this file (alfred_terminal_sensory_integration.py)
3. Copy each SECTION below into alfred_terminal.py at the indicated locations
4. Save alfred_terminal.py
5. Run: python alfred_terminal.py

Copy these sections into alfred_terminal.py to enable full sensory capabilities.

Author: Daniel J Rita (BATDAN)
"""

# ==============================================================================
# ⚠️ THIS FILE IS A TEMPLATE - NOT VALID PYTHON CODE ⚠️
# The code snippets below are intentionally not properly indented for standalone execution.
# They are designed to be copy-pasted into alfred_terminal.py at specific locations.
# ==============================================================================

TEMPLATE = r'''
# ==============================================================================
# SECTION 1: ADD THESE IMPORTS AT THE TOP (after line 43)
# ==============================================================================

from capabilities.vision.alfred_eyes import AlfredEyes
from capabilities.voice.alfred_ears_advanced import AlfredEarsAdvanced
from core.personal_memory import PersonalMemory


# ==============================================================================
# SECTION 2: ADD THESE TO __init__ METHOD (after line 63)
# ==============================================================================
# Sensory systems
self.eyes = None  # Vision system
self.ears = None  # Advanced hearing system
self.personal_memory = None  # Personal memory (BATDAN, Joe Dog)


# ==============================================================================
# SECTION 3: ADD TO _initialize_components METHOD (after self.voice initialization)
# ==============================================================================

            # Initialize personal memory (knows BATDAN and Joe Dog)
            self.personal_memory = PersonalMemory(self.brain)
            self.logger.info("💭 Personal memory initialized")

            # Initialize vision system (Alfred's eyes)
            try:
                self.eyes = AlfredEyes(brain=self.brain, camera_index=0)
                if self.eyes.active:
                    self.logger.info("👁️ Alfred's eyes initialized")
                else:
                    self.logger.warning("⚠️ Camera not available - vision disabled")
            except Exception as e:
                self.logger.warning(f"⚠️ Could not initialize vision: {e}")
                self.eyes = None

            # Initialize advanced hearing system (Alfred's ears)
            try:
                self.ears = AlfredEarsAdvanced(brain=self.brain)
                if self.ears.microphone:
                    self.logger.info("👂 Alfred's ears initialized")
                else:
                    self.logger.warning("⚠️ Microphone not available - hearing disabled")
            except Exception as e:
                self.logger.warning(f"⚠️ Could not initialize hearing: {e}")
                self.ears = None


# ==============================================================================
# SECTION 4: ADD THESE NEW COMMANDS TO commands DICT IN _handle_command (after line 222)
# ==============================================================================

            '/see': self._cmd_see,
            '/privacy': self._cmd_privacy,
            '/cloud': self._cmd_cloud,
            '/tools': self._cmd_tools,
            '/scan': self._cmd_scan,
            '/security': self._cmd_security,
            '/watch': self._cmd_watch,
            '/remember': self._cmd_remember_face,
            '/listen': self._cmd_listen,
            '/learn_voice': self._cmd_learn_voice,
            '/stop_listening': self._cmd_stop_listening,
            '/joe': self._cmd_joe_dog,
            '/status': self._cmd_status,


# ==============================================================================
# SECTION 5: ADD THESE NEW COMMAND METHODS (before run() method)
# ==============================================================================

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
        stats = self.brain.get_memory_stats()
        table.add_row(
            "🧠 Brain",
            "✅ Active",
            f"{stats['total_conversations']} conversations, {stats['total_knowledge']} knowledge entries"
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

# ==============================================================================
# SECTION 6: UPDATE show_greeting METHOD (replace existing)
# ==============================================================================

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

# ==============================================================================
# SECTION 7: UPDATE _cmd_help METHOD (replace existing)
# ==============================================================================

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

        self.console.print(Markdown(help_text))

# ==============================================================================
# SECTION 8: ADD cleanup TO _cmd_exit METHOD (before sys.exit(0))
# ==============================================================================

            # Cleanup sensory systems
            if self.eyes:
                self.eyes.close()
            if self.ears:
                self.ears.stop_listening()

# ==============================================================================
# END OF SENSORY INTEGRATION
# ==============================================================================
'''
