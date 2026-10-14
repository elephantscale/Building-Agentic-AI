# setup-keys.ps1 - put the class API keys in place on the Windows VM (no copy/paste needed).
#
# The class VMs block clipboard sharing, so you cannot paste keys in. Instead, the keys
# arrive as a file on your Desktop (env.txt). This script copies that file to labs/.env,
# which is where every lab reads its keys from. Run it once, from the repo root:
#
#     ./labs/setup-keys.ps1
#
# It does a file copy entirely inside the VM - no typing, no paste.

$ErrorActionPreference = "Stop"
$labsDir  = $PSScriptRoot
$dest     = Join-Path $labsDir ".env"
$desktop  = [Environment]::GetFolderPath("Desktop")

# Accept the common names IT might use for the keys file on the Desktop.
$candidates = @("env.txt", ".env", "keys.txt", "dotenv.txt") | ForEach-Object { Join-Path $desktop $_ }
$src = $candidates | Where-Object { Test-Path $_ } | Select-Object -First 1

if (-not $src) {
    Write-Host "Could not find a keys file on your Desktop." -ForegroundColor Red
    Write-Host "Looked for: env.txt, .env, keys.txt, dotenv.txt in $desktop"
    Write-Host "Ask your instructor where the keys file is, then re-run this script."
    exit 1
}

if (Test-Path $dest) {
    Write-Host "labs\.env already exists - leaving it as is." -ForegroundColor Yellow
    Write-Host "Delete it first if you want to replace it with $src."
    exit 0
}

Copy-Item -LiteralPath $src -Destination $dest
Write-Host "Keys installed: $src -> $dest" -ForegroundColor Green
Write-Host "You're ready. Verify with:  ./labs/verify-setup.ps1"
