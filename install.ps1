<#
.SYNOPSIS
    ALFRED_IV-Y-VI Installation Script for Windows
.DESCRIPTION
    Cross-platform installer for ALFRED_IV-Y-VI - AI Assistant with Persistent Memory
    Author: Daniel J. Rita aka BATDAN007
.NOTES
    Version: 2.0.0
    Requires: PowerShell 5.1+ and Python 3.10+
#>

[CmdletBinding()]
param(
    [switch]$SkipVenv,
    [switch]$Force,
    [string]$PythonPath = "python"
)

# Script configuration
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

# Colors and formatting
function Write-Info { param($Message) Write-Host "[INFO] " -ForegroundColor Cyan -NoNewline; Write-Host $Message }
function Write-Success { param($Message) Write-Host "[OK] " -ForegroundColor Green -NoNewline; Write-Host $Message }
function Write-Warn { param($Message) Write-Host "[WARN] " -ForegroundColor Yellow -NoNewline; Write-Host $Message }
function Write-Err { param($Message) Write-Host "[ERROR] " -ForegroundColor Red -NoNewline; Write-Host $Message }

# Banner
function Show-Banner {
    Write-Host ""
    Write-Host "    _    _     _____ ____  _____ ____    _   _ ______  __" -ForegroundColor Cyan
    Write-Host "   / \  | |   |  ___|  _ \| ____|  _ \  | | | | __ ) \/ /" -ForegroundColor Cyan
    Write-Host "  / _ \ | |   | |_  | |_) |  _| | | | | | | | |  _ \\  / " -ForegroundColor Cyan
    Write-Host " / ___ \| |___|  _| |  _ <| |___| |_| | | |_| | |_) /  \ " -ForegroundColor Cyan
    Write-Host "/_/   \_\_____|_|   |_| \_\_____|____/   \___/|____/_/\_\" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  AI Assistant with Persistent Memory & Adaptive Learning" -ForegroundColor White
    Write-Host "  https://github.com/Batdan007/ALFRED_IV-Y-VI" -ForegroundColor DarkGray
    Write-Host ""
}

# Check Python installation
function Test-Python {
    Write-Info "Checking Python installation..."
    
    try {
        $pythonVersion = & $PythonPath --version 2>&1
        if ($pythonVersion -match "Python (\d+)\.(\d+)") {
            $major = [int]$Matches[1]
            $minor = [int]$Matches[2]
            
            if ($major -ge 3 -and $minor -ge 10) {
                Write-Success "Found $pythonVersion"
                return $true
            } else {
                Write-Err "Python 3.10+ required, found $pythonVersion"
                return $false
            }
        }
    } catch {
        Write-Err "Python not found. Please install Python 3.10+ from https://python.org"
        return $false
    }
    return $false
}

# Check Git installation
function Test-Git {
    Write-Info "Checking Git installation..."
    
    try {
        $gitVersion = & git --version 2>&1
        Write-Success "Found $gitVersion"
        return $true
    } catch {
        Write-Warn "Git not found. Some features may be limited."
        return $false
    }
}

# Create virtual environment
function New-VirtualEnvironment {
    param([string]$VenvPath = "venv")
    
    if ($SkipVenv) {
        Write-Warn "Skipping virtual environment creation (-SkipVenv)"
        return $true
    }
    
    Write-Info "Creating virtual environment..."
    
    if (Test-Path $VenvPath) {
        if ($Force) {
            Write-Warn "Removing existing virtual environment..."
            Remove-Item -Recurse -Force $VenvPath
        } else {
            Write-Success "Virtual environment already exists"
            return $true
        }
    }
    
    try {
        & $PythonPath -m venv $VenvPath
        Write-Success "Virtual environment created at $VenvPath"
        return $true
    } catch {
        Write-Err "Failed to create virtual environment: $_"
        return $false
    }
}

# Activate virtual environment and install dependencies
function Install-Dependencies {
    param([string]$VenvPath = "venv")
    
    Write-Info "Installing dependencies..."
    
    # Determine pip path
    if (-not $SkipVenv -and (Test-Path "$VenvPath\Scripts\pip.exe")) {
        $pipPath = "$VenvPath\Scripts\pip.exe"
        $pythonExe = "$VenvPath\Scripts\python.exe"
    } else {
        $pipPath = "pip"
        $pythonExe = $PythonPath
    }
    
    # Upgrade pip first
    try {
        Write-Info "Upgrading pip..."
        & $pythonExe -m pip install --upgrade pip --quiet
        Write-Success "pip upgraded"
    } catch {
        Write-Warn "Could not upgrade pip: $_"
    }
    
    # Install from requirements.txt if it exists
    if (Test-Path "requirements.txt") {
        Write-Info "Installing from requirements.txt..."
        try {
            & $pipPath install -r requirements.txt --quiet
            Write-Success "Dependencies installed from requirements.txt"
        } catch {
            Write-Err "Failed to install dependencies: $_"
            return $false
        }
    } else {
        # Install core dependencies manually
        Write-Info "Installing core dependencies..."
        $packages = @(
            "anthropic",
            "openai",
            "groq",
            "fastapi",
            "uvicorn[standard]",
            "mcp",
            "rich",
            "prompt-toolkit",
            "pyttsx3",
            "pydantic",
            "python-dotenv",
            "aiohttp",
            "httpx"
        )
        
        foreach ($package in $packages) {
            Write-Info "  Installing $package..."
            try {
                & $pipPath install $package --quiet 2>&1 | Out-Null
            } catch {
                Write-Warn "  Could not install $package"
            }
        }
        Write-Success "Core dependencies installed"
    }
    
    return $true
}

# Create .env file template
function New-EnvFile {
    Write-Info "Setting up environment configuration..."
    
    if (Test-Path ".env") {
        Write-Success ".env file already exists"
        return
    }
    
    $envContent = @"
# ALFRED_IV-Y-VI Configuration
# Copy this file to .env and fill in your API keys

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
"@
    
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Success "Created .env from .env.example"
    } else {
        $envContent | Out-File -FilePath ".env" -Encoding UTF8
        Write-Success "Created .env template"
    }
}

# Add to PATH
function Add-ToPath {
    param([string]$InstallDir)
    
    Write-Info "Checking PATH configuration..."
    
    $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
    if ($userPath -notlike "*$InstallDir*") {
        Write-Info "Adding installation directory to PATH..."
        try {
            [Environment]::SetEnvironmentVariable(
                "Path",
                "$userPath;$InstallDir",
                "User"
            )
            $env:Path = "$env:Path;$InstallDir"
            Write-Success "Added to PATH (restart terminal to apply)"
        } catch {
            Write-Warn "Could not add to PATH automatically"
        }
    } else {
        Write-Success "Already in PATH"
    }
}

# Create launcher scripts
function New-LauncherScripts {
    Write-Info "Creating launcher scripts..."
    
    # Windows batch launcher
    $batchContent = @"
@echo off
cd /d "%~dp0"
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)
python main.py %*
"@
    
    $batchContent | Out-File -FilePath "alfred.bat" -Encoding ASCII
    Write-Success "Created alfred.bat"
    
    # PowerShell launcher
    $psContent = @"
`$ErrorActionPreference = "Stop"
Push-Location `$PSScriptRoot
try {
    if (Test-Path "venv\Scripts\Activate.ps1") {
        . .\venv\Scripts\Activate.ps1
    }
    python main.py @args
} finally {
    Pop-Location
}
"@
    
    $psContent | Out-File -FilePath "alfred.ps1" -Encoding UTF8
    Write-Success "Created alfred.ps1"
}

# Show final instructions
function Show-Instructions {
    Write-Host ""
    Write-Host "=" * 60 -ForegroundColor Green
    Write-Host " Installation Complete!" -ForegroundColor Green
    Write-Host "=" * 60 -ForegroundColor Green
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. Configure your API keys:" -ForegroundColor White
    Write-Host "   Edit the .env file and add your API key(s):" -ForegroundColor Gray
    Write-Host ""
    Write-Host '   $env:ANTHROPIC_API_KEY = "your-key"' -ForegroundColor Yellow
    Write-Host '   $env:OPENAI_API_KEY = "your-key"' -ForegroundColor Yellow
    Write-Host '   $env:GROQ_API_KEY = "your-key"' -ForegroundColor Yellow
    Write-Host ""
    Write-Host "2. Activate the virtual environment:" -ForegroundColor White
    Write-Host "   .\venv\Scripts\Activate.ps1" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "3. Run ALFRED:" -ForegroundColor White
    Write-Host "   python main.py" -ForegroundColor Yellow
    Write-Host "   # Or use the launcher:" -ForegroundColor Gray
    Write-Host "   .\alfred.bat" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Documentation: https://github.com/Batdan007/ALFRED_IV-Y-VI" -ForegroundColor DarkGray
    Write-Host ""
}

# Main installation flow
function Install-Alfred {
    Show-Banner
    
    # Check prerequisites
    if (-not (Test-Python)) {
        Write-Err "Installation aborted: Python 3.10+ is required"
        exit 1
    }
    
    Test-Git | Out-Null
    
    # Get installation directory
    $installDir = Get-Location
    Write-Info "Installing to: $installDir"
    
    # Create virtual environment
    if (-not (New-VirtualEnvironment)) {
        Write-Err "Failed to create virtual environment"
        exit 1
    }
    
    # Install dependencies
    if (-not (Install-Dependencies)) {
        Write-Err "Failed to install dependencies"
        exit 1
    }
    
    # Setup environment
    New-EnvFile
    
    # Create launchers
    New-LauncherScripts
    
    # Add to PATH (optional)
    # Add-ToPath -InstallDir $installDir
    
    # Show instructions
    Show-Instructions
}

# Run installation
Install-Alfred
