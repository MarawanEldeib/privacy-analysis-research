param([Parameter(Mandatory=$true)][ValidateSet('on','off','show')][string]$Mode)
# Sets/resets the WinHTTP default proxy so NATIVE apps (Office/augloop, Grammarly
# desktop, other WinHTTP clients) traverse mitmproxy. REQUIRES ADMIN.
# WinINET (browsers) is handled separately by proxy-toggle.ps1.
$bypass = "localhost;127.0.0.1;claude.ai;*.claude.ai;anthropic.com;*.anthropic.com;<local>"
switch ($Mode) {
  'on'   { netsh winhttp set proxy proxy-server="127.0.0.1:8080" bypass-list="$bypass" }
  'off'  { netsh winhttp reset proxy }
  'show' { netsh winhttp show proxy }
}
