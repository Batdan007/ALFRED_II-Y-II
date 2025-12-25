#!/usr/bin/env python3
"""
ALFRED_UBX Universal Installer
AI Assistant with Persistent Memory & Adaptive Learning

This installer works on all platforms: Windows, macOS, Linux, WSL, iOS (Pythonista/a-Shell)
Author: Daniel J. Rita aka BATDAN007
https://github.com/Batdan007/ALFRED_UBX

Usage:
    python install.py [options]
    
Options:
    --skip-venv     Skip virtual environment creation
    --force         Force reinstall (remove existing venv)
    --minimal       Install minimal dependencies only
    --help          Show this help message
"""

import os
import sys
import subprocess
import platform
import shutil
import argparse
from pathlib import Path
from typing import Optional, List, Tuple

# Minimum Python version
MIN_PYTHON = (3, 10)

# Core dependencies
CORE_PACKAGES = [
    "anthropic",
    "openai",
    "groq",
    "fastapi",
    "uvicorn[standard]",
    "mcp",
    "rich",
    "prompt-toolkit",
    "pydantic",
    "python-dotenv",
    "aiohttp",
    "httpx",
]

# Optional packages (may not work on all platforms)
OPTIONAL_PACKAGES = [
    "pyttsx3",  # Text-to-speech (not available on iOS)
]

# Minimal packages (for resource-constrained environments)
MINIMAL_PACKAGES = [
    "anthropic",
    "rich",
    "python-dotenv",
    "pydantic",
    "httpx",
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
    """Cross-platform installer for ALFRED_UBX."""
    
    def __init__(self, skip_venv: bool = False, force: bool = False, minimal: bool = False):
        self.skip_venv = skip_venv
        self.force = force
        self.minimal = minimal
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
        """Check if Python version meets minimum requirements."""
        self.info("Checking Python version...")
        
        version = sys.version_info
        if version >= MIN_PYTHON:
            self.success(f"Python {version.major}.{version.minor}.{version.micro}")
            return True
        else:
            self.error(f"Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]}+ required, found {version.major}.{version.minor}")
            return False
    
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
        """Install Python dependencies."""
        self.info("Installing dependencies...")
        
        # Upgrade pip first
        self.info("Upgrading pip...")
        self.run_pip(["install", "--upgrade", "pip"])
        self.success("pip upgraded")
        
        # Check for requirements.txt
        requirements_file = self.install_dir / "requirements.txt"
        if requirements_file.exists():
            self.info("Installing from requirements.txt...")
            if self.run_pip(["install", "-r", str(requirements_file)]):
                self.success("Dependencies installed from requirements.txt")
                return True
            else:
                self.warn("Some dependencies may have failed, continuing...")
        
        # Install packages based on mode
        packages = MINIMAL_PACKAGES if self.minimal else CORE_PACKAGES
        
        self.info(f"Installing {'minimal' if self.minimal else 'core'} dependencies...")
        for package in packages:
            self.info(f"  Installing {package}...")
            if not self.run_pip(["install", package]):
                self.warn(f"  Could not install {package}")
        
        # Install optional packages (non-iOS only)
        if not self.minimal and self.os_type != "ios":
            self.info("Installing optional dependencies...")
            for package in OPTIONAL_PACKAGES:
                self.info(f"  Installing {package}...")
                if not self.run_pip(["install", package]):
                    self.warn(f"  Could not install {package} (optional)")
        
        # Platform-specific dependencies
        if self.os_type == "macos":
            self.info("Installing macOS-specific dependencies...")
            self.run_pip(["install", "pyobjc-framework-Cocoa"])
        
        self.success("Dependencies installed")
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
        
        self.info(f"Detected OS: {self.os_type}")
        self.info(f"Install directory: {self.install_dir}")
        
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
        description="ALFRED_UBX Universal Installer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python install.py                  # Standard installation
    python install.py --skip-venv      # Install without virtual environment
    python install.py --minimal        # Install minimal dependencies
    python install.py --force          # Force reinstall
    python install.py --no-wizard      # Skip setup wizard
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
        "--no-wizard",
        action="store_true",
        help="Skip launching setup wizard after installation"
    )
    
    args = parser.parse_args()
    
    installer = Installer(
        skip_venv=args.skip_venv,
        force=args.force,
        minimal=args.minimal
    )
    
    result = installer.run()
    
    # Launch setup wizard automatically (unless skipped)
    if result == 0 and not args.no_wizard:
        print(f"\n{Colors.CYAN}Launching Setup Wizard...{Colors.NC}\n")
        setup_wizard = Path("setup_wizard.py")
        if setup_wizard.exists():
            try:
                subprocess.run([installer.get_python_command(), str(setup_wizard)])
            except Exception as e:
                print(f"Could not launch setup wizard: {e}")
                print("You can run it manually: python setup_wizard.py")
    
    sys.exit(result)


if __name__ == "__main__":
    main()
