<#
    conn_audit.ps1 — per-process TCP endpoint audit for native desktop clients.

    Purpose: confirm whether a native app (e.g. Grammarly desktop) sends any
    traffic that BYPASSES the mitmproxy system proxy. Run this WITH the proxy ON.

      * RemoteAddress 127.0.0.1 : port 8080  -> went through mitmproxy (we captured it)
      * any other PUBLIC RemoteAddress        -> BYPASSED the proxy (a channel we cannot see)

    Usage:
        .\scripts\capture\conn_audit.ps1                 # audits *grammarly* + notepad, 60s
        .\scripts\capture\conn_audit.ps1 -Seconds 90 -Match 'grammarly','notepad','deepl'
#>
param(
    [int]$Seconds = 60,
    [string[]]$Match = @('grammarly','notepad')
)

$deadline = (Get-Date).AddSeconds($Seconds)
$seen = @{}
Write-Host ("Auditing processes matching: {0}  for {1}s ..." -f ($Match -join ', '), $Seconds) -ForegroundColor Cyan

while ((Get-Date) -lt $deadline) {
    $procs = Get-Process -ErrorAction SilentlyContinue | Where-Object {
        $n = $_.ProcessName
        $Match | Where-Object { $n -like "*$_*" }
    }
    foreach ($p in $procs) {
        $conns = Get-NetTCPConnection -OwningProcess $p.Id -State Established -ErrorAction SilentlyContinue
        foreach ($c in $conns) {
            $key = "{0}:{1}" -f $c.RemoteAddress, $c.RemotePort
            if (-not $seen.ContainsKey($key)) {
                $seen[$key] = $p.ProcessName
            }
        }
    }
    Start-Sleep -Milliseconds 700
}

Write-Host "`n=== Established remote endpoints (proxy should be ON) ===" -ForegroundColor Yellow
$bypass = @()
$seen.GetEnumerator() | Sort-Object Name | ForEach-Object {
    $addr = ($_.Name -split ':')[0]
    $isLocal = ($addr -eq '127.0.0.1' -or $addr -eq '::1')
    $tag = if ($isLocal) { 'via-mitmproxy' } else { 'DIRECT (bypass!)' ; }
    if (-not $isLocal) { $bypass += $_.Name }
    "{0,-30}  {1,-16}  <- {2}" -f $_.Name, $tag, $_.Value
}

Write-Host "`n=== VERDICT ===" -ForegroundColor Yellow
if ($bypass.Count -eq 0) {
    Write-Host "All monitored-process connections went to 127.0.0.1:8080 -> fully proxied, no hidden channel." -ForegroundColor Green
} else {
    Write-Host ("{0} DIRECT connection(s) bypassed the proxy (list above) -> a channel our capture cannot see:" -f $bypass.Count) -ForegroundColor Red
    $bypass | ForEach-Object { "   $_" }
    Write-Host "(Public 443 endpoints here would need transparent-proxy/Frida to inspect.)"
}
