param(
  [Parameter(Mandatory=$true)][string]$ReceiptJson,
  [Parameter(Mandatory=$true)][string]$Contract,
  [Parameter(Mandatory=$true)][string]$RpcUrl,
  [Parameter(Mandatory=$true)][string]$PrivateKey
)

Set-StrictMode -Version Latest
$ErrorActionPreference="Stop"

function Die($m){ Write-Host "ERROR: $m" -ForegroundColor Red; exit 1 }
function Must($c,$m){ if(-not $c){ Die $m } }

$PrivateKey=$PrivateKey.Trim()
if($PrivateKey.StartsWith("0x")){ $PrivateKey=$PrivateKey.Substring(2) }
Must ($PrivateKey -match "^[0-9a-fA-F]{64}$") "Bad private key"
Must (Test-Path $ReceiptJson) "File not found: $ReceiptJson"
Must ($Contract -match "^0x[0-9a-fA-F]{40}$") "Bad contract"
Must (-not [string]::IsNullOrWhiteSpace($RpcUrl)) "RpcUrl empty"

# Canonicalize JSON (stable)
$obj = Get-Content $ReceiptJson -Raw | ConvertFrom-Json
$canon = ($obj | ConvertTo-Json -Depth 100 -Compress)

# Hash canonical string as UTF8
$bytes = [System.Text.Encoding]::UTF8.GetBytes($canon)
$sha = [System.Security.Cryptography.SHA256]::Create()
$hashBytes = $sha.ComputeHash($bytes)
$hex = ($hashBytes | ForEach-Object { $_.ToString("x2") }) -join ""
$receiptHash = "0x$hex"

Write-Host ""
Write-Host "RECEIPT_JSON = $ReceiptJson"
Write-Host "RECEIPT_HASH = $receiptHash"
Write-Host ""

$txOut = & cast send $Contract "anchor(bytes32)" $receiptHash --rpc-url $RpcUrl --private-key $PrivateKey 2>&1
$exit = $LASTEXITCODE
$txOut | Out-Host
if($exit -ne 0){ Die "cast send failed" }

$ok = cast call $Contract "isAnchored(bytes32)(bool)" $receiptHash --rpc-url $RpcUrl
Write-Host "isAnchored = $ok"
Write-Host ""