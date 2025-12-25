# Alfred Global Launchers

Run Alfred from anywhere in your terminal, just like Claude Code!

## Quick Install

Choose the method for your platform:

### Windows (Command Prompt)

**Option 1: Add to PATH (Recommended)**
```batch
# Add launchers directory to PATH
setx PATH "%PATH%;C:\ALFRED_UBX\launchers"

# Restart terminal and test
alfred --version
```

**Option 2: Copy to System32**
```batch
copy C:\ALFRED_UBX\launchers\alfred.bat C:\Windows\System32\alfred.bat
alfred --version
```

### Windows (PowerShell)

**Option 1: Add to PATH**
```powershell
# Add launchers directory to PATH
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\ALFRED_UBX\launchers", "User")

# Restart PowerShell and test
alfred --version
```

**Option 2: PowerShell Profile Alias**
```powershell
# Edit PowerShell profile
notepad $PROFILE

# Add this line:
function alfred { python -m alfred $args }

# Save, restart PowerShell
alfred --version
```

### Linux / macOS

**Option 1: Symlink to /usr/local/bin (Recommended)**
```bash
# Make script executable
chmod +x launchers/alfred.sh

# Create symlink
sudo ln -s "$(pwd)/launchers/alfred.sh" /usr/local/bin/alfred

# Test
alfred --version
```

**Option 2: Copy to /usr/local/bin**
```bash
chmod +x launchers/alfred.sh
sudo cp launchers/alfred.sh /usr/local/bin/alfred
alfred --version
```

**Option 3: Shell Alias**
```bash
# Add to ~/.bashrc or ~/.zshrc
echo 'alias alfred="python3 -m alfred"' >> ~/.bashrc

# Reload shell
source ~/.bashrc

# Test
alfred --version
```

## Usage

Once installed, use Alfred from any directory:

```bash
# Interactive mode
alfred

# Show memory statistics
alfred --stats

# Show version
alfred --version

# Show help
alfred --help
```

## Verify Installation

Test that Alfred is accessible globally:

```bash
cd ~
alfred --version  # Should print: Alfred v3.0.0-ultimate
```

## Troubleshooting

### "alfred: command not found"
- Windows: PATH environment variable not updated. Restart terminal after PATH change.
- Linux/macOS: Script not executable. Run `chmod +x launchers/alfred.sh`

### "Python not found"
- Ensure Python 3.7+ is installed and in PATH
- Windows: `where python`
- Linux/macOS: `which python3`

### "Module alfred not found"
- Run from Alfred root directory: `cd C:\ALFRED_UBX` (Windows) or `cd ~/alfred` (Linux/macOS)
- Or set PYTHONPATH: `export PYTHONPATH=/path/to/ALFRED_UBX`

### Permission Denied (Linux/macOS)
```bash
sudo chmod +x /usr/local/bin/alfred
```

## Uninstall

### Windows
```batch
# If using PATH method
setx PATH "%PATH:;C:\ALFRED_UBX\launchers=%"

# If using System32 method
del C:\Windows\System32\alfred.bat
```

### Linux/macOS
```bash
sudo rm /usr/local/bin/alfred
```

## Notes

- All launchers automatically start Ollama if needed
- No API key required for local mode
- Works from any directory
- Forwards all arguments to Alfred
