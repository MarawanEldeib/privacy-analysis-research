<#
    proxy-toggle.ps1 — safely turn the mitmproxy system proxy on/off (host capture)

    Usage:
        .\scripts\capture\proxy-toggle.ps1 on       # route Windows through 127.0.0.1:8080
        .\scripts\capture\proxy-toggle.ps1 off      # back to direct connection
        .\scripts\capture\proxy-toggle.ps1 status   # show current state

    SAFETY BUILT IN:
      * `on` REFUSES to enable the proxy unless mitmdump is already listening on 8080
        (so the machine can never be stranded on a dead proxy).
      * Claude / Anthropic domains + localhost BYPASS the proxy, so Claude Desktop
        stays connected even mid-capture. Target apps don't use those domains, so
        captures are unaffected.

    IF YOU EVER LOSE INTERNET: run  .\scripts\capture\proxy-toggle.ps1 off
#>
param([Parameter(Mandatory)][ValidateSet('on','off','status')][string]$Action)

$k = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings'
# Hosts that must NEVER go through the proxy (keeps Claude reachable + our traffic out of captures)
$bypass = 'claude.ai;*.claude.ai;anthropic.com;*.anthropic.com;<local>'

function Test-MitmUp {
    $c = New-Object Net.Sockets.TcpClient
    try { $c.Connect('127.0.0.1', 8080); return $true } catch { return $false } finally { $c.Close() }
}

switch ($Action) {
    'on' {
        if (-not (Test-MitmUp)) {
            Write-Host 'REFUSING: mitmdump is NOT listening on 127.0.0.1:8080.' -ForegroundColor Red
            Write-Host 'Start mitmdump first, THEN run this again. (This prevents stranding the machine.)' -ForegroundColor Red
            return
        }
        Set-ItemProperty $k ProxyServer   '127.0.0.1:8080'
        Set-ItemProperty $k ProxyOverride $bypass
        Set-ItemProperty $k ProxyEnable   1
        Write-Host 'Proxy ON  -> 127.0.0.1:8080  (Claude + localhost bypass; mitmdump confirmed up)' -ForegroundColor Yellow
    }
    'off' {
        Set-ItemProperty $k ProxyEnable 0
        Write-Host 'Proxy OFF -> direct connection' -ForegroundColor Green
    }
    'status' {
        Get-ItemProperty $k | Select-Object ProxyEnable, ProxyServer, ProxyOverride | Format-List
        Write-Host ("mitmdump on 8080: {0}" -f (Test-MitmUp))
    }
}

# Notify WinINET so already-running apps pick up the change immediately.
$sig = '[DllImport("wininet.dll", SetLastError=true)] public static extern bool InternetSetOption(IntPtr h, int o, IntPtr b, int l);'
$wininet = Add-Type -MemberDefinition $sig -Name 'WinINet' -Namespace 'Net' -PassThru
$null = $wininet::InternetSetOption([IntPtr]::Zero, 39, [IntPtr]::Zero, 0)  # SETTINGS_CHANGED
$null = $wininet::InternetSetOption([IntPtr]::Zero, 37, [IntPtr]::Zero, 0)  # REFRESH
