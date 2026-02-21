param(
    [Parameter(Mandatory=$true)]
    [string]$Root
)

# Validate root
if (-not ($Root -match "^0x[0-9a-fA-F]{64}$")) {
    Write-Host "ERROR: Invalid root format. Expected 0x + 64 hex chars."
    exit 1
}

# Load networks (raw prevents line-by-line issues)
try {
    $networks = Get-Content "..\config\networks.json" -Raw | ConvertFrom-Json
} catch {
    Write-Host "ERROR: Failed to parse ..\config\networks.json"
    Write-Host $_.Exception.Message
    exit 1
}

foreach ($n in $networks.PSObject.Properties) {

    $name = $n.Name
    $rpc  = $n.Value.rpc
    $reg  = $n.Value.registry

    Write-Host "=============================="
    Write-Host "Network : $name"
    Write-Host "RPC     : $rpc"
    Write-Host "Registry: $reg"
    Write-Host "=============================="

    if ($reg -eq "0x0000000000000000000000000000000000000000") {
        Write-Host "Skipping $name (registry not set)"
        Write-Host ""
        continue
    }

    cast call $reg "isRoot(uint256)" $Root `
        --rpc-url $rpc `
        --insecure `
        --rpc-timeout 20

    Write-Host ""
}