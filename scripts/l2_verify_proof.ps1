[CmdletBinding()]
param(
  [Parameter(Mandatory=$true)]
  [ValidateSet("op","arb")]
  [string]$Net,

  [Parameter(Mandatory=$true)]
  [string]$BatchDir,

  [string]$ProofPath,
  [string]$PublicPath,

  [string]$RpcUrl,
  [string]$Verifier
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Die([string]$msg){ throw $msg }
function CountOf($obj){ if($null -eq $obj){0} elseif($obj -is [System.Collections.ICollection]){$obj.Count} else {1} }
function AsArray($obj){ if($null -eq $obj){@()} elseif($obj -is [array]){@($obj)} else {@($obj)} }

function Assert-Addr([string]$name,[string]$addr){
  if(-not $addr -or ($addr -notmatch '^0x[0-9a-fA-F]{40}$')){
    Die ("Bad {0} address for {1}: {2}" -f $name,$Net,$addr)
  }
}

function Strip-Bom([string]$s){ return ($s -replace "^\uFEFF","") }
function Read-Json([string]$path){
  $raw = Get-Content -LiteralPath $path -Raw
  $raw = Strip-Bom $raw
  return ($raw | ConvertFrom-Json)
}

function ToUInt($x){
  if($null -eq $x){ Die "Null value where uint expected." }
  $s = ([string]$x).Trim()
  if($s -match '^0x[0-9a-fA-F]+$'){
    $hex=$s.Substring(2)
    $bi=[System.Numerics.BigInteger]::Parse("0"+$hex,[System.Globalization.NumberStyles]::AllowHexSpecifier)
    return $bi.ToString()
  }
  if($s -notmatch '^\d+$'){ Die ("Not uint: {0}" -f $s) }
  return $s
}

function NormalizePublic($publicObj){
  if($null -eq $publicObj){ return @() }
  if($publicObj -is [array]){ return @($publicObj) }
  if($publicObj -is [string]){ return @($publicObj) }

  try{
    $props = AsArray $publicObj.PSObject.Properties
    if((CountOf $props) -gt 0){
      $allNumeric=$true
      foreach($p in $props){ if($p.Name -notmatch '^\d+$'){ $allNumeric=$false; break } }
      $vals=@()
      if($allNumeric){
        foreach($p in ($props | Sort-Object { [int]$_.Name })){ $vals += $p.Value }
      } else {
        foreach($p in $props){ $vals += $p.Value }
      }
      return @($vals)
    }
  } catch {}

  return @($publicObj)
}

function ExtractSnarkjsProof($obj){
  try{ if($obj.pi_a -and $obj.pi_b -and $obj.pi_c){ return $obj } } catch {}
  try{ if($obj.proof -and $obj.proof.pi_a -and $obj.proof.pi_b -and $obj.proof.pi_c){ return $obj.proof } } catch {}
  return $null
}

function FindFiles($dir){
  if(-not (Test-Path -LiteralPath $dir)){ Die ("BatchDir not found: {0}" -f $dir) }

  if($ProofPath -and $PublicPath){
    return @{ Proof=(Resolve-Path -LiteralPath $ProofPath).Path; Public=(Resolve-Path -LiteralPath $PublicPath).Path }
  }

  $json = @(Get-ChildItem -LiteralPath $dir -Recurse -File -Filter "*.json" -ErrorAction SilentlyContinue)
  if((CountOf $json) -eq 0){ Die ("No JSON files found under BatchDir: {0}" -f $dir) }

  $pickedProof=$null
  $pickedPublic=$null

  # Proof: scan ALL json for pi_a/pi_b/pi_c
  foreach($f in ($json | Sort-Object LastWriteTime -Descending)){
    try{
      $o = Read-Json $f.FullName
      $p = ExtractSnarkjsProof $o
      if($p){ $pickedProof = $f.FullName; break }
    } catch { continue }
  }

  # Public: prefer public.json or *public* / *signal*
  $publicCands = @()
  $publicCands += @($json | Where-Object { $_.Name -ieq "public.json" })
  $publicCands += @($json | Where-Object { $_.Name -match 'public|signal' })
  $publicCands  = @($publicCands | Sort-Object LastWriteTime -Descending | Select-Object -Unique)

  foreach($f in $publicCands){
    try{
      $o = Read-Json $f.FullName
      $arr = NormalizePublic $o
      $null = CountOf $arr
      $pickedPublic = $f.FullName
      break
    } catch { continue }
  }

  if(-not $pickedProof){ Die ("Could not find a Groth16 proof json (pi_a/pi_b/pi_c) under BatchDir: {0}" -f $dir) }
  if(-not $pickedPublic){ Die ("Could not find a public signals json under BatchDir: {0}" -f $dir) }

  return @{ Proof=$pickedProof; Public=$pickedPublic }
}

function BuildCalldata($proofAny,$publicAny){
  $p = ExtractSnarkjsProof $proofAny
  if(-not $p){ Die "Proof JSON does not contain snarkjs Groth16 fields pi_a/pi_b/pi_c." }

  $pubArr = NormalizePublic $publicAny

  $a0=ToUInt $p.pi_a[0]; $a1=ToUInt $p.pi_a[1]
  $b00=ToUInt $p.pi_b[0][0]; $b01=ToUInt $p.pi_b[0][1]
  $b10=ToUInt $p.pi_b[1][0]; $b11=ToUInt $p.pi_b[1][1]
  $c0=ToUInt $p.pi_c[0]; $c1=ToUInt $p.pi_c[1]

  $pub=@()
  foreach($v in AsArray $pubArr){ $pub += (ToUInt $v) }

  return @{
    A=@($a0,$a1)
    B=@(@($b01,$b00),@($b11,$b10))
    C=@($c0,$c1)
    Pub=$pub
  }
}

# Defaults
$CFG=@{
  op  = @{ rpc="https://sepolia.optimism.io";            ver=$env:OP_VERIFIER  }
  arb = @{ rpc="https://sepolia-rollup.arbitrum.io/rpc"; ver=$env:ARB_VERIFIER }
}

if(-not $CFG.ContainsKey($Net)){ Die ("Unknown Net: {0}" -f $Net) }
if(-not $RpcUrl){ $RpcUrl = $CFG[$Net].rpc }
if(-not $Verifier){ $Verifier = $CFG[$Net].ver }
Assert-Addr "verifier" $Verifier

# Ensure cast exists
$castCmd = Get-Command cast -ErrorAction SilentlyContinue
if(-not $castCmd){ Die "Foundry 'cast' not found in PATH. Open a shell where 'cast' works, or reinstall Foundry." }
$cast = $castCmd.Source

$found = FindFiles $BatchDir
$ProofPath  = $found.Proof
$PublicPath = $found.Public

$proofObj  = Read-Json $ProofPath
$publicObj = Read-Json $PublicPath

$cd = BuildCalldata $proofObj $publicObj

$pubLen = CountOf $cd.Pub
$sig = ("verifyProof(uint256[2],uint256[2][2],uint256[2],uint256[{0}])(bool)" -f $pubLen)

$aArg="[" + ($cd.A -join ",") + "]"
$bArg="[[{0}],[{1}]]" -f (($cd.B[0]) -join ","), (($cd.B[1]) -join ",")
$cArg="[" + ($cd.C -join ",") + "]"
$pArg="[" + ($cd.Pub -join ",") + "]"

Write-Host ""
Write-Host ("NET      = {0}" -f $Net)
Write-Host ("RPC      = {0}" -f $RpcUrl)
Write-Host ("VERIFIER = {0}" -f $Verifier)
Write-Host ("PROOF    = {0}" -f $ProofPath)
Write-Host ("PUBLIC   = {0}" -f $PublicPath)
Write-Host ("PUB_LEN  = {0}" -f $pubLen)
Write-Host ("SIG      = {0}" -f $sig)
Write-Host ""

# IMPORTANT: invoke cast with an argument array (NOT a single string)
$args = @(
  "call",
  $Verifier,
  $sig,
  $aArg,
  $bArg,
  $cArg,
  $pArg,
  "--rpc-url",
  $RpcUrl
)

Write-Host ("RUN: {0} {1}" -f $cast, ($args -join " "))

$out = & $cast @args 2>&1 | Out-String
$out = $out.Trim()

Write-Host ""
Write-Host ("RESULT = {0}" -f $out)

if($out -match 'true' -or $out -match '1'){
  Write-Host "PASS"
  exit 0
}else{
  Write-Host "FAIL"
  exit 1
}