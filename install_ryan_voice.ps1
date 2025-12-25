# Install Microsoft Ryan (British Male) Voice
# Run this as Administrator

Write-Host "Installing Microsoft Ryan (British Male) Voice..." -ForegroundColor Cyan

# Method 1: Using Windows Settings (opens GUI)
Write-Host "`nOpening Windows Speech Settings..." -ForegroundColor Yellow
Start-Process "ms-settings:speech"

Write-Host "`n==================================================================" -ForegroundColor Green
Write-Host "MANUAL INSTALLATION STEPS:" -ForegroundColor Green
Write-Host "==================================================================" -ForegroundColor Green
Write-Host "1. In the Settings window that just opened, scroll down"
Write-Host "2. Click 'Add voices' or 'Manage voices'"
Write-Host "3. Search for 'Ryan' or 'English (United Kingdom)'"
Write-Host "4. Find 'Microsoft Ryan Online (Natural) - English (United Kingdom)'"
Write-Host "5. Click the Download button"
Write-Host "6. Wait for download to complete"
Write-Host ""
Write-Host "Alternative voices if Ryan not available:"
Write-Host "  - Microsoft George (British male)"
Write-Host "  - Any 'English (United Kingdom)' male voice"
Write-Host ""
Write-Host "After installation:"
Write-Host "  - Close Settings"
Write-Host "  - Run: python check_voices.py"
Write-Host "  - Verify Ryan appears in the list"
Write-Host "==================================================================" -ForegroundColor Green

Write-Host "`nPress any key when installation is complete..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

Write-Host "`nVerifying installation..." -ForegroundColor Cyan
python check_voices.py
