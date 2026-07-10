---
name: privacy-analysis-project
description: Marawan's privacy research project measuring data exposure in Grammarly and LanguageTool via mitmproxy on Kali. Use when the user mentions this project, the workspace folder "Research Project - Privacy analysis", either tool by name, mitmproxy capture, the canary token, or the analyzer scripts.
---

# Privacy Analysis Project — Working Context

This skill loads when Marawan is working on his university research project measuring how much of a confidential document gets silently transmitted when LLM-integrated browser extensions are running during normal use.

## Project at a glance

**Workspace folder:** `F:\Projects\Research Project - Privacy analysis\`
**Final deadline:** 2026-10-10
**Status (2026-07-10):** Data collection COMPLETE for the final tool set. Grammarly (99.0%, 12/12 secrets) and LanguageTool (91.9%, 12/12) are both automatic/background leakers; baseline 0%. Instrument bugs from the 2026-05-28 reviews are all fixed. Remaining: optional Gmail/Google-Docs representativeness run + the report. Entry point: `docs/WALKTHROUGH.md`.

**Threat model:** A user receives a confidential document, is told not to share it with AI tools, but has a writing-assistant browser extension running by default in the background. They paste content into a normal text field (email, doc, comment box). The extension silently transmits that content. We measure how much.

**Tools tested (final):** Grammarly + LanguageTool (both Firefox extensions, both automatic grammar checkers) vs a no-extension baseline. ProWritingAid (didn't attach to the controlled field), QuillBot (no official Firefox extension), and Wordtune (Firefox listing was a clone; genuine tool is on-demand) were evaluated and dropped — recorded as limitations. GitHub Copilot was excluded earlier (VS Code bypasses the Firefox proxy). **Key finding — two exposure classes:** automatic/background transmitters (Grammarly, LanguageTool) leak on paste; on-demand transmitters (Wordtune) don't. Always verify an extension's publisher before installing (the `/wordtune/` slug was a clone).

## Companion files in this skill (read as needed)

- `methodology.md` — decisions and their rationale (final scope: Grammarly + LanguageTool + baseline).
- `protocol.md` — per-run capture protocol as a checklist.
- `gotchas.md` — known failure modes.
- `interpretation.md` — how to read the analyzer's output.
- `future-skills.md` — skills to create when later phases begin (LaTeX template, etc.).

## Orientation reading

- `docs/WALKTHROUGH.md` — the doc map; start here. It points to the reproduction,
  narrative, and technical walkthroughs.
- `docs/Independent-Critical-Review-2026-05-28.md` — a historical review snapshot. The
  bugs it identified are all fixed; read it for context on *why* the instrument is
  built the way it is, not as an open bug list.

## Instrument status (historical reviews resolved)

The 2026-05-28 review bugs are all fixed (transcript fold-in, JSON-escape parsing,
`safe_body` on bad encoding, WS scheme flag, Makefile mkdir ordering, `.flow`
gitignored, analyzer cleanups). The doc reconciliation flagged back then is also
done (README, Timeline, QA, Metrics-Definition, Professor email, starter prompt all
brought to final scope on 2026-07-10; `Setup-Guide.md` retired in favour of
`Reproduction-Guide.md`). Do NOT re-flag these as open.

Deferred-by-design (only worth doing if the project turns into a product): DRY the
duplicated `SENSITIVE_TOKENS` list across the two scripts; `print`→`logging`;
broad `except: pass`. The instrument was frozen during collection and collection is
now done, so a careful structural pass is *permissible* but not required.

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
├── Makefile                              one-line commands for the capture cycle
├── Project-Dashboard.html                self-contained results/progress dashboard
├── docs/
│   ├── WALKTHROUGH.md                    ← doc map / entry point
│   ├── Reproduction-Guide.md             run the study from scratch (replaces Setup-Guide)
│   ├── Narrative-Walkthrough.md          the project story + dead ends
│   ├── Technical-Walkthrough.md          how the code works
│   ├── Project-Overview.md
│   ├── Capture-Protocol.md
│   ├── Metrics-Definition.md
│   ├── ENVIRONMENT.md
│   ├── QA-Professor.md
│   ├── Timeline.md
│   ├── Setup-Guide.md                    (RETIRED — redirect stub)
│   ├── Professor-Update-Email.md         (historical May-2026 draft)
│   ├── New-Chat-Starter-Prompt.md
│   └── *-Review-2026-05-28.md            historical review snapshots
├── input-data/
│   ├── test-document.txt
│   ├── test-page.html
│   └── README.md
├── scripts/
│   ├── capture/capture_addon.py          (v3.1 + 2026-05-28 fixes)
│   ├── capture/run_capture.sh
│   └── analysis/analyze.py               (v3.1; final TOOLS = grammarly, languagetool, baseline)
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
2. Tested vendors (Grammarly, LanguageTool) notified under responsible-disclosure norms, ≥90 days to respond.
3. Final results stable (no re-captures planned).

If Marawan asks about going public, **first check this gate**. Documented in `docs/Timeline.md`.
