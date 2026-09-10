# Changelog

All notable changes to this research project are documented here.
Format loosely follows [Keep a Changelog](https://keepachangelog.com/); dates are ISO 8601.
This is a research artifact, not a released product, so entries track research milestones
rather than software versions.

## [Unreleased] — in progress
### Planned
- Windows-VM phase: capture harness (mitmproxy + CA via `certutil` + system proxy), then
  Windows-only desktop clients (Grammarly desktop, DeepL app, iCloud for Windows) and the
  free consumer Avast, plus the USB auto-read test (which only meaningfully fires on
  Windows, where an indexer/AV/desktop client is present to auto-read the stick).

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
