# Per-app microphone/camera usage from Windows ConsentStore (read-only).
# LastUsedTimeStop == 0 => currently IN USE. Browsers appear under NonPackaged.
$caps = 'microphone','webcam'
foreach ($cap in $caps) {
  Write-Host ""
  Write-Host "==================== $cap ===================="
  $roots = @(
    "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\$cap",
    "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\$cap\NonPackaged"
  )
  $rows = foreach ($root in $roots) {
    if (Test-Path $root) {
      foreach ($k in Get-ChildItem $root) {
        $p = Get-ItemProperty $k.PSPath
        if ($null -ne $p.LastUsedTimeStart) {
          $start = $null
          if ($p.LastUsedTimeStart -gt 0) { $start = [DateTime]::FromFileTime($p.LastUsedTimeStart) }
          $stop = 'IN USE NOW'
          if ($p.LastUsedTimeStop -gt 0) { $stop = [DateTime]::FromFileTime($p.LastUsedTimeStop) }
          [pscustomobject]@{ App = ($k.PSChildName -replace '#','\'); Start = $start; Stop = $stop }
        }
      }
    }
  }
  $rows | Sort-Object Start -Descending | Format-Table -AutoSize
}
