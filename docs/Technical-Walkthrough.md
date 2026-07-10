# Technical Walkthrough — How the Machinery Works

A "how it's built" explainer for the capture and analysis pipeline. This is for
someone reading the code — an examiner, a contributor, or future-you — who wants
to understand *why* each piece exists and how a paste becomes a percentage. For
running it, see [`Reproduction-Guide.md`](Reproduction-Guide.md); for the story,
see [`Narrative-Walkthrough.md`](Narrative-Walkthrough.md).

---

## 1. The pipeline at a glance

```
  test-document.txt  ──paste──►  Firefox + one extension
        (12 secrets)                     │
                                         │ HTTPS / WebSocket
                                         ▼
                              mitmproxy (proxy on :8080)
                                         │  decrypts with trusted CA
                                         ▼
                    capture_addon.py  (scores each frame live)
                                         │  writes
                                         ▼
                    data/raw/<tool>/run_<id>.json   (+ .flow, .log)
                                         │  read by
                                         ▼
                    analyze.py  (aggregate 5 runs, subtract baseline)
                                         │  writes
                                         ▼
        results/<tool>_summary.json + comparison.json + chart.{png,svg}
```

Two programs do the real work: **`scripts/capture/capture_addon.py`** (a
mitmproxy add-on that scores traffic as it flies past) and
**`scripts/analysis/analyze.py`** (a stdlib-only aggregator that turns raw runs
into statistics). Everything else — the `Makefile`, the test page, the profiles —
exists to feed those two.

---

## 2. The input: a document engineered for detection

`input-data/test-document.txt` is 2,065 characters of realistic-looking but
entirely fictional business memo. Its job is to be *unambiguously detectable* in
network traffic, which it achieves two ways:

- **12 planted secrets** (`SENSITIVE_TOKENS`) — names, an email, a phone number,
  reference/approval/tax codes, and a UUID **canary**. None exist online, so any
  match is provably ours. This same list is duplicated verbatim in both
  `capture_addon.py` and `analyze.py` and documented in
  [`Metrics-Definition.md`](Metrics-Definition.md); the three must stay in sync.
- **Continuous prose** — so that beyond the discrete secrets, the study can also
  measure *what fraction of the whole document* was transmitted, character by
  character (see the sliding window below).

---

## 3. The capture add-on (`capture_addon.py`)

mitmproxy is a scriptable intercepting proxy. You point Firefox at it, trust its
CA in the profile, and it hands every decrypted request, response, and WebSocket
frame to your Python add-on. The add-on here is a single class, `ExposureTracker`,
registered at the bottom (`addons = [ExposureTracker()]`), whose methods are
mitmproxy *hooks* — callbacks fired on network events.

### 3.1 Configuration and startup

At import time the add-on reads a few environment variables — `TOOL_NAME`,
`RUN_ID`, and an optional `WINDOW_SIZE` (default **20**) — loads the test
document, and builds its matching structures. Making the window size an env var is
what lets you *re-analyze* a saved `.flow` file at a different granularity without
editing code.

### 3.2 The core idea: a sliding-window coverage set

To measure "how much of the document appears in traffic," the add-on slides a
**20-character window** across the document, producing every length-20 substring.
A window of 20 is long enough that ordinary words don't produce false matches, but
short enough to catch partial sends. For any captured payload, every document
window found in it marks that range of character positions as **covered**. The
metric is then just the size of the union of covered positions over the whole
document.

Doing that naively (every window against every payload) is O(n·m) and slow, so
when `pyahocorasick` is available the add-on compiles all unique windows into an
**Aho-Corasick automaton** (`WINDOW_AUTO`) that finds all matches in a payload in
one linear pass. If the library is missing it falls back to the slow scan — same
answer, just slower. This is `find_covered_positions()`.

### 3.3 Matching through encodings: the search corpus

Tools rarely send raw text — they gzip it, URL-encode it, or wrap it in JSON with
`\n` and `\uXXXX` escapes. If the add-on only searched the raw bytes, a
JSON-escaped document would score 0 %. So before matching, `build_search_corpus()`
expands each payload into several **variants**: the original, an NFC-normalized
form, a URL-decoded form, the string values pulled from parsed JSON, and an
in-place JSON-unescaped form. The design rule is that variants are **additive** —
each can only *add* coverage, never remove it — so a spurious unescape can never
inflate a false negative into a false positive. The same corpus feeds
`find_tokens_in_text()`, which checks the 12 secrets case-insensitively.

### 3.4 Reading bodies safely

`safe_body()` exists because of a subtle trap: mitmproxy's `message.content`
transparently decompresses gzip/deflate, but **raises `ValueError`** on an
encoding it can't handle (e.g. Brotli). A naive `message.content or b""` would let
that exception escape and the event would vanish — silently scored as "clean."
Instead `safe_body()` catches the error, falls back to `raw_content` plus the
header encoding (so the add-on's own `decompress()`, which includes Brotli, can
try), and if even that fails it records the miss in `session["read_failures"]`.
The principle throughout: **"couldn't read" must never be counted as "nothing
leaked."**

### 3.5 The hooks

- **`request()`** — the main path. Skips ignored hosts, builds the search text
  from URL + headers + decompressed body, computes covered positions and tokens,
  appends an event record, and buffers the raw body in `PER_HOST_BODIES` for the
  transcript pass (§3.6).
- **`response()`** — scores response bodies too, because some tools echo the
  document back. These are recorded but flagged `http_response`; they are
  **diagnostic only** and excluded from the headline (a decision made 2026-05-28:
  exposure means data going *out*, not echoes coming back).
- **`websocket_message()`** — grammar checkers stream over WebSockets, so this is
  where Grammarly's exposure actually shows up. It scores only **client→server**
  frames (`from_client`) and buffers them for the transcript pass.
- **`tls_failed_client()` / `tls_failed_server()`** — record handshakes that
  couldn't be intercepted (certificate pinning). Their contents are unknown, which
  is exactly why they're counted: a non-zero count means the reported exposure is a
  lower bound.

### 3.6 Two coverage passes: per-event and transcript

There's a gap in per-event scoring: if a tool splits the document across two
WebSocket frames so that no single frame contains a full 20-char window, per-event
matching misses the boundary. To close it, `done()` runs a second **transcript
pass**: for each host it concatenates *all* its buffered client→server bodies and
scans the joined text. This uses the **full** bodies, not the 4 KB
`body_preview` stored per event (previews are for human inspection and are too
small to catch chunking). Per-host transcript coverage is stored separately
(`transcript_covered_by_host`) so the analyzer can apply baseline subtraction to
it host-by-host before folding it in.

### 3.7 The host filter (a deliberate limitation)

`IGNORE_SUFFIXES` drops known browser/Mozilla/Google background hosts (telemetry,
safebrowsing, OCSP, etc.) **at capture time**. This is worth understanding because
it runs *before* events are recorded — so unlike baseline subtraction in the
analyzer, anything filtered here cannot be recovered later. The code comments flag
this and suggest re-checking the list against fresh baseline runs, because Mozilla
telemetry hostnames drift between Firefox versions.

### 3.8 Output

`done()` unions the per-event and transcript coverage, assembles a `summary`
(event counts, `https_event_pct`, `tls_handshake_failures`, `union_exposure_pct`,
`sensitive_token_count`, and the per-host transcript coverage), and writes the
whole session to `data/raw/<tool>/run_<id>.json`. Alongside it, mitmproxy's
`--save-stream-file` writes the raw `.flow` archive — the ground truth you can
replay later at a different window size.

---

## 4. The analyzer (`analyze.py`)

The analyzer deliberately imports **only the standard library** (`argparse`,
`json`, `math`, `re`, `statistics`) — no mitmproxy, no scipy. That means it runs
anywhere, including a plain Windows checkout, and it's why the reproducibility
manifest doesn't need the capture stack just to re-crunch numbers.

### 4.1 Baseline subtraction

`get_baseline_domains()` collects every host seen across the `baseline` runs. When
analyzing a tool, `analyze_run()` drops any event whose host is in that set —
removing ordinary browser background before scoring. The same rule is applied to
the transcript coverage host-by-host in `union_exposure_from_run()`.

### 4.2 Per-run exposure

`union_exposure_from_run()` unions the `covered_positions` across all outbound
events (skipping `http_response` echoes), folds in the baseline-filtered
transcript coverage, and divides by the document length to get that run's exposure
%. `--window N` offers a best-effort re-derivation from the 4 KB previews for quick
sensitivity checks; the *authoritative* way to change the window is to re-run the
capture add-on against the `.flow` file with `WINDOW_SIZE=N`.

### 4.3 Secrets and TLS visibility

`check_sensitive_tokens()` returns a `{token: bool}` map for the 12 secrets, using
the recorded hits and falling back to a scan of event previews.
`tls_visibility()` returns the **two separate numbers** — `https_event_pct` and
`tls_handshake_failures` — that the metrics design insists never be multiplied
into one composite "confidence" figure (an earlier composite formula was
explicitly rejected; see [`Metrics-Definition.md`](Metrics-Definition.md) §3).

### 4.4 Aggregating five runs

`analyze_tool()` runs `analyze_run()` over every `run_*.json` and computes median,
mean, min, max, and standard deviation of exposure. It attaches a **95 % confidence
interval** via `confidence_interval_95()`, which uses a hardcoded t-table
(`T_CRIT_95`, df 1–30) rather than depending on scipy — for five runs, df = 4,
t = 2.776. Standard deviation becomes a **reproducibility label**: High (< 3 pp),
Medium (3–10 pp), Low (> 10 pp). It tallies which secrets appeared in how many
runs, and composes a plain-language `conclusion` sentence whose **headline is the
planted-secret count** (with a special note when the canary is among them),
exposure % second. The result is written to `results/<tool>_summary.json`.

> A note on the sentence-level metric: `sentences_fully_leaked()` (a sentence
> counts as leaked at ≥ 90 % character coverage) is still computed and printed in
> the comparison table, but the reporting decision (QA §7) made the secret count
> the headline because the sentence unit had over-counted short header/label
> lines. Treat it as a secondary, interpretability figure.

### 4.5 Presentation

`print_tool_table()` renders one tool secrets-first. `print_comparison_table()`
puts the tools side by side and adds a **pairwise 95 % CI overlap** check —
non-overlapping intervals are informal evidence of a real difference between
tools. `make_comparison_chart()` draws a bar chart with CI error bars and saves
both **PNG** (slides) and **SVG** (LaTeX). The CLI (`main()`) wires up
`--all`, `--file`, `--no-baseline`, `--window`, `--sentence-threshold`, and
`--chart`.

---

## 5. Orchestration and the manual-paste decision

The `Makefile` turns the multi-terminal protocol into one-line targets
(`make page-grammarly`, `make grammarly-1 … 5`, `make baseline-1 … 3`,
`make analyze`, `make chart`). Its `run_one` macro loads the document into the
clipboard, starts the recorder with the right `TOOL_NAME`/`RUN_ID`, then **pauses
for a human to paste**. That pause is the single most important operational
detail in the whole system: an automated `xdotool` paste fills the box visually
but doesn't fire the DOM `input` event the extension listens for, so the tool
never ingests the text and you get a false 0 %. A real **Ctrl+V** does fire it.
An opt-in `AUTO=1` path exists for experiments but is documented as not
recommended.

---

## 6. Why the design choices hang together

Every non-obvious piece traces back to one goal — *a number you can defend*:

- **20-char window + additive encoding variants** → catch real transmission
  through gzip/URL/JSON without false positives.
- **Transcript pass** → chunked sends can't hide between frames.
- **`safe_body` + `read_failures`** → an unreadable body is flagged, never
  miscounted as clean.
- **Capture-time host filter + analyzer baseline subtraction** → two independent
  layers separating tool traffic from browser noise.
- **TLS failures counted, never merged** → exposure is always an honest lower
  bound.
- **Secret-count headline + canary** → the top-line claim rests on an unforgeable
  token, not a fuzzy percentage.
- **Stdlib-only analyzer + saved `.flow` files** → anyone can re-run the analysis,
  and re-derive it at a new window, long after capture.

---

*See also: [`Metrics-Definition.md`](Metrics-Definition.md) for exact metric
formulas, [`Capture-Protocol.md`](Capture-Protocol.md) for the locked per-run
steps, and [`ENVIRONMENT.md`](ENVIRONMENT.md) for pinned versions.*
