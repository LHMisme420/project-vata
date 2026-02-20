<#
.SYNOPSIS
  Anchor a root on OP Sepolia or Arbitrum Sepolia registry and confirm it is stored.

.EXAMPLE
  .\scripts\l2_anchor_root.ps1 -Net arb -Root 192170... -PrivateKey $env:PK
  .\scripts\l2_anchor_root.ps1 -Net op  -Root  0x2a... -PrivateKey $env:PK
#>

[CmdletBinding()]
param(
  [Parameter(Mandatory=$true)]
  [ValidateSet("op","arb")]
  [string]$Net,

  [Parameter(Mandatory=$true)]
  [string]$Root,

  [Parameter(Mandatory=$true)]
  [string]$PrivateKey,

  # Optional overrides
  [string]$RpcUrl,
  [string]$Registry,

  [switch]$Legacy
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Die($msg) { throw $msg }

function Assert-Addr([string]$name, [string]$addr) {
  if (-not $addr -or ($addr -notmatch '^0x[0-9a-fA-F]{40}$')) {
    Die ("Bad {0} address for {1}: {2}" -f $name, $Net, $addr)
  }
}

function Assert-PK([string]$pk) {
  $p = $pk.Trim()
  if ($p.StartsWith("0x")) { $p = $p.Substring(2) }
  if ($p -notmatch '^[0-9a-fA-F]{64}$') { Die "PrivateKey must be 64 hex chars (with or without 0x)." }
  return $p
}

function To-UIntString([string]$x) {
  $s = ([string]$x).Trim()
  if ($s -match '^0x[0-9a-fA-F]+$') {
    $hex = $s.Substring(2)
    $bi = [System.Numerics.BigInteger]::Parse("0" + $hex, [System.Globalization.NumberStyles]::AllowHexSpecifier)
    return $bi.ToString()
  }
  if ($s -notmatch '^\d+$') { Die ("Root must be uint decimal or 0x hex. Got: {0}" -f $s) }
  return $s
}

# -------------------- Defaults --------------------
$NETCFG = @{
  op  = @{
    RpcUrl   = "https://sepolia.optimism.io"
    # If you have OP registry address, put it here or set env var OP_REGISTRY or pass -Registry
    Registry = $env:OP_REGISTRY
  }
  arb = @{
    RpcUrl   = "https://sepolia-rollup.arbitrum.io/rpc"
    Registry = $env:ARB_REGISTRY
  }
}

if (-not $NETCFG.ContainsKey($Net)) { Die ("Unknown Net: {0}" -f $Net) }

if (-not $RpcUrl)   { $RpcUrl   = $NETCFG[$Net].RpcUrl }
if (-not $Registry) { $Registry = $NETCFG[$Net].Registry }

Assert-Addr "registry" $Registry

$pkClean = Assert-PK $PrivateKey
$rootU = To-UIntString $Root

Write-Host ""
Write-Host ("NET      = {0}" -f $Net)
Write-Host ("RPC      = {0}" -f $RpcUrl)
Write-Host ("REGISTRY = {0}" -f $Registry)
Write-Host ("ROOT(U)  = {0}" -f $rootU)
Write-Host ""

# 1) Pre-check
try {
  $pre = & cast call $Registry "isRoot(uint256)(bool)" $rootU --rpc-url $RpcUrl 2>$null
  if ($pre) {
    Write-Host ("isRoot BEFORE = {0}" -f $pre.Trim())
    if ($pre.Trim() -match 'true|1') {
      Write-Host "Already anchored ✅"
      exit 0
    }
  }
} catch {
  # not fatal
}

# 2) Send anchor tx
$sendArgs = @(
  "cast","send",
  $Registry,
  "anchorRoot(uint256)",
  $rootU,
  "--rpc-url",$RpcUrl,
  "--private-key",$pkClean
)
if ($Legacy) { $sendArgs += "--legacy" }

Write-Host ("RUN: {0}" -f ($sendArgs -join " "))
$txOut = & $sendArgs 2>&1 | Out-String
$txOut = $txOut.Trim()

Write-Host ""
Write-Host $txOut
Write-Host ""

# 3) Post-check
$post = & cast call $Registry "isRoot(uint256)(bool)" $rootU --rpc-url $RpcUrl 2>&1 | Out-String
$post = $post.Trim()

Write-Host ("isRoot AFTER  = {0}" -f $post)

if ($post -match 'true|1') {
  Write-Host "PASS ✅ Root is anchored on-chain."
  exit 0
} else {
  Write-Host "WARN ⚠️ anchor tx sent, but isRoot() did not return true yet."
  Write-Host "If you just broadcasted, wait for inclusion/finality and re-run the script."
  exit 1
}