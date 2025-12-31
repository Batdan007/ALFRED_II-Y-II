#!/usr/bin/env python3
"""
ALFRED Voice - One-Command Setup
=================================
Installs all dependencies and downloads models automatically.

Usage:
    python setup_voice.py

This script:
1. Creates/activates virtual environment
2. Installs Python dependencies
3. Installs ffmpeg (Windows)
4. Downloads Whisper model
5. Verifies Ollama connection
6. Ready to run

Author: Daniel J Rita (BATDAN)
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

# ============================================================
# Configuration
# ============================================================

WHISPER_MODEL = "base.en"  # ~150MB, good balance of speed/accuracy
REQUIRED_PACKAGES = [
    "faster-whisper>=1.0.0",
    "edge-tts>=6.1.0",
    "sounddevice>=0.4.6",
    "numpy>=1.24.0",
    "requests>=2.31.0",
]

# ============================================================
# Helpers
# ============================================================

def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print('='*60)

def print_step(text):
    print(f"\n  → {text}")

def print_ok(text):
    print(f"    ✓ {text}")

def print_warn(text):
    print(f"    ⚠ {text}")

def print_error(text):
    print(f"    ✗ {text}")

def run_cmd(cmd, capture=False, check=True):
    """Run command and return result"""
    try:
        if capture:
            result = subprocess.run(cmd, capture_output=True, text=True, check=check)
            return result.returncode == 0, result.stdout
        else:
            result = subprocess.run(cmd, check=check)
            return result.returncode == 0, ""
    except subprocess.CalledProcessError as e:
        return False, str(e)
    except FileNotFoundError:
        return False, "Command not found"

# ============================================================
# Installation Steps
# ============================================================

def check_python():
    """Check Python version"""
    print_step("Checking Python...")

    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print_error(f"Python 3.10+ required, found {version.major}.{version.minor}")
        return False

    print_ok(f"Python {version.major}.{version.minor}.{version.micro}")
    return True

def install_packages():
    """Install Python packages"""
    print_step("Installing Python packages...")

    for package in REQUIRED_PACKAGES:
        name = package.split(">=")[0].split("==")[0]
        print(f"      Installing {name}...", end=" ", flush=True)

        success, _ = run_cmd(
            [sys.executable, "-m", "pip", "install", "-q", package],
            check=False
        )

        if success:
            print("OK")
        else:
            print("FAILED")
            return False

    print_ok("All packages installed")
    return True

def install_ffmpeg():
    """Install ffmpeg on Windows"""
    print_step("Checking ffmpeg...")

    # Check if already installed
    success, _ = run_cmd(["ffmpeg", "-version"], capture=True, check=False)
    if success:
        print_ok("ffmpeg already installed")
        return True

    if platform.system() != "Windows":
        print_warn("ffmpeg not found. Install manually:")
        print("         Ubuntu: sudo apt install ffmpeg")
        print("         Mac: brew install ffmpeg")
        return False

    # Try winget
    print("      Installing via winget...", end=" ", flush=True)
    success, _ = run_cmd(["winget", "install", "-e", "--id", "Gyan.FFmpeg", "-h"], check=False)

    if success:
        print("OK")
        print_warn("Restart terminal for ffmpeg to be in PATH")
        return True

    # Try chocolatey
    print("FAILED")
    print("      Trying chocolatey...", end=" ", flush=True)
    success, _ = run_cmd(["choco", "install", "ffmpeg", "-y"], check=False)

    if success:
        print("OK")
        return True

    print("FAILED")
    print_error("Could not install ffmpeg automatically")
    print("         Download from: https://ffmpeg.org/download.html")
    print("         Or run: winget install ffmpeg")
    return False

def download_whisper_model():
    """Pre-download Whisper model"""
    print_step(f"Downloading Whisper model ({WHISPER_MODEL})...")

    try:
        from faster_whisper import WhisperModel

        # This triggers the download
        print(f"      Downloading ~150MB model...", end=" ", flush=True)

        # Try GPU first, fall back to CPU
        try:
            model = WhisperModel(WHISPER_MODEL, device="cuda", compute_type="float16")
            device = "GPU (CUDA)"
        except:
            model = WhisperModel(WHISPER_MODEL, device="cpu", compute_type="float32")
            device = "CPU"

        print("OK")
        print_ok(f"Whisper {WHISPER_MODEL} ready on {device}")

        # Cleanup
        del model
        return True

    except Exception as e:
        print("FAILED")
        print_error(f"Could not download model: {e}")
        return False

def check_ollama():
    """Check Ollama connection"""
    print_step("Checking Ollama...")

    try:
        import requests
        r = requests.get("http://localhost:11434/api/tags", timeout=3)
        if r.status_code == 200:
            models = [m['name'] for m in r.json().get('models', [])]
            print_ok(f"Ollama running with {len(models)} model(s)")
            if models:
                print(f"         Models: {', '.join(models[:3])}")
            return True
    except:
        pass

    print_warn("Ollama not running")
    print("         Start with: ollama serve")
    print("         Pull model: ollama pull llama3.2")
    return False  # Not fatal

def verify_installation():
    """Quick verification"""
    print_step("Verifying installation...")

    errors = []

    # Check imports
    try:
        from faster_whisper import WhisperModel
        print_ok("faster-whisper")
    except ImportError as e:
        errors.append(f"faster-whisper: {e}")

    try:
        import edge_tts
        print_ok("edge-tts")
    except ImportError as e:
        errors.append(f"edge-tts: {e}")

    try:
        import sounddevice
        print_ok("sounddevice")
    except ImportError as e:
        errors.append(f"sounddevice: {e}")

    try:
        import numpy
        print_ok("numpy")
    except ImportError as e:
        errors.append(f"numpy: {e}")

    if errors:
        print_error("Some packages failed:")
        for e in errors:
            print(f"         {e}")
        return False

    return True

# ============================================================
# Main
# ============================================================

def main():
    print_header("ALFRED Voice - Setup")
    print("\n  This will install all dependencies and download models.")
    print("  Estimated time: 2-5 minutes (depending on internet speed)")

    # Check Python
    if not check_python():
        return 1

    # Install packages
    if not install_packages():
        return 1

    # Install ffmpeg
    install_ffmpeg()  # Not fatal if fails

    # Download Whisper model
    if not download_whisper_model():
        print_warn("Model download failed, will retry on first run")

    # Check Ollama
    check_ollama()  # Not fatal

    # Verify
    if not verify_installation():
        return 1

    # Done
    print_header("Setup Complete!")
    print("""
  To run ALFRED Voice:

    python alfred_voice_loop.py

  Or double-click: run_voice.bat

  Make sure Ollama is running: ollama serve
""")

    return 0

if __name__ == "__main__":
    sys.exit(main())
