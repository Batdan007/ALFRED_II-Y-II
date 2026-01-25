#!/usr/bin/env python3
"""
ALFRED Setup Script
Automated installation for ALFRED AI Companion

Run: python setup_alfred.py

Author: Daniel J Rita (BATDAN)
GxEum Technologies / CAMDAN Enterprizes
"""

import subprocess
import sys
import os
from pathlib import Path

def print_banner():
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║     █████╗ ██╗     ███████╗██████╗ ███████╗██████╗            ║
║    ██╔══██╗██║     ██╔════╝██╔══██╗██╔════╝██╔══██╗           ║
║    ███████║██║     █████╗  ██████╔╝█████╗  ██║  ██║           ║
║    ██╔══██║██║     ██╔══╝  ██╔══██╗██╔══╝  ██║  ██║           ║
║    ██║  ██║███████╗██║     ██║  ██║███████╗██████╔╝           ║
║    ╚═╝  ╚═╝╚══════╝╚═╝     ╚═╝  ╚═╝╚══════╝╚═════╝            ║
║                                                               ║
║         Your Personal AI Companion with Memory                ║
║              Created by BATDAN | GxEum Tech                   ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
    """)

def check_python():
    """Check Python version"""
    print("Checking Python version...", end=" ")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 10:
        print(f"OK (Python {version.major}.{version.minor}.{version.micro})")
        return True
    else:
        print(f"FAILED (Python {version.major}.{version.minor} - need 3.10+)")
        return False

def install_requirements():
    """Install Python dependencies"""
    print("\nInstalling dependencies...")
    requirements_file = Path(__file__).parent / "requirements.txt"

    if not requirements_file.exists():
        print("  WARNING: requirements.txt not found")
        return False

    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r",
            str(requirements_file), "-q"
        ])
        print("  Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("  ERROR: Failed to install dependencies")
        return False

def check_ollama():
    """Check if Ollama is available"""
    print("\nChecking for Ollama (local AI)...", end=" ")
    try:
        result = subprocess.run(
            ["ollama", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print(f"OK ({result.stdout.strip()})")
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    print("Not installed (optional)")
    print("  To install: https://ollama.ai")
    return False

def setup_directories():
    """Create necessary directories"""
    print("\nSetting up directories...", end=" ")
    dirs = ["data", "logs", "config"]
    base = Path(__file__).parent

    for d in dirs:
        (base / d).mkdir(exist_ok=True)

    print("OK")
    return True

def create_env_template():
    """Create .env template if it doesn't exist"""
    env_file = Path(__file__).parent / ".env"
    env_example = Path(__file__).parent / ".env.example"

    if not env_file.exists():
        print("\nCreating .env template...", end=" ")
        template = """# ALFRED Configuration
# Uncomment and fill in API keys for cloud AI providers

# Anthropic Claude (recommended)
# ANTHROPIC_API_KEY=sk-ant-...

# OpenAI GPT
# OPENAI_API_KEY=sk-...

# Groq (fast)
# GROQ_API_KEY=gsk_...

# Google Gemini
# GOOGLE_API_KEY=...

# Ollama (local - no key needed)
OLLAMA_URL=http://localhost:11434

# Privacy mode: local, cloud, or auto
ALFRED_PRIVACY_MODE=local
"""
        env_file.write_text(template)
        print("OK")
        print("  Edit .env to add your API keys")

def run_test():
    """Quick test to see if ALFRED can start"""
    print("\nTesting ALFRED startup...", end=" ")
    try:
        # Just try to import the main modules
        sys.path.insert(0, str(Path(__file__).parent))
        from core.brain import Brain
        from core.cortex import CORTEX
        print("OK")
        print("  Core modules loaded successfully!")
        return True
    except ImportError as e:
        print(f"FAILED ({e})")
        return False

def main():
    print_banner()

    print("=" * 60)
    print("ALFRED Setup Wizard")
    print("=" * 60)

    # Check prerequisites
    if not check_python():
        print("\nPlease install Python 3.10 or higher")
        sys.exit(1)

    # Install dependencies
    install_requirements()

    # Check Ollama
    has_ollama = check_ollama()

    # Setup directories
    setup_directories()

    # Create env template
    create_env_template()

    # Test startup
    run_test()

    # Summary
    print("\n" + "=" * 60)
    print("Setup Complete!")
    print("=" * 60)
    print()
    print("To start ALFRED:")
    print("  python alfred_terminal.py")
    print()

    if not has_ollama:
        print("For local AI (recommended):")
        print("  1. Install Ollama: https://ollama.ai")
        print("  2. Run: ollama pull llama3.2")
        print()

    print("For cloud AI:")
    print("  Edit .env and add your API keys")
    print()
    print("Joe Dog's Rule: Every AI pledges to protect all life.")
    print()

if __name__ == "__main__":
    main()
