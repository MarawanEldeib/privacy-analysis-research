Write-Host '=== DNS cache: Office / augloop / Microsoft (did Office phone home OUTSIDE the proxy?) ==='
Get-DnsClientCache | Where-Object { $_.Entry -match 'augloop|officeapps|office\.com|office\.net|substrate|microsoft|grammarly' } |
    Select-Object Entry | Sort-Object Entry -Unique | Format-Table -AutoSize
Write-Host '=== Established :443 connections by Office/Word/Grammarly processes ==='
$offpids = (Get-Process WINWORD,OfficeClickToRun,ai.exe,Grammarly.Desktop -ErrorAction SilentlyContinue).Id
Get-NetTCPConnection -State Established -ErrorAction SilentlyContinue |
    Where-Object { $_.RemotePort -eq 443 -and $offpids -contains $_.OwningProcess } |
    Select-Object RemoteAddress, OwningProcess | Sort-Object RemoteAddress -Unique | Format-Table -AutoSize
