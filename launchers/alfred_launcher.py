"""
ALFRED Chat - Universal Launcher
Detects OS and launches ALFRED Chat with appropriate interface

Supports:
- Windows (desktop shortcut + browser UI)
- macOS (app bundle + browser UI)
- Linux (desktop entry + browser UI)
- iOS (Safari via network)
"""

import sys
import platform
import subprocess
import json
import time
from pathlib import Path
from typing import Optional
from enum import Enum


class OS(Enum):
    WINDOWS = "windows"
    MACOS = "darwin"
    LINUX = "linux"
    IOS = "ios"


def get_os() -> OS:
    """Detect operating system"""
    system = platform.system().lower()

    if system == "windows":
        return OS.WINDOWS
    elif system == "darwin":
        return OS.MACOS
    elif system == "linux":
        return OS.LINUX
    else:
        return OS.LINUX


def check_python() -> bool:
    """Check if Python 3.10+ is available"""
    version = sys.version_info
    return version.major >= 3 and version.minor >= 10


def check_dependencies() -> bool:
    """Check if required dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        return True
    except ImportError:
        return False


def install_dependencies():
    """Install required dependencies"""
    print("Installing required dependencies...")
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-q", "fastapi", "uvicorn[standard]", "aiohttp"],
        check=True
    )
    print("✓ Dependencies installed")


def check_ollama() -> bool:
    """Check if Ollama is running"""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/version", timeout=2)
        return response.status_code == 200
    except:
        return False


def start_alfred_windows():
    """Start ALFRED on Windows"""
    alfred_dir = Path(__file__).parent.parent
    launcher = alfred_dir / "launchers" / "alfred_chat.bat"

    if not launcher.exists():
        print(f"Error: Launcher not found at {launcher}")
        return False

    print("Starting ALFRED Chat (Windows)...")
    subprocess.Popen(str(launcher))
    return True


def start_alfred_macos():
    """Start ALFRED on macOS"""
    alfred_dir = Path(__file__).parent.parent

    # Check if app bundle exists
    app_path = Path.home() / "Applications" / "ALFRED.app"
    if not app_path.exists():
        print("Creating ALFRED app bundle...")
        launcher = alfred_dir / "launchers" / "setup_macos_app.sh"
        subprocess.run(["bash", str(launcher)], check=True)

    print("Starting ALFRED Chat (macOS)...")
    subprocess.run(["open", str(app_path)])
    return True


def start_alfred_linux():
    """Start ALFRED on Linux"""
    alfred_dir = Path(__file__).parent.parent
    launcher = alfred_dir / "launchers" / "alfred_chat.sh"

    if not launcher.exists():
        print(f"Error: Launcher not found at {launcher}")
        return False

    print("Starting ALFRED Chat (Linux)...")
    subprocess.Popen(["bash", str(launcher)])
    return True


def show_setup_menu(current_os: OS):
    """Show setup/launcher menu"""
    menu = f"""
╔═══════════════════════════════════════╗
║         ALFRED Chat Launcher          ║
║  Private AI Assistant with Memory     ║
╚═══════════════════════════════════════╝

Current System: {current_os.value.upper()}

Options:
1. Start ALFRED Chat
2. Setup Desktop Shortcuts
3. Check Ollama (Local Privacy)
4. View Configuration
5. Install/Update Dependencies
6. Exit

Select option (1-6): """

    return menu


def main():
    """Main launcher"""
    print()
    print("╔═══════════════════════════════════════╗")
    print("║         ALFRED Chat Launcher          ║")
    print("║  Private AI Assistant with Memory     ║")
    print("╚═══════════════════════════════════════╝")
    print()

    # Detect OS
    current_os = get_os()
    print(f"Detected OS: {current_os.value}")

    # Check Python
    print(f"Python version: {sys.version_info.major}.{sys.version_info.minor}")
    if not check_python():
        print("❌ Python 3.10+ required")
        return

    # Check dependencies
    print("Checking dependencies...", end=" ")
    if not check_dependencies():
        print("Missing")
        install_dependencies()
    else:
        print("✓")

    # Check Ollama
    print("Checking Ollama (local privacy)...", end=" ")
    if check_ollama():
        print("✓ Running")
    else:
        print("⚠ Not running")
        print("  Install Ollama for maximum privacy: https://ollama.ai")

    print()

    # Show menu and get choice
    while True:
        choice = input(show_setup_menu(current_os)).strip()

        if choice == "1":
            # Start ALFRED
            if current_os == OS.WINDOWS:
                start_alfred_windows()
            elif current_os == OS.MACOS:
                start_alfred_macos()
            elif current_os == OS.LINUX:
                start_alfred_linux()

            print("✓ ALFRED is starting...")
            print("  Opening browser to http://localhost:8000 in 3 seconds...")
            time.sleep(3)
            break

        elif choice == "2":
            # Setup shortcuts
            print("\nSetting up desktop shortcuts...")

            if current_os == OS.WINDOWS:
                launcher = Path(__file__).parent.parent / "launchers" / "setup_windows_shortcuts.bat"
                subprocess.run(str(launcher))

            elif current_os == OS.MACOS:
                launcher = Path(__file__).parent.parent / "launchers" / "setup_macos_app.sh"
                subprocess.run(["bash", str(launcher)])

            elif current_os == OS.LINUX:
                launcher = Path(__file__).parent.parent / "launchers" / "setup_linux_menu.sh"
                subprocess.run(["bash", str(launcher)])

        elif choice == "3":
            # Check Ollama
            print("\nChecking Ollama...")
            if check_ollama():
                print("✓ Ollama is running (local privacy enabled)")
            else:
                print("⚠ Ollama is not running")
                print("  Install from: https://ollama.ai")
                print("  Or use: ollama serve")

        elif choice == "4":
            # Show configuration
            print("\nConfiguration:")
            print("  Server: http://localhost:8000")
            print("  Privacy Mode: LOCAL-FIRST (default)")
            print("  Cloud Access: Requires permission")
            print("  Brain Location: See core/path_manager.py")

        elif choice == "5":
            # Install/update dependencies
            print("\nInstalling/updating dependencies...")
            install_dependencies()
            print("✓ Done")

        elif choice == "6":
            # Exit
            print("Goodbye!")
            break

        print()


if __name__ == "__main__":
    main()
