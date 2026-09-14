# READ-ONLY permission + autostart inventory. Nothing is changed.
# NOTE: holding a permission != misuse. This is an inventory/over-permission flag,
# not malware detection (that is what the AV/Avast step is for).
$ts  = Get-Date -Format 'yyyyMMdd-HHmmss'
$out = "F:\Projects\Research Project - Privacy analysis\results\permission_audit_$ts.txt"
Start-Transcript -Path $out -Force | Out-Null

Write-Host "############ 1. CAPABILITY PERMISSIONS (Windows ConsentStore, ALL categories) ############"
$sensitive = 'location','microphone','webcam','contacts','appointments','phoneCall',
             'phoneCallHistory','email','chat','userDataTasks','userNotificationListener',
             'broadFileSystemAccess','documentsLibrary','picturesLibrary','videosLibrary',
             'downloadsFolder','graphicsCaptureProgrammatic','graphicsCaptureWithoutBorder',
             'humanPresence','sensors','activity','bluetoothSync','radios','cellularData'
$bases = "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore",
         "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore"
$all = foreach ($base in $bases) {
  if (-not (Test-Path $base)) { continue }
  foreach ($capKey in Get-ChildItem $base) {
    $cap = $capKey.PSChildName
    $subs = @($capKey.PSPath)
    $np = Join-Path $capKey.PSPath 'NonPackaged'
    if (Test-Path $np) { $subs += $np }
    foreach ($s in $subs) {
      foreach ($appKey in (Get-ChildItem $s -ErrorAction SilentlyContinue)) {
        if ($appKey.PSChildName -eq 'NonPackaged') { continue }
        $p = Get-ItemProperty $appKey.PSPath
        $last = $null
        if ($p.LastUsedTimeStart -gt 0) { $last = [DateTime]::FromFileTime($p.LastUsedTimeStart) }
        [pscustomobject]@{
          Capability = $cap
          Value      = $p.Value
          App        = ($appKey.PSChildName -replace '#','\')
          LastUsed   = $last
          Sensitive  = ($sensitive -contains $cap)
        }
      }
    }
  }
}
Write-Host "`n--- SENSITIVE capabilities currently ALLOWED (review list) ---"
$all | Where-Object { $_.Sensitive -and $_.Value -eq 'Allow' } | Sort-Object Capability,App | Format-Table Capability,App,LastUsed -AutoSize
Write-Host "`n--- broadFileSystemAccess holders (full-disk read) ---"
$all | Where-Object { $_.Capability -eq 'broadFileSystemAccess' } | Sort-Object Value,App | Format-Table Value,App,LastUsed -AutoSize
Write-Host "`n--- FULL capability x app matrix ---"
$all | Sort-Object Capability,App | Format-Table Capability,Value,App,LastUsed -AutoSize

Write-Host "`n############ 2. AUTOSTART / PERSISTENCE (what runs in the background) ############"
Write-Host "`n--- Run / RunOnce registry keys ---"
$runKeys = 'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run',
           'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run',
           'HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Run',
           'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce',
           'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce'
foreach ($rk in $runKeys) {
  if (Test-Path $rk) {
    Write-Host "  [$rk]"
    (Get-ItemProperty $rk).PSObject.Properties | Where-Object { $_.Name -notmatch '^PS' } | ForEach-Object { Write-Host ("    {0} = {1}" -f $_.Name, $_.Value) }
  }
}
Write-Host "`n--- Startup folders ---"
$sf = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup", "$env:ProgramData\Microsoft\Windows\Start Menu\Programs\Startup"
foreach ($f in $sf) { if (Test-Path $f) { Get-ChildItem $f -ErrorAction SilentlyContinue | ForEach-Object { Write-Host ("    "+$_.FullName) } } }
Write-Host "`n--- Enabled scheduled tasks (non-Microsoft) ---"
Get-ScheduledTask | Where-Object { $_.State -ne 'Disabled' -and $_.TaskPath -notlike '\Microsoft\*' } | ForEach-Object {
  [pscustomobject]@{ Task=$_.TaskName; Path=$_.TaskPath; Run=(($_.Actions|ForEach-Object{$_.Execute}) -join '; ') }
} | Format-Table -AutoSize
Write-Host "`n--- Auto-start services with path outside C:\Windows (third-party) ---"
Get-CimInstance Win32_Service | Where-Object { $_.StartMode -eq 'Auto' -and $_.PathName -and $_.PathName -notmatch 'C:\\Windows' } | Select-Object Name,DisplayName,PathName | Format-Table -AutoSize

Stop-Transcript | Out-Null
Write-Host "`nFull report saved to: $out"
