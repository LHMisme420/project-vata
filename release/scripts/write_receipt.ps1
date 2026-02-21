param(
  [string]$ROOT,
  [string]$OP_REG="0xe0C202DF9D1d0187d84f4b94c8966cA6CD9c4d8e",
  [string]$ARB_REG="0x1a88C73407e349F91E5C1DDb03e1300d24e2cC35",
  [string]$OP_RPC="https://sepolia.optimism.io",
  [string]$ARB_RPC="https://sepolia-rollup.arbitrum.io/rpc",
  [string]$OP_TX="0x2b4ea282ba531820562bcb4394f4307265f0e770e72d8975d770d379ab5ee6c5",
  [string]$ARB_TX="0x69c4383761e4c6dbff4926b30afea1896371c22bec1f27b72f28de8a8dbb38fa",
  [string]$EPOCH="0001"
)

New-Item -ItemType Directory -Force receipts | Out-Null

$op_ok = (cast call $OP_REG "isRoot(uint256)(bool)" $ROOT --rpc-url $OP_RPC).Trim()
$arb_ok = (cast call $ARB_REG "isRoot(uint256)(bool)" $ROOT --rpc-url $ARB_RPC).Trim()

if ($op_ok -ne "true") { throw "OP verification failed" }
if ($arb_ok -ne "true") { throw "ARB verification failed" }

$FILE = "receipts\epoch-$EPOCH.md"

@"
# VATA Epoch $EPOCH

Root:
$ROOT

---

## Optimism Sepolia
Registry: $OP_REG  
Anchor Tx: $OP_TX  

Verify:
cast call $OP_REG "isRoot(uint256)(bool)" $ROOT --rpc-url $OP_RPC  
Result: true

---

## Arbitrum Sepolia
Registry: $ARB_REG  
Anchor Tx: $ARB_TX  

Verify:
cast call $ARB_REG "isRoot(uint256)(bool)" $ROOT --rpc-url $ARB_RPC  
Result: true
"@ | Set-Content $FILE

Write-Host ""
Write-Host "Receipts written to $FILE"
Write-Host "PASS: Root verified on Optimism + Arbitrum"