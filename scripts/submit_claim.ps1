param(
  [Parameter(Mandatory=$true)][string]$File,
  [Parameter(Mandatory=$true)][string]$Contract,     # ReceiptAnchor address (has anchor(bytes32))
  [Parameter(Mandatory=$true)][string]$RpcUrl,
  [Parameter(Mandatory=$true)][string]$PrivateKey
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Die([string]$m) { Write-Host "ERROR: $m" -ForegroundColor Red; exit 1 }
function Must([bool]$c, [string]$m) { if(-not $c){ Die $m } }

# --- Normalize PK (allow raw or 0x) ---
$PrivateKey = $PrivateKey.Trim()
if ($PrivateKey.StartsWith("0x")) { $PrivateKey = $PrivateKey.Substring(2) }
Must ($PrivateKey -match "^[0-9a-fA-F]{64}$") "PrivateKey must be 64 hex chars (optionally 0x-prefixed)"

Must (Test-Path $File) "File not found: $File"
Must ($Contract -match "^0x[0-9a-fA-F]{40}$") "Contract must be 0x + 40 hex"
Must (-not [string]::IsNullOrWhiteSpace($RpcUrl)) "RpcUrl is empty"

# --- Batch folder ---
$STAMP = (Get-Date).ToString("yyyyMMdd_HHmmss")
$BATCH = Join-Path "merkle\batches" ("claim_" + $STAMP)
New-Item -ItemType Directory -Force -Path $BATCH | Out-Null

$LOG = Join-Path $BATCH "run.log"
"START $(Get-Date -Format o)" | Set-Content -Encoding utf8 $LOG

# --- Hash file to receiptHash(bytes32) ---
$H = (Get-FileHash $File -Algorithm SHA256).Hash.ToLower()
$RECEIPT = "0x$H"  # bytes32

Copy-Item $File (Join-Path $BATCH (Split-Path $File -Leaf)) -Force

@"
{
  "file": "$File",
  "sha256": "$RECEIPT",
  "contract": "$Contract",
  "rpc": "$RpcUrl",
  "type": "ReceiptAnchor.anchor(bytes32)"
}
"@ | Set-Content (Join-Path $BATCH "claim_meta.json") -Encoding utf8

Write-Host ""
Write-Host "FILE        = $File"
Write-Host "RECEIPT_HASH = $RECEIPT"
Write-Host "CONTRACT     = $Contract"
Write-Host "BATCH        = $BATCH"
Write-Host ""

# --- Send tx: anchor(bytes32) (NONPAYABLE: do NOT send value) ---
Write-Host "Anchoring receipt hash..." -ForegroundColor Cyan

$txOut = & cast send $Contract `
  "anchor(bytes32)" `
  $RECEIPT `
  --rpc-url $RpcUrl `
  --private-key $PrivateKey 2>&1

$exit = $LASTEXITCODE
$txOut | Tee-Object -FilePath (Join-Path $BATCH "tx.txt") | Out-Null

if ($exit -ne 0) {
  Die "cast send failed (exit=$exit). See $BATCH\tx.txt"
}

$txText = ($txOut | Out-String)
if ($txText -notmatch "0x[0-9a-fA-F]{64}") {
  Die "No tx hash detected. See $BATCH\tx.txt"
}

# --- Verify anchored ---
$ok = & cast call $Contract "isAnchored(bytes32)(bool)" $RECEIPT --rpc-url $RpcUrl 2>&1
$okExit = $LASTEXITCODE
$ok | Tee-Object -FilePath (Join-Path $BATCH "verify.txt") | Out-Null

if ($okExit -ne 0) {
  Die "Verification call failed. See $BATCH\verify.txt"
}

Write-Host ""
Write-Host "===============================" -ForegroundColor Green
Write-Host "CLAIM ANCHORED ✅" -ForegroundColor Green
Write-Host "===============================" -ForegroundColor Green
Write-Host $txText.Trim()
Write-Host "isAnchored = $($ok.ToString().Trim())"
Write-Host ""

@"
FILE:        $File
SHA256:      $RECEIPT
CONTRACT:    $Contract
RPC:         $RpcUrl
BATCH:       $BATCH

Verify:
cast call $Contract "isAnchored(bytes32)(bool)" $RECEIPT --rpc-url $RpcUrl
"@ | Set-Content (Join-Path $BATCH "PROOF.md") -Encoding utf8