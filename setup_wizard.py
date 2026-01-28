#!/usr/bin/env python3
"""
ALFRED_IV-Y-VI Setup Wizard
A graphical interface for configuring ALFRED without using the terminal.

Author: Daniel J. Rita aka BATDAN007
https://github.com/Batdan007/ALFRED_IV-Y-VI

Usage:
    python setup_wizard.py
    
    Or double-click on Windows/macOS
"""

import os
import sys
import json
import subprocess
import webbrowser
from pathlib import Path
from typing import Optional, Dict

# Check if tkinter is available
try:
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False


class SetupWizard:
    """GUI Setup Wizard for ALFRED_IV-Y-VI."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ALFRED_IV-Y-VI Setup Wizard")
        self.root.geometry("600x700")
        self.root.resizable(True, True)
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.root.winfo_screenheight() // 2) - (700 // 2)
        self.root.geometry(f"+{x}+{y}")
        
        # Configuration
        self.config_file = Path("config.json")
        self.env_file = Path(".env")
        self.config = self._load_config()
        
        # Variables
        self.api_keys = {
            "anthropic": tk.StringVar(value=self.config.get("anthropic_key", "")),
            "openai": tk.StringVar(value=self.config.get("openai_key", "")),
            "groq": tk.StringVar(value=self.config.get("groq_key", "")),
        }
        self.default_provider = tk.StringVar(value=self.config.get("default_provider", "anthropic"))
        self.memory_enabled = tk.BooleanVar(value=self.config.get("memory_enabled", True))
        self.voice_enabled = tk.BooleanVar(value=self.config.get("voice_enabled", True))
        self.server_port = tk.StringVar(value=str(self.config.get("port", "8000")))
        
        # Build UI
        self._create_ui()
    
    def _load_config(self) -> Dict:
        """Load existing configuration."""
        config = {}
        
        # Try loading from config.json
        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    data = json.load(f)
                    if "api_keys" in data:
                        config["anthropic_key"] = data["api_keys"].get("anthropic", "")
                        config["openai_key"] = data["api_keys"].get("openai", "")
                        config["groq_key"] = data["api_keys"].get("groq", "")
                    if "model" in data:
                        config["default_provider"] = data["model"].get("default_provider", "anthropic")
                    if "memory" in data:
                        config["memory_enabled"] = data["memory"].get("enabled", True)
                    if "voice" in data:
                        config["voice_enabled"] = data["voice"].get("enabled", True)
                    if "server" in data:
                        config["port"] = data["server"].get("port", 8000)
            except (json.JSONDecodeError, IOError):
                pass
        
        # Try loading from .env
        if self.env_file.exists():
            try:
                with open(self.env_file, "r") as f:
                    for line in f:
                        line = line.strip()
                        if "=" in line and not line.startswith("#"):
                            key, value = line.split("=", 1)
                            key = key.strip()
                            value = value.strip()
                            
                            if key == "ANTHROPIC_API_KEY":
                                config["anthropic_key"] = value
                            elif key == "OPENAI_API_KEY":
                                config["openai_key"] = value
                            elif key == "GROQ_API_KEY":
                                config["groq_key"] = value
                            elif key == "DEFAULT_PROVIDER":
                                config["default_provider"] = value
                            elif key == "PORT":
                                config["port"] = int(value)
            except IOError:
                pass
        
        return config
    
    def _create_ui(self):
        """Create the user interface."""
        # Main container with scrollbar
        canvas = tk.Canvas(self.root)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Header
        header_frame = ttk.Frame(scrollable_frame)
        header_frame.pack(fill="x", padx=20, pady=20)
        
        title_label = ttk.Label(
            header_frame,
            text="🤖 ALFRED_IV-Y-VI Setup",
            font=("Helvetica", 24, "bold")
        )
        title_label.pack()
        
        subtitle_label = ttk.Label(
            header_frame,
            text="AI Assistant with Persistent Memory & Adaptive Learning",
            font=("Helvetica", 10)
        )
        subtitle_label.pack(pady=(5, 0))
        
        # Separator
        ttk.Separator(scrollable_frame, orient="horizontal").pack(fill="x", padx=20, pady=10)
        
        # API Keys Section
        self._create_api_keys_section(scrollable_frame)
        
        # Separator
        ttk.Separator(scrollable_frame, orient="horizontal").pack(fill="x", padx=20, pady=10)
        
        # Settings Section
        self._create_settings_section(scrollable_frame)
        
        # Separator
        ttk.Separator(scrollable_frame, orient="horizontal").pack(fill="x", padx=20, pady=10)
        
        # Buttons Section
        self._create_buttons_section(scrollable_frame)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(
            scrollable_frame,
            textvariable=self.status_var,
            relief="sunken",
            anchor="w"
        )
        status_bar.pack(fill="x", side="bottom", padx=20, pady=10)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def _create_api_keys_section(self, parent):
        """Create API keys configuration section."""
        frame = ttk.LabelFrame(parent, text="🔑 API Keys", padding=10)
        frame.pack(fill="x", padx=20, pady=10)
        
        # Instructions
        info_label = ttk.Label(
            frame,
            text="Enter at least one API key to use ALFRED.\nClick the links to get your API keys.",
            wraplength=500
        )
        info_label.pack(anchor="w", pady=(0, 10))
        
        # Anthropic
        anthropic_frame = ttk.Frame(frame)
        anthropic_frame.pack(fill="x", pady=5)
        
        ttk.Label(anthropic_frame, text="Anthropic (Claude):", width=18).pack(side="left")
        anthropic_entry = ttk.Entry(
            anthropic_frame,
            textvariable=self.api_keys["anthropic"],
            width=40,
            show="•"
        )
        anthropic_entry.pack(side="left", padx=5)
        
        anthropic_show = ttk.Button(
            anthropic_frame,
            text="👁",
            width=3,
            command=lambda: self._toggle_visibility(anthropic_entry)
        )
        anthropic_show.pack(side="left")
        
        anthropic_link = ttk.Label(
            anthropic_frame,
            text="Get Key",
            foreground="blue",
            cursor="hand2"
        )
        anthropic_link.pack(side="left", padx=10)
        anthropic_link.bind("<Button-1>", lambda e: webbrowser.open("https://console.anthropic.com/"))
        
        # OpenAI
        openai_frame = ttk.Frame(frame)
        openai_frame.pack(fill="x", pady=5)
        
        ttk.Label(openai_frame, text="OpenAI (GPT):", width=18).pack(side="left")
        openai_entry = ttk.Entry(
            openai_frame,
            textvariable=self.api_keys["openai"],
            width=40,
            show="•"
        )
        openai_entry.pack(side="left", padx=5)
        
        openai_show = ttk.Button(
            openai_frame,
            text="👁",
            width=3,
            command=lambda: self._toggle_visibility(openai_entry)
        )
        openai_show.pack(side="left")
        
        openai_link = ttk.Label(
            openai_frame,
            text="Get Key",
            foreground="blue",
            cursor="hand2"
        )
        openai_link.pack(side="left", padx=10)
        openai_link.bind("<Button-1>", lambda e: webbrowser.open("https://platform.openai.com/api-keys"))
        
        # Groq
        groq_frame = ttk.Frame(frame)
        groq_frame.pack(fill="x", pady=5)
        
        ttk.Label(groq_frame, text="Groq:", width=18).pack(side="left")
        groq_entry = ttk.Entry(
            groq_frame,
            textvariable=self.api_keys["groq"],
            width=40,
            show="•"
        )
        groq_entry.pack(side="left", padx=5)
        
        groq_show = ttk.Button(
            groq_frame,
            text="👁",
            width=3,
            command=lambda: self._toggle_visibility(groq_entry)
        )
        groq_show.pack(side="left")
        
        groq_link = ttk.Label(
            groq_frame,
            text="Get Key",
            foreground="blue",
            cursor="hand2"
        )
        groq_link.pack(side="left", padx=10)
        groq_link.bind("<Button-1>", lambda e: webbrowser.open("https://console.groq.com/keys"))
        
        # Default provider
        provider_frame = ttk.Frame(frame)
        provider_frame.pack(fill="x", pady=(15, 5))
        
        ttk.Label(provider_frame, text="Default Provider:", width=18).pack(side="left")
        provider_combo = ttk.Combobox(
            provider_frame,
            textvariable=self.default_provider,
            values=["anthropic", "openai", "groq"],
            state="readonly",
            width=15
        )
        provider_combo.pack(side="left", padx=5)
    
    def _create_settings_section(self, parent):
        """Create settings configuration section."""
        frame = ttk.LabelFrame(parent, text="⚙️ Settings", padding=10)
        frame.pack(fill="x", padx=20, pady=10)
        
        # Memory
        memory_check = ttk.Checkbutton(
            frame,
            text="Enable Persistent Memory (remembers conversations)",
            variable=self.memory_enabled
        )
        memory_check.pack(anchor="w", pady=2)
        
        # Voice
        voice_check = ttk.Checkbutton(
            frame,
            text="Enable Voice Output (text-to-speech)",
            variable=self.voice_enabled
        )
        voice_check.pack(anchor="w", pady=2)
        
        # Server port
        port_frame = ttk.Frame(frame)
        port_frame.pack(fill="x", pady=(10, 5))
        
        ttk.Label(port_frame, text="Server Port:").pack(side="left")
        port_entry = ttk.Entry(port_frame, textvariable=self.server_port, width=10)
        port_entry.pack(side="left", padx=10)
        ttk.Label(port_frame, text="(default: 8000)", foreground="gray").pack(side="left")
    
    def _create_buttons_section(self, parent):
        """Create buttons section."""
        frame = ttk.Frame(parent)
        frame.pack(fill="x", padx=20, pady=20)
        
        # Save button
        save_btn = ttk.Button(
            frame,
            text="💾 Save Configuration",
            command=self._save_config
        )
        save_btn.pack(side="left", padx=5)
        
        # Install button
        install_btn = ttk.Button(
            frame,
            text="📦 Install Dependencies",
            command=self._install_dependencies
        )
        install_btn.pack(side="left", padx=5)
        
        # Run button
        run_btn = ttk.Button(
            frame,
            text="▶️ Run ALFRED",
            command=self._run_alfred
        )
        run_btn.pack(side="left", padx=5)
        
        # Help button
        help_btn = ttk.Button(
            frame,
            text="❓ Help",
            command=self._show_help
        )
        help_btn.pack(side="right", padx=5)
    
    def _toggle_visibility(self, entry):
        """Toggle password visibility."""
        current = entry.cget("show")
        entry.configure(show="" if current else "•")
    
    def _save_config(self):
        """Save configuration to files."""
        try:
            # Validate port
            try:
                port = int(self.server_port.get())
                if port < 1 or port > 65535:
                    raise ValueError()
            except ValueError:
                messagebox.showerror("Error", "Invalid port number. Must be 1-65535.")
                return
            
            # Check if at least one API key is provided
            has_key = any(
                key.get() and not key.get().startswith("your_")
                for key in self.api_keys.values()
            )
            
            if not has_key:
                result = messagebox.askyesno(
                    "Warning",
                    "No API keys entered. ALFRED will not work without at least one API key.\n\nSave anyway?"
                )
                if not result:
                    return
            
            # Save to config.json
            config_data = {
                "api_keys": {
                    "anthropic": self.api_keys["anthropic"].get(),
                    "openai": self.api_keys["openai"].get(),
                    "groq": self.api_keys["groq"].get(),
                },
                "model": {
                    "default_provider": self.default_provider.get(),
                    "anthropic_model": "claude-sonnet-4-20250514",
                    "openai_model": "gpt-4o",
                    "groq_model": "llama-3.3-70b-versatile",
                },
                "memory": {
                    "enabled": self.memory_enabled.get(),
                    "path": "./memory",
                },
                "voice": {
                    "enabled": self.voice_enabled.get(),
                },
                "server": {
                    "host": "127.0.0.1",
                    "port": port,
                },
            }
            
            with open(self.config_file, "w") as f:
                json.dump(config_data, f, indent=2)
            
            # Save to .env
            env_content = f"""# ALFRED_IV-Y-VI Configuration
# Generated by Setup Wizard

# AI Provider API Keys
ANTHROPIC_API_KEY={self.api_keys["anthropic"].get()}
OPENAI_API_KEY={self.api_keys["openai"].get()}
GROQ_API_KEY={self.api_keys["groq"].get()}

# Default Provider
DEFAULT_PROVIDER={self.default_provider.get()}

# Memory Settings
MEMORY_ENABLED={str(self.memory_enabled.get()).lower()}
MEMORY_PATH=./memory

# Voice Settings
VOICE_ENABLED={str(self.voice_enabled.get()).lower()}

# Server Settings
HOST=127.0.0.1
PORT={port}
"""
            
            with open(self.env_file, "w") as f:
                f.write(env_content)
            
            self.status_var.set("Configuration saved successfully!")
            messagebox.showinfo("Success", "Configuration saved!\n\nFiles created:\n• config.json\n• .env")
            
        except Exception as e:
            self.status_var.set(f"Error: {e}")
            messagebox.showerror("Error", f"Failed to save configuration:\n{e}")
    
    def _install_dependencies(self):
        """Install Python dependencies."""
        self.status_var.set("Installing dependencies...")
        self.root.update()
        
        try:
            # Check if requirements.txt exists
            req_file = Path("requirements.txt")
            if not req_file.exists():
                messagebox.showerror(
                    "Error",
                    "requirements.txt not found!\n\nPlease ensure you're running this from the ALFRED_IV-Y-VI directory."
                )
                return
            
            # Run pip install
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.status_var.set("Dependencies installed successfully!")
                messagebox.showinfo("Success", "Dependencies installed successfully!")
            else:
                self.status_var.set("Installation failed")
                messagebox.showerror("Error", f"Installation failed:\n{result.stderr[:500]}")
                
        except Exception as e:
            self.status_var.set(f"Error: {e}")
            messagebox.showerror("Error", f"Failed to install dependencies:\n{e}")
    
    def _run_alfred(self):
        """Run ALFRED."""
        # Check for API keys
        has_key = any(
            key.get() and not key.get().startswith("your_")
            for key in self.api_keys.values()
        )
        
        if not has_key:
            messagebox.showerror(
                "Error",
                "No API keys configured!\n\nPlease enter at least one API key and save the configuration."
            )
            return
        
        # Check if main.py exists
        main_file = Path("main.py")
        if not main_file.exists():
            messagebox.showerror(
                "Error",
                "main.py not found!\n\nPlease ensure all ALFRED files are in place."
            )
            return
        
        # Save config first
        self._save_config()
        
        self.status_var.set("Starting ALFRED...")
        self.root.update()
        
        try:
            # Start ALFRED in a new process
            if sys.platform == "win32":
                subprocess.Popen(
                    [sys.executable, "main.py"],
                    creationflags=subprocess.CREATE_NEW_CONSOLE
                )
            else:
                subprocess.Popen(
                    [sys.executable, "main.py"],
                    start_new_session=True
                )
            
            self.status_var.set("ALFRED started!")
            messagebox.showinfo(
                "ALFRED Started",
                f"ALFRED is now running!\n\nWeb interface: http://127.0.0.1:{self.server_port.get()}"
            )
            
        except Exception as e:
            self.status_var.set(f"Error: {e}")
            messagebox.showerror("Error", f"Failed to start ALFRED:\n{e}")
    
    def _show_help(self):
        """Show help information."""
        help_text = """ALFRED_IV-Y-VI Setup Wizard Help

🔑 API KEYS
You need at least one API key to use ALFRED:
• Anthropic: Best for Claude models
• OpenAI: For GPT models  
• Groq: Free tier available

Click "Get Key" links to sign up and get your keys.

⚙️ SETTINGS
• Persistent Memory: Saves conversation history
• Voice Output: Text-to-speech responses
• Server Port: Web interface port (default 8000)

💾 SAVE CONFIGURATION
Saves your settings to config.json and .env files.

📦 INSTALL DEPENDENCIES
Installs required Python packages.

▶️ RUN ALFRED
Starts the ALFRED AI assistant.

Need more help?
https://github.com/Batdan007/ALFRED_IV-Y-VI
"""
        
        help_window = tk.Toplevel(self.root)
        help_window.title("Help")
        help_window.geometry("500x500")
        
        text = tk.Text(help_window, wrap="word", padx=10, pady=10)
        text.insert("1.0", help_text)
        text.configure(state="disabled")
        text.pack(fill="both", expand=True)
        
        close_btn = ttk.Button(
            help_window,
            text="Close",
            command=help_window.destroy
        )
        close_btn.pack(pady=10)
    
    def run(self):
        """Run the setup wizard."""
        self.root.mainloop()


def run_cli_setup():
    """Fallback CLI setup if tkinter is not available."""
    print("\n" + "=" * 60)
    print("  ALFRED_IV-Y-VI Setup (Command Line)")
    print("=" * 60)
    print("\ntkinter not available. Using command line setup.\n")
    
    config = {}
    
    print("Enter your API keys (press Enter to skip):\n")
    
    config["anthropic"] = input("Anthropic API Key: ").strip()
    config["openai"] = input("OpenAI API Key: ").strip()
    config["groq"] = input("Groq API Key: ").strip()
    
    print("\nSelect default provider:")
    print("  1. Anthropic (Claude)")
    print("  2. OpenAI (GPT)")
    print("  3. Groq")
    
    choice = input("\nChoice [1]: ").strip() or "1"
    providers = {"1": "anthropic", "2": "openai", "3": "groq"}
    config["provider"] = providers.get(choice, "anthropic")
    
    # Save configuration
    env_content = f"""# ALFRED_IV-Y-VI Configuration
ANTHROPIC_API_KEY={config.get('anthropic', '')}
OPENAI_API_KEY={config.get('openai', '')}
GROQ_API_KEY={config.get('groq', '')}
DEFAULT_PROVIDER={config['provider']}
MEMORY_ENABLED=true
HOST=127.0.0.1
PORT=8000
"""
    
    with open(".env", "w") as f:
        f.write(env_content)
    
    print("\n✅ Configuration saved to .env")
    print("\nNext steps:")
    print("  1. Install dependencies: pip install -r requirements.txt")
    print("  2. Run ALFRED: python main.py")


def main():
    """Main entry point."""
    if TKINTER_AVAILABLE:
        wizard = SetupWizard()
        wizard.run()
    else:
        run_cli_setup()


if __name__ == "__main__":
    main()
