[CmdletBinding()]
param(
  [Parameter(Mandatory=$true)]
  [string]$BatchDir,

  # Optional: where proof/public already exist
  [string]$ProofSrcDir
)

Set-StrictMode -Version Latest
$ErrorActionPreference="Stop"

function Die($m){ throw $m }
function AsArray($o){ if($null -eq $o){ @() } elseif($o -is [array]){ @($o) } else { @($o) } }

if(-not (Test-Path -LiteralPath $BatchDir)){ Die "BatchDir not found: $BatchDir" }

# Where to search by default (adjustable)
$roots = @()
if($ProofSrcDir){
  if(-not (Test-Path -LiteralPath $ProofSrcDir)){ Die "ProofSrcDir not found: $ProofSrcDir" }
  $roots += (Resolve-Path -LiteralPath $ProofSrcDir).Path
} else {
  # Common places relative to repo root
  $roots += (Resolve-Path ".").Path
  $roots += (Join-Path (Resolve-Path ".").Path "build")
  $roots += (Join-Path (Resolve-Path ".").Path "verifier\build")
  $roots += (Join-Path (Resolve-Path ".").Path "evidence\verifier\build")
  $roots += (Join-Path (Resolve-Path ".").Path "merkle\build")
}

# Collect candidate files named like proof/public
$proofCand = @()
$pubCand   = @()

foreach($r in $roots){
  if(Test-Path -LiteralPath $r){
    $proofCand += @(Get-ChildItem -LiteralPath $r -Recurse -File -Filter "*proof*.json" -ErrorAction SilentlyContinue)
    $pubCand   += @(Get-ChildItem -LiteralPath $r -Recurse -File -Filter "*public*.json" -ErrorAction SilentlyContinue)
    $pubCand   += @(Get-ChildItem -LiteralPath $r -Recurse -File -Filter "*signal*.json" -ErrorAction SilentlyContinue)
  }
}

# Prefer newest
$proofCand = @($proofCand | Sort-Object LastWriteTime -Descending | Select-Object -Unique)
$pubCand   = @($pubCand   | Sort-Object LastWriteTime -Descending | Select-Object -Unique)

if($proofCand.Count -eq 0){
  Die "Could not find any *proof*.json in search roots. Provide -ProofSrcDir that contains proof.json."
}
if($pubCand.Count -eq 0){
  Die "Could not find any *public*.json/*signal*.json in search roots. Provide -ProofSrcDir that contains public.json."
}

$proofSrc = $proofCand[0].FullName
$pubSrc   = $pubCand[0].FullName

$proofDst = Join-Path $BatchDir "proof.json"
$pubDst   = Join-Path $BatchDir "public.json"

Copy-Item -LiteralPath $proofSrc -Destination $proofDst -Force
Copy-Item -LiteralPath $pubSrc   -Destination $pubDst   -Force

Write-Host ""
Write-Host "EXPORTED:"
Write-Host " proof:  $proofSrc"
Write-Host "   ->   $proofDst"
Write-Host " public: $pubSrc"
Write-Host "   ->   $pubDst"
Write-Host ""