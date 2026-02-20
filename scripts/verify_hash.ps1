param(
  [Parameter(Mandatory=$true)][string]$ReceiptHash,  # 0x + 64 hex
  [Parameter(Mandatory=$true)][string]$Contract,
  [Parameter(Mandatory=$true)][string]$RpcUrl
)

Set-StrictMode -Version Latest
$ErrorActionPreference="Stop"

function Die($m){ Write-Host "ERROR: $m" -ForegroundColor Red; exit 1 }

$ReceiptHash = $ReceiptHash.Trim()
if(-not($ReceiptHash -match "^0x[0-9a-fA-F]{64}$")){ Die "ReceiptHash must be 0x + 64 hex" }
if(-not($Contract -match "^0x[0-9a-fA-F]{40}$")){ Die "Contract must be 0x + 40 hex" }

$ok = cast call $Contract "isAnchored(bytes32)(bool)" $ReceiptHash --rpc-url $RpcUrl
Write-Host ""
Write-Host "RECEIPT_HASH = $ReceiptHash"
Write-Host "isAnchored   = $ok"
Write-Host ""