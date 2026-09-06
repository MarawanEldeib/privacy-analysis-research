# Project Review — Findings (5 September 2026)

Read-only audit of the privacy-analysis project (capture + analysis code, methodology,
statistics, and doc/report/dashboard/deck consistency). Produced by the
`privacy-analysis-review` skill via two subagents. **No files were changed.**

> **Status (5 Sep 2026):** All six High items **H1–H6 fixed** in `capture_addon.py`,
> `analyze.py`, and `traffic_timeline.py`. Re-analysis of the existing runs is unchanged
> (Grammarly 99.0% / LanguageTool 91.9% / 12·12 secrets), confirming the fixes don't
> regress anything. The H2 (coverage) improvement will only show in the *percentage* after
> re-capturing over the saved `.flow` files with the fixed addon (Kali command below).
> **Mediums/Lows: all actioned (5 Sep 2026).** M1 single-source token list + drift test
> (`tests/test_token_lists_in_sync.py`); M2 `--window` documented as a strict lower bound;
> M3 `body_read_failures` surfaced in analysis output; M4 base64, M5 UTF-16, L2 HTML-entity
> variants added to the search corpus; M6 sentence-leak column removed; M7 zero-width-CI
> overclaim reworded in code and report; M8 limitations (single OS/browser, manual timing,
> unequal n) + desktop future-work added; Lows fixed (n<2 reproducibility guard, chart
> caption, CI half-width from raw bounds, clarified event/byte labels, missing-file guard,
> timeline stub). Tests: 10/10 pass; report recompiles (10 pp); numbers unchanged.
> **Accepted trade-off (L1):** low-entropy windows (e.g. whitespace runs) are kept, not
> dropped — dropping them would conflict with the H2 fix (reaching true 100% coverage);
> the false-positive risk on synthetic-unique content is negligible and is noted in the
> report's detection-method limitation.

**Overall:** the headline result is safe. Every code bug found causes leaks to be
*under-counted*, never inflated — so the true exposure can only be ≥ what is reported,
which strengthens rather than weakens the claim. The secret-detection headline (12/12,
matched independently of the coverage window) is unaffected by all of these. Numbers are
consistent across every file; the gitignore and canary containment are correct.

---

## Critical / High — fix before the report is final

**H1. WebSocket fragmentation not reassembled** (`capture_addon.py` transcript pass,
~517–525). Per-host bodies are joined with `"\n"`, so a secret or 20-char window split
across two WebSocket frames gets a newline injected into the middle and never matches.
Worst for keystroke-streaming tools (one delta per frame). *Effect:* under-counts
coverage. *Fix:* also search the empty-string join (`"".join(parts)`) and union results.

**H2. Aho-Corasick fast path only records each 20-gram's first occurrence**
(`capture_addon.py` ~133–139; inherited by `analyze.py` re-window ~149–152). Repeated
20-grams (whitespace runs, repeated headings) can never reach 100% coverage, and the fast
path (with `pyahocorasick`) yields *different* numbers than the slow fallback. *Effect:*
exposure % systematically depressed and not reproducible across machines. **This may be
part of why Grammarly reads 99.0% not 100% — fixing it could raise the reported %.** *Fix:*
store all positions per window; add a unit test asserting fast == slow on a doc with repeats.

**H3. `zstd`-compressed bodies not decompressed** (`capture_addon.py` decompress, ~180–194;
handles gzip/deflate/br only). Firefox advertises zstd; a tool using it would be scored
"clean." *Effect:* false-negative with no signal. *Fix:* add a zstd branch guarded by an
optional `zstandard` import, mirroring brotli.

**H4. Baseline subtraction is host-granular and can erase real leaks** (`analyze.py`
~219–255). Any host present in the baseline is dropped wholesale from the tool run; a
shared CDN / analytics / fonts host would remove genuine leaking events. *Effect:*
under-count, invisible in output. *Fix:* subtract at host+path granularity, or subtract
baseline-covered document positions rather than whole hosts; log what was removed.

**H5. Offline re-window overwrites the live JSON** (`capture_addon.py` `done()` ~560–565).
The documented `mitmdump -nr … WINDOW_SIZE=12` re-analysis re-writes `run_<id>.json`, but
TLS/read-failure hooks don't fire on replay, so the "0 handshake failures / 0 read
failures" completeness claim is silently zeroed after any re-window. *Fix:* write
re-window output to a distinct filename (e.g. `run_<id>.w12.json`); never overwrite on `-nr`.

**H6. `traffic_timeline.py` ignores event direction (latent).** The `outbound` flag is
computed but unused; `doc_spike` selection and the blue "document sent to <host>"
annotation would mislabel an inbound `http_response` echo as an outbound send. Harmless on
today's data (no response carries the document) but will misfire on any future tool that
echoes content. *Fix:* filter to `OUTBOUND_KINDS` before coloring/annotating.

---

## Medium

- **M1. Three duplicated hardcoded token lists** (`analyze.py`, `capture_addon.py`,
  `info_type_breakdown.py`'s `SECRET_TAXONOMY`). In sync today, but a rename in one place
  silently makes the breakdown report `0/…` for that item. *Fix:* single shared source, or
  assert `SECRET_TAXONOMY` keys == `analyze.SENSITIVE_TOKENS` and fail loudly.
- **M2. `--window` re-derivation is doubly lossy** — scans the 4 KB `body_preview` only and
  skips `build_search_corpus` transforms, so sensitivity-analysis numbers are an
  under-estimate. *Fix:* document it as a strict lower bound; ideally reuse the corpus.
- **M3. `body_read_failures` never surfaced by `analyze.py`.** The capture side records
  them but the reports don't show them, so a run with unreadable bodies looks identical to
  a clean one. *Fix:* aggregate and print alongside TLS failures; caveat the conclusion when >0.
- **M4. base64 payloads not decoded** (`build_search_corpus`). A base64-encoded document
  transmission would read as 0. *Fix:* add a base64-decode variant for long base64-looking runs.
- **M5. UTF-16 / non-UTF-8 mis-decoded** — `bytes_to_text` falls back to `latin-1`, which
  turns UTF-16 into NUL-interleaved text that never matches. *Fix:* try UTF-16 (BOM) before latin-1.
- **M6. Deprecated sentence-leak metric still printed** (`analyze.py` table) though the code
  comment says it's discredited. *Fix:* remove/relabel as diagnostic-only.
- **M7. Zero-variance CI framed as a strength** (`report/main.tex` ~317–319; `analyze.py`
  "DISJOINT (clear difference)"). std dev 0.0 means *deterministic behaviour*, not a tight
  population estimate; a zero-width t-interval isn't a valid inferential claim. *Fix:* report
  as an exact/deterministic observation; drop or heavily caveat the CI-difference wording.
- **M8. Report limitations omit** single-OS/single-browser, manual paste timing, and uneven
  n (3 vs 5). Add these bullets and add desktop/system-level testing to Future Work (matches
  the 23 July decision).

---

## Low (polish / pre-empt reviewer questions)

- Low-entropy 20-grams (whitespace runs) can cause false-positive coverage — partly offsets
  H2 but muddies the metric; consider dropping near-constant windows.
- HTML-entity transports (`&amp;`, `&#8212;`) not in corpus — add an HTML-unescape variant.
- Chart caption hardcodes "over 5 runs" regardless of `num_runs` (baseline has 3).
- `reproducibility="High"` is emitted even at n=1 — guard with n≥3.
- CI half-width computed after clamping to [0,100] — compute from raw bounds or note the clamp.
- `exposed_events` counts response echoes while exposure % excludes them — different bases; relabel.
- `total_request_bytes` uses compressed on-the-wire size but is labelled outbound bytes — clarify.
- `info_type_breakdown.py` has no guard if a `<tool>_summary.json` is missing — add `f.exists()`.
- "representative run = run_1" is asserted, not verified — add a one-line assertion vs the median.
- Token detection is case-insensitive substring with no word boundaries — fine for synthetic
  unique tokens; add one method sentence explaining why false-positive risk is negligible.
- 14 run dirs on disk vs "13 captures" — the `grammarly_demo` run is correctly excluded
  everywhere; optionally annotate the "13 captures" label "(excludes the live-demo run)".
- `.flow` and `credentials.local.txt` are gitignored (safe) but travel with a zip/copy —
  scrub before any non-git distribution.

---

## Verified correct (do not "fix")

t-table values and df=n-1 selection; exposure % provably bounded ≤100 with no
double-counting; `safe_body` catching undecodable content instead of scoring it clean;
additive search corpus (old JSON bug fixed); responses excluded from outbound exposure;
`should_ignore` exact/dotted-suffix matching (no substring bypass); case handling
consistent between token and window matching; HTTP/2/3 and chunked handled via mitmproxy's
normalized API. Headline numbers (99.0 / 91.9 / 0.0, 12/12, 100% HTTPS, 0 TLS, std dev 0.0)
agree across results JSON, README, dashboard, report, and deck; run counts 5+5+3=13 are
consistent and the demo run is not double-counted; gitignore covers `.flow`, `*.har`,
`Worklog.xlsx`, `credentials.local.txt`; canary appears only in expected locations.
