# Fix LangSmith CLI Issue - Complete Fix
# This script removes the conflicting global langsmith installation AND leftover executables

Write-Host "Fixing LangSmith CLI conflict..." -ForegroundColor Yellow
Write-Host ""

# Step 1: Uninstall global langsmith package (if exists)
Write-Host "Step 1: Removing global langsmith package..." -ForegroundColor Cyan
try {
    python -m pip uninstall -y langsmith 2>$null
    Write-Host "  ✅ Package uninstalled (or was already removed)" -ForegroundColor Green
} catch {
    Write-Host "  ℹ️  Package was not installed" -ForegroundColor Gray
}

Write-Host ""

# Step 2: Remove leftover executable files
Write-Host "Step 2: Removing leftover executable files..." -ForegroundColor Cyan

$scriptsPath = "$env:APPDATA\Python\Python312\Scripts"
$langsmithExe = Join-Path $scriptsPath "langsmith.exe"

if (Test-Path $langsmithExe) {
    try {
        Remove-Item $langsmithExe -Force
        Write-Host "  ✅ Removed: $langsmithExe" -ForegroundColor Green
    } catch {
        Write-Host "  ❌ Failed to remove: $langsmithExe" -ForegroundColor Red
        Write-Host "  Please delete this file manually" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ℹ️  No langsmith.exe found in global Scripts" -ForegroundColor Gray
}

Write-Host ""
Write-Host "=" * 60 -ForegroundColor Green
Write-Host "✅ LangSmith CLI Fix Complete!" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Green
Write-Host ""
Write-Host "The langsmith package in your virtual environment (.venv) is intact." -ForegroundColor Cyan
Write-Host ""
Write-Host "To verify the fix worked:" -ForegroundColor Yellow
Write-Host "  1. Activate venv:  .venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "  2. Test CLI:       python -m langsmith --version" -ForegroundColor White
Write-Host ""
Write-Host "Note: Use 'python -m langsmith' instead of just 'langsmith'" -ForegroundColor Cyan
