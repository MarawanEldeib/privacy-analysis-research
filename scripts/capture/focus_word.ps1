$ws = New-Object -ComObject WScript.Shell
# focus the Word window by its title substring
$ok = $ws.AppActivate('test-document.docx')
Start-Sleep -Milliseconds 700
if (-not $ok) { $ok = $ws.AppActivate('Word') ; Start-Sleep -Milliseconds 700 }
# harmless cursor navigation (no text change) to make Grammarly scan the active doc
$ws.SendKeys('^{HOME}')
Start-Sleep -Milliseconds 300
$ws.SendKeys('{DOWN}{DOWN}{DOWN}{DOWN}{DOWN}{RIGHT}{RIGHT}{RIGHT}')
Write-Host ("AppActivate ok = " + $ok)
