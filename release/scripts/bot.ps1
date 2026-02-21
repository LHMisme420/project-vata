# Watches ..\examples\root.txt for changes and anchors automatically.

$ROOT_FILE = "..\examples\root.txt"
$LOG_FILE  = "..\anchor_bot.log"

# Debounce: don't double-trigger on multiple write events
$lastHash = ""

Write-Host "Bot watching: $ROOT_FILE"
Write-Host "Logging to  : $LOG_FILE"
Write-Host "Press Ctrl+C to stop."
Write-Host ""

while ($true) {

    if (Test-Path $ROOT_FILE) {

        $raw = (Get-Content $ROOT_FILE -Raw).Trim()

        if ($raw -match "^0x[0-9a-fA-F]{64}$") {

            $h = (Get-FileHash $ROOT_FILE -Algorithm SHA256).Hash

            if ($h -ne $lastHash) {
                $lastHash = $h

                $ts = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
                Add-Content $LOG_FILE "[$ts] NEW ROOT: $raw"

                Write-Host "[$ts] New root detected. Anchoring..."

                # Anchor (writes tx receipts to console)
                & .\anchor.ps1 $raw

                # Verify again (clean status)
                Add-Content $LOG_FILE "[$ts] VERIFY:"
                $v = & .\verify.ps1 $raw
                Add-Content $LOG_FILE $v
                Add-Content $LOG_FILE ""

                Write-Host "[$ts] Done."
                Write-Host ""
            }
        }
    }

    Start-Sleep -Seconds 5
}