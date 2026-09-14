# Changelog

All notable changes to this research project are documented here.
Format loosely follows [Keep a Changelog](https://keepachangelog.com/); dates are ISO 8601.
This is a research artifact, not a released product, so entries track research milestones
rather than software versions.

## [Unreleased] — in progress
### Planned (future work)
- External-validity breadth: real-field runs (Gmail, Google Docs); the two further
  documents of the intended three-document set (longer report + code snippet); a
  primary-browser (Chrome/Edge) and macOS environment; a dedicated OneDrive drop-and-sync
  run; more captures to lift remaining single-run host probes to n>=3.
- Mechanistic: Frida for certificate-pinned channels; an outbound-byte-volume detector to
  bound opaque uploads; broaden the Presidio sweep to a full unplanted-PII inventory.

## 2026-09-14
### Added (host & system-level phase — completed, integrated into the report)
- **Word / Office augloop reproduced (n=3):** merely *opening* the .docx transmits 96.8%
  of the document + 12/12 secrets to `augloop.svc.cloud.microsoft`, passively on open.
- **Mitigation / causation:** disabling the single Office setting "experiences that
  analyse your content" drops the Word leak to 0% (augloop socket opens but sends no
  content) — establishes cause and a one-switch mitigation.
- **Word Protected View:** with the "Enable Editing" banner still up, augloop stays
  silent (Protected View contains Microsoft's own AI) but the **Grammarly desktop client
  still exfiltrates 94.2%** to `capi.grammarly.com` — Protected View does not stop a
  third-party assistant.
- **Edge/Copilot PDF (n=3):** invoking Copilot to summarise the PDF sends 76.9% + 12/12
  to `copilot.microsoft.com`; in one run Copilot's visible reply declined to reveal the
  secrets yet the full document (canary included) had already been transmitted — refusal
  in the reply != non-transmission on the wire.
- **DeepL desktop (n=3):** ~99.6% mean to `www2.deepl.com`.
- **Negatives / controls:** Edge PDF passive (not invoked) ~0%; iCloud Drive sync = no
  cleartext content; `.md` in Notepad = 0%; VS Code passive = 5.5% telemetry only, 0/12;
  Avast = uploads an unknown *executable* (CyberCapture) + reputation/telemetry, **not**
  document content.
- **Permissions audit (F8/F9):** no writing/translation tool holds mic/camera/full-disk
  access; the channel is the browser "all-sites" text permission. Autostart confirms the
  always-on background-actor model (Grammarly `--autostart`, DeepL Startup folder).
  Scripts: `scripts/capture/mic_audit.ps1`, `scripts/capture/permission_audit.ps1`.
- Findings log `Host-Capture-Findings.md` (F7–F10), `results/final_summary_table.md`,
  updated `results/action-spectrum.md`, and a redesigned horizontal action-spectrum figure.
### Changed
- Report integrated with all of the above (abstract, contributions, results, permissions
  subsection, limitations, conclusion/future work); action-spectrum figure redesigned
  (horizontal, sorted, colour-coded by interaction class, no empty-bar dead space).
- Trimmed tangential citation-piles in Related Work (removed 4 background/mobile-PII
  citations that did not carry the argument); documented OneDrive + the 3-document set as
  explicit scope limitations rather than dropping them silently.

## 2026-09-10
### Added
- **Independent no-proxy corroboration** of the Grammarly leak: with the proxy removed
  entirely, a `tcpdump` capture shows the browser resolving `assets.grammarly.com` and
  uploading the document directly to Grammarly infrastructure (AWS EC2 +
  `*.fra60.r.cloudfront.net`) on paste — ruling out the "did the proxy change behaviour?"
  objection. Evidence: `results/evidence/grammarly_noproxy_evidence.md`,
  `report/figures/evidence/*.png`.
- **Idle / background-behaviour finding:** 20-min capture, extension loaded, no user
  action. Grammarly is not dormant (23/27 events to `auth`/`config.extension`/`gateway`/
  `capi`/`f-log-extension` hosts — userinfo, A/B experimentation, config, telemetry,
  WebSocket) but transmits **no document content or secrets while idle** (0% / 0-of-12).
  A Firefox-background positive control (`ads.mozilla.org`) confirms the capture was live.
  Evidence: `results/evidence/grammarly_idle_finding.md`.
- Two new Results subsections in `report/main.tex` ("Independent corroboration without a
  proxy", "Background behaviour when idle"); report now 10 pages, compiles clean.
- `scripts/capture/device_permissions.sh` — device/permissions snapshot helper.
### Notes
- Firefox ESR on Kali does **not** honour `SSLKEYLOGFILE` (verified: curl writes keys,
  Firefox does not), so independent TLS-key decryption is not possible on this browser;
  the no-proxy corroboration relies on destination + timing instead. Recorded as a
  methodology limitation.
- Avast Linux is a paid Business product with a currently-unavailable package repo, so the
  Avast "security-tool background behaviour" probe is deferred to the Windows phase (free
  consumer Avast, one-click install).

## 2026-09-06
### Added
- `docs/Desktop-Capture-Runbook.md` — step-by-step Linux/Kali desktop & system-level
  capture guide (CA trust, explicit/transparent proxy, Java truststore specifics, Frida
  for pinning, SSLKEYLOGFILE fallback, background/idle + permissions, USB auto-read).
- `CHANGELOG.md` (this file).
### Changed
- Refreshed `README.md` to current state: results-at-a-glance table, updated repo
  structure, supervisor-approved status, and links to the new documents.
### Removed
- Stray scratch file `project.txt` that had been committed by accident.

## 2026-09-05
### Added
- Information-type breakdown (`scripts/analysis/info_type_breakdown.py`) — the 12 planted
  secrets grouped into categories, with a heatmap figure.
- Traffic-over-time figure (`scripts/analysis/traffic_timeline.py`) — paste spike vs.
  background transmission.
- `docs/Tooling-Landscape.md` (tools used vs. considered) and
  `docs/Review-Findings-2026-09-05.md` (full QA audit).
- `privacy-analysis-review` skill (project QA reviewer) and a token-list-in-sync test
  (`tests/test_token_lists_in_sync.py`).
- Related-work expanded to ~22 cited papers (`report/refs.bib`, `docs/Related-Work-Research.md`).
### Changed
- **Report** converted to IEEE two-column layout; related-work, limitations and
  future-work sections extended with the new citations.
- **Capture** (`capture_addon.py`): fixed WebSocket-fragmentation reassembly, made the
  Aho-Corasick coverage count all positions (fast path == slow path), added zstd
  decompression, base64/UTF-16/HTML-entity search variants, and made offline re-window
  runs write to a distinct file so they never overwrite a live capture.
- **Analysis** (`analyze.py`): baseline subtraction no longer discards leaking events on
  hosts shared with the baseline; surfaced body-read failures; removed the discredited
  sentence-leak metric; reframed the zero-variance CI as a deterministic observation.
- Dashboard updated to the post-meeting state (evidence figures, supervisor feedback,
  refreshed roadmap).

## 2026-07-23
### Added
- Supervisor progress deck (`presentation/`), meeting notes, and a code-and-files guide.
### Changed
- Dashboard fixed to render charts offline; added tool-policy, related-research and
  open-questions sections.

## 2026-07-10 – 2026-07-14
### Added
- First full LaTeX research report draft with the exposure figure; related work
  strengthened; `refs.bib` moved to a Zotero/Better BibTeX auto-export.
- `docs/WALKTHROUGH.md` + `docs/ENVIRONMENT.md`.
### Changed
- Reconciled all docs and skill files to the final scope (Grammarly + LanguageTool +
  baseline, manual paste); retired the old Setup-Guide.
### Results
- Grammarly and LanguageTool each transmit ~the full document and all 12 secrets;
  baseline 0%. Self-contained dashboard added.

## 2026-05-28 – 2026-05-29
### Added
- Pytest suite (matching, transcript+baseline, sentence parser); pinned runtime deps;
  pytest/ruff/black config; 2026-05-28 engineering + independent reviews and operational prompts.
### Changed
- Capture: JSON-aware matching, safe body decode, WebSocket TLS flag, full-body
  transcript buffer, folded per-host transcript coverage into exposure (post-baseline).
- Analysis: outbound-only exposure leading with the secret count; real outbound-byte
  accounting; dead-code cleanup.
### Security
- `.flow` archives gitignored (they hold decrypted auth tokens).

## 2026-05-23
### Added
- Initial commit: v3.1 methodology, capture/analysis scripts, docs, project skill, Makefile.
