param([int]$Seconds = 90)
# Keep the Word doc focused and "active" for $Seconds so Grammarly scans it and
# Office connected-experiences (augloop) run. Navigation keys only — NO text edits.
$ws = New-Object -ComObject WScript.Shell
$deadline = (Get-Date).AddSeconds($Seconds)
$i = 0
while ((Get-Date) -lt $deadline) {
  [void]$ws.AppActivate('test-document.docx')
  Start-Sleep -Milliseconds 400
  # gentle reading motion; arrows/PageDown/PageUp never modify the document
  $ws.SendKeys('{PGDN}')
  Start-Sleep -Milliseconds 800
  $ws.SendKeys('{PGUP}')
  $i++
  Start-Sleep -Seconds 12
}
Write-Host ("capture window done: {0}s, {1} activity cycles" -f $Seconds, $i)
