Write-Host '=== WINWORD ==='
Get-Process WINWORD -ErrorAction SilentlyContinue | Select-Object Id, MainWindowTitle | Format-Table -AutoSize

$sig = @'
using System;
using System.Runtime.InteropServices;
using System.Text;
public class FG {
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
  [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint p);
}
'@
Add-Type $sig
$h  = [FG]::GetForegroundWindow()
$sb = New-Object System.Text.StringBuilder 300
[void][FG]::GetWindowText($h, $sb, 300)
$p = 0
[void][FG]::GetWindowThreadProcessId($h, [ref]$p)
$pn = (Get-Process -Id $p -ErrorAction SilentlyContinue).ProcessName
Write-Host ('=== FOREGROUND: ' + $pn + '  |  title=' + $sb.ToString())

Write-Host '=== top visible windows (by process) ==='
Get-Process | Where-Object { $_.MainWindowTitle -ne '' } |
    Select-Object ProcessName, Id, MainWindowTitle | Format-Table -AutoSize
