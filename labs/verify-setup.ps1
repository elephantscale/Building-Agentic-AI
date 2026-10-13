# verify-setup.ps1 - quick pre-flight for the Building Agentic AI labs (Windows / PowerShell).
# PowerShell port of verify-setup.sh. Run from anywhere:  ./labs/verify-setup.ps1
$ErrorActionPreference = "Continue"
$fail = 0
function Ok   ($m) { Write-Host "  PASS  $m" -ForegroundColor Green }
function Warn ($m) { Write-Host "  WARN  $m" -ForegroundColor Yellow }
function Bad  ($m) { Write-Host "  FAIL  $m" -ForegroundColor Red; $script:fail++ }

$labsDir = $PSScriptRoot

Write-Host "Building Agentic AI - lab environment check`n"

# Python 3.11+  (Windows: 'python', not 'python3')
$py = $null
foreach ($c in @("python", "python3", "py")) {
    if (Get-Command $c -ErrorAction SilentlyContinue) { $py = $c; break }
}
if ($py) {
    $ver = & $py -c "import sys;print('%d.%d'%sys.version_info[:2])"
    $parts = $ver.Split(".")
    if ([int]$parts[0] -ge 3 -and [int]$parts[1] -ge 11) { Ok "$py $ver" }
    else { Bad "$py $ver (need 3.11+)" }
} else {
    Bad "python not found"
}

# pip
if ((Get-Command pip -ErrorAction SilentlyContinue) -or (Get-Command pip3 -ErrorAction SilentlyContinue)) {
    Ok "pip present"
} else {
    Bad "pip not found"
}

# .env
$envFile = Join-Path $labsDir ".env"
if (Test-Path $envFile) {
    Ok ".env present"
    $txt = Get-Content $envFile -Raw
    if ($txt -match "OPENAI_API_KEY=sk-")      { Ok   "OPENAI_API_KEY looks set" }    else { Warn "OPENAI_API_KEY not set yet" }
    if ($txt -match "ANTHROPIC_API_KEY=sk-ant") { Ok   "ANTHROPIC_API_KEY looks set" } else { Warn "ANTHROPIC_API_KEY not set yet" }
} else {
    Warn ".env not found - copy .env.example to .env and add your keys"
}

Write-Host ""
if ($fail -eq 0) {
    Write-Host "Environment looks ready." -ForegroundColor Green
    exit 0
} else {
    Write-Host "$fail blocking issue(s). Fix before labs." -ForegroundColor Red
    exit 1
}
