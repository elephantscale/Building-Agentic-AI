# start-here.ps1 - one-command class setup for the Windows VM (no copy/paste needed).
#
# After cloning the repo, run ONE short command from the repo root:
#
#     ./labs/start-here.ps1
#
# It does everything: create the virtualenv, install the pinned packages, copy the
# keys from Desktop\env.txt into labs/.env, prove the libraries import, and run the
# environment check. Nothing to paste, nothing to type beyond that one line.

$ErrorActionPreference = "Stop"
$labsDir  = $PSScriptRoot
$repoRoot = Split-Path $labsDir -Parent
Set-Location $repoRoot

function Step($msg) { Write-Host "`n==> $msg" -ForegroundColor Cyan }

# 1. Virtualenv -------------------------------------------------------------
Step "Creating the virtual environment (.venv)"
$pyLauncher = if (Get-Command py -ErrorAction SilentlyContinue) { "py" } else { "python" }
if (-not (Test-Path ".venv")) {
    & $pyLauncher -m venv .venv
} else {
    Write-Host "  .venv already exists - reusing it."
}
$venvPy = Join-Path $repoRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPy)) { throw "venv python not found at $venvPy" }

# 2. Install the pinned packages -------------------------------------------
Step "Installing pinned packages (this takes a minute or two)"
& $venvPy -m pip install --upgrade pip --quiet
& $venvPy -m pip install -r (Join-Path $labsDir "requirements-lock.txt")

# 3. Keys: Desktop\env.txt -> labs\.env ------------------------------------
Step "Installing API keys from the Desktop"
& (Join-Path $labsDir "setup-keys.ps1")

# 4. Prove the libraries import --------------------------------------------
Step "Checking that the core libraries import"
& $venvPy -c "import openai, anthropic, langgraph, dspy; print('  libraries import OK')"

# 5. Environment check ------------------------------------------------------
Step "Running the environment check"
& (Join-Path $labsDir "verify-setup.ps1")

Write-Host "`nSetup complete." -ForegroundColor Green
Write-Host "To use the environment in this terminal:  .venv\Scripts\Activate.ps1"
