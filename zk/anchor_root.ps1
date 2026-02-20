param(
  [Parameter(Mandatory=$true)][string]$RPC,
  [Parameter(Mandatory=$true)][string]$REGISTRY,
  [Parameter(Mandatory=$true)][string]$ROOT,
  [Parameter(Mandatory=$true)][string]$PRIVATE_KEY
)

$ErrorActionPreference = "Stop"

if ($REGISTRY -notmatch '^0x[0-9a-fA-F]{40}$') { throw "Bad REGISTRY: $REGISTRY" }

# Send anchor tx
$tx = cast send $REGISTRY "anchorRoot(uint256)" $ROOT --rpc-url $RPC --private-key $PRIVATE_KEY
"TX=$tx"

# Confirm stored
$res = cast call $REGISTRY "isRoot(uint256)(bool)" $ROOT --rpc-url $RPC
"IS_ROOT=$res"
