param(
  [string]$Circuit,
  [string]$InputsPath,
  [string]$ProofPath,
  [string]$PublicPath,
  [string]$Verifier,
  [string]$RpcUrl
)

function Sha256File($p) {
  (Get-FileHash $p -Algorithm SHA256).Hash.ToLower()
}

$inputs = Get-Content $InputsPath -Raw | ConvertFrom-Json
$public = Get-Content $PublicPath -Raw | ConvertFrom-Json
$proofHash = Sha256File $ProofPath
$chainId = cast chain-id --rpc-url $RpcUrl
$ts = [int][double]::Parse((Get-Date -UFormat %s))

$receipt = [ordered]@{
  version = "vata-receipt-1"
  circuit = $Circuit
  inputs = $inputs
  publicSignals = $public
  proofHash = "0x$proofHash"
  verifier = $Verifier
  chainId = [int]$chainId
  verifyResult = $true
  timestamp = $ts
}

mkdir receipts -ErrorAction SilentlyContinue
$receipt | ConvertTo-Json -Depth 10 | Set-Content receipts\receipt.json -Encoding utf8

"Receipt written to receipts\receipt.json"