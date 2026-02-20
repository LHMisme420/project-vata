param(
  [string]$ReceiptDir = "receipts",
  [string]$OutDir = "merkle"
)

function Sha256HexOfHex($hex) {
  # hex string -> bytes -> SHA256 -> hex string
  $bytes = for ($i = 0; $i -lt $hex.Length; $i += 2) {
    [Convert]::ToByte($hex.Substring($i,2),16)
  }
  $sha = [System.Security.Cryptography.SHA256]::Create()
  ($sha.ComputeHash($bytes) | ForEach-Object { $_.ToString("x2") }) -join ""
}

# Force array semantics
$files = @(Get-ChildItem $ReceiptDir -Filter *.json -File)

if ($files.Length -eq 0) {
  throw "No receipts found in '$ReceiptDir' (expected *.json)"
}

# Deterministic ordering (important!)
$files = $files | Sort-Object Name

# Leaf hashes are SHA256(file bytes) via Get-FileHash
$leaves = @()
foreach ($f in $files) {
  $h = (Get-FileHash $f.FullName -Algorithm SHA256).Hash.ToLower()
  $leaves += $h
}

mkdir $OutDir -ErrorAction SilentlyContinue | Out-Null

# Save leaves + manifest for auditability
$leafLines = @()
for ($i=0; $i -lt $files.Length; $i++) {
  $leafLines += ("{0}`t{1}`t{2}" -f $i, $leaves[$i], $files[$i].Name)
}
$leafLines | Set-Content (Join-Path $OutDir "leaves.tsv") -Encoding utf8
$leaves    | Set-Content (Join-Path $OutDir "leaves.txt") -Encoding utf8

# Build Merkle levels
$levels = @()
$levels += ,$leaves

$current = $leaves
while ($current.Length -gt 1) {
  $next = @()
  for ($i = 0; $i -lt $current.Length; $i += 2) {
    $left = $current[$i]
    $right = if ($i + 1 -lt $current.Length) { $current[$i+1] } else { $current[$i] } # duplicate last if odd
    $next += (Sha256HexOfHex ($left + $right))
  }
  $levels += ,$next
  $current = $next
}

$root = $current[0]
$root | Set-Content (Join-Path $OutDir "root.txt") -Encoding ascii

# Save full tree for proof generation later
$treeObj = [ordered]@{
  version = "vata-merkle-1"
  hash = "sha256"
  leafHash = "sha256(file)"
  leafOrder = "sorted_by_filename"
  receiptDir = $ReceiptDir
  leafCount = $leaves.Length
  root = "0x$root"
  levels = $levels
  files = ($files | ForEach-Object { $_.Name })
}
$treeObj | ConvertTo-Json -Depth 50 | Set-Content (Join-Path $OutDir "tree.json") -Encoding utf8

"Merkle leafCount = $($leaves.Length)"
"Merkle root      = 0x$root"
"Written:"
"  $OutDir\leaves.tsv"
"  $OutDir\leaves.txt"
"  $OutDir\root.txt"
"  $OutDir\tree.json"