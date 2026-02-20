param(
  [Parameter(Mandatory=$true)][string]$BatchDir
)

$ErrorActionPreference = "Stop"

$RPC = "https://sepolia-rollup.arbitrum.io/rpc"
$VERIFIER = $env:ARB_VERIFIER

if (-not $VERIFIER) { throw "ARB_VERIFIER is empty. Set `$env:ARB_VERIFIER and restart UI." }

$CAST = "$env:USERPROFILE\.foundry\bin\cast.exe"
if (-not (Test-Path $CAST)) { $CAST = "cast.exe" }

$PROOF  = Join-Path $BatchDir "proof.json"
$PUBLIC = Join-Path $BatchDir "public.json"

if (-not (Test-Path $PROOF))  { throw "Missing: $PROOF" }
if (-not (Test-Path $PUBLIC)) { throw "Missing: $PUBLIC" }

# Public signals length
$PUB = Get-Content $PUBLIC -Raw | ConvertFrom-Json
$PUB_LEN = $PUB.Count

if ($PUB_LEN -ne 1) { throw "PUB_LEN=$PUB_LEN. This verifier expects 1 public signal." }

$SIG = "verifyProof(uint256[2],uint256[2][2],uint256[2],uint256[1])(bool)"

# Load proof/public fields (snarkjs format)
$p = Get-Content $PROOF -Raw | ConvertFrom-Json

$A = "[{0},{1}]" -f $p.pi_a[0], $p.pi_a[1]
$B = "[[{0},{1}],[{2},{3}]]" -f $p.pi_b[0][1],$p.pi_b[0][0],$p.pi_b[1][1],$p.pi_b[1][0]
$C = "[{0},{1}]" -f $p.pi_c[0], $p.pi_c[1]
$PUB1 = "[{0}]" -f $PUB[0]

Write-Host ""
Write-Host "=== VERIFY (ARB) ==="
Write-Host ""
Write-Host ("NET      = arb")
Write-Host ("RPC      = {0}" -f $RPC)
Write-Host ("VERIFIER = {0}" -f $VERIFIER)
Write-Host ("PROOF    = {0}" -f $PROOF)
Write-Host ("PUBLIC   = {0}" -f $PUBLIC)
Write-Host ("PUB_LEN  = {0}" -f $PUB_LEN)
Write-Host ("SIG      = {0}" -f $SIG)
Write-Host ""

$CMD = "$CAST call $VERIFIER `"$SIG`" $A $B $C $PUB1 --rpc-url $RPC"
Write-Host ("RUN: " + $CMD)
Write-Host ""

# Execute
$RESULT = & $CAST call $VERIFIER $SIG $A $B $C $PUB1 --rpc-url $RPC
$RESULT = $RESULT.Trim()

Write-Host ("RESULT = " + $RESULT)

if ($RESULT -eq "true") { Write-Host "PASS"; exit 0 }
Write-Host "FAIL"
exit 1

