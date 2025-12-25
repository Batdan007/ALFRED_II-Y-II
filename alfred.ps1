$ErrorActionPreference = "Stop"
Push-Location $PSScriptRoot
try {
    if (Test-Path "venv\Scripts\Activate.ps1") {
        . .\venv\Scripts\Activate.ps1
    }
    python main.py @args
} finally {
    Pop-Location
}
