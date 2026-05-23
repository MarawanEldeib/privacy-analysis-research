---
name: privacy-analysis-project
description: Marawan's university research project measuring data exposure in Grammarly, ProWritingAid, and Wordtune using mitmproxy on Kali Linux. Use whenever the user mentions privacy analysis, data exposure measurement, Grammarly capture, mitmproxy, ProWritingAid, Wordtune, or references the workspace folder "Research Project - Privacy analysis". Captures the locked methodology, capture protocol, known failure modes, and how to interpret the analyzer's output so you don't re-derive context from scratch.
---

# Privacy Analysis Project — Working Context

This skill loads when Marawan is working on his university research project measuring how much of a confidential document gets silently transmitted when LLM-integrated browser extensions are running during normal use.

## Project at a glance

**Workspace folder:** `F:\Research Project - Privacy analysis\`
**Final deadline:** 2026-10-10
**Status:** Methodology + scripts locked at v3.1 (after two critical reviews). Data collection has not started yet on Kali.

**Threat model:** A user receives a confidential document, is told not to share it with AI tools, but has a writing-assistant browser extension running by default in the background. They paste content into a normal text field (email, doc, comment box). The extension silently transmits that content. We measure how much.

**Tools tested:** Grammarly, ProWritingAid, Wordtune (all Firefox extensions). GitHub Copilot was dropped — VS Code doesn't use the Firefox proxy reliably.

## Companion files in this skill (read as needed)

- `methodology.md` — every locked decision with the rationale. Read this BEFORE suggesting any methodology change.
- `protocol.md` — the per-run capture protocol as a checklist.
- `gotchas.md` — known failure modes. Read this when results look off.
- `interpretation.md` — how to read the analyzer's output.
- `future-skills.md` — skills to create proactively when the project hits the next phase (e.g., LaTeX template when writing begins). Check this when Marawan moves into a new phase of work.

## Working style notes

- Marawan asks "why" — explain reasoning, not just instructions. He pushes back on mismatched ideas; listen and re-think.
- Student, not a security researcher. Plain words first, technical terms second. Define acronyms inline.
- Prefers decisions step by step. Use AskUserQuestion for methodology choices, one at a time, with concrete examples.
- Comfortable saying "I'm lost" — reset and re-explain rather than continuing past confusion.

## Repository layout

```
Research Project - Privacy analysis/
├── Makefile                              one-line commands for the 18-run cycle
├── docs/
│   ├── Project-Overview.md               high-level summary
│   ├── Capture-Protocol.md               LOCKED per-run protocol
│   ├── Setup-Guide.md                    Kali install instructions (v4)
│   ├── Metrics-Definition.md             exact formulas (v3)
│   ├── QA-Professor.md                   decisions + open questions
│   ├── Timeline.md                       milestones to Oct 10
│   ├── Professor-Update-Email.md         draft email (not sent yet)
│   └── New-Chat-Starter-Prompt.md        starter prompt for new sessions
├── input-data/
│   ├── test-document.txt                 synthetic memo with 12 planted tokens
│   ├── test-page.html                    local page with one textarea
│   └── README.md                         canonical 12-token list
├── scripts/
│   ├── capture/
│   │   ├── capture_addon.py              mitmproxy addon (v3.1)
│   │   └── run_capture.sh                shell wrapper
│   └── analysis/
│       └── analyze.py                    analysis script (v3.1)
├── data/raw/                             capture outputs (one folder per tool)
├── results/                              analyzer outputs
└── skills/privacy-analysis-project/      this skill
```

## What Marawan needs from me, in priority order

1. **Don't undo locked decisions silently.** Check `methodology.md` first; most things have been debated already.
2. **Be a sanity check during data collection.** If results look off, refer to `gotchas.md` before guessing.
3. **Explain results in plain terms.** Refer to `interpretation.md` for the agreed framing of reproducibility, CI, sentence leaks.
4. **Stay aligned with LaTeX as the final report format.** Charts produce PNG + SVG.

## Quick recall: the 4 primary metrics

1. **Exposure %** — fraction of test-document characters whose 20-char window appears in captured traffic. Baseline-subtracted.
2. **Reproducibility** — std dev of exposure % across 5 runs. High (<3pp) / Medium (3-10pp) / Low (>10pp).
3. **Traffic visibility** — two numbers (HTTPS-event share + TLS-handshake-failure count). Never multiplied into one composite.
4. **Sensitive token detection** — N of 12 planted tokens found.

Plus 95% CI on the mean for each tool, and sentences-leaked-per-run as a secondary, more interpretable metric.


## Open questions still going to the professor

See `docs/QA-Professor.md`. Three are open: TLS framing acceptable? 20-char + sentence granularity sufficient? CI alone or formal pairwise t-tests required?

## ⚠ Publication gate — do NOT skip

The repo is fully **prepared** for public release (MIT LICENSE, CITATION.cff, README disclaimer block, methodology framed neutrally). But it must stay **PRIVATE** until ALL three:

1. Professor has explicitly approved publication (and any university IP rules are cleared).
2. Vendors (Grammarly, ProWritingAid, Wordtune) have been notified under responsible-disclosure norms and given at least 90 days to respond.
3. Final results are stable (no re-captures planned).

If Marawan asks about going public, **first check this gate**. Don't encourage opening the repo until all three hold. The gate is documented in `docs/Timeline.md` under "Post-submission: open-source publication gate".
