"""
ALFRED Chat Installation Verification
Checks all components are properly installed and configured
"""

import sys
import subprocess
from pathlib import Path
import json


class AlfredInstallationVerifier:
    """Verify ALFRED Chat installation"""

    def __init__(self):
        self.checks_passed = 0
        self.checks_failed = 0
        self.warnings = 0
        self.results = []

    def check(self, name: str, test_func, critical: bool = False):
        """Run a check"""
        try:
            result = test_func()
            if result:
                print(f"✅ {name}")
                self.results.append({"name": name, "status": "PASS"})
                self.checks_passed += 1
            else:
                if critical:
                    print(f"❌ {name} [CRITICAL]")
                    self.checks_failed += 1
                else:
                    print(f"⚠️  {name}")
                    self.warnings += 1
                self.results.append({"name": name, "status": "FAIL", "critical": critical})
        except Exception as e:
            if critical:
                print(f"❌ {name}: {str(e)}")
                self.checks_failed += 1
            else:
                print(f"⚠️  {name}: {str(e)}")
                self.warnings += 1
            self.results.append({"name": name, "status": "ERROR", "error": str(e)})

    def verify_python(self):
        """Check Python version"""
        def test():
            return sys.version_info >= (3, 10)
        self.check(f"Python 3.10+ ({sys.version_info.major}.{sys.version_info.minor})", test, critical=True)

    def verify_dependencies(self):
        """Check required dependencies"""
        deps = {
            "fastapi": "Web framework",
            "uvicorn": "ASGI server",
            "aiohttp": "Async HTTP",
            "requests": "HTTP client",
            "rich": "Terminal UI",
        }

        for dep, desc in deps.items():
            def test(d=dep):
                __import__(d)
                return True
            self.check(f"{dep}: {desc}", test, critical=True)

    def verify_core_modules(self):
        """Check core ALFRED modules"""
        core_files = {
            "core/brain.py": "Persistent memory",
            "core/task_classifier.py": "Task classification",
            "core/agent_selector.py": "Agent selection",
            "core/response_quality_checker.py": "Response validation",
            "ui/chat_interface.py": "Chat interface",
        }

        alfred_dir = Path(__file__).parent.parent
        for file, desc in core_files.items():
            file_path = alfred_dir / file
            def test(p=file_path):
                return p.exists()
            self.check(f"{file}: {desc}", test, critical=True)

    def verify_launchers(self):
        """Check launcher scripts"""
        launchers = {
            "launchers/alfred_chat.bat": "Windows launcher",
            "launchers/alfred_chat.sh": "macOS/Linux launcher",
            "launchers/alfred_chat.ps1": "PowerShell launcher",
            "launchers/alfred_launcher.py": "Universal launcher",
        }

        alfred_dir = Path(__file__).parent.parent
        for launcher, desc in launchers.items():
            launcher_path = alfred_dir / launcher
            def test(p=launcher_path):
                return p.exists()
            self.check(f"{launcher}: {desc}", test, critical=False)

    def verify_ollama(self):
        """Check Ollama (optional but recommended)"""
        def test():
            import requests
            response = requests.get("http://localhost:11434/api/version", timeout=2)
            return response.status_code == 200
        self.check("Ollama running (optional, for maximum privacy)", test, critical=False)

    def verify_brain_location(self):
        """Check brain database location"""
        def test():
            from core.path_manager import PathManager
            brain_path = PathManager.BRAIN_DB
            return brain_path.exists() or brain_path.parent.exists()
        self.check("Brain database location accessible", test, critical=False)

    def verify_config(self):
        """Check configuration files"""
        config_files = {
            "config.json": "Main config",
        }

        alfred_dir = Path(__file__).parent.parent
        for config, desc in config_files.items():
            config_path = alfred_dir / config
            def test(p=config_path):
                return p.exists()
            self.check(f"{config}: {desc}", test, critical=False)

    def verify_ports(self):
        """Check if port 8000 is available"""
        def test():
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('127.0.0.1', 8000))
            sock.close()
            return result != 0  # 0 means port is in use
        self.check("Port 8000 available (default ALFRED port)", test, critical=False)

    def run_all_checks(self):
        """Run all verification checks"""
        print()
        print("╔═══════════════════════════════════════╗")
        print("║   ALFRED Chat Installation Verify    ║")
        print("╚═══════════════════════════════════════╝")
        print()

        print("Core Requirements:")
        self.verify_python()
        self.verify_dependencies()
        print()

        print("ALFRED Modules:")
        self.verify_core_modules()
        print()

        print("Launchers:")
        self.verify_launchers()
        print()

        print("Optional Components:")
        self.verify_ollama()
        self.verify_brain_location()
        self.verify_config()
        self.verify_ports()
        print()

        # Summary
        print("=" * 40)
        print(f"✅ Passed: {self.checks_passed}")
        if self.warnings > 0:
            print(f"⚠️  Warnings: {self.warnings}")
        if self.checks_failed > 0:
            print(f"❌ Failed: {self.checks_failed}")
        print("=" * 40)
        print()

        if self.checks_failed > 0:
            print("❌ INSTALLATION INCOMPLETE")
            print()
            print("Critical components are missing. Please:")
            print("1. Install Python 3.10+: https://www.python.org")
            print("2. Install dependencies: pip install -r requirements.txt")
            print("3. Run again to verify")
            return False

        elif self.warnings > 0:
            print("✅ INSTALLATION OK (with optional components missing)")
            print()
            print("ALFRED is ready to use!")
            print()
            print("Optional recommendations:")
            print("• Install Ollama for maximum privacy: https://ollama.ai")
            print("• Set up desktop shortcuts: see launchers/setup_*.bat/sh")
            print()
            return True

        else:
            print("✅ INSTALLATION COMPLETE")
            print()
            print("All components verified!")
            print()
            print("Quick start:")
            system = sys.platform
            if system.startswith('win'):
                print("  Windows: .\\launchers\\alfred_chat.bat")
            elif system == 'darwin':
                print("  macOS: ./launchers/alfred_chat.sh")
            else:
                print("  Linux: ./launchers/alfred_chat.sh")
            print()
            return True

    def save_report(self, filename: str = "alfred_install_report.json"):
        """Save verification report"""
        report = {
            "checks_passed": self.checks_passed,
            "checks_failed": self.checks_failed,
            "warnings": self.warnings,
            "total_checks": len(self.results),
            "results": self.results
        }

        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)

        return filename


def main():
    """Main entry point"""
    verifier = AlfredInstallationVerifier()
    success = verifier.run_all_checks()

    # Save report
    report_file = verifier.save_report()
    print(f"Report saved to: {report_file}")

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
