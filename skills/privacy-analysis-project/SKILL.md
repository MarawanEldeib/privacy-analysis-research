---
name: privacy-analysis-project
description: Marawan's privacy research project measuring data exposure in Grammarly, ProWritingAid, and Wordtune via mitmproxy on Kali. Use when the user mentions this project, the workspace folder "Research Project - Privacy analysis", any of the three tools by name, mitmproxy capture, the canary token, or the analyzer scripts.
---

# Privacy Analysis Project — Working Context

This skill loads when Marawan is working on his university research project measuring how much of a confidential document gets silently transmitted when LLM-integrated browser extensions are running during normal use.

## Project at a glance

**Workspace folder:** `F:\Research Project - Privacy analysis\`
**Final deadline:** 2026-10-10
**Status:** Third-review bugs FIXED + committed 2026-05-28 (see status section below). Instrument idioms deliberately deferred until after captures. Reviews: `docs/Independent-Critical-Review-2026-05-28.md` and `docs/Engineering-Architecture-Review-2026-05-28.md`.

**Threat model:** A user receives a confidential document, is told not to share it with AI tools, but has a writing-assistant browser extension running by default in the background. They paste content into a normal text field (email, doc, comment box). The extension silently transmits that content. We measure how much.

**Tools tested:** Grammarly, ProWritingAid, Wordtune (all Firefox extensions). GitHub Copilot was dropped — VS Code doesn't use the Firefox proxy reliably.

## Companion files in this skill (read as needed)

- `methodology.md` — locked decisions and their rationale. **NOT FINAL** — some have been challenged by the third review; cross-check before defending any locked decision.
- `protocol.md` — per-run capture protocol as a checklist.
- `gotchas.md` — known failure modes.
- `interpretation.md` — how to read the analyzer's output.
- `future-skills.md` — skills to create when later phases begin (LaTeX template, etc.).

## REQUIRED reading outside the skill before suggesting anything

- `docs/Independent-Critical-Review-2026-05-28.md` — third independent review. Identifies real bugs (the analyzer drops transcript coverage so chunked sends report 0%; JSON-unescape is dead code; `decompress()` runs on already-decompressed bytes; WS scheme check probably wrong; Makefile mkdir ordering bug). Read this BEFORE treating anything in `methodology.md` as still locked.

## Third-review findings — current status

**Fixed + committed 2026-05-28 (do NOT re-flag these as bugs):**
1. `analyze.py::union_exposure_from_run` now folds in the addon's per-host transcript coverage (post-baseline) — chunked WebSocket sends no longer read as ~0%.
2. `build_search_corpus()` now parses JSON + unescapes `\n`/`\uXXXX` in place; the dead `json.loads(f'"..."')` whole-body path is gone.
3. `safe_body()` wraps `.content` (falls back to `raw_content`, records `read_failures`) — no more silent event drops on bad encoding.
4. `websocket_message` uses `scheme in ("https", "wss")` — `https_event_pct` no longer tanks for WS-heavy tools.
5. Makefile creates `data/raw/<tool>/` BEFORE mitmdump writes the log/flow — no silent first-run failure.
6. `data/raw/*/run_*.flow` is gitignored — decrypted auth tokens are not committed (verified: none ever were).
7. `analyze.py` cleanups: dead TLS-bytes fallback removed; `total_request_bytes` computed from events (was always 0); unused `ci_mean_raw` dropped.

**Still open — deliberately deferred (instrument frozen until after captures):**
- `SENSITIVE_TOKENS` + window/token matching duplicated across both scripts (DRY); implicit JSON-schema coupling.
- Residual `.content` reads on length fields (`capture_addon.py:386/:414`); module-level side effects + `sys.exit` on import; module globals vs instance state; broad `except: pass`; `print` vs `logging`; provenance env vars unset.
- Sentence parser counts label lines; responses counted in the exposure union (Blocker B).
- Doc reconciliation: Professor-Update-Email (typing/bytes), QA Q3 + Timeline Phase 3 (rejected composite formula), starter prompt, README, Metrics-Definition "11"→12.

## What's confirmed VALID strengths

- Saving raw `.flow` files per run (lets us re-analyze after fixing bugs without re-capturing).
- The two-number TLS visibility framing (rejecting the multiplicative composite).
- The UUID canary + `.invalid` email design.
- The publication gate (3 conditions: professor approval, vendor disclosure, results stable).
- `gotchas.md` as operational documentation.

## Engineering & change-safety rules (apply to ALL work on this repo)

Distilled from the 2026-05-28 reviews — these override generic "refactor everything" instincts.

1. **Freeze the instrument during data collection.** Don't change the *logic* of `capture_addon.py` / `analyze.py` between the first and last capture run — it breaks reproducibility. Structural refactors wait until captures are done.
2. **Tests before refactors.** `pytest` must pass before and after any change to the two scripts; add a test that locks a bug before fixing related code.
3. **Small, isolated, behavior-preserving.** One logical change per commit, short imperative messages. Don't change observable behavior without saying why. Marawan commits on Windows — never run git from Kali.
4. **No premature abstraction.** ~1,200 lines of research code: don't add design patterns, layers, packages, or dependencies unless they clearly earn their keep. If a change feels "enterprise," it's probably overkill — say so and skip it.
5. **Reproducibility first.** Pin deps (`pip freeze > requirements.txt` after install). Never edit `test-document.txt` / `test-page.html` once captures start.
6. **Lead with the canary.** The headline result is the unique UUID reaching a vendor server, not the exposure %.
7. **When uncertain, ask — don't guess.** Especially for anything touching the instrument or a "locked" methodology decision.
8. **Keep `docs/New-Chat-Starter-Prompt.md` current.** Whenever decisions, status, or the project vision change, update the starter prompt so a fresh session is bootstrapped with the latest picture.

**Overkill for this project (skip unless it becomes a product):** CI/CD pipelines, layered architecture, package restructure, scalability work, and running separate architect/hygiene/language review passes — one consolidated review is enough.

## Working style notes for me

- Marawan asks "why" — explain reasoning, not just instructions. He pushes back; listen and re-think.
- Undergraduate, not a security researcher. Plain words first, technical terms second. Define acronyms inline.
- Prefers decisions step by step. Use AskUserQuestion for methodology choices, one at a time, with concrete examples.
- Comfortable saying "I'm lost" — reset and re-explain rather than continuing past confusion.

## Repository layout

```
Research Project - Privacy analysis/
├── Makefile                              one-line commands for the capture cycle (has mkdir ordering bug)
├── docs/
│   ├── Project-Overview.md
│   ├── Capture-Protocol.md
│   ├── Setup-Guide.md
│   ├── Metrics-Definition.md
│   ├── QA-Professor.md                   (has doc drift — see review §2.7)
│   ├── Timeline.md                       (has doc drift — Phase 3 still mentions rejected composite formula)
│   ├── Professor-Update-Email.md         (not sent yet)
│   ├── New-Chat-Starter-Prompt.md
│   └── Independent-Critical-Review-2026-05-28.md   ← READ THIS FIRST
├── input-data/
│   ├── test-document.txt
│   ├── test-page.html
│   └── README.md
├── scripts/
│   ├── capture/capture_addon.py          (v3.1 + 2026-05-28 fixes; idioms deferred)
│   ├── capture/run_capture.sh
│   └── analysis/analyze.py               (v3.1 — has known bugs above)
└── skills/privacy-analysis-project/      this skill
```

## What Marawan needs from me, in priority order

1. **Fix the bugs from the third review before any data collection.** Don't treat "locked methodology" as binding when the review demonstrates the lock was wrong.
2. **If a methodology change is tempting, check `methodology.md` for the rationale first** — most things have been considered. But also check `docs/Independent-Critical-Review-2026-05-28.md` — some "locked" decisions are now known to be unsound.
3. **Be a sanity check during data collection.** If results look off, refer to `gotchas.md` AND the review's list of silent-failure modes.
4. **Lead with the canary, not the percentage.** The strongest evidence is "unique UUID arrived at vendor server seconds after paste." The percentage is supporting detail.
5. **Stay aligned with LaTeX as the final report format.** Charts produce PNG + SVG.

## The 4 metrics — current state

1. **Exposure %** — character-level via 20-char sliding window. (Transcript fold-in + JSON-escape fixes landed 2026-05-28; chunked / escaped sends are now counted.)
2. **Reproducibility** — std dev across 5 runs. n=5 on ONE document measures pipeline jitter, not tool behavior (review Blocker 3).
3. **Traffic visibility** — two numbers (HTTPS event share + TLS handshake failures). (WS scheme fix landed 2026-05-28; WebSocket events now count as HTTPS.)
4. **Sensitive token detection** — N of 12 planted tokens. **STRONGEST METRIC** — the canary is unique, network-detectable, and a binary yes/no. This should be the headline.

Plus 95% CI on the mean (questionable validity — see review Blocker 3) and sentence-level leak count (sentence parser counts label lines as sentences — review §3).

## Open questions still going to the professor

See `docs/QA-Professor.md` — but note the document drift in Q3 and the headline framing question raised by the review: scope claims to "this document" (drop CIs) OR add 3-5 documents (then CIs mean something).

## ⚠ Publication gate — do NOT skip

The repo is prepared for public release (MIT LICENSE, CITATION.cff, README disclaimer) but stays **PRIVATE** until ALL three:

1. Professor explicitly approves publication; university IP rules cleared.
2. Vendors (Grammarly, ProWritingAid, Wordtune) notified under responsible-disclosure norms, ≥90 days to respond.
3. Final results stable (no re-captures planned).

If Marawan asks about going public, **first check this gate**. Documented in `docs/Timeline.md`.
