# GamePilot — Windows verification script (PowerShell equivalent of verify.sh).
#
# Usage:
#   PS> .\verify.ps1
#
# Exits non-zero if any check fails so this can be used in CI.

$ErrorActionPreference = "Continue"
$failed = 0

function Check ($label, [scriptblock]$test) {
  try {
    if (& $test) {
      Write-Host "[OK] $label" -ForegroundColor Green
    } else {
      Write-Host "[X]  $label" -ForegroundColor Red
      $script:failed++
    }
  } catch {
    Write-Host "[X]  $label  ($($_.Exception.Message))" -ForegroundColor Red
    $script:failed++
  }
}

Write-Host "========================================="
Write-Host "GamePilot Verification (Windows)"
Write-Host "========================================="
Write-Host ""

# 1. Python version
Check "Python 3.10-3.12" {
  $v = & python --version 2>&1
  $v -match "Python 3\.(10|11|12)"
}

# 2. gamepilot package importable
Check "gamepilot package imports" {
  & uv run python -c "import gamepilot" 2>$null
  $LASTEXITCODE -eq 0
}

# 3. Frontend assets present
Check "frontend/colors_and_type.css" { Test-Path "frontend\colors_and_type.css" }
Check "frontend/app.html"            { Test-Path "frontend\app.html" }
Check "frontend/landing.html"        { Test-Path "frontend\landing.html" }
Check "frontend/api.js"              { Test-Path "frontend\api.js" }

# 4. Discover module
Check "discover/steam_client.py"           { Test-Path "gamepilot\app\discover\steam_client.py" }
Check "discover/compatibility.py"          { Test-Path "gamepilot\app\discover\compatibility.py" }
Check "discover/news_service.py"           { Test-Path "gamepilot\app\discover\news_service.py" }
Check "discover/compatibility_index.json"  { Test-Path "gamepilot\app\discover\compatibility_index.json" }

# 5. FastAPI app loads (smoke import)
Check "FastAPI app importable" {
  & uv run python -c "from gamepilot.app.api.server import app; print(len(app.routes))" 2>$null
  $LASTEXITCODE -eq 0
}

# 6. /news endpoint registered
Check "/news endpoint registered" {
  $out = & uv run python -c "from gamepilot.app.api.server import app; print(' '.join(getattr(r,'path','') for r in app.routes))" 2>$null
  ($LASTEXITCODE -eq 0) -and ($out -match "/news")
}

# 7. Bootstrap helper available
Check "scripts/bootstrap.py runs" {
  & python scripts\bootstrap.py --help 2>$null | Out-Null
  $LASTEXITCODE -eq 0
}

# 8. uv on PATH
Check "uv on PATH" {
  Get-Command uv -ErrorAction SilentlyContinue | Out-Null
  $?
}

Write-Host ""
Write-Host "========================================="
if ($failed -eq 0) {
  Write-Host "All checks passed." -ForegroundColor Green
  exit 0
} else {
  Write-Host "$failed check(s) failed." -ForegroundColor Red
  exit 1
}
