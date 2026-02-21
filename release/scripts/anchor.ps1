param(
  [Parameter(Mandatory=$true)]
  [string]$Root
)

$networks = Get-Content "..\config\networks.json" | ConvertFrom-Json

foreach ($n in $networks.PSObject.Properties) {

    $rpc = $n.Value.rpc
    $reg = $n.Value.registry
if ($reg -eq "0x0000000000000000000000000000000000000000") {
    Write-Host "Skipping $($n.Name) (registry not set)"
    Write-Host ""
    continue
}

    Write-Host "Anchoring on $($n.Name)..."

    cast send $reg "anchorRoot(uint256)" $Root `
      --rpc-url $rpc `
      --private-key $env:PK

    $ok = cast call $reg "isRoot(uint256)" $Root --rpc-url $rpc

    Write-Host "Verify: $ok"
    Write-Host ""
}