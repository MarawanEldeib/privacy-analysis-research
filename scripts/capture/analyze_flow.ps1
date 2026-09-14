param(
  [Parameter(Mandatory=$true)][string]$Tool,
  [int]$Run = 1
)
# Offline re-analysis of a saved .flow -> writes data\raw\<Tool>\run_<Run>.json
$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $root
Set-Item -Path Env:TOOL_NAME -Value $Tool
Set-Item -Path Env:RUN_ID    -Value ([string]$Run)
$rel = "data\raw\{0}\run_{1}.flow" -f $Tool,$Run
Write-Host ("replaying {0} ..." -f $rel)
& 'F:\python\Scripts\mitmdump.exe' -nr $rel -s 'scripts\capture\capture_addon.py' 2>&1 | Select-Object -Last 5
Write-Host "--- json written? ---"
Get-ChildItem ("data\raw\{0}\run_{1}.json" -f $Tool,$Run) -ErrorAction SilentlyContinue | Select-Object Name,Length
