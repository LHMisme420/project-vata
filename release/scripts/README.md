# VATA Root Anchor – Public Release

Deterministic anchoring of cryptographic roots to multiple L2 networks
using Foundry Cast and PowerShell.

## Requirements
- Windows
- PowerShell
- Foundry (forge + cast)
- $env:PK set to your private key (no 0x)

## Setup
$env:PK="YOUR_PRIVATE_KEY_WITHOUT_0x"

## Verify
cd scripts
.\verify.ps1 0xYOUR_ROOT

## Anchor
.\anchor.ps1 0xYOUR_ROOT

## Dry run
.\anchor.ps1 0xYOUR_ROOT -DryRun

## Networks
config\networks.json