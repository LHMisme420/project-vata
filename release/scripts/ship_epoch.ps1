param(
  [Parameter(Mandatory=$true)][string]$ROOT,
  [string]$EPOCH = "0002",
  [string]$OP_REG="0xe0C202DF9D1d0187d84f4b94c8966cA6CD9c4d8e",
  [string]$ARB_REG="0x1a88C73407e349F91E5C1DDb03e1300d24e2cC35",
  [string]$OP_RPC="https://sepolia.optimism.io",
  [string]$ARB_RPC="https://sepolia-rollup.arbitrum.io/rpc",
  [switch]$Commit
)

if (-not $env:PK) { throw "env:PK not set" }

New-Item -ItemType Directory -Force receipts | Out-Null

function Anchor-And-Verify($name, $reg, $rpc, $root) {
  Write-Host "== $name =="

  $before = (cast call $reg "isRoot(uint256)(bool)" $root --rpc-url $rpc).Trim()
  Write-Host "isRoot before: $before"

  if ($before -ne "true") {
    Write-Host "Anchoring..."
    $out = cast send $reg "anchorRoot(uint256)" $root --rpc-url $rpc --private-key $env:PK
    $tx  = ($out | Select-String "transactionHash" | ForEach-Object { $_.ToString().Split()[-1] })
    if (-not $tx) { $tx = "UNKNOWN_TX_HASH (cast output parse failed)" }
  } else {
    $tx = "ALREADY_ANCHORED"
  }

  $after = (cast call $reg "isRoot(uint256)(bool)" $root --rpc-url $rpc).Trim()
  Write-Host "isRoot after : $after"

  if ($after -ne "true") { throw "$name verify failed" }

  return @{
    Tx = $tx
    Verified = $after
  }
}

$op  = Anchor-And-Verify "Optimism Sepolia" $OP_REG $OP_RPC $ROOT
$arb = Anchor-And-Verify "Arbitrum Sepolia" $ARB_REG $ARB_RPC $ROOT

$FILE = "receipts\epoch-$EPOCH.md"
$ts = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")

@"
# VATA Epoch $EPOCH

Timestamp (local):
$ts

Root (uint256):
$ROOT

---

## Optimism Sepolia
RPC: $OP_RPC  
Registry: $OP_REG  
Anchor Tx: $($op.Tx)  
Verify: $($op.Verified)

Command:
cast call $OP_REG "isRoot(uint256)(bool)" $ROOT --rpc-url $OP_RPC

---

## Arbitrum Sepolia
RPC: $ARB_RPC  
Registry: $ARB_REG  
Anchor Tx: $($arb.Tx)  
Verify: $($arb.Verified)

Command:
cast call $ARB_REG "isRoot(uint256)(bool)" $ROOT --rpc-url $ARB_RPC
"@ | Set-Content $FILE

Write-Host "`nReceipts written to $FILE"
Write-Host "PASS: Root anchored + verified on OP + ARB"

if ($Commit) {
  git add $FILE | Out-Null
  git commit -m "Add Epoch $EPOCH receipts (OP+ARB)" | Out-Null
  git tag "epoch-$EPOCH" | Out-Null
  Write-Host "Committed + tagged epoch-$EPOCH"
}