# Install British Male Voices - ADMIN VERSION
# Run this with administrator privileges
# Author: Daniel J Rita (BATDAN)

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "BRITISH VOICE INSTALLATION (ADMIN MODE)" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

# Check if running as admin
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ERROR: Not running as administrator!" -ForegroundColor Red
    Write-Host "`nTo fix:" -ForegroundColor Yellow
    Write-Host "1. Right-click PowerShell" -ForegroundColor White
    Write-Host "2. Select 'Run as administrator'" -ForegroundColor White
    Write-Host "3. Run this script again`n" -ForegroundColor White
    exit 1
}

Write-Host "Running as administrator - Good!`n" -ForegroundColor Green

# Remove old speech capability
Write-Host "[1/3] Removing old speech capability..." -ForegroundColor Cyan
try {
    Remove-WindowsCapability -Online -Name "Language.Speech~~~en-GB~0.0.1.0" -ErrorAction SilentlyContinue | Out-Null
    Write-Host "      Done`n" -ForegroundColor Green
} catch {
    Write-Host "      (Not found, skipping)`n" -ForegroundColor Gray
}

Start-Sleep -Seconds 2

# Install speech capability
Write-Host "[2/3] Installing British English speech (with male voices)..." -ForegroundColor Cyan
Write-Host "      This downloads George/Ryan voices - may take 2-5 minutes..." -ForegroundColor Yellow

try {
    $result = Add-WindowsCapability -Online -Name "Language.Speech~~~en-GB~0.0.1.0"

    if ($result.RestartNeeded) {
        Write-Host "      Installation complete!`n" -ForegroundColor Green
        Write-Host "      RESTART REQUIRED`n" -ForegroundColor Red
    } else {
        Write-Host "      Installation complete!`n" -ForegroundColor Green
    }
} catch {
    Write-Host "      ERROR: $_`n" -ForegroundColor Red
    Write-Host "      You may need to:" -ForegroundColor Yellow
    Write-Host "      1. Check internet connection" -ForegroundColor White
    Write-Host "      2. Update Windows" -ForegroundColor White
    Write-Host "      3. Try manual installation`n" -ForegroundColor White
    exit 1
}

# Install Text-to-Speech capability
Write-Host "[3/3] Installing Text-to-Speech capability..." -ForegroundColor Cyan
try {
    Add-WindowsCapability -Online -Name "Language.TextToSpeech~~~en-GB~0.0.1.0" -ErrorAction SilentlyContinue | Out-Null
    Write-Host "      Done`n" -ForegroundColor Green
} catch {
    Write-Host "      (Already installed or not needed)`n" -ForegroundColor Gray
}

# Check installed voices
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "CHECKING INSTALLED VOICES" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

Add-Type -AssemblyName System.Speech
$synthesizer = New-Object System.Speech.Synthesis.SpeechSynthesizer
$found_george = $false
$found_ryan = $false

foreach ($voice in $synthesizer.GetInstalledVoices()) {
    $name = $voice.VoiceInfo.Name
    $gender = $voice.VoiceInfo.Gender
    $culture = $voice.VoiceInfo.Culture.Name

    if ($name -like "*George*") {
        Write-Host "  [PERFECT!] $name ($gender, $culture)" -ForegroundColor Green
        $found_george = $true
    } elseif ($name -like "*Ryan*") {
        Write-Host "  [PERFECT!] $name ($gender, $culture)" -ForegroundColor Green
        $found_ryan = $true
    } elseif ($name -like "*James*") {
        Write-Host "  [GOOD!] $name ($gender, $culture)" -ForegroundColor Green
    } elseif ($gender -eq "Male" -and $culture -like "*GB*") {
        Write-Host "  [OK] $name ($gender, $culture)" -ForegroundColor Yellow
    } else {
        Write-Host "  [  ] $name ($gender, $culture)" -ForegroundColor Gray
    }
}

Write-Host "`n============================================================" -ForegroundColor Cyan

if ($found_george -or $found_ryan) {
    Write-Host "SUCCESS! British male voice installed!" -ForegroundColor Green
    Write-Host "`nYou can test it now with:" -ForegroundColor Green
    Write-Host "  python test_voices_simple.py`n" -ForegroundColor White
} else {
    Write-Host "Voices installed but not yet visible" -ForegroundColor Yellow
    Write-Host "`nRESTART WINDOWS to load new voices!`n" -ForegroundColor Red
}

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "INSTALLATION COMPLETE" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

Write-Host "Next steps:" -ForegroundColor White
Write-Host "1. RESTART WINDOWS (required for voices to load)" -ForegroundColor Red
Write-Host "2. After restart, test with: python test_voices_simple.py" -ForegroundColor Yellow
Write-Host "3. You should hear George or Ryan speaking!`n" -ForegroundColor Green

Write-Host "Press any key to exit..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
