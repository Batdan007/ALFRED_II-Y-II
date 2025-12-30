"""
ALFRED Unified Launcher - Control Panel for All ALFRED Tools

Single launching point for:
- ALFRED Terminal (main assistant)
- ALFRED_Y (private unrestricted assistant)
- Strix Security Scanner
- Bug Bounty Hunter
- DontLookUp DVB-S2 Parser
- MCP Servers

Author: Daniel J Rita (BATDAN)
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Optional, Dict, List

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.prompt import Prompt, Confirm
    from rich.text import Text
    from rich.layout import Layout
    from rich.live import Live
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("Rich not installed. Run: pip install rich")
    sys.exit(1)

console = Console()

# Base paths
ALFRED_II_PATH = Path(__file__).parent
ALFRED_Y_PATH = Path("C:/Users/danie/Projects/ALFRED_Y_PRIVATE")
PROJECTS_PATH = Path("C:/Users/danie/Projects")


class AlfredLauncher:
    """Unified launcher for all ALFRED tools"""

    def __init__(self):
        self.console = Console()
        self.running_processes: Dict[str, subprocess.Popen] = {}

        # Tool definitions
        self.tools = {
            "1": {
                "name": "ALFRED Terminal",
                "description": "Main AI assistant with persistent memory",
                "path": ALFRED_II_PATH / "alfred_terminal.py",
                "command": ["python", "alfred_terminal.py"],
                "cwd": ALFRED_II_PATH,
                "interactive": True
            },
            "2": {
                "name": "ALFRED_Y (Private)",
                "description": "Unrestricted assistant with VPN/Tor/security tools",
                "path": ALFRED_Y_PATH / "alfred_y.py",
                "command": ["python", "alfred_y.py"],
                "cwd": ALFRED_Y_PATH,
                "interactive": True
            },
            "3": {
                "name": "Strix Security Scanner",
                "description": "AI-powered vulnerability scanning",
                "path": None,  # CLI tool
                "command": ["strix"],
                "cwd": ALFRED_II_PATH,
                "interactive": True,
                "requires_target": True
            },
            "4": {
                "name": "Bug Bounty Hunter",
                "description": "Automated recon and vulnerability hunting",
                "path": ALFRED_Y_PATH / "tools" / "bug_bounty_hunter.py",
                "command": ["python", "tools/bug_bounty_hunter.py"],
                "cwd": ALFRED_Y_PATH,
                "interactive": False,
                "requires_target": True
            },
            "5": {
                "name": "DontLookUp Parser",
                "description": "DVB-S2 satellite communication parser",
                "path": ALFRED_II_PATH / "capabilities" / "security" / "dontlookup_scanner.py",
                "command": ["python", "-m", "capabilities.security.dontlookup_scanner"],
                "cwd": ALFRED_II_PATH,
                "interactive": False
            },
            "6": {
                "name": "MCP Server (Brain)",
                "description": "Start ALFRED Brain MCP server for Claude Code",
                "path": ALFRED_II_PATH / "mcp" / "alfred_mcp_server.py",
                "command": ["python", "-m", "mcp.alfred_mcp_server"],
                "cwd": ALFRED_II_PATH,
                "interactive": False,
                "background": True
            },
            "7": {
                "name": "Quick Scan",
                "description": "Run quick security scan on a target",
                "action": "quick_scan"
            },
            "8": {
                "name": "Full Recon",
                "description": "Complete reconnaissance on a target",
                "action": "full_recon"
            },
            "9": {
                "name": "System Status",
                "description": "Check status of all tools and dependencies",
                "action": "status"
            }
        }

    def display_banner(self):
        """Display the launcher banner"""
        banner = """
    +===========================================================+
    |      _    _     _____ ____  _____ ____                    |
    |     / \\  | |   |  ___|  _ \\| ____|  _ \\                   |
    |    / _ \\ | |   | |_  | |_) |  _| | | | |                  |
    |   / ___ \\| |___|  _| |  _ <| |___| |_| |                  |
    |  /_/   \\_\\_____|_|   |_| \\_\\_____|____/                   |
    |                                                           |
    |              UNIFIED CONTROL PANEL v1.0                   |
    |                     by BATDAN                             |
    +===========================================================+
        """
        self.console.print(Panel(
            Text(banner, style="bold cyan"),
            border_style="cyan"
        ))

    def display_menu(self):
        """Display the main menu"""
        table = Table(
            title="Available Tools",
            show_header=True,
            header_style="bold magenta",
            border_style="blue"
        )

        table.add_column("#", style="cyan", width=3)
        table.add_column("Tool", style="green", width=25)
        table.add_column("Description", style="white", width=45)
        table.add_column("Status", style="yellow", width=12)

        for key, tool in self.tools.items():
            status = self._check_tool_status(tool)
            status_style = "green" if status == "Ready" else "red" if status == "Missing" else "yellow"
            table.add_row(
                key,
                tool["name"],
                tool["description"],
                f"[{status_style}]{status}[/{status_style}]"
            )

        self.console.print(table)
        self.console.print()
        self.console.print("[cyan]Commands:[/] [white]Enter number to launch | [yellow]q[/] to quit | [yellow]s[/] for status[/]")

    def _check_tool_status(self, tool: dict) -> str:
        """Check if a tool is available"""
        if "action" in tool:
            return "Ready"

        if tool.get("path") and not tool["path"].exists():
            return "Missing"

        # Check if it's a CLI tool
        if tool.get("path") is None:
            try:
                result = subprocess.run(
                    [tool["command"][0], "--version"],
                    capture_output=True,
                    timeout=5
                )
                return "Ready" if result.returncode == 0 else "Error"
            except FileNotFoundError:
                return "Missing"
            except Exception:
                return "Unknown"

        return "Ready"

    def check_all_status(self):
        """Display detailed status of all tools and dependencies"""
        self.console.print(Panel("[bold]System Status Check[/bold]", border_style="cyan"))

        # Python version
        self.console.print(f"[cyan]Python:[/] {sys.version.split()[0]}")

        # Check each tool
        status_table = Table(show_header=True, header_style="bold")
        status_table.add_column("Component", style="cyan")
        status_table.add_column("Status", style="white")
        status_table.add_column("Details", style="dim")

        # ALFRED Terminal
        alfred_term = ALFRED_II_PATH / "alfred_terminal.py"
        status_table.add_row(
            "ALFRED Terminal",
            "[green]OK[/]" if alfred_term.exists() else "[red]Missing[/]",
            str(alfred_term)
        )

        # ALFRED_Y
        alfred_y = ALFRED_Y_PATH / "alfred_y.py"
        status_table.add_row(
            "ALFRED_Y",
            "[green]OK[/]" if alfred_y.exists() else "[red]Missing[/]",
            str(alfred_y)
        )

        # Strix
        try:
            result = subprocess.run(["strix", "--version"], capture_output=True, text=True, timeout=5)
            strix_version = result.stdout.strip() if result.returncode == 0 else "Error"
            status_table.add_row(
                "Strix Scanner",
                "[green]OK[/]" if result.returncode == 0 else "[red]Error[/]",
                strix_version
            )
        except FileNotFoundError:
            status_table.add_row("Strix Scanner", "[red]Missing[/]", "pipx install strix-agent")
        except Exception as e:
            status_table.add_row("Strix Scanner", "[yellow]Unknown[/]", str(e))

        # Bug Bounty Hunter
        bb_hunter = ALFRED_Y_PATH / "tools" / "bug_bounty_hunter.py"
        status_table.add_row(
            "Bug Bounty Hunter",
            "[green]OK[/]" if bb_hunter.exists() else "[red]Missing[/]",
            str(bb_hunter)
        )

        # DontLookUp
        dontlookup = ALFRED_II_PATH / "capabilities" / "security" / "dontlookup_scanner.py"
        status_table.add_row(
            "DontLookUp Parser",
            "[green]OK[/]" if dontlookup.exists() else "[red]Missing[/]",
            str(dontlookup)
        )

        # MCP Server
        mcp_server = ALFRED_II_PATH / "mcp" / "alfred_mcp_server.py"
        status_table.add_row(
            "MCP Server",
            "[green]OK[/]" if mcp_server.exists() else "[red]Missing[/]",
            str(mcp_server)
        )

        # Docker (for Strix)
        try:
            result = subprocess.run(["docker", "--version"], capture_output=True, text=True, timeout=5)
            docker_version = result.stdout.strip().split(",")[0] if result.returncode == 0 else "Error"
            status_table.add_row(
                "Docker",
                "[green]OK[/]" if result.returncode == 0 else "[red]Error[/]",
                docker_version
            )
        except FileNotFoundError:
            status_table.add_row("Docker", "[yellow]Missing[/]", "Optional - needed for Strix")
        except Exception:
            status_table.add_row("Docker", "[yellow]Unknown[/]", "")

        # Ollama
        try:
            result = subprocess.run(["ollama", "--version"], capture_output=True, text=True, timeout=5)
            status_table.add_row(
                "Ollama",
                "[green]OK[/]" if result.returncode == 0 else "[yellow]Not Running[/]",
                result.stdout.strip() if result.returncode == 0 else "ollama serve"
            )
        except FileNotFoundError:
            status_table.add_row("Ollama", "[yellow]Missing[/]", "Optional - for local AI")
        except Exception:
            status_table.add_row("Ollama", "[yellow]Unknown[/]", "")

        self.console.print(status_table)
        self.console.print()

        # Environment variables
        env_table = Table(title="Environment Variables", show_header=True, header_style="bold")
        env_table.add_column("Variable", style="cyan")
        env_table.add_column("Status", style="white")

        env_vars = ["ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GROQ_API_KEY", "STRIX_LLM", "ALFRED_HOME"]
        for var in env_vars:
            value = os.environ.get(var)
            if value:
                masked = value[:8] + "..." if len(value) > 10 else "[set]"
                env_table.add_row(var, f"[green]{masked}[/]")
            else:
                env_table.add_row(var, "[dim]Not set[/]")

        self.console.print(env_table)

    def run_quick_scan(self):
        """Run a quick security scan"""
        target = Prompt.ask("[cyan]Enter target URL or domain[/]")
        if not target:
            self.console.print("[red]No target specified[/]")
            return

        self.console.print(f"\n[yellow]Running quick scan on {target}...[/]\n")

        # Try Strix first
        try:
            subprocess.run(
                ["strix", "-n", "--target", target],
                cwd=str(ALFRED_II_PATH)
            )
        except FileNotFoundError:
            # Fallback to bug bounty hunter
            self.console.print("[yellow]Strix not found, using Bug Bounty Hunter...[/]")
            subprocess.run(
                ["python", "tools/bug_bounty_hunter.py", target],
                cwd=str(ALFRED_Y_PATH)
            )

    def run_full_recon(self):
        """Run full reconnaissance on a target"""
        target = Prompt.ask("[cyan]Enter target URL or domain[/]")
        if not target:
            self.console.print("[red]No target specified[/]")
            return

        self.console.print(f"\n[yellow]Running full reconnaissance on {target}...[/]\n")

        subprocess.run(
            ["python", "tools/bug_bounty_hunter.py", target, "--full"],
            cwd=str(ALFRED_Y_PATH)
        )

    def launch_tool(self, tool_key: str):
        """Launch a specific tool"""
        if tool_key not in self.tools:
            self.console.print(f"[red]Unknown tool: {tool_key}[/]")
            return

        tool = self.tools[tool_key]

        # Handle special actions
        if "action" in tool:
            if tool["action"] == "status":
                self.check_all_status()
            elif tool["action"] == "quick_scan":
                self.run_quick_scan()
            elif tool["action"] == "full_recon":
                self.run_full_recon()
            return

        # Check if tool exists
        if tool.get("path") and not tool["path"].exists():
            self.console.print(f"[red]Tool not found: {tool['path']}[/]")
            return

        # Get target if required
        target = None
        if tool.get("requires_target"):
            target = Prompt.ask(f"[cyan]Enter target for {tool['name']}[/]")
            if not target:
                self.console.print("[red]No target specified[/]")
                return

        # Build command
        cmd = tool["command"].copy()
        if target:
            cmd.append(target)
            if tool["name"] == "Bug Bounty Hunter":
                if Confirm.ask("Run full scan?", default=False):
                    cmd.append("--full")

        self.console.print(f"\n[green]Launching {tool['name']}...[/]\n")

        try:
            if tool.get("background"):
                # Run in background
                process = subprocess.Popen(
                    cmd,
                    cwd=str(tool["cwd"]),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                self.running_processes[tool["name"]] = process
                self.console.print(f"[green]{tool['name']} started in background (PID: {process.pid})[/]")
            elif tool.get("interactive"):
                # Run interactively
                subprocess.run(cmd, cwd=str(tool["cwd"]))
            else:
                # Run and wait
                subprocess.run(cmd, cwd=str(tool["cwd"]))
        except FileNotFoundError as e:
            self.console.print(f"[red]Command not found: {e}[/]")
        except Exception as e:
            self.console.print(f"[red]Error launching tool: {e}[/]")

    def run(self):
        """Main launcher loop"""
        self.display_banner()

        while True:
            self.console.print()
            self.display_menu()
            self.console.print()

            choice = Prompt.ask("[bold cyan]Select tool[/]", default="q")

            if choice.lower() == "q":
                # Clean up background processes
                for name, proc in self.running_processes.items():
                    if proc.poll() is None:
                        self.console.print(f"[yellow]Stopping {name}...[/]")
                        proc.terminate()
                self.console.print("[cyan]Goodbye, sir.[/]")
                break
            elif choice.lower() == "s":
                self.check_all_status()
            elif choice in self.tools:
                self.launch_tool(choice)
            else:
                self.console.print("[red]Invalid selection[/]")


def main():
    """Entry point"""
    launcher = AlfredLauncher()
    try:
        launcher.run()
    except KeyboardInterrupt:
        console.print("\n[cyan]Interrupted. Goodbye, sir.[/]")


if __name__ == "__main__":
    main()
