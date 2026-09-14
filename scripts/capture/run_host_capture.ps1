param(
  [Parameter(Mandatory=$true)][string]$Tool,
  [int]$Run = 1
)
# Host-phase capture launcher (Windows). Launches mitmdump DETACHED so it survives
# the parent shell / MCP disconnects. Uses RELATIVE paths (no spaces) via -WorkingDirectory
# to avoid arg-splitting. Writes data\raw\<Tool>\run_<Run>.json (+ .flow).
$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
# kill any existing mitmdump so we never stack captures
Get-Process mitmdump -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 1
$raw  = Join-Path $root ("data\raw\{0}" -f $Tool)
New-Item -ItemType Directory -Force -Path $raw | Out-Null
$relFlow = "data\raw\{0}\run_{1}.flow" -f $Tool,$Run
$log = Join-Path $raw ("run_{0}.mitm.log" -f $Run)
Remove-Item (Join-Path $root $relFlow) -ErrorAction SilentlyContinue
Set-Item -Path Env:TOOL_NAME -Value $Tool
Set-Item -Path Env:RUN_ID    -Value ([string]$Run)
$mitmArgs = @('--listen-host','127.0.0.1','--listen-port','8080','--ssl-insecure',
              '--save-stream-file', $relFlow, '-s', 'scripts\capture\capture_addon.py')
$p = Start-Process -FilePath 'F:\python\Scripts\mitmdump.exe' -ArgumentList $mitmArgs `
        -WorkingDirectory $root -WindowStyle Hidden -PassThru -RedirectStandardError $log
Start-Sleep -Seconds 4
$listening = (Test-NetConnection 127.0.0.1 -Port 8080 -WarningAction SilentlyContinue).TcpTestSucceeded
Write-Host ("mitmdump PID={0}  listening8080={1}  -> data\raw\{2}\run_{3}.json" -f $p.Id,$listening,$Tool,$Run)
if (-not $listening) { Write-Host '--- mitm log tail ---'; Get-Content $log -Tail 15 -ErrorAction SilentlyContinue }
