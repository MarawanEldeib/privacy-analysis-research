# Zero-to-Hero Guide — Every File & How the Code Works

A study guide for the supervisor meeting. Read it top to bottom once and you'll be
able to explain any file in the project and defend how the code works. It is written
in plain language — concepts first, code second.

---

## Part 0 — The one-paragraph mental model

You built a **measurement pipeline**. It answers one question: *when a
writing-assistant extension is running, how much of a confidential document does it
silently send to its servers?* The pipeline has two custom programs. The first
(`capture_addon.py`) sits inside a proxy, watches the browser's outgoing traffic,
and — because you planted unique markers in the document — records how much of the
document and which secrets left the machine. The second (`analyze.py`) takes those
recordings from five runs per tool, subtracts the "no-extension" baseline, and turns
them into statistics and a headline: *N of 12 secrets sent, ~X% of the document*.
Everything else in the folder supports, documents, or presents those two programs.

**The data flow, in one line:**
`test-document.txt` → (paste into `test-page.html`) → Firefox → **mitmproxy +
capture_addon.py** → `data/raw/<tool>/run_N.json` → **analyze.py** →
`results/<tool>_summary.json` → the report & dashboard.

---

## Part 1 — The folder map (what each folder is for)

| Folder | What lives there | Why it exists |
|---|---|---|
| `scripts/capture/` | the mitmproxy add-on + a shell wrapper | **captures** traffic and scores it |
| `scripts/analysis/` | the analyzer | turns raw captures into **statistics** |
| `input-data/` | the test document + the test web page | the **controlled input** |
| `data/raw/` | one JSON (+ raw `.flow`) per run | the **raw evidence** |
| `results/` | one summary JSON per tool | the **aggregated findings** |
| `docs/` | methodology, protocol, walkthroughs, this guide | the **written record** |
| `report/` | the LaTeX academic report + figure | the **deliverable** |
| `presentation/` | the slide deck | for **this meeting** |
| `tests/` | pytest regression tests | prove the code **stays correct** |
| `skills/` | notes that auto-load into Claude sessions | project **memory** |

---

## Part 2 — The input (start here; everything measures against this)

### `input-data/test-document.txt`
A fake "confidential memo" — 2,065 characters, 35 sentences. It **looks** like a real
compliance document (a budget for "Project Nighthawk-3", signed by "Helena Voss"), but
every sensitive detail is invented. Hidden inside it are **12 unique identifiers** you
planted: names, an email, a phone number, reference/approval/tax codes, and the star of
the show — the **canary**: `CANARY-BC267061-67DC-485B-8E51-6F5494765CAB`.

**Why it's built this way:** none of these strings exist anywhere on the internet. So
if any of them shows up in captured traffic, it *must* have come from your document —
there's no other possible source. That turns a vague question ("did some text leak?")
into a hard yes/no. The canary is the most unique of all, so it's your undeniable proof.

> **Meeting soundbite:** "I don't rely on guessing what personal data is — I plant
> markers I control, so every detection is provable."

### `input-data/README.md`
A table listing all 12 tokens and their type. It also notes one subtlety: the document
contains `#2026-LGL-00847` (with a `#`), but the analyzer searches for it *without* the
`#`, so it still matches if a tool strips punctuation. This file is the "source of
truth" for the token list — it must stay in sync with the two Python files.

### `input-data/test-page.html`
A bare web page with one text box (`<textarea>`) and a second `contenteditable` "rich
editor" box. No analytics, no third-party scripts, nothing. **Why:** the extension
behaves on this page exactly as it would on Gmail, but with zero background noise to
filter out — so whatever traffic you see is *only* the extension. The second rich-editor
box was added for tools (ProWritingAid/Wordtune) that don't attach to a plain textarea.

---

## Part 3 — THE CAPTURE CODE: `scripts/capture/capture_addon.py` (the heart)

This is a **mitmproxy add-on**. mitmproxy is a proxy that decrypts HTTPS; an "add-on"
is a Python file it loads that gets to inspect every request. Think of it as a customs
officer you wrote, standing between the browser and the internet, opening every parcel.

It runs top to bottom once at load (setup), then mitmproxy calls your functions
("hooks") every time traffic happens. Here's how it's coded, in order:

### 3.1 Setup (runs once when the proxy starts)
- Reads **environment variables** `TOOL_NAME`, `RUN_ID`, and `WINDOW_SIZE` (default 20).
  These tell it which tool/run it's recording and how long the matching window is.
- Loads `test-document.txt` into memory (`TEST_CONTENT`), stores its length
  (`TOTAL_CHARS = 2065`) and a lowercased copy (`TEST_LOWER`) for case-insensitive
  matching.
- Defines `SENSITIVE_TOKENS` — the same 12 planted strings.
- Defines `IGNORE_SUFFIXES` — a list of background hosts (Mozilla telemetry, Google
  safe-browsing, certificate servers). Traffic to these is skipped so browser noise
  doesn't get counted. **Important nuance:** this filter runs *at capture time*, so
  anything filtered here can't be recovered later.

### 3.2 The core idea: the 20-character "sliding window"
To measure *how much* of the document leaked, the code needs to find pieces of the
document inside the traffic. It slides a **20-character window** across the document:
characters 0–19, then 1–20, then 2–21, and so on — producing every possible 20-char
snippet. For any captured payload, every snippet found in it marks those character
positions as "covered." Exposure % is then just *how many of the 2,065 positions got
covered*.

**Why 20 characters?** Too short (say 3) and common words like "the" would match random
internet traffic — false positives. Too long and you'd miss partial sends. 20 is the
sweet spot: long enough to be unique to *your* document, short enough to catch fragments.

**How it's made fast:** comparing every window against every payload is slow. So at
startup the code builds an **Aho-Corasick automaton** (`WINDOW_AUTO`) — a data structure
that finds all of the snippets in a payload in a single pass. (If the optional library
isn't installed, it falls back to a slower but identical scan.) This is
`find_covered_positions()`.

### 3.3 Matching through disguises: `build_search_corpus()`
Tools rarely send raw text. They gzip it, or URL-encode it, or wrap it in JSON where a
newline becomes `\n` and an em-dash becomes `—`. If the code only searched the raw
bytes, a JSON-wrapped document would score 0%. So before matching, this function makes
several **variants** of each payload: the original, a Unicode-normalized form, a
URL-decoded form, the text pulled out of parsed JSON, and a JSON-unescaped form. It
searches all of them. The rule is that variants can only *add* coverage, never remove
it — so a wrong guess is harmless. (There's a dedicated test locking this in, because a
bug here once cost ~5–8 percentage points.)

### 3.4 Reading bodies safely: `safe_body()`
A subtle trap: mitmproxy's `.content` auto-decompresses gzip, but **throws an error** on
an encoding it can't handle (like Brotli). A naive read would let that error make the
whole event vanish — silently scored as "clean" (a false negative). `safe_body()`
catches the error, falls back to the raw bytes so the code's own decompressor can try,
and if even that fails it **records the failure** in `read_failures`. The principle
running through the whole file: *"couldn't read" must never be counted as "nothing
leaked."*

### 3.5 The hooks (mitmproxy calls these on live traffic)
- **`request()`** — the main one. For each outgoing request it skips ignored hosts,
  gathers the URL + headers + decompressed body, finds covered positions and any of the
  12 tokens, saves an event record, and stashes the raw body for the transcript pass
  (below).
- **`response()`** — scores replies too (some tools echo the document back), but marks
  them `http_response`. These are **diagnostic only** — a decision was made that
  "exposure" means data going *out*, not echoes coming back, so responses never count
  toward the headline.
- **`websocket_message()`** — Grammarly streams over a WebSocket (a live two-way
  connection), so *this* is where its leak actually shows up. It scores only
  **client→server** frames (data leaving you).
- **`tls_failed_client()` / `tls_failed_server()`** — record any connection that
  couldn't be decrypted (e.g. certificate pinning). Their contents are unknown, which is
  exactly why they're counted: a non-zero count means your exposure figure is a *lower
  bound*, reported honestly.

### 3.6 Two coverage passes, then save: `done()`
There's a gap in per-event scoring: if a tool splits the document across two WebSocket
frames so no single frame holds a full 20-char window, per-event matching misses the
seam. So `done()` runs a second **transcript pass**: for each host it glues together
*all* that host's outgoing bodies and scans the joined text. It stores this per host
(`transcript_covered_by_host`) so the analyzer can subtract the baseline host-by-host
later. Finally it unions the two passes, builds the `summary`, and writes everything to
`data/raw/<tool>/run_N.json`. mitmproxy separately saves the raw `.flow` archive — the
untouched evidence you can re-analyze offline.

> **Meeting soundbite:** "The add-on scores traffic live, handles compression and
> encoding, counts what it *couldn't* see, and catches leaks split across frames — so
> the number is a careful lower bound, not an optimistic guess."

---

## Part 4 — THE ANALYSIS CODE: `scripts/analysis/analyze.py`

This program **imports only the Python standard library** — no mitmproxy, no scipy. That
means it runs anywhere (even a plain Windows laptop), and it's why you can re-crunch
numbers without the capture stack. Here's how it's built:

### 4.1 Setup
- `TOOLS = ["grammarly", "languagetool", "baseline"]` — the final scope.
- Re-defines the same 12 `SENSITIVE_TOKENS` (kept in sync with the capture file).
- Loads the document, splits it into **sentences** (`_parse_sentences` → 35 sentences),
  used for a secondary "how many whole sentences leaked" figure.

### 4.2 Statistics without scipy
- `T_CRIT_95` is a small hard-coded lookup table of t-distribution critical values.
  `confidence_interval_95()` uses it to compute a **95% confidence interval** on the
  mean exposure — the honest "the true value is likely in this range" band — without
  needing a heavy stats library. For 5 runs the t-value is 2.776.

### 4.3 Turning one run into numbers: `analyze_run()` + `union_exposure_from_run()`
- `get_baseline_domains()` collects every host seen in the baseline (no-extension) runs.
- `union_exposure_from_run()` takes a run, **unions the covered positions** across all
  *outbound* events (skipping `http_response` echoes), folds in the transcript coverage
  *minus any baseline host*, and divides by 2,065 to get that run's exposure %.
- `check_sensitive_tokens()` returns which of the 12 secrets were found.
- `tls_visibility()` returns the **two separate numbers** — HTTPS event share and TLS
  failure count — that the methodology insists never be multiplied into one score.

### 4.4 Aggregating five runs: `analyze_tool()`
Runs the above over every `run_*.json`, then computes median, mean, min, max, and
**standard deviation** of exposure; attaches the 95% CI; converts the std dev into a
**reproducibility label** (High < 3pp, Medium 3–10pp, Low > 10pp); tallies which secrets
appeared in how many runs; and writes a plain-English **conclusion** sentence whose
*headline is the secret count* (with a special note if the canary is among them). Result
saved to `results/<tool>_summary.json`.

### 4.5 Presentation
- `print_tool_table()` prints one tool, secrets first.
- `print_comparison_table()` puts tools side by side and adds a **pairwise CI-overlap
  check** — if two tools' confidence intervals don't overlap, that's informal evidence
  they really differ.
- `make_comparison_chart()` draws the bar chart with error bars and saves **PNG** (for
  slides) and **SVG** (for LaTeX).
- `main()` is the command-line interface: `--all`, `--file`, `--no-baseline`,
  `--window`, `--sentence-threshold`, `--chart`.

> **Meeting soundbite:** "The analyzer is deliberately plain — stdlib only, a hard-coded
> t-table instead of scipy — so anyone can reproduce the statistics, and the raw `.flow`
> files mean the whole analysis can be re-run at a different setting without re-capturing."

---

## Part 5 — Orchestration: `Makefile` & `run_capture.sh`

### `Makefile`
Turns the multi-step protocol into one-line commands: `make check` (verify tools),
`make page-grammarly` (open the page in the right profile), `make grammarly-1` (record
run 1), `make analyze`, `make chart`. Its `run_one` macro loads the document into the
clipboard, starts the recorder, then **pauses for you to paste manually**. That pause is
the single most important operational detail: a *scripted* paste fills the box but
doesn't fire the DOM `input` event the extension listens for, so nothing is sent — a
false 0%. A **real Ctrl+V** is what makes the tool ingest the text.

### `scripts/capture/run_capture.sh`
An earlier, simpler shell wrapper that does the same capture for one tool/run. *Heads-up
for the meeting:* its built-in tool list still names the old set
(`grammarly/prowritingaid/wordtune/baseline`) — it predates the final scope. The
**Makefile is the current entry point**; the shell script is kept as a manual fallback.
If the professor opens it, that's the honest explanation.

---

## Part 6 — The evidence: `data/raw/` and `results/`

### A run file — `data/raw/grammarly/run_1.json`
The full record of one capture. Key fields: a list of `requests` and `ws_messages`
(each with `host`, `covered_positions`, `exposure_pct`, `tokens_found`, and a 4 KB
`body_preview` for human inspection), plus a `summary` block with `union_exposure_pct`,
`sensitive_token_count`, `https_event_pct`, `tls_handshake_failures`, and the per-host
transcript coverage. The matching `.flow` file (gitignored — it holds decrypted auth
tokens) is the raw archive.

### A summary file — `results/grammarly_summary.json`
The analyzer's output for one tool: `exposures_per_run`, `median/mean_exposure_pct`,
`stdev`, the 95% CI, `reproducibility`, `sensitive_tokens_detected`, the per-run details,
and the `conclusion` sentence. This is what feeds the report and dashboard.

*(There's also a `grammarly_demo` run — that's the live demo you ran; safe to ignore or
delete.)*

---

## Part 7 — Tests: `tests/` (why the code is trustworthy)

Two pytest files that lock in the correctness of the tricky parts. Run with `pytest`
from the repo root.

- **`test_matching.py`** — proves the capture matcher recovers the document even when
  it's sent as JSON (escaped newlines / em-dashes), detects the canary in a JSON body,
  and produces **no false positives** on unrelated text.
- **`test_analyze.py`** — proves the analyzer folds in the transcript coverage (a bug
  once dropped it → false 0%), subtracts the baseline host-by-host, excludes server
  echoes from the headline, maps sentence offsets correctly, and computes CIs sanely. It
  also **anchors the document** (`assert TOTAL_CHARS == 2065`) so an accidental edit to
  the test document fails loudly instead of silently invalidating all runs.

> **Meeting soundbite:** "Every bug I found in review is frozen by a regression test, so
> it can't silently come back."

---

## Part 8 — Config & housekeeping files

- **`requirements.txt`** — pinned Python dependencies (mitmproxy 12.2.3, brotli,
  pyahocorasick, matplotlib).
- **`pyproject.toml`** — dev-tool config (pytest, ruff, black). Deliberately *not* an
  installable package — it's a set of scripts.
- **`.gitignore`** — keeps secrets and bulky/derived files out of git: `credentials.local.txt`,
  `Worklog.xlsx`, the `.flow` archives (they contain decrypted tokens), and LaTeX build junk.
- **`.gitattributes`** — forces **LF line endings** on `.sh`/`.py`/Makefile so Windows
  git doesn't add carriage returns that would break the scripts on Kali.
- **`LICENSE`** (MIT) and **`CITATION.cff`** — make the repo publishable/citable later.
- **`credentials.local.txt`** — throwaway test-account logins (gitignored, never pushed).
- **`Worklog.xlsx`** — your hours log (gitignored).

---

## Part 9 — The documents (`docs/`) in one line each

- **`WALKTHROUGH.md`** — the doc map / entry point.
- **`Reproduction-Guide.md`** — run the whole study from scratch (commands + verified links).
- **`Narrative-Walkthrough.md`** — the project story, including the dead ends.
- **`Technical-Walkthrough.md`** — how the code works (a sibling to this guide).
- **`Capture-Protocol.md`** — the locked per-run steps.
- **`Metrics-Definition.md`** — exact formulas for every metric.
- **`ENVIRONMENT.md`** — pinned software versions for reproducibility.
- **`Project-Overview.md`** — the high-level summary + status.
- **`QA-Professor.md`** — the decision log (why each choice was made).
- **`Related-Work-Research.md`** — the cited literature digest.
- **`Timeline.md`** — the schedule.
- `Setup-Guide.md` (retired → points to Reproduction-Guide), `Operational-Prompts.md`,
  `New-Chat-Starter-Prompt.md`, `Professor-Update-Email.md`, and the two dated
  `*-Review-2026-05-28.md` snapshots are historical/support docs.

**`report/`** holds the LaTeX report (`main.tex`), bibliography (`refs.bib`, now
Zotero-managed), the figure, and the compiled `main.pdf`. **`Project-Dashboard.html`** is
a self-contained results dashboard you can open in any browser.

---

## Part 10 — Likely professor questions & crisp answers

**"Isn't it obvious these tools send data?"** — That they transmit, yes. That they
transmit the *entire* confidential document, *every* secret, silently, 99% reproducibly,
while other tools send nothing — that had to be measured, and nobody had done it in a
consistent, comparable way with per-secret proof.

**"How do you know it really leaked?"** — The canary. It exists nowhere else, so finding
it in the outbound traffic is undeniable. The baseline reads 0%, so the browser isn't the
source.

**"You're decrypting HTTPS — is that legitimate?"** — It's my own machine, my own
browser, with a certificate I installed myself. I'm reading what my own browser sends. No
attack on the vendor.

**"Why only two tools / all browser grammar checkers?"** — I tried to broaden (four tools)
but three didn't fit the method for documented reasons (didn't attach / no Firefox
extension / counterfeit clone + on-demand). Two independent tools showing identical
behaviour is strong within-class replication; broadening to other integration types is
the planned next step.

**"How much of this is reproducible?"** — All of it. The protocol is locked, versions are
pinned, the raw `.flow` files are archived, and regression tests guard the analysis. The
*method* reproduces exactly; the specific percentages reflect tool behaviour at capture
time.

**"How confident are the numbers?"** — Reported honestly as separate figures:
reproducibility (std dev 0.0 — identical every run), traffic visibility (100% HTTPS, 0
un-decryptable handshakes), and a 95% CI. I deliberately rejected a single composite
"confidence %" because it hides which kind of uncertainty you're looking at.

---

*If you can explain Parts 3 and 4 in your own words, you can defend the whole project.
Everything else supports those two files.*
