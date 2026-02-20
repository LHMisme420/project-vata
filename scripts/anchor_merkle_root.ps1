param(
  [Parameter(Mandatory=$true)]
  [string]$Anchor,          # ReceiptAnchor contract address

  [Parameter(Mandatory=$true)]
  [string]$RpcUrl,

  [Parameter(Mandatory=$true)]
  [string]$PrivateKey,

  [string]$MerkleDir = "merkle"
)

$rootPath = Join-Path $MerkleDir "root.txt"
if (-not (Test-Path $rootPath)) {
  throw "Missing $rootPath. Run .\scripts\build_merkle.ps1 first."
}

$rootHex = (Get-Content $rootPath -Raw).Trim()
if ($rootHex.Length -ne 64) {
  throw "root.txt must be 64 hex chars (no 0x). Got length=$($rootHex.Length)"
}

$root = "0x$rootHex"
"ROOT = $root"

# idempotent check
$anch = cast call $Anchor "isAnchored(bytes32)(bool)" $root --rpc-url $RpcUrl
if ($anch -match "true") {
  "Already anchored: $root"
} else {
  "Anchoring root..."
  $tx = cast send $Anchor "anchor(bytes32)" $root --rpc-url $RpcUrl --private-key $PrivateKey
  $tx
}

# snapshot batch
$ts = Get-Date -Format "yyyyMMdd_HHmmss"
$batchDir = Join-Path $MerkleDir ("batches\batch_" + $ts)
mkdir $batchDir -Force | Out-Null

copy (Join-Path $MerkleDir "root.txt")     (Join-Path $batchDir "root.txt")     -Force
copy (Join-Path $MerkleDir "leaves.txt")   (Join-Path $batchDir "leaves.txt")   -Force
copy (Join-Path $MerkleDir "leaves.tsv")   (Join-Path $batchDir "leaves.tsv")   -Force
copy (Join-Path $MerkleDir "tree.json")    (Join-Path $batchDir "tree.json")    -Force

# store anchor address + chainId for provenance
$chainId = cast chain-id --rpc-url $RpcUrl
@"
anchor=$Anchor
chainId=$chainId
root=$root
timestamp=$ts
"@ | Set-Content (Join-Path $batchDir "batch_meta.txt") -Encoding utf8

"Batch snapshot: $batchDir"