[CmdletBinding()]
param(
  [Parameter(Mandatory=$true)]
  [string]$BatchDir,

  # Optional override: source claim dir to copy from
  [string]$FromClaimDir
)

Set-StrictMode -Version Latest
$ErrorActionPreference="Stop"

function Die($m){ throw $m }

if(-not (Test-Path -LiteralPath $BatchDir)){ Die "BatchDir not found: $BatchDir" }

# If not provided, pick most recent claim_* dir that contains BOTH proof.json + public.json + witness.wtns
if(-not $FromClaimDir){
  $root = Split-Path -Parent $BatchDir
  $cands = Get-ChildItem -LiteralPath $root -Directory -Filter "claim_*" |
           Sort-Object LastWriteTime -Descending

  foreach($c in $cands){
    $p = Join-Path $c.FullName "proof.json"
    $u = Join-Path $c.FullName "public.json"
    $w = Join-Path $c.FullName "witness.wtns"
    if((Test-Path $p) -and (Test-Path $u) -and (Test-Path $w)){
      $FromClaimDir = $c.FullName
      break
    }
  }
}

if(-not $FromClaimDir){ Die "Could not auto-find a source claim dir containing proof.json + public.json + witness.wtns. Provide -FromClaimDir." }
if(-not (Test-Path -LiteralPath $FromClaimDir)){ Die "FromClaimDir not found: $FromClaimDir" }

$files = @("proof.json","public.json","witness.wtns","claim_meta.json")
foreach($f in $files){
  $src = Join-Path $FromClaimDir $f
  if(Test-Path $src){
    Copy-Item -LiteralPath $src -Destination (Join-Path $BatchDir $f) -Force
  }
}

Write-Host ""
Write-Host "SYNCED claim artifacts"
Write-Host " FROM: $FromClaimDir"
Write-Host "   TO: $BatchDir"
Write-Host ""