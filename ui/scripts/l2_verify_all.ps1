param(
  [Parameter(Mandatory=$true)][string]$BatchDir
)

$ErrorActionPreference = "Stop"

$HERE = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "# Running: scripts\l2_verify_all.ps1 -BatchDir $BatchDir"

& (Join-Path $HERE "l2_verify_arb.ps1") -BatchDir $BatchDir
if ($LASTEXITCODE -ne 0) { exit 1 }

& (Join-Path $HERE "l2_verify_op.ps1") -BatchDir $BatchDir
if ($LASTEXITCODE -ne 0) { exit 1 }

Write-Host ""
Write-Host "ALL PASS ✅"
exit 0
