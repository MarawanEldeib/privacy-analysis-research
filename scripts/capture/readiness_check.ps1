# Readiness check for a host capture run. Read-only.
$ErrorActionPreference = 'SilentlyContinue'

Write-Host '==== PROCESSES (relevant apps) ===='
$want = 'WINWORD','Grammarly','GrammarlyDesktop','Grammarly.Desktop','iCloud','iCloudServices','AdobeCollabSync','Adobe Desktop Service','Creative Cloud','CCXProcess','mitmdump'
Get-Process | Where-Object { $n=$_.ProcessName; $want | Where-Object { $n -like "*$_*" } } |
    Select-Object ProcessName, Id | Sort-Object ProcessName -Unique | Format-Table -AutoSize

Write-Host '==== PROXY + MITM ===='
$reg = Get-ItemProperty 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings'
"ProxyEnable = $($reg.ProxyEnable)   ProxyServer = $($reg.ProxyServer)"
"mitmdump on 8080 = $((Test-NetConnection 127.0.0.1 -Port 8080 -WarningAction SilentlyContinue).TcpTestSucceeded)"

Write-Host ''
Write-Host '==== DNS CACHE (evidence apps are phoning home = active/logged-in) ===='
$pat = 'grammarly|icloud|apple|adobe|augloop|officeapps|office\.net|office\.com|live\.com|microsoftonline|1drv|sharepoint'
Get-DnsClientCache | Where-Object { $_.Entry -match $pat } |
    Select-Object Entry | Sort-Object Entry -Unique | Format-Table -AutoSize

Write-Host '==== TEST DOC ===='
Get-Item 'F:\Projects\Research Project - Privacy analysis\input-data\usb-test\test-document.docx' | Select-Object Name,Length,LastWriteTime | Format-Table -AutoSize
