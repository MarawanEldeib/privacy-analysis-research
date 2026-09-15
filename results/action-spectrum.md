# Action-Spectrum Results (host + browser phases) — updated 2026-09-14

| Condition | Document exposure | Destination | N | Notes |
|---|---|---|---|---|
| DeepL desktop (paste) | 99.6% (mean of clean runs) | www2.deepl.com | 3 | 12/12 incl. canary; runs 100/99.1/(93.6 conflated w/ Grammarly). Full input sent though free tier translates 1500 chars |
| Grammarly (browser, paste) | 99.0% | capi.grammarly.com | 5 | 12/12, sigma 0 |
| Word — open .docx | 96.8% | augloop.svc.cloud.microsoft | 3 | 12/12 incl. canary; passive on open; Office AI on by default |
| Word — Protected View (banner up) | 94.2% | capi.grammarly.com | 2 | augloop SILENT in Protected View; Grammarly desktop bypasses the sandbox |
| LanguageTool (browser, paste) | 91.9% | api.languagetool.org | 5 | 12/12, sigma 0 |
| Edge Copilot — PDF (invoked) | 76.9% | copilot.microsoft.com | 3 | 12/12 incl. canary; sigma 0; refusal in the reply != non-transmission |
| Word — Office AI disabled (mitigation) | 0.0% | — | 1 | augloop silenced by one Trust-Center toggle (causation) |
| Edge — PDF open, not invoked (passive) | 1.8% | — | 1 | 0/12; Edge leaks only when Copilot invoked |
| PDF in Chrome / Acrobat (open) | 0.0% | (Adobe telemetry only) | 1 | file:// PDF not readable by extensions; some Adobe channels pinned (lower bound) |
| .txt / .md in Notepad (open) | 0.0% | — | 1 | no cloud integration -> silent; file format alone does not leak |
| Notepad + Grammarly DESKTOP (attached) | inconclusive (content) | in/gnar.grammarly.com (telemetry); capi ABSENT; Grammarly.Desktop → AWS 174.129.115.145:443 DIRECT | 2 | 0/12 on proxied channels (telemetry only, ~63 KB); primary channel bypasses system proxy → content UNMEASURED, not zero (F11/F12). Contrast: Grammarly-in-Word hit capi and WAS captured (94.2%) |
| VS Code — .md open, passive | 5.5% | (telemetry only) | 1 | 0/12; ChatGPT/azureml telemetry, no document content |
| iCloud Drive drop (auto-sync) | 0.0% | (icloud channels decrypted) | 1 | 0/12 cleartext; content client-side encrypted or not synced in window |
| Avast AV (scan file) | 0.0% doc content | avast/avcdn telemetry | 1 | CyberCapture uploaded an unknown EXECUTABLE (mitmdump.exe), not the document |
| Insert USB, don't open | 0.0% | — | 2 | only indexer/shell metadata probing; iCloud running as background actor |
| Baseline (idle) | 0.0% | — | 3 | clean background only |
