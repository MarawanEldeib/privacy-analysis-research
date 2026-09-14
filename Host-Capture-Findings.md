# Host-Capture Findings (Windows phase)

## F1 — Windows Cloud Clipboard transmits copied content to Microsoft (incidental / OS-level)

**Date:** 2026-09-11 ~23:41
**Evidence file:** `data/raw/deepl_desktop/run_1_clipboard-confound.json`

**What happened:** Immediately after the synthetic test document was placed on the
Windows clipboard (`Set-Clipboard`), the **entire document (2065/2065 chars, 100%, all 12
sensitive tokens including the canary)** was POSTed to **`activity.windows.com`**
(`/v3/feeds/me/$batch`) — ~2 seconds later, and **before any target app touched it.**

**Attribution (clean):** `transcript_covered_by_host` shows the document content reached
**only `activity.windows.com`**. No other host received it. This is Windows **Cloud
Clipboard / Activity History** sync (machine is signed into a Microsoft account — MSA token
traffic to `login.live.com` observed; "sync across devices" enabled).

**Why it matters:**
- A host/OS-level data-exposure channel independent of any LLM tool: copying sensitive text
  sends it to Microsoft servers.
- **Methodological consequence:** clipboard-based input delivery is a *confound* for
  per-tool measurement. Mitigation: attribute exposure **per host** (the add-on already does
  this) and/or disable Cloud Clipboard before tool runs. The leak must NOT be attributed to
  the app under test.

**Config caveat:** depends on Microsoft-account sign-in + Cloud Clipboard "sync across
devices" being ON. Frame in the report as conditional on that configuration, not universal.

**Status:** DeepL itself produced **no traffic** in this run (app was on its login screen;
nothing translated) → DeepL measurement still pending a clean run.

---

## F2 — DeepL desktop transmits the full input document to its servers

**Date:** 2026-09-11 ~23:52
**Evidence file:** `data/raw/deepl_desktop/run_2.json`
**Task:** pasted the synthetic test document, translated EN→German, then EN→Arabic (free tier).

**Result:** the **entire document (2065/2065 chars, 100%, all 12 tokens incl. canary)** was
POSTed to **`www2.deepl.com`** (`/jsonrpc?method=LMT_handleAdditionalData`). Per-host
attribution: **only `www2.deepl.com`** received document content — no other host did.

**Notable nuances:**
- Free tier translated only 1500/2065 chars, but the **full 2065 chars were still uploaded** —
  the char cap is on translation output, not on what leaves the machine.
- 1 TLS handshake failure on `www.deepl.com` (a static-asset connection refused MITM), but the
  translation API `www2.deepl.com` decrypted normally → payload fully observed.
- DeepL telemetry also seen: `s.deepl.com` (StatisticsService), `ott.deepl.com` (OpenTelemetry).
- Background noise present (WhatsApp Web media CDN, Grammarly, Datadog) but per-host attribution
  confirms none of it received the document — clean attribution.

**Exposure verdict (DeepL desktop, free):** HIGH — known input appears in transmitted content
at 100%, high confidence (decrypted payload, canary + all 12 tokens present).

---

## F3 — USB passive insertion ("inserted, not opened"): NO auto-read, NO transmission

**Date:** 2026-09-12 · **Evidence:** `data/raw/usb_passive/run_1.json`, `run_2.json` (network), `data/raw/usb_passive/procmon_run2.csv` (file reads)
**Setup:** planted files (`confidential-memo.pdf`, `hr-record.pdf`, `test-document.txt` — all 12 tokens) on a freshly-formatted removable drive (D:); background actors running (Windows Search, iCloud, Grammarly, Perplexity, WhatsApp/YouTube in browser); **no third-party AV yet (Avast not installed)**. Insert the drive, **open nothing**, capture ~5 min. Two runs.

**Result — clean negative:**
- **Network:** 0/2065 chars, 0/12 tokens transmitted in both runs. (TLS-pinned Microsoft telemetry `*.events.data.microsoft.com` opaque = lower bound.)
- **Process Monitor (at mount):** only metadata/AutoPlay probing — `SearchIndexer.exe` registered the volume (wrote its `IndexerVolumeGuid` marker) but did **not** read the files; `svchost.exe` probed for `autorun.inf`/DVD/camera markers (all NOT FOUND); `Explorer.EXE` enumerated the directory. **No process opened or read the contents of any planted file.**

**Conclusion:** On Windows 11 with these apps, **merely inserting a USB (without opening files) did not cause any process to read or transmit the confidential documents.** Windows does not deep-index removable drives by default; the shell only checks for AutoPlay media types. This bounds the passive threat: the exposure requires *opening* the file, not just receiving/mounting it.

**Caveats / still to test:**
- Procmon window captured the insertion burst (D: was silent afterwards); a longer explicit window can re-confirm.
- **Avast not yet installed** — antivirus cloud-scan is the most likely remaining passive-read candidate; test after installing it.
- **"Opened it" variant still pending** — double-click a planted PDF in its default viewer (no copy/paste) and re-measure. This is the other half of the professor's "I just opened it" scenario and the more likely positive.

---

## F4 — USB "opened it" ("someone sent me a file and I just opened it")

**Date:** 2026-09-12 · **Evidence:** `data/raw/usb_opened/run_1.json` (network), `data/raw/usb_opened/procmon_run1.csv` (file reads)
**Setup:** same drive/files as F3; this time **double-click to open** — PDFs in **Adobe Acrobat**, `test-document.txt` in **Notepad**; capture live.

**Who read the files (Procmon):**
- `Acrobat.exe` (opened PDFs) and `Notepad.exe` (opened txt) — expected, user action.
- **`MsMpEng.exe` (Windows Defender) on-access-scanned both PDFs** — a *local* read triggered by opening (did NOT occur on mere insertion in F3).
- `Explorer.exe` tagged files with `:Zone.Identifier` (Mark-of-the-Web from removable media).

**Network:**
- **`.txt` opened in Notepad → zero network activity** (clean control: a non-cloud viewer leaks nothing, even plaintext).
- **PDF opened in Acrobat → heavy Adobe cloud contact** (`rna-resource.acrobat.com`, `cc-embed.adobe.com`, `quick-actions.express.adobe.com`, `cc-api-data.adobe.io/ingest`, `crs.cr.adobe.com`) — telemetry + Document-Cloud/Quick-Actions UI load on open.
- **No planted secret transmitted in cleartext (0/12, outbound coverage 0).** The single `[! EXPOSURE]` was a coincidental 20-char match inside an **inbound** Adobe JS asset — a false positive, not a leak.
- **Lower bound:** several Adobe channels (and Defender's `*.events.data.microsoft.com`) are **TLS-pinned/opaque**, so silent content upload over those cannot be fully excluded.

**Conclusion (action spectrum, this machine):**
- **Insert, don't open (F3):** no file read, nothing transmitted.
- **Open in a plain viewer (Notepad):** read locally, nothing transmitted.
- **Open a PDF in Acrobat:** read locally by Acrobat + Windows Defender; **extensive Adobe cloud telemetry on open**, but no observable cleartext exfiltration of the document contents (pinned channels = lower bound).
- **Actively hand content to an LLM tool (Grammarly/LanguageTool/DeepL, F2 + browser phase):** full content transmitted.

So "just opening a received file" did not silently ship its contents in our observable capture — the strong, confirmed exposure is via the LLM writing/translation tools when the user submits the text. Opening a PDF still announces use to Adobe's cloud immediately (a privacy-relevant behavior worth noting).

---

## F5 — USB "opened in browser" (PDF in Chrome, AI extensions active): NO content exfil

**Date:** 2026-09-12 · **Evidence:** `data/raw/browser_pdf/run_1.json`
**Setup:** open `D:\confidential-memo.pdf` in **Chrome** (loaded with extensions: Grammarly, ChatGPT, Coda, 1Password, Bitwarden, AdBlock; Monica/Perplexity seen in other runs), view ~2 min, no AI button clicked.

**Result:** **0/12 tokens, 0% exposure, `transcript_covered_by_host` empty** across **47 domains** of extension/background chatter. No extension received the document.
**Why:** Chrome renders local PDFs in its sandboxed viewer; page-reading extensions can't access `file://` PDFs without explicit "Allow access to file URLs." So a browser-opened local PDF is not exposed to the AI extensions either.
**Caveat:** 20 TLS handshake failures (many Google/Chrome channels pinned) → lower bound; but the AI-extension endpoints that *were* decrypted carried config/telemetry, not document content.

**Combined passive picture (F3–F5):** inserting a USB, or opening the file in Notepad / Acrobat / a browser, did **not** silently transmit the document's contents. Exposure requires the content to enter a **monitored editable surface** (a field the assistant watches, or active submit/paste). Next: Word + Grammarly add-in — the one "opened it" path where an LLM integration *does* watch the editable surface (expected positive).

---

## F6 — ⭐ Word "opened it": Microsoft Office streams the document to its cloud (POSITIVE)

**Date:** 2026-09-12 · **Evidence:** `data/raw/word_docx/run_1.json`
**Setup:** open `D:\test-document.docx` in **Microsoft Word** (Microsoft 365, signed in), click into the text, view ~2 min. Grammarly for Windows also running.

**Result — strong positive:** **96.76% of the document (1998/2065 chars), all 12 tokens incl. the canary**, transmitted to **`augloop.svc.cloud.microsoft`** over a WebSocket (55 KB frame). 100% HTTPS, **0 TLS failures — fully decrypted, high confidence.**

**Attribution (clean):** `transcript_covered_by_host` = **only `augloop.svc.cloud.microsoft`**. This is Microsoft's **"Augmentation Loop"** — the cloud backend for Office **Editor / Copilot intelligent services** (POSTs to `/workflows/OfficeCopilotOrchestrationWorkflow` observed). **It is NOT Grammarly** — Grammarly sent only telemetry (`f-log-extension`, `femetrics`); the document content went to **Microsoft**.

**Why it matters (headline):** *Merely opening a confidential document in Word* — no paste, no submit — **streams ~97% of it (every planted secret + the canary) to Microsoft's cloud**, because Office's AI/Editor services are **on by default** in Microsoft 365. This is the strongest, cleanest "just opened it" exposure in the study, and it comes from the *default productivity suite itself*, not a third-party tool.

---

## Action-spectrum summary (this machine)
| Action | Content transmitted? | To whom |
|---|---|---|
| Insert USB, don't open (F3) | No | — |
| Open `.txt` in Notepad (F4) | No | — |
| Open PDF in Acrobat (F4) | No content (telemetry only; some pinned) | Adobe (telemetry) |
| Open PDF in Chrome, AI extensions (F5) | No (extensions can't read file:// PDF) | — |
| Open PDF in Comet AI browser, passive (F5b) | No (assistant doesn't auto-scrape; would need active "summarize") | — |
| **Open `.docx` in Word (F6)** | **YES — 96.8%, all 12 secrets + canary** | **Microsoft (augloop / Office Copilot-Editor)** |
| Paste into Grammarly/LanguageTool/DeepL (browser phase + F2) | YES — ~99–100% | the tool's servers |

**Thesis takeaway:** exposure is *surface-dependent*. Passively receiving/opening a file leaks nothing **unless the app has a default cloud-AI integration watching the content** — Word does (Office Editor/Copilot → Microsoft), plain viewers (Notepad, Acrobat local render, browser PDF viewer) do not. And actively feeding text to an LLM writing/translation tool always leaks.

---

## Candidate additional tools observed phoning home (leads, not yet measured)
- Grammarly (desktop/extension): `in.grammarly.com`, `gnar.grammarly.com`,
  `win-extension.femetrics.grammarly.io`, `applet-bundles.grammarly.net` — steady telemetry.
- Perplexity: `count.perplexity.ai` (seen in an earlier baseline).
- QuillBot: `stream.quillbot.com` (WebSocket, seen earlier).
- Also installed and in-scope for later runs: Kimi, MiniMax Code, Antigravity, Zed, Ollama.

## F7 — Grammarly-ACTIVE Word open (word_grammarly/run_2, 2026-09-14)
**Setup (verified, not assumed):** WinINET proxy ON + **WinHTTP proxy ON** (`netsh winhttp set proxy 127.0.0.1:8080`, admin) — the missing piece that made native-app (Office/Grammarly) traffic traverse mitmproxy; earlier WinINET-only runs (run_1) showed 0% because Word/Grammarly use WinHTTP and bypassed it (recorded as a methodology lesson). Grammarly for Windows signed in (test acct REDACTED_EMAIL@gmail.com, indicator active, produced suggestions). Positive control: example.com 200 + live background traffic. Doc opened in Word (Compatibility Mode, editable), ~90 s focused.
**Result:** UNION exposure **96.76%** (1998/2065 chars), **12/12 secrets incl. canary**. Two exfiltration destinations from a single passive open:
- `augloop.svc.cloud.microsoft` (Microsoft Office Editor/Copilot) — 96.76%, 12/12, canary; WebSocket, POST `/workflows/OfficeCopilotOrchestrationWorkflow`.
- `capi.grammarly.com` (Grammarly desktop) — **94.24%**, 12/12, canary; `/fpws` WebSocket. **NEW: Grammarly desktop receives the doc in addition to Microsoft.** JWT access token exposed in the fpws URL (credential finding, desktop path).
**Traffic visibility:** 565/577 HTTPS events intercepted; **8 TLS-handshake fails** (pinned: googleapis, some grammarly f-log, 1password) → figure is a lower bound.
**Note:** interception now covers native apps because BOTH proxies are set; add `netsh winhttp reset proxy` to teardown. (Consider adding bridge.claudeusercontent.com + platform.claude.com to the bypass next time — this session's own traffic was intercepted, harmless but noise.)

### F7 provenance correction (operator note, 2026-09-14)
Delivery channel for run_2 = **USB stick (D:)**: the operator connected the USB and opened the `.docx` directly from it (not the F: working copy, which is byte-identical / same 12 tokens). This makes F7 the literal "someone sent me a file and I just opened it" headline: **USB receipt → open in Word → dual leak to Microsoft (augloop 96.76%) AND Grammarly (capi 94.24%), 12/12 secrets + canary.** Record the delivery channel as USB in the report's action-spectrum / passive-open row (supersedes the earlier assumption that it opened from F:).

---

## F8 — Device-permissions audit (mic/camera + extension permissions) — 2026-09-14

**Method:** Windows Settings → Privacy & security → Microphone app list + `edge://extensions`/`chrome://extensions` Details → Permissions & Site access. (Mic/camera use is a local OS API — invisible to mitmproxy — so this is a declared/granted-permission audit, not a network capture.)

**Microphone (Windows):** The document-scraping AI tools have mic **OFF** — ChatGPT (Off), ChatGPT Classic (Off), Copilot (Off), Microsoft 365 Copilot (Off). Mic is ON only for conversational/voice apps: Claude (last used 2026-09-14), Comet, plus comms/dictation apps (Teams, Slack, Telegram, WhatsApp, Webex, superwhisper) — all expected voice features. **No grammar/translation writing tool (Grammarly, DeepL, QuillBot, LanguageTool) holds microphone access.** Camera: same expected pattern (writing tools absent).

**Extension permissions / site access (the real vector):**
- ChatGPT ext: "Read and change all your data on all websites" + "read/change browsing history on all signed-in devices" + native-messaging + downloads + bookmarks + tab groups.
- Claude in Chrome: "Read and change all your data on all websites" + page-debugger backend + native-messaging + downloads + tab groups.
- DeepL ext: "On all sites" site access; read browsing history; block content; notifications.
- Mouse Tooltip Translator: "On all sites"; read browsing history.
- Grammarly ext: declared perms modest ("read browsing history", "notifications") — yet it exfiltrated 99% (F: browser runs). Declared-permission minimalism UNDERSTATES actual access: content scripts read editable-field text via host/all-sites access.

**Finding:** The exposure vector is **not** audio/video — no writing tool requests mic/camera. It is the broad **"read & change all your data on all websites" / "On all sites"** host permission, which silently authorises full-page and editable-field text scraping. Grammarly shows declared permissions can look minimal while actual data access (and exfiltration) is near-total.

### F8 addendum — mic/camera usage timeline (ConsentStore, terminal method)

**Method:** `scripts/capture/mic_audit.ps1` reads `HKCU\...\CapabilityAccessManager\ConsentStore\{microphone,webcam}` (incl. NonPackaged) — Windows logs every app that has *ever* used the device, with LastUsedTimeStart/Stop; Stop==0 => currently in use. Absence from the list = never accessed. Corroborates the Settings UI and adds precise timestamps + live-use detection.

**Result (2026-09-14):**
- Mic/camera users are ONLY: general browsers (Edge/Chrome/Comet/Firefox — device granted to *meeting websites*, not writing extensions), voice/conversational apps (Claude desktop, Comet, superwhisper, Voice Access, Windows Speech), meeting/comms apps (Teams, Zoom, Webex, Slack, Discord, Telegram, TeamViewer), games, OBS.
- **Every text-exfiltrating writing/AI tool is ABSENT from both mic and camera lists**: Grammarly, DeepL, LanguageTool, QuillBot, ChatGPT extension, Microsoft 365 Copilot, Word/augloop — never accessed mic or camera. None `IN USE NOW`.

**Conclusion:** The writing/AI tools' data-exposure channel is purely TEXT (via broad "read all site data"/"On all sites" host permission), not audio/video. Mic/camera access belongs to a separate, expected class of apps. Caveat: a browser in the list reflects a website using the device, not the writing extension.

### F9 — Full capability-permission + autostart inventory — 2026-09-14

**Method:** `scripts/capture/permission_audit.ps1` (read-only) enumerates ALL Windows ConsentStore capability categories per app + autostart/persistence. Full report: `results/permission_audit_20260914-173801.txt`. NB: a held permission != misuse; this is an inventory/over-permission flag, not malware detection.

**Study-relevant findings:**
1. The third-party writing/grammar/translation tools (Grammarly, DeepL, LanguageTool, QuillBot) hold **no** sensitive OS capability (mic/webcam/location/contacts/broadFileSystemAccess). Confirms their data-exposure vector is TEXT via browser "all-sites"/host access, not OS device permissions.
2. Over-permission flags (AI desktop apps): **ChatGPT Desktop = location:Allow**; **OpenAI Codex = webcam:Allow** — more than a text/coding assistant needs (flag, not proof of misuse).
3. Reassuring negatives: **broadFileSystemAccess = no holders**; no writing tool holds mic/camera.
4. Autostart confirms the always-on background-actor model behind passive leaks: **Grammarly (`--autostart`), DeepL (Startup folder), Comet, Ollama, full iCloud suite (iCloudServices/Drive/Photos/PhotoStreams)** all launch at boot.
5. Windows first-party apps now hold `systemAIModels` (Notepad, Photos, Outlook) — on-device AI is now default even in Notepad.
6. Remote/dev services running (legit, non-malicious): TeamViewer, Cisco Secure Client VPN, WSL, Docker. No hidden/unknown persistence found; all entries map to installed software.

## F10 — Avast consumer AV cloud-scan — 2026-09-14

**Setup:** Avast Free freshly installed (browser extras declined, location denied). Capture while right-click-scanning a canary .txt copy; Grammarly desktop still running as a background actor.

**Attribution (critical):** UNION shows 94.24% / 12-of-12 — but per-host attribution proves this was carried by **capi.grammarly.com** (Grammarly desktop re-scanning the canary), NOT Avast. Avast's own decrypted hosts (`analytics.ff.avast.com`, `ipm.avcdn.net`, `s-install.avcdn.net`) carried telemetry/marketing only — **0 document tokens**. Separately, Avast **CyberCapture uploaded an unknown executable (`mitmdump.exe`) to its cloud** and returned a verdict.

**Finding:** Consumer AV (Avast) uploads unknown **executables** (CyberCapture) + telemetry/file-reputation, but does **not** upload document **content**. Distinct threat class from the AI writing tools. This run also validates the per-host attribution method: a naive total would have mis-credited Grammarly's 94% leak to Avast. (Grammarly-as-background-actor confound noted.)
