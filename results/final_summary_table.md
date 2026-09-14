# Final results summary — data exposure by tool (union %, secrets/12, receiving host)
Generated 2026-09-14. Per-host attribution from transcript_covered_by_host.

## POSITIVES — content leaked to a third party
| Tool / scenario | Mode | Union% | Secrets | Host | n |
|---|---|---|---|---|---|
| Grammarly (browser) | active (paste) | 99.03 | 12/12 | capi.grammarly.com | 5 (σ=0) |
| DeepL desktop | active (paste) | 100 / 99.13 | 12/12 | www2.deepl.com | 2 clean (+run4 conflated w/ Grammarly) |
| Word + Office AI (augloop) | passive (open) | 96.76 | 12/12 | augloop.svc.cloud.microsoft | 3 (σ=0) |
| Grammarly desktop (in Word) | passive (open) | 94.24 | 12/12 | capi.grammarly.com | dual-leak w/ augloop |
| Word Protected-View | passive (banner up) | 94.24 | 12/12 | capi.grammarly.com (augloop SILENT) | 2 |
| LanguageTool (browser) | active (paste) | 91.91 | 12/12 | api.languagetool.org | 5 (σ=0) |
| Edge Copilot (PDF summarize) | active (invoked) | 76.85 | 12/12 | copilot.microsoft.com | 3 (σ=0) |

## NEGATIVES / CONTROLS — no content leaked
| Tool / scenario | Union% | Note |
|---|---|---|
| baseline (no ext) | 0 | negative control (n=3) |
| Word, Office AI disabled | 0 | MITIGATION/causation (augloop silenced) |
| Edge PDF passive (no Copilot) | 1.79 | passive; leaks only when invoked |
| Chrome PDF / Comet PDF | 0 | sandboxed viewers |
| LanguageTool desktop | 0 | on-device, transmits nothing |
| .md in Notepad | 0 | format alone doesn't leak |
| .md in VS Code (passive) | 5.52 | telemetry only (chatgpt/azureml), 0 secrets |
| USB passive-insert | 0 | iCloud running as background actor |
| USB opened (plain viewer) | 0.97 | Acrobat/Notepad, no secrets |
| iCloud Drive drop | 0 | channels decrypted, no cleartext content (client-side enc / not synced in window) |
| Grammarly idle | 0 | always-connected, no doc while idle |
| Avast (AV) | 0 doc content | CyberCapture uploaded mitmdump.exe (executable) + telemetry; 94% in run was Grammarly confound |

## Methodology notes
- Per-host attribution repeatedly disambiguated Grammarly-as-background-actor confounds (DeepL run4, Avast run1, Protected-View) from the tool under test.
- Passive vs active axis: Word/augloop + Grammarly desktop leak UNPROMPTED on open; Edge Copilot & DeepL only when invoked.
- TLS-handshake failures recorded per run = opaque lower bound (telemetry/pinned channels e.g. events.data.microsoft.com, iCloud, Avast).
- Device permissions (F8/F9): writing tools hold NO mic/camera; vector is text via "all-sites" host access. broadFileSystemAccess: no holders.
