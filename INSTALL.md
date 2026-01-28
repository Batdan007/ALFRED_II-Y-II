# ALFRED_IV-Y-VI Installation Guide

AI Assistant with Persistent Memory & Adaptive Learning

## Quick Start

### Universal Installer (Recommended)

The Python installer works on all platforms:

```bash
python install.py
```

### Platform-Specific Installers

#### Windows (PowerShell)
```powershell
.\install.ps1
```

#### Linux / macOS / WSL
```bash
chmod +x install.sh
./install.sh
```

## Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| Python | 3.10+ | Required |
| Git | Any | Optional, recommended |
| pip | Latest | Auto-upgraded during install |

### Platform-Specific Requirements

#### Windows
- PowerShell 5.1+ (comes with Windows 10/11)
- Or use `install.py` with Command Prompt

#### Linux/WSL
```bash
# Debian/Ubuntu
sudo apt update
sudo apt install python3.12 python3.12-venv python3-pip espeak-ng

# Fedora/RHEL
sudo dnf install python3.12 espeak-ng

# Arch
sudo pacman -S python python-pip espeak-ng
```

#### macOS
```bash
# Using Homebrew
brew install python@3.12
```

#### iOS (Pythonista/a-Shell)
```bash
# Use the minimal installer
python install.py --minimal --skip-venv
```

## Installation Options

### Standard Installation
```bash
python install.py
```

### Installation Options

| Option | Description |
|--------|-------------|
| `--skip-venv` | Don't create virtual environment |
| `--force` | Remove existing venv and reinstall |
| `--minimal` | Install only essential packages |
| `--help` | Show help message |

### Examples

```bash
# Force reinstall
python install.py --force

# Minimal installation for resource-constrained systems
python install.py --minimal

# Install without virtual environment
python install.py --skip-venv
```

## Post-Installation Setup

### 1. Configure API Keys

Edit `.env` file with your API keys:

```env
# At least one is required
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GROQ_API_KEY=gsk_...
```

Or set as environment variables:

**Windows (PowerShell):**
```powershell
$env:ANTHROPIC_API_KEY = "your-key-here"
```

**Linux/macOS:**
```bash
export ANTHROPIC_API_KEY="your-key-here"
```

### 2. Activate Virtual Environment

**Windows:**
```powershell
.\venv\Scripts\Activate.ps1
```

**Linux/macOS:**
```bash
source venv/bin/activate
```

### 3. Run ALFRED

```bash
python main.py
```

Or use the launcher scripts:
- Windows: `alfred.bat` or `alfred.ps1`
- Linux/macOS: `./alfred`

## Running as a Service (Linux)

A systemd service file is created during installation:

```bash
# Copy service file
sudo cp alfred.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable and start
sudo systemctl enable alfred
sudo systemctl start alfred

# Check status
sudo systemctl status alfred
```

## Troubleshooting

### Python not found
- Ensure Python 3.10+ is installed
- On Windows, check "Add Python to PATH" during installation
- Try `python3` instead of `python`

### Virtual environment errors
- Use `--skip-venv` to install globally
- On Windows, you may need to run as Administrator
- Check Python venv module: `python -m venv --help`

### Permission denied (Linux/macOS)
```bash
chmod +x install.sh
chmod +x alfred
```

### Text-to-speech not working (Linux)
```bash
# Install espeak-ng
sudo apt install espeak-ng
```

### Missing dependencies
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

## Uninstallation

```bash
# Remove virtual environment
rm -rf venv

# Remove configuration (optional)
rm .env

# Remove launcher scripts
rm alfred alfred.bat alfred.ps1 alfred.service
```

## Support

- **Repository**: https://github.com/Batdan007/ALFRED_IV-Y-VI
- **Issues**: https://github.com/Batdan007/ALFRED_IV-Y-VI/issues

---
*Created by Daniel J. Rita aka BATDAN007*
