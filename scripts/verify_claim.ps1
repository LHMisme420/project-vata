param(
  [Parameter(Mandatory=$true)][string]$File,
  [Parameter(Mandatory=$true)][string]$Contract,
  [Parameter(Mandatory=$true)][string]$RpcUrl
)

Set-StrictMode -Version Latest
$ErrorActionPreference="Stop"

function Die($m){ Write-Host "ERROR: $m" -ForegroundColor Red; exit 1 }
if(-not(Test-Path $File)){ Die "File not found: $File" }
if(-not($Contract -match "^0x[0-9a-fA-F]{40}$")){ Die "Bad contract address" }

$h=(Get-FileHash $File -Algorithm SHA256).Hash.ToLower()
$receipt="0x$h"

$ok = cast call $Contract "isAnchored(bytes32)(bool)" $receipt --rpc-url $RpcUrl
Write-Host ""
Write-Host "FILE        = $File"
Write-Host "RECEIPT_HASH = $receipt"
Write-Host "isAnchored   = $ok"
Write-Host ""