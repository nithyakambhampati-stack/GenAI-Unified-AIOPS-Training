<#
  bootstrap_windows.ps1
  ---------------------
  One-shot setup for the shared Windows lab VM (PowerShell).

  Run from the repository root:
      powershell -ExecutionPolicy Bypass -File .\setup\bootstrap_windows.ps1
  Add -InstallClaude to also install Claude Code CLI if it is missing:
      powershell -ExecutionPolicy Bypass -File .\setup\bootstrap_windows.ps1 -InstallClaude

  What it does:
    1. Checks Python 3.11+ and Git are available
    2. Creates a virtual environment in .venv
    3. Installs requirements.txt (and tries the optional embeddings package)
    4. Creates .env from .env.example if you do not have one yet
    5. Checks for the Claude Code CLI (installs it only when -InstallClaude is given)
#>
param([switch]$InstallClaude)

$ErrorActionPreference = "Stop"
# Always work from the repo root, wherever the script was launched from.
Set-Location (Split-Path -Parent $PSScriptRoot)

Write-Host "== 1/5  Checking Python and Git" -ForegroundColor Cyan
# 'py -3.11' uses the Windows Python launcher; fall back to plain 'python'.
$python = $null
if (Get-Command py -ErrorAction SilentlyContinue) { $python = "py -3.11" }
elseif (Get-Command python -ErrorAction SilentlyContinue) { $python = "python" }
if (-not $python) { throw "Python 3.11+ not found. Install it from python.org, then open a NEW terminal." }
if (-not (Get-Command git -ErrorAction SilentlyContinue)) { throw "Git not found. Install Git for Windows, then open a NEW terminal." }

Write-Host "== 2/5  Creating virtual environment (.venv)" -ForegroundColor Cyan
if (-not (Test-Path ".venv")) { Invoke-Expression "$python -m venv .venv" }

Write-Host "== 3/5  Installing Python packages" -ForegroundColor Cyan
# Call the venv's own pip so we do not depend on activation state.
& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
# Optional package: a failure here is fine, the Day 2 demo has an offline fallback.
try { & .\.venv\Scripts\python.exe -m pip install -r requirements-embeddings.txt }
catch { Write-Host "Optional embeddings package not installed (demo will use the toy embedder)." -ForegroundColor Yellow }

Write-Host "== 4/5  Preparing .env" -ForegroundColor Cyan
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env - open it and paste the programme API key: notepad .env" -ForegroundColor Yellow
} else { Write-Host ".env already exists - leaving it untouched." }

Write-Host "== 5/5  Claude Code CLI" -ForegroundColor Cyan
if (Get-Command claude -ErrorAction SilentlyContinue) {
    Write-Host ("Found: " + (claude --version))
} elseif ($InstallClaude) {
    # Official native installer for Windows PowerShell (from the Claude Code documentation).
    Write-Host "Installing Claude Code CLI..."
    Invoke-RestMethod https://claude.ai/install.ps1 | Invoke-Expression
    Write-Host "Done. Close this window and open a NEW terminal so PATH refreshes." -ForegroundColor Yellow
} else {
    Write-Host "Claude Code CLI not found. Re-run with -InstallClaude, or run:  irm https://claude.ai/install.ps1 | iex" -ForegroundColor Yellow
}

Write-Host "`nNext:  .\.venv\Scripts\Activate.ps1   then   python setup\check_environment.py" -ForegroundColor Green
