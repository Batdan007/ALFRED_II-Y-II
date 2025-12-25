# Alfred Global Launcher (Windows PowerShell)
#
# Installation:
#   1. Add C:\ALFRED_UBX\launchers to your PATH environment variable
#   2. Set-ExecutionPolicy RemoteSigned (if not already done)
#   3. alfred  (from any directory)
#
# Or create a PowerShell profile alias:
#   notepad $PROFILE
#   Add: function alfred { python -m alfred $args }
#
# Author: Daniel J Rita (BATDAN)

# Get the directory where this script is located
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Determine Alfred root directory
if (Test-Path "$ScriptDir\..\alfred\__init__.py") {
    # Script is in launchers\ subdirectory
    $AlfredRoot = Resolve-Path "$ScriptDir\.."
} elseif (Test-Path "$ScriptDir\alfred\__init__.py") {
    # Script is in alfred root
    $AlfredRoot = $ScriptDir
} else {
    # Try to run from current directory
    $AlfredRoot = $null
}

# Change to Alfred directory if found
if ($AlfredRoot) {
    Set-Location $AlfredRoot
}

# Run Alfred as Python module
python -m alfred $args
