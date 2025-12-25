"""
ALFRED II-Y-II Client Builder
Builds protected client packages for deployment

Author: Daniel J. Rita (BATDAN)
"""

import os
import shutil
import py_compile
import argparse
from pathlib import Path
from datetime import datetime


class ClientBuilder:
    """Build protected ALFRED client packages"""

    # Files to include in client build
    INCLUDE_FILES = [
        "alfred_terminal.py",
        "config.py",
        "requirements.txt",
    ]

    # Directories to include
    INCLUDE_DIRS = [
        "core",
        "ai",
        "capabilities/voice",
        "capabilities/knowledge",
    ]

    # Files to NEVER include (your secrets)
    EXCLUDE_FILES = [
        ".env",
        "*.key",
        "licenses.json",
        "client_deploy/*",
        "mcp/*",  # Keep MCP for enterprise only
        "tools/bug_bounty_hunter.py",
    ]

    # Enterprise-only directories
    ENTERPRISE_ONLY = [
        "mcp",
        "tools",
        "capabilities/security",
        "capabilities/rag",
        "agents",
    ]

    def __init__(self, source_dir: str = None):
        self.source_dir = Path(source_dir) if source_dir else Path(__file__).parent.parent
        self.build_dir = Path("builds")
        self.build_dir.mkdir(exist_ok=True)

    def build(self, license_key: str, tier: str = "basic", client_name: str = "client") -> Path:
        """
        Build a protected client package

        Args:
            license_key: The client's license key
            tier: basic, pro, or enterprise
            client_name: Client identifier for the build

        Returns:
            Path to the built package
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        build_name = f"alfred_{client_name}_{tier}_{timestamp}"
        output_dir = self.build_dir / build_name

        print(f"\n{'='*50}")
        print(f"Building ALFRED Client Package")
        print(f"{'='*50}")
        print(f"Tier: {tier.upper()}")
        print(f"Client: {client_name}")
        print(f"Output: {output_dir}")
        print(f"{'='*50}\n")

        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)

        # Copy and compile files based on tier
        self._copy_core_files(output_dir, tier)

        # Create license file
        self._create_license_file(output_dir, license_key)

        # Create client launcher
        self._create_launcher(output_dir, tier)

        # Create client config
        self._create_client_config(output_dir, tier)

        # Create README for client
        self._create_client_readme(output_dir, tier)

        # Compile Python files to .pyc (obfuscation)
        self._compile_python_files(output_dir)

        print(f"\n{'='*50}")
        print(f"BUILD COMPLETE")
        print(f"{'='*50}")
        print(f"Package: {output_dir}")
        print(f"Size: {self._get_dir_size(output_dir):.2f} MB")
        print(f"{'='*50}\n")

        return output_dir

    def _copy_core_files(self, output_dir: Path, tier: str):
        """Copy files based on tier"""
        print("[*] Copying core files...")

        # Copy main files
        for file in self.INCLUDE_FILES:
            src = self.source_dir / file
            if src.exists():
                shutil.copy(src, output_dir / file)
                print(f"    + {file}")

        # Copy directories
        dirs_to_copy = self.INCLUDE_DIRS.copy()

        # Add enterprise directories if applicable
        if tier == "enterprise":
            dirs_to_copy.extend(self.ENTERPRISE_ONLY)
        elif tier == "pro":
            dirs_to_copy.append("capabilities/rag")

        for dir_name in dirs_to_copy:
            src = self.source_dir / dir_name
            if src.exists():
                dst = output_dir / dir_name
                shutil.copytree(src, dst, ignore=shutil.ignore_patterns(
                    "*.pyc", "__pycache__", "*.log", ".env", "*.key"
                ))
                print(f"    + {dir_name}/")

        # Copy license validator
        validator_src = self.source_dir / "client_deploy" / "license_validator.py"
        if validator_src.exists():
            shutil.copy(validator_src, output_dir / "license_validator.py")

    def _create_license_file(self, output_dir: Path, license_key: str):
        """Create the license file"""
        print("[*] Creating license file...")
        license_file = output_dir / "license.key"
        license_file.write_text(license_key)

    def _create_launcher(self, output_dir: Path, tier: str):
        """Create the client launcher script"""
        print("[*] Creating launcher...")

        launcher_code = '''#!/usr/bin/env python3
"""
ALFRED II-Y-II Client
Licensed to: {CLIENT}

Contact: danieljrita@hotmail.com
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Validate license first
from license_validator import LicenseValidator

def main():
    # Check license
    validator = LicenseValidator()
    result = validator.enforce()  # Exits if invalid

    # Import and run ALFRED
    from alfred_terminal import main as alfred_main
    alfred_main()

if __name__ == "__main__":
    main()
'''

        launcher_file = output_dir / "run_alfred.py"
        launcher_file.write_text(launcher_code)

        # Also create batch file for Windows
        batch_content = '''@echo off
python run_alfred.py
pause
'''
        batch_file = output_dir / "ALFRED.bat"
        batch_file.write_text(batch_content)

    def _create_client_config(self, output_dir: Path, tier: str):
        """Create client configuration"""
        print("[*] Creating config...")

        # Tier-specific config
        providers = {
            "basic": ["ollama"],
            "pro": ["ollama", "anthropic", "groq"],
            "enterprise": ["ollama", "anthropic", "openai", "groq", "google"]
        }

        config = {
            "tier": tier,
            "allowed_providers": providers.get(tier, ["ollama"]),
            "voice_enabled": tier in ["pro", "enterprise"],
            "web_ui_enabled": tier in ["pro", "enterprise"],
            "mcp_enabled": tier == "enterprise",
            "support_email": "danieljrita@hotmail.com"
        }

        import json
        config_file = output_dir / "client_config.json"
        config_file.write_text(json.dumps(config, indent=2))

    def _create_client_readme(self, output_dir: Path, tier: str):
        """Create README for client"""
        readme = f'''# ALFRED II-Y-II

## Your AI Assistant

**License Tier:** {tier.upper()}

## Getting Started

1. Install Python 3.10+ from python.org
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run ALFRED:
   ```
   python run_alfred.py
   ```
   Or double-click `ALFRED.bat` on Windows

## Commands

| Command | Description |
|---------|-------------|
| /help | Show help |
| /memory | View memory |
| /voice on | Enable voice |
| /exit | Exit ALFRED |

## Support

Email: danieljrita@hotmail.com

## License

This software is licensed to you. Do not distribute.
License violations will result in immediate revocation.

---
ALFRED II-Y-II by Daniel J. Rita (BATDAN)
'''

        readme_file = output_dir / "README.md"
        readme_file.write_text(readme)

    def _compile_python_files(self, output_dir: Path):
        """Compile .py files to .pyc for basic obfuscation"""
        print("[*] Compiling Python files...")

        for py_file in output_dir.rglob("*.py"):
            try:
                py_compile.compile(str(py_file), cfile=str(py_file) + "c")
                # Optionally remove .py files (uncomment for more protection)
                # py_file.unlink()
                print(f"    + {py_file.name}")
            except Exception as e:
                print(f"    ! Failed to compile {py_file.name}: {e}")

    def _get_dir_size(self, path: Path) -> float:
        """Get directory size in MB"""
        total = 0
        for f in path.rglob("*"):
            if f.is_file():
                total += f.stat().st_size
        return total / (1024 * 1024)


def main():
    parser = argparse.ArgumentParser(description="Build ALFRED Client Package")
    parser.add_argument("--license", required=True, help="Client license key")
    parser.add_argument("--tier", default="basic", choices=["basic", "pro", "enterprise"])
    parser.add_argument("--client", default="client", help="Client name/identifier")

    args = parser.parse_args()

    builder = ClientBuilder()
    output = builder.build(
        license_key=args.license,
        tier=args.tier,
        client_name=args.client
    )

    print(f"\nDeploy this folder to client: {output}")


if __name__ == "__main__":
    main()
