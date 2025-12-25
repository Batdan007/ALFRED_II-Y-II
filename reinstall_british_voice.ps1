# Reinstall British Male Voices for Alfred
# Author: Daniel J Rita (BATDAN)

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "REINSTALLING BRITISH MALE VOICES FOR ALFRED" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

Write-Host "Current situation:" -ForegroundColor Yellow
Write-Host "  - You have Hazel (British FEMALE)" -ForegroundColor White
Write-Host "  - You NEED George or Ryan (British MALE)`n" -ForegroundColor Red

Write-Host "Opening Windows Settings for manual reinstall...`n" -ForegroundColor Cyan

# Open settings
Start-Process "ms-settings:regionlanguage"
Start-Sleep -Seconds 2

Write-Host "============================================================" -ForegroundColor Green
Write-Host "MANUAL INSTALLATION STEPS" -ForegroundColor Green
Write-Host "============================================================`n" -ForegroundColor Green

Write-Host "STEP 1: Remove old English (GB) language pack" -ForegroundColor Cyan
Write-Host "  - In Settings, find 'English (United Kingdom)'" -ForegroundColor White
Write-Host "  - Click ... (three dots) next to it" -ForegroundColor White
Write-Host "  - Click 'Remove'" -ForegroundColor White
Write-Host "  - Confirm removal`n" -ForegroundColor White

Write-Host "STEP 2: Add English (GB) back with ALL features" -ForegroundColor Cyan
Write-Host "  - Click 'Add a language'" -ForegroundColor White
Write-Host "  - Search for 'English (United Kingdom)'" -ForegroundColor White
Write-Host "  - Select it and click Next" -ForegroundColor White
Write-Host "  - IMPORTANT: Check ALL boxes:" -ForegroundColor Yellow
Write-Host "    [✓] Install language pack" -ForegroundColor Yellow
Write-Host "    [✓] Text-to-speech" -ForegroundColor Yellow
Write-Host "    [✓] Speech recognition" -ForegroundColor Yellow
Write-Host "    [✓] Handwriting" -ForegroundColor Yellow
Write-Host "  - Click Install`n" -ForegroundColor White

Write-Host "STEP 3: Wait for download" -ForegroundColor Cyan
Write-Host "  - This may take 5-10 minutes" -ForegroundColor White
Write-Host "  - Don't close Settings until complete" -ForegroundColor White
Write-Host "  - You'll see a checkmark when done`n" -ForegroundColor White

Write-Host "STEP 4: Restart Windows" -ForegroundColor Red
Write-Host "  - Close all programs" -ForegroundColor White
Write-Host "  - Restart your computer" -ForegroundColor White
Write-Host "  - This is REQUIRED for voices to load`n" -ForegroundColor Yellow

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "ALTERNATIVE: Quick PowerShell Install (may not work)" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

$response = Read-Host "Try automated PowerShell install? (y/n)"

if ($response -eq 'y') {
    Write-Host "`nAttempting automated install..." -ForegroundColor Yellow

    Write-Host "[1/3] Removing old en-GB..." -ForegroundColor Cyan
    try {
        $LangList = Get-WinUserLanguageList
        $ToRemove = $LangList | Where-Object { $_.LanguageTag -eq "en-GB" }
        if ($ToRemove) {
            $LangList.Remove($ToRemove)
            Set-WinUserLanguageList $LangList -Force
            Write-Host "  Done`n" -ForegroundColor Green
        }
    } catch {
        Write-Host "  Failed`n" -ForegroundColor Red
    }

    Start-Sleep -Seconds 2

    Write-Host "[2/3] Adding en-GB back..." -ForegroundColor Cyan
    try {
        $LangList = Get-WinUserLanguageList
        $LangList.Add("en-GB")
        Set-WinUserLanguageList $LangList -Force
        Write-Host "  Done`n" -ForegroundColor Green
    } catch {
        Write-Host "  Failed`n" -ForegroundColor Red
    }

    Write-Host "[3/3] Installing speech..." -ForegroundColor Cyan
    try {
        Add-WindowsCapability -Online -Name "Language.Speech~~~en-GB~0.0.1.0"
        Write-Host "  Done`n" -ForegroundColor Green
    } catch {
        Write-Host "  Failed (need admin)`n" -ForegroundColor Red
    }

    Write-Host "Automated install attempted." -ForegroundColor Yellow
    Write-Host "You STILL need to restart Windows!`n" -ForegroundColor Red
}

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "AFTER RESTART" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

Write-Host "Run this to test:" -ForegroundColor Green
Write-Host "  python test_voices_simple.py`n" -ForegroundColor White

Write-Host "You should see:" -ForegroundColor Green
Write-Host "  Microsoft George (British Male) - PERFECT!" -ForegroundColor Green
Write-Host "  Microsoft Ryan (British Male) - PERFECT!" -ForegroundColor Green

Write-Host "`nPress any key to see current voices..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

Write-Host "`nCurrent voices:" -ForegroundColor Cyan
Add-Type -AssemblyName System.Speech
$synthesizer = New-Object System.Speech.Synthesis.SpeechSynthesizer
foreach ($voice in $synthesizer.GetInstalledVoices()) {
    $name = $voice.VoiceInfo.Name
    $gender = $voice.VoiceInfo.Gender
    $culture = $voice.VoiceInfo.Culture.Name

    if ($name -like "*George*" -or $name -like "*Ryan*") {
        Write-Host "  [OK] $name - $gender - $culture" -ForegroundColor Green
    } else {
        Write-Host "  [  ] $name - $gender - $culture" -ForegroundColor Gray
    }
}

Write-Host "`n============================================================" -ForegroundColor Red
Write-Host "REMEMBER: RESTART WINDOWS for voices to load!" -ForegroundColor Red
Write-Host "============================================================`n" -ForegroundColor Red
