param(
  [Parameter(Mandatory=$true)][string]$Tool,
  [int]$Run = 1
)
$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Get-Process mitmdump -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 1
$rel  = "data\raw\{0}\run_{1}.flow" -f $Tool,$Run
$json = Join-Path $root ("data\raw\{0}\run_{1}.json" -f $Tool,$Run)
$rlog = Join-Path $root ("data\raw\{0}\run_{1}.replay.log" -f $Tool,$Run)
Remove-Item $json -ErrorAction SilentlyContinue
Set-Item -Path Env:TOOL_NAME -Value $Tool
Set-Item -Path Env:RUN_ID    -Value ([string]$Run)
$a = @('-nr', $rel, '-s', 'scripts\capture\capture_addon.py')
$p = Start-Process -FilePath 'F:\python\Scripts\mitmdump.exe' -ArgumentList $a `
       -WorkingDirectory $root -WindowStyle Hidden -PassThru -RedirectStandardOutput $rlog
Write-Host ("replay started detached PID={0} (reading {1})" -f $p.Id, $rel)
