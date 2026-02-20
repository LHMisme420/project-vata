param(
  [Parameter(Mandatory=$true)][string]$RPC,
  [Parameter(Mandatory=$true)][string]$VERIFIER
)

$ErrorActionPreference = "Stop"

# Generate calldata parts (4 top-level args)
$cal = snarkjs zkesc .\zk\public.json .\zk\proof.json

$parts=@(); $buf=""; $depth=0
foreach($ch in $cal.ToCharArray()){
  if($ch -eq '['){$depth++}
  if($ch -eq ']'){$depth--}
  if($ch -eq ',' -and $depth -eq 0){$parts += $buf.Trim(); $buf=""; continue}
  $buf += $ch
}
$parts += $buf.Trim()

if($parts.Count -ne 4){
  throw "Expected 4 calldata parts, got $($parts.Count). Calldata was: $cal"
}

# Build cast args safely (no backticks)
$args = @(
  "call",
  $VERIFIER,
  "verifyProof(uint256[2],uint256[2][2],uint256[2],uint256[1])(bool)",
  $parts[0], $parts[1], $parts[2], $parts[3],
  "--rpc-url", $RPC
)

cast @args
