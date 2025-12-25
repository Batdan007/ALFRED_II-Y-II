# Auto-Install British Male Voices (No Prompts)
# Author: Daniel J Rita (BATDAN)

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "AUTOMATED BRITISH VOICE INSTALLATION" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

Write-Host "Attempting automated install of George/Ryan voices...`n" -ForegroundColor Yellow

# Step 1: Remove old en-GB
Write-Host "[1/4] Removing old English (GB)..." -ForegroundColor Cyan
try {
    $LangList = Get-WinUserLanguageList
    $ToRemove = $LangList | Where-Object { $_.LanguageTag -eq "en-GB" }
    if ($ToRemove) {
        $LangList.Remove($ToRemove)
        Set-WinUserLanguageList $LangList -Force
        Write-Host "      Removed!`n" -ForegroundColor Green
    } else {
        Write-Host "      Not found (skipping)`n" -ForegroundColor Gray
    }
} catch {
    Write-Host "      Failed: $_`n" -ForegroundColor Red
}

Start-Sleep -Seconds 3

# Step 2: Add en-GB back
Write-Host "[2/4] Adding English (GB) to language list..." -ForegroundColor Cyan
try {
    $LangList = Get-WinUserLanguageList
    $LangList.Add("en-GB")
    Set-WinUserLanguageList $LangList -Force
    Write-Host "      Added!`n" -ForegroundColor Green
} catch {
    Write-Host "      Failed: $_`n" -ForegroundColor Red
}

Start-Sleep -Seconds 3

# Step 3: Install speech components
Write-Host "[3/4] Installing speech components..." -ForegroundColor Cyan
Write-Host "      This may take a few minutes...`n" -ForegroundColor Yellow

try {
    # Remove old first
    Remove-WindowsCapability -Online -Name "Language.Speech~~~en-GB~0.0.1.0" -ErrorAction SilentlyContinue | Out-Null
    Start-Sleep -Seconds 2

    # Install fresh
    Add-WindowsCapability -Online -Name "Language.Speech~~~en-GB~0.0.1.0" | Out-Null
    Write-Host "      Speech installed!`n" -ForegroundColor Green
} catch {
    Write-Host "      Failed: $_" -ForegroundColor Red
    Write-Host "      (This often requires admin rights)`n" -ForegroundColor Yellow
}

# Step 4: Install additional features
Write-Host "[4/4] Installing additional language features..." -ForegroundColor Cyan

$features = @(
    "Language.Basic~~~en-GB~0.0.1.0",
    "Language.TextToSpeech~~~en-GB~0.0.1.0"
)

foreach ($feature in $features) {
    try {
        Add-WindowsCapability -Online -Name $feature -ErrorAction SilentlyContinue | Out-Null
    } catch {
        # Silent fail
    }
}

Write-Host "      Done!`n" -ForegroundColor Green

# Check current voices
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "CURRENT VOICES (before restart)" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

Add-Type -AssemblyName System.Speech
$synthesizer = New-Object System.Speech.Synthesis.SpeechSynthesizer
$found_british_male = $false

foreach ($voice in $synthesizer.GetInstalledVoices()) {
    $name = $voice.VoiceInfo.Name
    $gender = $voice.VoiceInfo.Gender
    $culture = $voice.VoiceInfo.Culture.Name

    if ($name -like "*George*" -or $name -like "*Ryan*" -or $name -like "*James*") {
        Write-Host "  [PERFECT!] $name ($gender, $culture)" -ForegroundColor Green
        $found_british_male = $true
    } elseif ($gender -eq "Male") {
        Write-Host "  [MALE] $name ($gender, $culture)" -ForegroundColor Yellow
    } else {
        Write-Host "  [Female] $name ($gender, $culture)" -ForegroundColor Gray
    }
}

Write-Host "`n============================================================" -ForegroundColor Cyan

if ($found_british_male) {
    Write-Host "SUCCESS! British male voice found!" -ForegroundColor Green
    Write-Host "No restart needed - George/Ryan already available!`n" -ForegroundColor Green
} else {
    Write-Host "British male voice NOT YET VISIBLE" -ForegroundColor Yellow
    Write-Host "`nRESTART WINDOWS NOW to load the new voices!`n" -ForegroundColor Red
}

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "NEXT STEPS" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

if ($found_british_male) {
    Write-Host "Test now:" -ForegroundColor Green
    Write-Host "  python test_voices_simple.py`n" -ForegroundColor White
} else {
    Write-Host "1. RESTART WINDOWS (required!)" -ForegroundColor Red
    Write-Host "2. After restart, run:" -ForegroundColor Yellow
    Write-Host "   python test_voices_simple.py`n" -ForegroundColor White
}

Write-Host "You should hear George or Ryan speaking!`n" -ForegroundColor Green
