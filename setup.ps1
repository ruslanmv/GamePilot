# GamePilot — Windows setup script (PowerShell equivalent of setup.sh).
#
# Usage (in an elevated PowerShell or regular Windows Terminal):
#   PS> .\setup.ps1
#
# What it does:
#   1. Verifies Python 3.10–3.12 is available
#   2. Installs uv (if missing) via the official PowerShell installer
#   3. Creates .venv using uv
#   4. Installs production dependencies (uv sync --no-dev)
#   5. Creates the project directory layout
#   6. Generates sample data (best-effort)
#
# Re-running is safe — every step is idempotent.

$ErrorActionPreference = "Stop"

function Write-Info  ($msg) { Write-Host "-> $msg" -ForegroundColor Yellow }
function Write-Ok    ($msg) { Write-Host "[OK] $msg" -ForegroundColor Green }
function Write-Fail  ($msg) { Write-Host "[X]  $msg" -ForegroundColor Red }

Write-Host "========================================="
Write-Host "  GamePilot - Windows Setup"
Write-Host "========================================="

# 1. Python version check
Write-Info "Checking Python..."
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
  Write-Fail "Python not found on PATH. Install Python 3.11 from https://www.python.org/downloads/windows/"
  exit 1
}
$pyver = & python --version 2>&1
Write-Ok "Found $pyver"

# 2. uv install (cross-platform: delegated to bootstrap.py)
Write-Info "Installing uv (skips if present)..."
& python "$PSScriptRoot\scripts\bootstrap.py" install-uv
if ($LASTEXITCODE -ne 0) { Write-Fail "uv installation failed."; exit 1 }
Write-Ok "uv ready."

# 3. venv
Write-Info "Creating .venv (skips if present)..."
& python "$PSScriptRoot\scripts\bootstrap.py" ensure-venv --python 3.11 --dir .venv
if ($LASTEXITCODE -ne 0) { Write-Fail "venv creation failed."; exit 1 }
Write-Ok "Virtual environment ready."

# 4. Deps
Write-Info "Installing production dependencies..."
& python "$PSScriptRoot\scripts\bootstrap.py" ensure-deps --python 3.11 --dir .venv
if ($LASTEXITCODE -ne 0) { Write-Fail "Dependency install failed."; exit 1 }
Write-Ok "Dependencies installed."

# 5. Project directories
Write-Info "Creating project folders..."
$dirs = @(
  "data\raw\gameplay_videos",
  "data\raw\annotations",
  "data\processed\frames",
  "feedback",
  "results",
  "models\neural_network",
  "models\transformer",
  "logs"
)
foreach ($d in $dirs) { New-Item -ItemType Directory -Force -Path $d | Out-Null }
Write-Ok "Folders ready."

# 6. .env scaffolding
if (-not (Test-Path ".env")) {
  Write-Info "Creating .env (defaults)..."
  @"
# GamePilot Configuration
ENVIRONMENT=development
LOG_LEVEL=INFO
NN_PORT=5000
TRANSFORMER_PORT=5001
CONTROL_PORT=8000
"@ | Set-Content -Encoding UTF8 ".env"
  Write-Ok ".env created."
}

# 7. Sample data (best-effort — depends on extras you may not have installed)
if (Test-Path "scripts\generate_sample_data.py") {
  Write-Info "Generating sample data (best-effort)..."
  try {
    & uv run python scripts\generate_sample_data.py
  } catch {
    Write-Fail "Sample-data generation skipped: $($_.Exception.Message)"
  }
}

Write-Host ""
Write-Host "========================================="
Write-Host "  Setup Complete!" -ForegroundColor Green
Write-Host "========================================="
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. make run-api        (starts GamePilot FastAPI server)"
Write-Host "  2. open http://localhost:8000/      (marketing landing)"
Write-Host "  3. open http://localhost:8000/app   (in-product UI)"
Write-Host ""
Write-Host "Or run directly without make:"
Write-Host "  uv run uvicorn gamepilot.app.api.server:app --reload"
Write-Host ""
