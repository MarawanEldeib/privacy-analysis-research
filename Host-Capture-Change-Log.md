# Host Capture — Change Log & Revert Checklist

**Machine:** Marawan's laptop (Windows 11 Home, the daily-driver host — NOT a VM)
**Why this file exists:** The Windows capture phase was moved from a throwaway VirtualBox VM
onto the host laptop. The VM's isolation is gone, so **every system-level change made for the
capture is recorded here with its exact reversal**, so the laptop can be returned to its
original state afterwards.

**Golden rule:** nothing here is permanent. When the Windows phase is done (or abandoned), run
the **FULL REVERT CHECKLIST** below and the laptop is back to normal.

---

## ⚡ FULL REVERT CHECKLIST (run all of these to restore the laptop)

> Tick each off during teardown. Commands are filled in as each change is actually applied.
> Items marked _(planned)_ have not been done yet.

- [ ] **System proxy** → currently OFF (restored during recovery). Full restore = clear the leftover strings too: `$k='HKCU:\...\Internet Settings'; Set-ItemProperty $k ProxyEnable 0; Set-ItemProperty $k ProxyServer ''; Set-ItemProperty $k ProxyOverride ''`. During capture use `scripts\capture\proxy-toggle.ps1 on|off` — it refuses to enable unless mitmdump is up, and bypasses Claude/Anthropic + localhost so Claude Desktop stays connected.
- [ ] **mitmproxy root CA** → **⚠️ INSTALLED in BOTH stores, remove both at teardown** (SHA1 `b9639d7a0119fdbb112842f477a100f8b88135a5`): `certutil -delstore Root mitmproxy` (machine, admin) **and** `certutil -user -delstore Root mitmproxy` (current user)
- [ ] **mitmproxy CA files** → delete `%USERPROFILE%\.mitmproxy\` _(planned)_
- [ ] **Python packages** → `pip uninstall -y mitmproxy brotli pyahocorasick zstandard` (+ frida-tools if installed) _(planned)_
- [x] **Test apps** — user opted to KEEP these (uses DeepL; owns an iPhone → keeps Apple software). NOT part of teardown:
  - Grammarly — pre-existing, keep
  - DeepL — **keep** (user uses it)
  - iCloud + Apple deps (App Support x64/x86, Software Update, Bonjour) — **keep** (user has iPhone)
  - Avast (only if installed later) — remove after: `winget uninstall --id Avast.AvastFreeAntivirus` **and** run Avast's `avastclear` remover for a full wipe
- [ ] **Avast Web Shield** → re-enable if it was paused _(planned)_
- [ ] **Proxifier** → uninstall if it was installed _(only if used)_
- [ ] **Wireshark / Npcap** → uninstall if installed _(only if used)_
- [ ] Confirm normal internet works with proxy off; confirm no mitmproxy cert remains
      (`certutil -store Root | findstr /i mitmproxy` returns nothing).

---

## 0. Baseline snapshot (state BEFORE any changes)

_Recorded so we can restore exactly. Filled in from the baseline capture command._

| Setting | Original value |
|---|---|
| System proxy (ProxyEnable) | **0 (disabled)** — restore to this |
| System proxy (ProxyServer) | **(none / empty)** — restore to this |
| System proxy (ProxyOverride / AutoConfigURL) | (none) |
| mitmproxy present | No (confirmed — `pip show mitmproxy` empty, no CA file) |
| Python | 3.13.1 at `F:\python` (`python` and `py`) |

---

## Chronological log (append one row per change as it happens)

| # | Timestamp | Change | Exact command used | How to reverse | Status |
|---|---|---|---|---|---|
| 1 | 2026-09-11 ~22:40 | Installed capture toolchain (mitmproxy 12.2.3 + pyahocorasick; brotli/zstandard already present) | `pip install mitmproxy brotli pyahocorasick zstandard` | `pip uninstall -y mitmproxy mitmproxy-rs mitmproxy-windows pyahocorasick aioquic pydivert` | ✅ Done |
| 1a | (same) | Side effect of #1: `cryptography` upgraded 46.0.4 → 48.0.1 (mitmproxy dep) | (automatic) | `pip install cryptography==46.0.4` if the old version is needed | ℹ️ Noted |
| 2 | 2026-09-11 ~22:35 | Generated mitmproxy CA (files under `C:\Users\Marawan\.mitmproxy\`) | ran `mitmdump --listen-port 8080` once, then Ctrl+C | `Remove-Item "$env:USERPROFILE\.mitmproxy" -Recurse -Force` | ✅ Done |
| 3 | 2026-09-11 ~22:45 | Trusted mitmproxy CA in Windows Trusted Root store (SHA1 b9639d7a…35a5) | `certutil -addstore -f Root "C:\Users\Marawan\.mitmproxy\mitmproxy-ca-cert.cer"` (admin) | `certutil -delstore Root mitmproxy` (admin) | ✅ Done |
| 4 | 2026-09-11 ~22:47 | Turn ON system proxy → 127.0.0.1:8080 | `Set-ItemProperty $k ProxyServer '127.0.0.1:8080'; Set-ItemProperty $k ProxyEnable 1` | `Set-ItemProperty $k ProxyEnable 0` (baseline was 0) | ✅ Applied |
| — | — | Smoke test (no change): curl through proxy → HTTP 200, decrypted | `curl.exe -x http://127.0.0.1:8080 --ssl-no-revoke https://example.com` | n/a | ✅ Verified |
| — | 2026-09-11 ~22:58 | Harness test: add-on ran, decoders all True, wrote `data\raw\harness_test\run_1.json` (32 events, 0 exposure — expected) | `TOOL_NAME=harness_test mitmdump -s scripts\capture\capture_addon.py` | delete `data\raw\harness_test\` (scratch) | ✅ W1 done |
| 4b | 2026-09-11 ~23:10 | System proxy auto-disabled during recovery (Ctrl+C killed mitmdump while proxy still ON → Claude Desktop/browser lost net). Fixed by other session. | `Set-ItemProperty $k ProxyEnable 0` | n/a (this IS the revert) | ✅ Proxy now OFF |
| 5 | 2026-09-11 ~23:15 | Added `scripts\capture\proxy-toggle.ps1` (safe on/off/status helper) | (new file) | delete the file | ✅ Done |
| 6 | 2026-09-11 ~23:33 | **Upgraded** Grammarly for Windows to 1.2.294.1953 (was ALREADY installed — user's own) | `winget install --id Grammarly.Grammarly` | leave as-is (pre-existing, do NOT uninstall) | ✅ Done |
| 7 | 2026-09-11 ~23:33 | Installed DeepL 26.8.2 (NEW) | `winget install --id DeepL.DeepL` | `winget uninstall --id DeepL.DeepL` | ✅ Done |
| 8 | 2026-09-11 ~23:34 | Installed iCloud (Legacy) 7.21 + deps (Apple App Support x64/x86, Apple Software Update, Bonjour) (all NEW) | `winget install --id Apple.iCloud` | `winget uninstall --id Apple.iCloud` + the 4 Apple deps | ✅ Done |

---

## Notes / scope reminders
- Synthetic test document only (`input-data\test-document.txt`). No real personal accounts
  signed into the apps while the proxy/CA are active.
- Captures written to `data\raw\<tool>\run_*.json` via the existing add-on; analysis via
  `scripts\analysis\analyze.py`.
- The mitmproxy CA is a system-wide trust change: while installed, keep the laptop off
  untrusted networks and remove the CA as soon as the capture sessions are finished.
