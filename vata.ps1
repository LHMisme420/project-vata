param(
  [Parameter(Mandatory=$true)]
  [ValidateSet("prove")]
  [string]$Command,

  [Parameter(Mandatory=$true)]
  [string]$InputsPath
)

$CIRCUIT  = "action_verifier"
$RPC      = $env:RPC
$PK       = $env:PK
$VERIFIER = $env:VERIFIER

if (-not $RPC)      { throw "RPC not set" }
if (-not $PK)       { throw "PK not set" }
if (-not $VERIFIER) { throw "VERIFIER not set" }

$BUILD = ".\build\action_verifier_js"
$ZKEY  = ".\build\action_verifier.zkey"

if ($Command -eq "prove") {

  Write-Host "▶ Generating witness..."

  node "$BUILD\generate_witness.js" `
    "$BUILD\action_verifier.wasm" `
    $InputsPath `
    ".\proofs\witness.wtns"

  Write-Host "▶ Proving..."

  snarkjs groth16 prove `
    $ZKEY `
    ".\proofs\witness.wtns" `
    ".\proofs\proof.json" `
    ".\proofs\public.json"

  Write-Host "▶ Local verify..."

  snarkjs groth16 verify `
    ".\build\action_verifier_vkey.json" `
    ".\proofs\public.json" `
    ".\proofs\proof.json"

  Write-Host "▶ Export calldata..."

  $cd = snarkjs zkey export soliditycalldata `
    ".\proofs\public.json" `
    ".\proofs\proof.json"

  # ---------- ROBUST SPLITTER ----------
  $clean = ($cd | Out-String).Replace(" ","").Replace("`n","").Replace("`r","")
  $depth = 0
  $parts = @()
  $buf = ""

  foreach ($ch in $clean.ToCharArray()) {
    if ($ch -eq '[') { $depth++ }
    if ($ch -eq ']') { $depth-- }

    if ($ch -eq ',' -and $depth -eq 0) {
      $parts += $buf
      $buf = ""
    } else {
      $buf += $ch
    }
  }
  $parts += $buf

  if ($parts.Count -ne 4) {
    throw "Could not parse calldata"
  }

  $A = $parts[0]
  $B = $parts[1]
  $C = $parts[2]
  $I = $parts[3]
  # ------------------------------------

  Write-Host "▶ Onchain verify..."

  $res = cast call $VERIFIER `
    "verifyProof(uint256[2],uint256[2][2],uint256[2],uint256[2])(bool)" `
    $A `
    $B `
    $C `
    $I `
    --rpc-url $RPC

  if ($res -notmatch "true") {
    throw "Onchain verification failed"
  }

  Write-Host "▶ Writing receipt..."

  .\scripts\new_receipt.ps1 `
    -Circuit $CIRCUIT `
    -InputsPath $InputsPath `
    -ProofPath ".\proofs\proof.json" `
    -PublicPath ".\proofs\public.json" `
    -Verifier $VERIFIER `
    -RpcUrl $RPC

  Write-Host ""
  Write-Host "PASS"
}