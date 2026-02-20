# CLEAN_RUN_MIN.ps1
# Clean, repeatable demo run for MINIMAL RootRegistry (anchorRoot + isRoot only)
# Network: OP Sepolia by default
# Requires: $env:PK set (64 hex, with or without 0x)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Step($t) {
  Write-Host ""
  Write-Host "============================================================"
  Write-Host "STEP: $t"
  Write-Host "============================================================"
}

function Pause { Start-Sleep -Seconds 2 }

function NormalizePK($raw) {
  if ([string]::IsNullOrWhiteSpace($raw)) { throw "Missing env var PK" }
  $k = $raw.Trim()
  if ($k.StartsWith("0x")) { $k = $k.Substring(2) }
  if ($k.Length -ne 64 -or ($k -notmatch '^[0-9a-fA-F]{64}$')) {
    throw "PK must be 64 hex chars (optionally prefixed with 0x)"
  }
  return $k
}

function ShortReceipt($tx, $rpc) {
  $r = cast receipt $tx --rpc-url $rpc --json | ConvertFrom-Json
  [PSCustomObject]@{
    txHash  = $r.transactionHash
    status  = $r.status
    block   = $r.blockNumber
    gasUsed = $r.gasUsed
    logs    = ($r.logs | Measure-Object).Count
    to      = $r.to
    from    = $r.from
  }
}

function IsRoot($reg, $root, $rpc) {
  cast call $reg "isRoot(uint256)(bool)" $root --rpc-url $rpc
}

function SendAnchor($reg, $root, $rpc, $pk) {
  (cast send $reg "anchorRoot(uint256)" $root --rpc-url $rpc --private-key $pk --json | ConvertFrom-Json).transactionHash
}

# ---------------- CONFIG ----------------
$RPC = "https://sepolia.optimism.io"

# Your deployed MINIMAL registry
$REG = "0xdE91c6E5606A99A072ab335C1798E2551cE5de14"

$PK = NormalizePK $env:PK

# Fresh demo roots each run
$base = [int](Get-Date -UFormat %s)
$ROOTS = @(
  ($base + 1),
  ($base + 2),
  ($base + 3)
)

# Transcript log
$log = "clean_run_min_" + (Get-Date -Format "yyyyMMdd_HHmmss") + ".log"
Start-Transcript -Path $log | Out-Null

try {

  Step "Environment"
  Pause
  "RPC   = $RPC"
  "CHAIN = " + (cast chain-id --rpc-url $RPC)
  "REG   = $REG"

  Step "Signer"
  Pause
  $ME = cast wallet address --private-key $PK
  if (-not $ME) { throw "Could not derive wallet from PK" }
  "ME    = $ME"

  Step "Contract Code Exists"
  Pause
  $code = cast code $REG --rpc-url $RPC
  if ($code -eq "0x") { throw "No code at REG on this RPC" }
  "BYTECODE LENGTH = $($code.Length)"

  Step "Roots To Anchor"
  Pause
  $ROOTS

  foreach ($R in $ROOTS) {

    Step "Check isRoot BEFORE ($R)"
    Pause
    $before = IsRoot $REG $R $RPC
    "isRoot BEFORE = $before"

    if ($before -eq "true") {
      "SKIP (already true) – choose new roots"
      continue
    }

    Step "Anchor Root ($R)"
    Pause
    $TX = SendAnchor $REG $R $RPC $PK
    "TX = $TX"

    Step "Receipt"
    Pause
    ShortReceipt $TX $RPC | Format-List

    Step "Verify AFTER ($R)"
    Pause
    $after = IsRoot $REG $R $RPC
    "isRoot AFTER  = $after"
    if ($after -ne "true") { throw "Verification failed: isRoot did not become true" }
  }

  Step "Done"
  Pause
  "All roots verified true."

  Step "Log Saved"
  $log
}
finally {
  Stop-Transcript | Out-Null
}
