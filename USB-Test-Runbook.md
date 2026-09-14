# USB Auto-Read Test — Runbook (host, Windows) · THE #1 experiment

**Goal:** insert a USB with planted-secret files, **open nothing**, and detect whether any
process (Windows Search indexer / antivirus / cloud tool) auto-reads and/or transmits them.
A hit (content leaves with zero user action) is the headline finding.

---

## ✅ Prepared tonight (ready to go)
- Harness installed & proven: mitmproxy + trusted CA + `scripts\capture\proxy-toggle.ps1` + capture add-on.
- Planted files staged in repo `input-data\usb-test\`: `confidential-memo.pdf`, `hr-record.pdf` — **verified to contain all 12 secrets** (incl. the canary).
- Clean host baseline already captured (`data\raw\baseline\run_2.json`).

## ⬜ Do first thing tomorrow (5–10 min prep)
1. **Get Process Monitor** — download the official Sysinternals *ProcessMonitor.zip* from Microsoft (learn.microsoft.com/sysinternals/downloads/procmon), unzip, run `Procmon64.exe`. Portable, no install (~5 MB). *(This is a download — you grab it yourself.)*
2. **Load the USB stick** — copy these three onto it, then safely eject and have it ready:
   - `input-data\usb-test\confidential-memo.pdf`
   - `input-data\usb-test\hr-record.pdf`
   - `input-data\test-document.txt`  ← plain-text copy of the same 12 secrets (see "two layers" below — improves network detectability)
3. **Background actors ON:** Windows Search indexing (default on), iCloud running, Grammarly running. (Avast = optional second pass after you install it.)

---

## ⚠️ Detection works on TWO layers (why we need both tools)
- **Process Monitor = did any process READ the file?** Works regardless of encoding. This is the ground truth for "something touched the file with no user action."
- **mitmproxy = was recognizable content TRANSMITTED?** The **.txt** tokens upload as plaintext → the add-on will string-match them. **Raw PDF uploads may be opaque** (PDF text lives in compressed streams, so it won't string-match in the HTTP body). If you see a file *read* + an *upload* but no token match → record it as **"file read + upload observed, payload opaque = likely exfiltration (lower bound)"** — consistent with the study's honest TLS-failure framing.

---

## ▶️ Run (safe order — can't strand the machine)
1. **Window A — start capture:**
   ```powershell
   cd "F:\Projects\Research Project - Privacy analysis"
   $env:TOOL_NAME="usb_passive"; $env:RUN_ID="1"
   mitmdump --listen-host 127.0.0.1 --listen-port 8080 -s scripts\capture\capture_addon.py
   ```
2. **Open Process Monitor.** Filter → add: `Operation is ReadFile` (and once you know the USB letter, `Path contains E:\` etc.). Make sure capture (magnifier) is ON.
3. **Window B — proxy on:** `.\scripts\capture\proxy-toggle.ps1 on`
4. **Insert the USB stick — and DO NOTHING.** Don't open Explorer to it, don't click a file. Let it sit **~3–5 minutes.**
5. **Watch:** Procmon for `ReadFile` on the planted files by any process (note the **Process Name**); mitmdump for `[! EXPOSURE]` lines or uploads to unexpected hosts.
6. **Window B — proxy off:** `.\scripts\capture\proxy-toggle.ps1 off`
7. **Window A — Ctrl+C** to finalize.
8. **Variant (run 2):** repeat, but this time **double-click to open** one PDF in its default viewer (still no copy/paste) → compare "sat untouched" vs "opened".

---

## 📊 Analyze
```powershell
$u = Get-Content "data\raw\usb_passive\run_1.json" -Raw | ConvertFrom-Json
$u.summary
"--- hosts that received content ---"; $u.summary.transcript_covered_by_host
"--- domains ---"; $u.requests.host | Sort-Object -Unique
```
Also in Procmon: **File → Save** the log (CSV or PML) into `data\raw\usb_passive\` as evidence of which processes read the files.

## Outcomes (all are reportable)
- Read by an app/indexer/AV **+** matching upload → **headline hit** (auto-exfil, no user action).
- Read **+** opaque upload → likely exfil, lower bound (document honestly).
- No reads, no uploads → clean negative: "merely inserting a USB did not cause transmission on this config" — still a valid bounding result.

## Cleanup
`proxy-toggle.ps1 off` is in the flow; everything else per `Host-Capture-Change-Log.md`.
