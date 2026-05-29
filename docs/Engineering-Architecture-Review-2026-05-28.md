# Engineering & Architecture Review — Privacy Analysis Repo

> **STATUS — updated 2026-05-28:** The safe items (deps pinning, tests, `analyze.py` cleanups, doc reconciliation, type hints, narrowed exceptions) are **applied**; the remaining backlog is tracked in the session task list and `skills/privacy-analysis-project/SKILL.md`. Kept as the reference for the refactor plan.

**Reviewer:** senior engineer / architect pass · **Date:** 2026-05-28
**Scope:** whole repo, read-only. **No code changed.** Line refs are against the
post-fix files (`capture_addon.py` 576 lines, `analyze.py` 618 lines).

> Calibration note up front: this is a small, **generally clean** research codebase
> (~1,200 LOC of Python across two entry points, plus a Makefile and docs). It is
> well-commented and reasonably named. The dominant risks here are **over-engineering**
> and **touching the measurement instrument right before you use it** — not messiness.
> I flag real issues, but I deliberately do not invent SOLID/design-pattern work that
> would make a 470-line script worse. Most of the highest-value wins are *additive*.

---

## 1. Summary

- Architecture is sound for its purpose: a two-stage **capture → analyze** pipeline with a **durable raw `.flow` archive** decoupling the two. That archive is the single best decision in the repo — it's what made last week's bug fixes recoverable without re-capturing. Keep it.
- The code is clean and well-commented; naming is good; docstrings cover the important functions. This is **not** a codebase that needs a rewrite.
- Highest-value, lowest-risk improvements are **additive and don't touch instrument logic**: pin dependencies (`requirements.txt`) for reproducibility, and add a `tests/` regression guard for the three bugs just fixed.
- The one legitimate structural debt is **duplication across the two entry points** (`SENSITIVE_TOKENS` verbatim in both; matching logic conceptually duplicated) plus **implicit JSON-schema coupling**. Real DRY/SOLID issues — but the fix edits both instrument files, so do it *with* tests or *after* captures.
- A few small **safe** correctness/cleanliness nits in `analyze.py` (dead TLS fallback, an always-zero metric, one unused variable) can be fixed now with no behavior risk.
- **Engineering-practice gaps for a public/portfolio repo:** no `requirements.txt`/`pyproject.toml`, no CI, no linter/formatter config, and several **stale docs** that contradict the current code.
- **Overarching recommendation:** freeze `capture_addon.py` / `analyze.py` *logic* until after the P8 validation gate and the capture runs. Apply only additive/safe changes now.

---

## 2. Key engineering issues

**P1 — Reproducibility: no pinned dependencies.**
- *Where:* repo root (no `requirements.txt` / `pyproject.toml`); deps only in prose (`README.md`, `docs/Setup-Guide.md`).
- *Why it matters:* results depend on mitmproxy's behavior, which **changed across versions** (the `.content` decode semantics and WS scheme handling you just worked around). An unpinned environment means your captures may not be reproducible by you in October or by anyone re-running the study.
- *Fix:* add `requirements.txt` with pinned versions (e.g. `mitmproxy==X.Y.Z`, `brotli`, `pyahocorasick`, `matplotlib`). Additive, safe, do now.

**P1 — No automated tests.**
- *Where:* no `tests/`.
- *Why it matters:* the matching logic is subtle and just produced silently-wrong numbers (transcript drop, JSON-escape undercount, WS TLS flag). Nothing guards against re-introducing them.
- *Fix:* add `tests/` covering `build_search_corpus` (escaped-JSON coverage), `union_exposure_from_run` (transcript fold-in + baseline subtraction), and `_parse_sentences`. Additive, safe — but see P2 issue on import side-effects (tests may need to import the addon).

**P2 — `analyze.py`: an always-zero metric is reported as fact.**
- *Where:* `avg_request_bytes` computed at `analyze.py:397` from `r["total_request_bytes"]` (`:274`), which reads `summary.get("total_request_bytes", 0)` — a key the addon never writes. Printed at `:443` as "Avg request bytes: 0".
- *Why it matters:* the proposal lists "volume of outbound data (bytes)" as an indicator; it silently reads 0 in every run. A reported number that's always zero is worse than no number.
- *Fix:* compute from summed event `content_length`, or drop the metric. Safe to do now (output-only).

**P2 — `analyze.py`: dead `tls_visibility` fallback.**
- *Where:* `analyze.py:173-176` references `total_request_bytes` / `tls_request_bytes`, neither of which exists in the addon's schema.
- *Why it matters:* dead code that pretends a legacy schema still exists; misleads future readers.
- *Fix:* delete the fallback (the addon always writes `https_event_pct`). Safe now.

**P2 — Incomplete hardening: `.content` still accessed raw for length fields.**
- *Where:* `capture_addon.py:386` (`len(flow.request.content or b"")`) and `:414` (`flow.response.content`). You fixed body extraction via `safe_body()` (`:312`), but these length fields still touch `.content`, which raises `ValueError` on a bad content-encoding *before* the `or` runs — crashing the hook for exactly the events `safe_body` was meant to save.
- *Why it matters:* same silent-drop bug class you just closed, left open on the length field.
- *Fix:* derive length from the bytes `safe_body` already returns. **Touches instrument — defer or do with tests.**

**P3 — Module-level side effects + `sys.exit` on import.**
- *Where:* `capture_addon.py:116-143` (reads test doc, builds automaton, prints; `sys.exit(1)` at `:118`).
- *Why it matters:* importing the module (e.g. from a test) does heavy work and can kill the process. Hurts testability — which you need for the P1 test suite.
- *Fix:* move heavy init into a function or the addon `load()` hook; `raise` instead of `sys.exit`. **Touches instrument — defer.**

**P3 — Global mutable state instead of instance state.**
- *Where:* `session` (`:147`) and `PER_HOST_BODIES` (`:168`) are module globals mutated by `ExposureTracker`.
- *Why it matters:* the idiomatic mitmproxy pattern is per-addon-instance state (`__init__`/`load`); globals rely on one-process-per-run and are hard to test.
- *Fix:* move state into `ExposureTracker`. **Touches instrument — defer.**

**P3 — Broad `except Exception: pass`.**
- *Where:* `decompress` (`:192`), `build_search_corpus` (`:250, :255, :267, :274`), `safe_body` (`:328, :334`), `websocket_message` (`:435`).
- *Why it matters:* silent swallowing hides genuine errors; conventionally you catch the specific type (`zlib.error`, `brotli.error`, `json.JSONDecodeError`, `UnicodeDecodeError`, `ValueError`).
- *Fix:* narrow the excepts; optionally debug-log. Several are defensible (additive variants) — low priority, and touches instrument.

**P3 — `print()` instead of `logging`.**
- *Where:* throughout both scripts.
- *Why it matters:* no levels, can't quiet/redirect, mixes with mitmproxy's own output. (Mitigated by the per-run `.log` file, so it's a convention nit, not a bug.)
- *Fix:* a module `logging` logger with levels. Low priority; touches instrument.

**P3 — Provenance metadata never populated.**
- *Where:* `capture_addon.py:154-156` — `tool_version` / `browser_version` / `os_info` default `"unknown"` and are never set.
- *Why it matters:* every run records "unknown"; weak provenance for a study you may publish.
- *Fix:* set via env in `run_capture.sh` / Makefile, or capture programmatically. Safe-ish (capture-side), low priority.

**P3 — Minor: unused variable.**
- *Where:* `analyze.py:316` — `ci_mean_raw` unpacked but never used.
- *Fix:* `_`. Trivial, safe.

---

## 3. Key architectural issues

**A1 — Duplication across the two entry points (DRY).**
- `SENSITIVE_TOKENS` is copy-pasted verbatim: `capture_addon.py:67-80` and `analyze.py:34-47` (plus prose copies in `docs/Metrics-Definition.md` and `input-data/README.md`). Drift already happened — `Metrics-Definition.md §4` says "11 planted identifiers" then lists 12.
- *Why it matters:* four copies of the canonical list = guaranteed eventual divergence; the tokens are the project's strongest evidence, so a drift here is costly.
- *Change:* one source of truth — a `constants.py` imported by both scripts (and the docs reference it rather than re-listing). **Touches both instrument files — do with tests or after captures.**

**A2 — Matching logic conceptually duplicated.**
- `capture_addon.py:236-301` (`build_search_corpus` / `find_covered_positions` / `find_tokens_in_text`) vs `analyze.py:122-148` (`rederive_covered_positions_from_previews`) are two implementations of "match document windows in text," with different capabilities.
- *Why it matters:* they can (and did) diverge; the analyzer's is a weaker 4 KB-preview re-derivation.
- *Change:* extract a shared `matching.py`. **Defer (post-data).**

**A3 — Implicit JSON-schema coupling.**
- `analyze.py` depends on exact keys the addon writes (`covered_positions`, `tokens_found`, `transcript_covered_by_host`, `summary.*`) with no shared definition.
- *Why it matters:* a renamed key silently breaks analysis — this is exactly the class of bug that bit v2 (analyzer read a `body_preview` token field the addon never wrote).
- *Change:* a shared schema (dataclasses or a documented `schema.md`). **Defer.**

**A4 — "Scalability" is largely N/A — and that's fine.**
- This is a controlled experiment, not a service; there's no request volume to scale. The only scale concern is large captures, already handled by `.flow` + the Aho-Corasick fast path.
- *Why it matters:* I'm flagging this so the review is honest — don't add queues, workers, or caching layers here. That would be pure over-engineering.

**Architectural strengths (keep):** clean capture/analysis separation; durable `.flow` raw store enabling offline re-analysis; one-direction dependency (analysis → capture's output); Makefile as a thin orchestration layer; the mitmproxy addon-class/hook pattern used correctly.

---

## 4. Proposed refactors (in priority order)

**R1 — Add `requirements.txt` (and optional `pyproject.toml`).** *(apply now, safe)*
- *Scope:* repo root. *Plan:* pin the exact installed versions of mitmproxy/brotli/pyahocorasick/matplotlib. *Benefit:* reproducibility — the #1 property a measurement study needs.

**R2 — Add a `tests/` regression suite.** *(apply now, safe — additive)*
- *Scope:* new `tests/`. *Plan:* port the functional checks already validated — escaped-JSON coverage, transcript fold-in + baseline subtraction, sentence parsing. Run via `pytest`. *Benefit:* locks in the three fixes; prevents silent re-regression.

**R3 — `analyze.py` safe cleanups.** *(apply now, low risk — output-only)*
- *Scope:* `analyze.py`. *Plan:* drop the dead `tls_visibility` fallback (`:173-176`); fix or remove `avg_request_bytes` (`:397/:443`); `_` the unused `ci_mean_raw` (`:316`). *Benefit:* removes misleading output and dead code without changing exposure numbers.

**R4 — Doc reconciliation.** *(apply now, safe — docs only)*
- *Scope:* `Professor-Update-Email.md` (typing→paste, drop bytes-ratio), `QA-Professor.md` Q3 + `Timeline.md` Phase 3 (remove rejected composite formula), `New-Chat-Starter-Prompt.md` ("all fixed"→point at review), `README.md` ("two reviews"→three), `Metrics-Definition.md` §4 ("11"→12). *Benefit:* docs stop contradicting the code before the professor sees them.

**R5 — Single source of truth for `SENSITIVE_TOKENS` (+ matching).** *(DEFER until after captures, or do with R2 tests)*
- *Scope:* new `constants.py` (later `matching.py`), imported by both scripts. *Plan:* move the token list out of both files; have docs reference it. *Benefit:* kills the drift risk. *Risk:* edits both instrument files — gate behind R2's tests.

**R6 — Instrument hardening + idiom pass.** *(DEFER until after captures)*
- *Scope:* `capture_addon.py`. *Plan:* length-from-`safe_body` (`:386/:414`); state into `ExposureTracker`; init behind `load()`/raise-not-exit; narrow excepts; optional `logging`. *Benefit:* testability + closes the residual `.content` crash. *Risk:* behavior-adjacent on the measurement instrument — not before data collection.

**R7 — Light tooling for a public/portfolio repo.** *(apply now, safe)*
- *Scope:* `pyproject.toml` (black/ruff config), a minimal `.github/workflows/ci.yml` running lint + `pytest`. *Benefit:* portfolio signal + automated regression guard.

---

## 5. Target architecture sketch (only if this becomes a portfolio showpiece)

The current flat `scripts/` layout is fine for the study. *If* you later want it to read as a polished software portfolio piece, the minimal restructure is a small package that removes the duplication (R5/R6) without adding abstraction:

```
privacy_analysis/
  __init__.py
  constants.py        # SENSITIVE_TOKENS, IGNORE_SUFFIXES, default WINDOW_SIZE
  matching.py         # build_search_corpus / find_covered_positions / find_tokens
  capture/addon.py    # ExposureTracker (state in instance; imports matching+constants)
  analysis/analyze.py # imports matching+constants
tests/                # pytest
requirements.txt
pyproject.toml
```

**Explicit warning (you asked for this):** for ~1,200 LOC this is borderline over-engineering. Do it only if the repo's *purpose* shifts to "portfolio showpiece." For the research goal, R1 + R2 (deps + tests) deliver almost all the value with none of the restructuring risk. **Do not** add factories, strategies, plugin registries, or a config framework here — there's nothing to vary, and premature abstraction would reduce clarity.

---

## Apply-now vs defer (my scope recommendation)

| Now (additive / safe, zero instrument-logic risk) | Defer until after captures (touches the instrument) |
|---|---|
| R1 deps pinning · R2 tests · R3 analyze cleanups · R4 doc reconciliation · R7 tooling | R5 token/matching de-dup · R6 hardening + idioms · sentence-parser change (also a methodology call) · responses-as-exposure (Blocker B) |

This keeps the measurement code byte-for-byte stable through the validation gate and the 18 runs, while still improving reproducibility, test coverage, docs, and portfolio polish today.

*No code was changed for this review. Tell me which refactors to perform (I'd suggest R1–R4, R7 now) and I'll do them as isolated changes with short commit messages, exactly as before.*
