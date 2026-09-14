# Windows Capture Setup — Throwaway VM (Windows phase)

Repeat the browser-phase measurement for **Windows-only desktop clients** — Grammarly
desktop, the DeepL app, iCloud for Windows, and free consumer Avast — plus the **USB
auto-read test**, inside an **isolated throwaway Windows 11 VM** in VirtualBox. Same rules
as the Linux phase: **synthetic data only**, throwaway/test accounts, the mitmproxy CA
trusted **only inside this VM**, git stays on the Windows host, and the VM is deleted after.

---

## 0. Downloads (get these first)
| Item | Where | Notes |
|---|---|---|
| **Windows 11 Enterprise Evaluation ISO** | microsoft.com Evaluation Center → Windows 11 Enterprise | 90-day, free, **no licence key**, perfect for a throwaway. ~6 GB |
| VirtualBox **Extension Pack** | virtualbox.org (matching your VBox version) | Needed to pass the physical **USB stick** into the VM for the USB test |
| (inside the VM later) Python 3 | python.org | tick "Add python.exe to PATH" |
| (inside the VM later) Wireshark | wireshark.org | packet-level evidence |
| (inside the VM later) the four apps | vendor sites / Microsoft Store | Grammarly desktop, DeepL app, iCloud for Windows, Avast Free |

---

## 1. Create the VM
VirtualBox → **New**:
- Name `win11-capture`, Type **Microsoft Windows**, Version **Windows 11 (64-bit)**.
- RAM **4096 MB+**, CPUs **2+**, Disk **64 GB**.
- Windows 11 requires **EFI + TPM 2.0 + Secure Boot** — VirtualBox 7 supplies a virtual TPM.
  In the VM's **Settings → System** enable **EFI**; VBox 7's Windows 11 preset enables the
  vTPM automatically. If install complains, enable **TPM 2.0** there.
- Attach the ISO (Settings → Storage → optical drive) and boot.
- During Windows setup: choose **"I don't have a product key"**, edition **Windows 11
  Enterprise Evaluation**; create a **LOCAL account** (avoid signing into a real Microsoft
  account — keep it throwaway).
- After first boot: **Devices → Insert Guest Additions CD → install** (gives shared
  clipboard, shared folders, and proper display). Reboot.

---

## 2. Shared folder to the repo
So the VM can reach the test document and the capture add-on:
- VM **Settings → Shared Folders → +** → Folder Path `F:\Projects\Research Project - Privacy
  analysis`, Name `privacy_analysis`, **Auto-mount**, **Make Permanent**.
- In Windows it appears under **`\\VBOXSVR\privacy_analysis`** (or a mapped drive). The test
  doc is `input-data\test-document.txt`; the add-on is `scripts\capture\capture_addon.py`.

> Keep captures written **inside the shared folder** (`data\raw\<tool>\`) so they land on the
> host repo automatically — same trick as Kali.

---

## 3. Capture toolchain inside the VM (PowerShell)
```powershell
# Python packages for mitmproxy + the add-on's decoders
pip install mitmproxy brotli pyahocorasick zstandard
# (optional) certificate-pinning bypass for stubborn apps
pip install frida-tools
```
Install **Wireshark** from wireshark.org (accept the Npcap driver) for packet evidence.

---

## 4. Trust the mitmproxy CA — VM ONLY
```powershell
mitmdump         # let it start once, then Ctrl+C — this generates the CA
# trust it system-wide (run PowerShell as Administrator):
certutil -addstore -f Root "$env:USERPROFILE\.mitmproxy\mitmproxy-ca-cert.cer"
```
Undo later with `certutil -delstore Root mitmproxy` (or by thumbprint). The CA never leaves
this VM.

---

## 5. Route traffic to mitmproxy
```powershell
# Terminal 1 — start the capture (from the shared repo)
cd \\VBOXSVR\privacy_analysis      # or the mapped drive
$env:TOOL_NAME="grammarly_desktop"; $env:RUN_ID="1"
mitmdump --listen-host 127.0.0.1 --listen-port 8080 -s scripts\capture\capture_addon.py
```
Point Windows at the proxy: **Settings → Network & Internet → Proxy → Manual → Address
`127.0.0.1`, Port `8080`, Save.** Most Electron apps honour the system proxy.
- Apps that ignore the system proxy → use **Proxifier** (free trial) to force them through
  `127.0.0.1:8080`, or note the app as "not routable via system proxy" in results.

---

## 6. Per-app capture (same 12-secret test document)
For each app: start the capture, make sure it's signed into a **throwaway/synthetic account
or none**, paste/translate the test document, record ~60 s, stop, then run the analyzer.

| App | Delivery | Expectation |
|---|---|---|
| **Grammarly for Windows** | Electron | Uses the Chromium/system trust store → system-proxy + CA should decrypt. Paste the doc into its editor. |
| **DeepL app** | Electron | Paste the doc to translate; watch for upload to `*.deepl.com`. Likely decryptable. |
| **iCloud for Windows** | native (Apple) | Apple **pins** aggressively → may NOT decrypt. If TLS fails, record "pinned — connection present via tcpdump, payload opaque" as a limitation. Real test: does iCloud auto-sync/read a file dropped into the iCloud Drive folder? |
| **Avast Free** | native (security) | Update/telemetry channel likely **pinned**. Capture its background/telemetry **hosts** via tcpdump; Avast matters most in the USB test below. |

---

## 7. USB auto-read test (the Windows-native test)
The planted-secret PDFs are already staged on the USB (`confidential-memo.pdf`,
`hr-record.pdf`).
- VirtualBox → enable **USB** (needs the Extension Pack) and pass the physical stick into the
  VM (Devices → USB → select the stick).
- With Grammarly / Avast / iCloud running, the **Windows Search indexer** on, and a capture
  live, **insert/mount the USB and do NOT open any file.**
- Watch whether any tool / indexer / AV **auto-reads and transmits** the PDFs — use tcpdump/
  mitmproxy for the network side and **Sysinternals Process Monitor** (filter on the USB
  path) for file reads. A hit here (a running tool silently reading and sending the USB
  contents with no user action) is the strongest, most novel finding of the study.

---

## 8. Analyze (unchanged pipeline)
The add-on writes `data\raw\<tool>\run_*.json`; then on the host or in the VM:
```
python scripts\analysis\analyze.py <tool>          # per-tool summary
python scripts\analysis\analyze.py --all --chart   # comparison + chart
```
Add each Windows app as its own `TOOL_NAME`.

---

## Feasibility notes (set expectations)
- **Electron apps (Grammarly, DeepL)** → interceptable via the system cert store; expect full
  decrypt like the browser extensions.
- **iCloud, Avast** → likely certificate-pinned; may yield only connection-level (tcpdump)
  evidence. Frida can attempt a bypass but is involved on Windows — if it doesn't work,
  document as a limitation (this mirrors the honest "TLS-failure = lower bound" framing used
  throughout the study).
- Everything synthetic; the MITM CA and all test accounts stay in the throwaway VM, which is
  deleted when the phase is done. This is optional work per the supervisor (partial additions
  are acceptable) — feasible apps first, pinned ones documented as limitations.
