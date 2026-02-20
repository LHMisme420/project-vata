[CmdletBinding()]
param(
  [Parameter(Mandatory=$true)]
  [string]$BatchDir
)

Set-StrictMode -Version Latest
$ErrorActionPreference="Stop"

function Die($m){ throw $m }

if(-not (Test-Path -LiteralPath $BatchDir)){ Die "BatchDir not found: $BatchDir" }

if(-not $env:ARB_VERIFIER -or $env:ARB_VERIFIER -notmatch '^0x[0-9a-fA-F]{40}$'){
  Die "ARB_VERIFIER env var missing/invalid. Set `$env:ARB_VERIFIER to the deployed ARB verifier address."
}
if(-not $env:OP_VERIFIER -or $env:OP_VERIFIER -notmatch '^0x[0-9a-fA-F]{40}$'){
  Die "OP_VERIFIER env var missing/invalid. Set `$env:OP_VERIFIER to the deployed OP verifier address."
}

Write-Host ""
Write-Host "=== VERIFY (ARB) ==="
.\scripts\l2_verify_proof.ps1 -Net arb -BatchDir $BatchDir

Write-Host ""
Write-Host "=== VERIFY (OP) ==="
.\scripts\l2_verify_proof.ps1 -Net op -BatchDir $BatchDir

Write-Host ""
Write-Host "ALL PASS ✅"