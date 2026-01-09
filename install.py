#!/usr/bin/env python3
"""
ALFRED II-Y-II Universal Installer
===================================
One command to install EVERYTHING - all dependencies, voice, the works.

Usage:
    python install.py              # Full install
    python install.py --quick      # Skip optional heavy components
    python install.py --no-voice   # Skip voice system
    python install.py --minimal    # Bare minimum only

After install, just type: alfred

Author: Daniel J. Rita (BATDAN)
Patent-pending technology - GxEum Technologies / CAMDAN Enterprizes

IMPORTANT: Requires Python 3.11 or 3.12 (NOT 3.13/3.14)
Many packages don't have pre-built wheels for Python 3.13+
"""

import os
import sys
import subprocess
import platform
import shutil
import argparse
from pathlib import Path
from typing import Optional, List, Tuple

# Python version requirements
MIN_PYTHON = (3, 10)
MAX_PYTHON = (3, 12)  # 3.13+ has compatibility issues
RECOMMENDED_PYTHON = "3.11"
WHISPER_MODEL = "base.en"  # ~150MB for voice

# Core dependencies (always installed)
CORE_PACKAGES = [
    "anthropic",
    "openai",
    "groq",
    "google-generativeai",
    "rich",
    "prompt-toolkit",
    "typer",
    "pydantic",
    "pydantic-settings",
    "python-dotenv",
    "aiohttp",
    "httpx",
    "requests",
]

# Voice packages
VOICE_PACKAGES = [
    "faster-whisper",
    "edge-tts",
    "sounddevice",
    "numpy",
    "SpeechRecognition",
]

# Optional heavy packages (can fail gracefully)
OPTIONAL_PACKAGES = [
    "chromadb",
    "sentence-transformers",
    "opencv-python",
    "pillow",
    "beautifulsoup4",
    "pyttsx3",
]

# Minimal packages (for resource-constrained environments)
MINIMAL_PACKAGES = [
    "anthropic",
    "rich",
    "python-dotenv",
    "pydantic",
    "httpx",
    "requests",
]


class Colors:
    """ANSI color codes for terminal output."""
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    CYAN = "\033[0;36m"
    WHITE = "\033[1;37m"
    GRAY = "\033[0;90m"
    NC = "\033[0m"  # No Color
    
    @classmethod
    def disable(cls):
        """Disable colors for non-TTY output."""
        cls.RED = cls.GREEN = cls.YELLOW = cls.CYAN = ""
        cls.WHITE = cls.GRAY = cls.NC = ""


class Installer:
    """Cross-platform installer for ALFRED II-Y-II."""

    def __init__(self, skip_venv: bool = False, force: bool = False,
                 minimal: bool = False, no_voice: bool = False, quick: bool = False):
        self.skip_venv = skip_venv
        self.force = force
        self.minimal = minimal
        self.no_voice = no_voice
        self.quick = quick
        self.venv_dir = Path("venv")
        self.install_dir = Path.cwd()
        self.os_type = self._detect_os()
        self.python_cmd = sys.executable

        # Disable colors if not a TTY
        if not sys.stdout.isatty():
            Colors.disable()
    
    def _detect_os(self) -> str:
        """Detect the operating system."""
        system = platform.system().lower()
        
        if system == "darwin":
            return "macos"
        elif system == "linux":
            # Check for WSL
            try:
                with open("/proc/version", "r") as f:
                    if "microsoft" in f.read().lower():
                        return "wsl"
            except FileNotFoundError:
                pass
            return "linux"
        elif system == "windows":
            return "windows"
        elif system == "ios" or "iphone" in platform.platform().lower():
            return "ios"
        else:
            return "unknown"
    
    def info(self, msg: str):
        """Print info message."""
        print(f"{Colors.CYAN}[INFO]{Colors.NC} {msg}")
    
    def success(self, msg: str):
        """Print success message."""
        print(f"{Colors.GREEN}[OK]{Colors.NC} {msg}")
    
    def warn(self, msg: str):
        """Print warning message."""
        print(f"{Colors.YELLOW}[WARN]{Colors.NC} {msg}")
    
    def error(self, msg: str):
        """Print error message."""
        print(f"{Colors.RED}[ERROR]{Colors.NC} {msg}")
    
    def show_banner(self):
        """Display the installation banner."""
        banner = f"""
{Colors.CYAN}    _    _     _____ ____  _____ ____    _  _ ______  __{Colors.NC}
{Colors.CYAN}   / \\  | |   |  ___|  _ \\| ____|  _ \\  | | | | __ ) \\/ /{Colors.NC}
{Colors.CYAN}  / _ \\ | |   | |_  | |_) |  _| | | | | | | | |  _ \\\\  / {Colors.NC}
{Colors.CYAN} / ___ \\| |___|  _| |  _ <| |___| |_| | | |_| | |_) /  \\ {Colors.NC}
{Colors.CYAN}/_/   \\_\\_____|_|   |_| \\_\\_____|____/   \\___/|____/_/\\_\\{Colors.NC}

{Colors.WHITE}  AI Assistant with Persistent Memory & Adaptive Learning{Colors.NC}
{Colors.GRAY}  https://github.com/Batdan007/ALFRED_UBX{Colors.NC}
"""
        print(banner)
    
    def check_python_version(self) -> bool:
        """Check if Python version meets requirements."""
        self.info("Checking Python version...")

        version = sys.version_info
        version_str = f"{version.major}.{version.minor}.{version.micro}"

        if version < MIN_PYTHON:
            self.error(f"Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]}+ required, found {version_str}")
            return False

        if version > MAX_PYTHON:
            self.warn(f"Python {version_str} detected - may have compatibility issues")
            self.warn(f"Recommended: Python {RECOMMENDED_PYTHON}")
            self.info("  Some packages (faster-whisper) don't have wheels for Python 3.13+")
            self.info(f"  Consider using: py -{RECOMMENDED_PYTHON} install.py")
            # Continue anyway, but warn
            self.success(f"Python {version_str} (may have issues)")
            return True

        self.success(f"Python {version_str}")
        return True
    
    def check_git(self) -> bool:
        """Check if Git is installed."""
        self.info("Checking Git installation...")
        
        try:
            result = subprocess.run(
                ["git", "--version"],
                capture_output=True,
                text=True,
                check=True
            )
            self.success(result.stdout.strip())
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.warn("Git not found. Some features may be limited.")
            return False
    
    def create_venv(self) -> bool:
        """Create virtual environment."""
        if self.skip_venv:
            self.warn("Skipping virtual environment creation (--skip-venv)")
            return True
        
        # iOS doesn't support venv
        if self.os_type == "ios":
            self.warn("Virtual environments not supported on iOS, skipping")
            self.skip_venv = True
            return True
        
        self.info("Creating virtual environment...")
        
        if self.venv_dir.exists():
            if self.force:
                self.warn("Removing existing virtual environment...")
                shutil.rmtree(self.venv_dir)
            else:
                self.success("Virtual environment already exists")
                return True
        
        try:
            subprocess.run(
                [self.python_cmd, "-m", "venv", str(self.venv_dir)],
                check=True
            )
            self.success(f"Virtual environment created at {self.venv_dir}")
            return True
        except subprocess.CalledProcessError as e:
            self.error(f"Failed to create virtual environment: {e}")
            return False
    
    def get_pip_command(self) -> str:
        """Get the appropriate pip command."""
        if self.skip_venv:
            return sys.executable + " -m pip"
        
        if self.os_type == "windows":
            pip_path = self.venv_dir / "Scripts" / "pip.exe"
        else:
            pip_path = self.venv_dir / "bin" / "pip"
        
        if pip_path.exists():
            return str(pip_path)
        return sys.executable + " -m pip"
    
    def get_python_command(self) -> str:
        """Get the appropriate python command for the venv."""
        if self.skip_venv:
            return sys.executable
        
        if self.os_type == "windows":
            python_path = self.venv_dir / "Scripts" / "python.exe"
        else:
            python_path = self.venv_dir / "bin" / "python"
        
        if python_path.exists():
            return str(python_path)
        return sys.executable
    
    def run_pip(self, args: List[str], quiet: bool = True) -> bool:
        """Run pip with the given arguments."""
        pip_cmd = self.get_pip_command()
        cmd = pip_cmd.split() + args
        
        if quiet:
            cmd.append("--quiet")
        
        try:
            subprocess.run(cmd, check=True, capture_output=quiet)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def install_dependencies(self) -> bool:
        """Install Python dependencies from requirements.txt."""
        self.info("Installing dependencies...")

        # Upgrade pip first
        self.info("Upgrading pip...")
        self.run_pip(["install", "--upgrade", "pip"])
        self.success("pip upgraded")

        # Install from requirements.txt (the single source of truth)
        requirements_file = self.install_dir / "requirements.txt"
        if requirements_file.exists():
            self.info("Installing from requirements.txt...")
            if self.run_pip(["install", "-r", str(requirements_file)], quiet=False):
                self.success("All dependencies installed from requirements.txt")
            else:
                self.warn("Some dependencies may have failed")
                self.info("  This is often due to Python version compatibility")
                self.info(f"  Try: py -{RECOMMENDED_PYTHON} -m pip install -r requirements.txt")
        else:
            # Fallback to individual packages if no requirements.txt
            packages = MINIMAL_PACKAGES if self.minimal else CORE_PACKAGES

            self.info(f"Installing {'minimal' if self.minimal else 'core'} dependencies...")
            for package in packages:
                self.info(f"  Installing {package}...")
                if not self.run_pip(["install", package]):
                    self.warn(f"  Could not install {package}")

            # Install voice packages (unless --no-voice or minimal)
            if not self.minimal and not self.no_voice and self.os_type != "ios":
                self.info("Installing voice system...")
                for package in VOICE_PACKAGES:
                    self.info(f"  Installing {package}...")
                    if not self.run_pip(["install", package]):
                        self.warn(f"  Could not install {package} (voice may not work)")

        # Platform-specific dependencies
        if self.os_type == "macos":
            self.info("Installing macOS-specific dependencies...")
            self.run_pip(["install", "pyobjc-framework-Cocoa"])

        self.success("Dependencies installed")
        return True

    def install_ffmpeg(self) -> bool:
        """Install/check ffmpeg for voice."""
        if self.no_voice:
            return True

        self.info("Checking ffmpeg (required for voice)...")

        if shutil.which("ffmpeg"):
            self.success("ffmpeg already installed")
            return True

        if self.os_type != "windows":
            self.warn("ffmpeg not found - install manually:")
            self.info("  Ubuntu: sudo apt install ffmpeg")
            self.info("  macOS: brew install ffmpeg")
            return True

        # Windows: try winget
        self.info("Installing ffmpeg via winget...")
        try:
            subprocess.run(
                ["winget", "install", "-e", "--id", "Gyan.FFmpeg", "-h", "--accept-source-agreements"],
                capture_output=True, timeout=120
            )
            self.success("ffmpeg installed (restart terminal for PATH)")
            return True
        except Exception:
            self.warn("ffmpeg install failed - download from ffmpeg.org")
            return True

    def download_whisper_model(self) -> bool:
        """Download Whisper model for offline speech recognition."""
        if self.no_voice or self.quick or self.minimal:
            return True

        self.info(f"Downloading Whisper model ({WHISPER_MODEL})...")

        try:
            from faster_whisper import WhisperModel  # pyright: ignore[reportMissingImports]

            self.info("  Downloading ~150MB model (this may take a minute)...")

            # Try GPU first
            try:
                model = WhisperModel(WHISPER_MODEL, device="cuda", compute_type="float16")
                device = "GPU"
            except Exception:
                model = WhisperModel(WHISPER_MODEL, device="cpu", compute_type="float32")
                device = "CPU"

            del model
            self.success(f"Whisper model ready ({device})")
            return True

        except ImportError:
            self.warn("faster-whisper not installed, skipping model")
            return True
        except Exception as e:
            self.warn(f"Model download failed: {e}")
            self.info("  Model will download on first use")
            return True

    def check_ollama(self) -> bool:
        """Check Ollama connection."""
        self.info("Checking Ollama (local AI)...")

        try:
            import requests  # type: ignore
            r = requests.get("http://localhost:11434/api/tags", timeout=3)
            if r.status_code == 200:
                models = r.json().get('models', [])
                if models:
                    names = [m['name'].split(':')[0] for m in models[:3]]
                    self.success(f"Ollama running: {', '.join(names)}")
                else:
                    self.success("Ollama running (no models)")
                    self.info("  Pull a model: ollama pull llama3.2")
                return True
        except Exception:
            pass

        self.warn("Ollama not running")
        self.info("  Start with: ollama serve")
        self.info("  Download: https://ollama.com")
        return True

    def install_package(self) -> bool:
        """Install ALFRED package in editable mode."""
        self.info("Installing ALFRED package...")

        try:
            result = subprocess.run(
                [self.get_python_command(), "-m", "pip", "install", "-e", "."],
                capture_output=True, text=True, timeout=120
            )
            if result.returncode == 0:
                self.success("alfred command registered")
                return True
            else:
                self.warn(f"Package install issue: {result.stderr[:100]}")
                return True  # Non-fatal
        except Exception as e:
            self.warn(f"Package install error: {e}")
            return True
    
    def create_env_file(self):
        """Create .env configuration file."""
        self.info("Setting up environment configuration...")
        
        env_file = self.install_dir / ".env"
        env_example = self.install_dir / ".env.example"
        
        if env_file.exists():
            self.success(".env file already exists")
            return
        
        if env_example.exists():
            shutil.copy(env_example, env_file)
            self.success("Created .env from .env.example")
            return
        
        env_content = """# ALFRED_UBX Configuration
# Fill in your API keys below

# AI Provider API Keys (at least one required)
ANTHROPIC_API_KEY=your_anthropic_key_here
OPENAI_API_KEY=your_openai_key_here
GROQ_API_KEY=your_groq_key_here

# Optional: Default AI Provider (anthropic, openai, groq)
DEFAULT_PROVIDER=anthropic

# Optional: Model Settings
DEFAULT_MODEL=claude-sonnet-4-20250514

# Optional: Memory Settings
MEMORY_ENABLED=true
MEMORY_PATH=./memory

# Optional: Server Settings
HOST=127.0.0.1
PORT=8000
"""
        
        with open(env_file, "w") as f:
            f.write(env_content)
        self.success("Created .env template")
    
    def create_launcher(self):
        """Create platform-specific launcher scripts."""
        self.info("Creating launcher scripts...")
        
        if self.os_type == "windows":
            # Windows batch file
            batch_content = """@echo off
cd /d "%~dp0"
if exist "venv\\Scripts\\activate.bat" (
    call venv\\Scripts\\activate.bat
)
python main.py %*
"""
            with open("alfred.bat", "w") as f:
                f.write(batch_content)
            self.success("Created alfred.bat")
            
            # PowerShell script
            ps_content = """$ErrorActionPreference = "Stop"
Push-Location $PSScriptRoot
try {
    if (Test-Path "venv\\Scripts\\Activate.ps1") {
        . .\\venv\\Scripts\\Activate.ps1
    }
    python main.py @args
} finally {
    Pop-Location
}
"""
            with open("alfred.ps1", "w") as f:
                f.write(ps_content)
            self.success("Created alfred.ps1")
        
        elif self.os_type in ("linux", "macos", "wsl"):
            # Unix shell script
            bash_content = """#!/usr/bin/env bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [[ -f "venv/bin/activate" ]]; then
    source venv/bin/activate
fi

python main.py "$@"
"""
            launcher_path = Path("alfred")
            with open(launcher_path, "w") as f:
                f.write(bash_content)
            launcher_path.chmod(0o755)
            self.success("Created ./alfred launcher")
    
    def show_instructions(self):
        """Display post-installation instructions."""
        print(f"""
{Colors.GREEN}================================================================{Colors.NC}
{Colors.GREEN} Installation Complete!{Colors.NC}
{Colors.GREEN}================================================================{Colors.NC}

{Colors.YELLOW}Next Steps:{Colors.NC}

{Colors.WHITE}1. Configure your API keys:{Colors.NC}
{Colors.GRAY}   Edit the .env file and add your API key(s):{Colors.NC}
""")
        
        if self.os_type == "windows":
            print(f"""
{Colors.YELLOW}   $env:ANTHROPIC_API_KEY = "your-key"{Colors.NC}
{Colors.YELLOW}   $env:OPENAI_API_KEY = "your-key"{Colors.NC}
{Colors.YELLOW}   $env:GROQ_API_KEY = "your-key"{Colors.NC}

{Colors.WHITE}2. Activate the virtual environment:{Colors.NC}
{Colors.YELLOW}   .\\venv\\Scripts\\Activate.ps1{Colors.NC}

{Colors.WHITE}3. Run ALFRED:{Colors.NC}
{Colors.YELLOW}   python main.py{Colors.NC}
{Colors.GRAY}   # Or use the launcher:{Colors.NC}
{Colors.YELLOW}   .\\alfred.bat{Colors.NC}
""")
        else:
            print(f"""
{Colors.YELLOW}   export ANTHROPIC_API_KEY="your-key"{Colors.NC}
{Colors.YELLOW}   export OPENAI_API_KEY="your-key"{Colors.NC}
{Colors.YELLOW}   export GROQ_API_KEY="your-key"{Colors.NC}

{Colors.WHITE}2. Activate the virtual environment:{Colors.NC}
{Colors.YELLOW}   source venv/bin/activate{Colors.NC}

{Colors.WHITE}3. Run ALFRED:{Colors.NC}
{Colors.YELLOW}   python main.py{Colors.NC}
{Colors.GRAY}   # Or use the launcher:{Colors.NC}
{Colors.YELLOW}   ./alfred{Colors.NC}
""")
        
        print(f"{Colors.GRAY}Documentation: https://github.com/Batdan007/ALFRED_UBX{Colors.NC}")
        print()
    
    def run(self) -> int:
        """Run the installation."""
        self.show_banner()

        mode = "minimal" if self.minimal else ("quick" if self.quick else "full")
        self.info(f"Detected OS: {self.os_type}")
        self.info(f"Install directory: {self.install_dir}")
        self.info(f"Install mode: {mode}" + (" (no voice)" if self.no_voice else ""))

        # Check prerequisites
        if not self.check_python_version():
            return 1

        self.check_git()

        # Create virtual environment
        if not self.create_venv():
            return 1

        # Install dependencies
        if not self.install_dependencies():
            self.warn("Some dependencies may not have been installed")

        # Install ffmpeg for voice
        self.install_ffmpeg()

        # Install ALFRED as a package
        self.install_package()

        # Download Whisper model
        self.download_whisper_model()

        # Check Ollama
        self.check_ollama()

        # Setup configuration
        self.create_env_file()

        # Create launchers
        self.create_launcher()

        # Show instructions
        self.show_instructions()

        return 0


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="ALFRED II-Y-II Universal Installer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python install.py                  # Full installation with voice
    python install.py --quick          # Skip optional heavy components
    python install.py --no-voice       # Skip voice system
    python install.py --minimal        # Bare minimum dependencies
    python install.py --skip-venv      # Install without virtual environment
    python install.py --force          # Force reinstall (remove venv)

After install, just type: alfred
"""
    )

    parser.add_argument(
        "--skip-venv",
        action="store_true",
        help="Skip virtual environment creation"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force reinstall (remove existing venv)"
    )
    parser.add_argument(
        "--minimal",
        action="store_true",
        help="Install minimal dependencies only"
    )
    parser.add_argument(
        "--no-voice",
        action="store_true",
        help="Skip voice system (faster-whisper, edge-tts)"
    )
    parser.add_argument(
        "--quick", "-q",
        action="store_true",
        help="Quick install - skip optional heavy components"
    )

    args = parser.parse_args()

    installer = Installer(
        skip_venv=args.skip_venv,
        force=args.force,
        minimal=args.minimal,
        no_voice=args.no_voice,
        quick=args.quick
    )

    result = installer.run()
    sys.exit(result)


if __name__ == "__main__":
    main()
