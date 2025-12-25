# Install British Male Voices for Alfred
# George (older gentleman) or Ryan (younger British)
# Author: Daniel J Rita (BATDAN)

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "INSTALLING BRITISH MALE VOICES FOR ALFRED" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

Write-Host "Current problem:" -ForegroundColor Yellow
Write-Host "  - You only have David (US male), Hazel (British FEMALE), Zira (US female)" -ForegroundColor Yellow
Write-Host "  - Alfred needs a BRITISH MALE voice`n" -ForegroundColor Yellow

Write-Host "Target voices:" -ForegroundColor Green
Write-Host "  1. Microsoft George (Older British gentleman) - BEST" -ForegroundColor Green
Write-Host "  2. Microsoft Ryan (Younger British male) - Good" -ForegroundColor Green
Write-Host "  3. Microsoft James (British male) - Alternative`n" -ForegroundColor Green

Write-Host "Installing additional Windows speech voices...`n" -ForegroundColor Cyan

# Method 1: Try to install via Windows Settings
Write-Host "[1/3] Opening Windows Speech Settings..." -ForegroundColor Cyan
Write-Host "       Please install British English (GB) language pack`n"

Start-Process "ms-settings:speech"
Start-Sleep -Seconds 3

# Method 2: PowerShell language pack installation
Write-Host "[2/3] Attempting to install British English language pack..." -ForegroundColor Cyan

try {
    # Install British English language pack
    $LangList = Get-WinUserLanguageList
    $LangList.Add("en-GB")
    Set-WinUserLanguageList $LangList -Force
    Write-Host "       ✅ British English added to language list`n" -ForegroundColor Green
} catch {
    Write-Host "       ⚠️  Could not auto-install. Manual installation needed.`n" -ForegroundColor Yellow
}

# Method 3: Direct voice pack installation
Write-Host "[3/3] Installing speech components..." -ForegroundColor Cyan

try {
    Add-WindowsCapability -Online -Name "Language.Speech~~~en-GB~0.0.1.0"
    Write-Host "       ✅ Speech components installed`n" -ForegroundColor Green
} catch {
    Write-Host "       ⚠️  Requires admin rights or manual installation`n" -ForegroundColor Yellow
}

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "MANUAL INSTALLATION STEPS (if auto-install didn't work):" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

Write-Host "1. Open Settings (Win + I)" -ForegroundColor White
Write-Host "2. Go to: Time & Language > Language & Region" -ForegroundColor White
Write-Host "3. Click 'Add a language'" -ForegroundColor White
Write-Host "4. Search for 'English (United Kingdom)'" -ForegroundColor White
Write-Host "5. Install it with 'Text-to-speech' option checked" -ForegroundColor White
Write-Host "6. Wait for download/install to complete" -ForegroundColor White
Write-Host "7. Restart ALFRED-UBX`n" -ForegroundColor White

Write-Host "After installation, you should have:" -ForegroundColor Green
Write-Host "  - George (older British male) 🎩" -ForegroundColor Green
Write-Host "  - OR Ryan (younger British male) 🎩" -ForegroundColor Green
Write-Host "  - These are PROPER British gentlemen voices!`n" -ForegroundColor Green

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "ALTERNATIVE: Use ElevenLabs for Premium Alfred Voice" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

Write-Host "If Windows voices aren't good enough, we can use ElevenLabs:" -ForegroundColor Yellow
Write-Host "  - Professional voice cloning" -ForegroundColor Yellow
Write-Host "  - Sounds EXACTLY like movie Alfred (Michael Caine/Jeremy Irons)" -ForegroundColor Yellow
Write-Host "  - Cost: ~`$5-11/month" -ForegroundColor Yellow
Write-Host "  - 100% worth it for the experience`n" -ForegroundColor Yellow

Write-Host "To install ElevenLabs:" -ForegroundColor White
Write-Host "  pip install elevenlabs`n" -ForegroundColor White

Write-Host "Press any key to check current voices..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Show current voices
Write-Host "`nCurrent voices installed:" -ForegroundColor Cyan
Add-Type -AssemblyName System.Speech
$synthesizer = New-Object System.Speech.Synthesis.SpeechSynthesizer
foreach ($voice in $synthesizer.GetInstalledVoices()) {
    $name = $voice.VoiceInfo.Name
    $gender = $voice.VoiceInfo.Gender
    $culture = $voice.VoiceInfo.Culture.Name

    $color = "White"
    if ($name -like "*George*" -or $name -like "*Ryan*" -or $name -like "*James*") {
        $color = "Green"
        Write-Host "  ✅ $name ($gender, $culture) - PERFECT FOR ALFRED!" -ForegroundColor $color
    } elseif ($gender -eq "Male") {
        Write-Host "  ⚠️  $name ($gender, $culture) - Male but wrong accent" -ForegroundColor Yellow
    } else {
        Write-Host "  ❌ $name ($gender, $culture) - Female (not suitable)" -ForegroundColor Red
    }
}

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "Next: Run test_voices_simple.py again to hear new voices" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan
