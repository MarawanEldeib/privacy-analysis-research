# Starter Prompt — paste at the start of a new Claude session on this project

> Keep this file current with the latest project vision. Whenever decisions, status,
> or scope change, update it so a fresh session is bootstrapped correctly.

You are helping me with my university research project. Read the files listed below
(in order) before doing anything, then give me an honest status check and tell me the
single next action.

## Project in one paragraph

I measure how much of a confidential document is silently transmitted to a writing
tool's servers when an LLM-integrated **browser extension** (e.g. Grammarly, LanguageTool)
is running by default. Scenario: a user is told not to share a document with
AI tools but has the extension active in the background; they paste the document into a
normal text field; the extension transmits it. I capture outbound traffic with
**mitmproxy** (SSL interception) on **Kali**, compare against a no-extension baseline,
and report — **leading with the planted-secret count** (how many of 12 unique fictional
identifiers, including a UUID canary, reached the servers), with exposure % as a
supporting number. Final deadline: **2026-10-10**. (Use today's date from the
environment — this file is not re-dated each session.)

## Workspace

`F:\Projects\Research Project - Privacy analysis\` on Windows; mirrored to Kali at
`/media/sf_privacy_analysis/`. I commit from Windows only (never git from Kali).

## Read first — the project skill (auto-loads, but read in full)

1. `skills/privacy-analysis-project/SKILL.md` — current state, engineering rules, what's fixed vs open
2. `skills/privacy-analysis-project/methodology.md` — locked decisions + rationale (cross-check vs the review)
3. `skills/privacy-analysis-project/protocol.md` — per-run capture checklist
4. `skills/privacy-analysis-project/gotchas.md` — known failure modes
5. `skills/privacy-analysis-project/interpretation.md` — how to read the analyzer output

## Then read

- `docs/Meeting-Notes-2026-07-23.md` — **supervisor feedback + agreed next directions** (most current decisions)
- `docs/Review-Findings-2026-09-05.md` — QA audit of code/methodology and the fixes applied (H1–H6 + all M/L)
- `docs/QA-Professor.md` — confirmed decisions (top) + any remaining open questions
- `docs/Desktop-Capture-Runbook.md` — how to run the desktop / system-level pass on Linux
- `docs/Tooling-Landscape.md` — tools used vs considered · `docs/Related-Work-Research.md` — ~22 cited papers
- `docs/Independent-Critical-Review-2026-05-28.md`, `docs/Engineering-Architecture-Review-2026-05-28.md` — early reviews (history)
- `docs/Operational-Prompts.md` — P5–P9 setup/capture prompts to run on Kali
- `docs/Capture-Protocol.md`, `docs/Metrics-Definition.md`, `docs/Timeline.md`, `CHANGELOG.md`
- `input-data/test-document.txt`, `input-data/test-page.html`, `input-data/README.md`
- `scripts/capture/capture_addon.py`, `scripts/analysis/analyze.py`, `tests/`

## Confirmed direction

1. **Tool set (browser phase, done): Grammarly + LanguageTool** — two independent automatic grammar checkers — vs a no-extension baseline. ProWritingAid / QuillBot / Wordtune dropped and recorded as limitations.
2. **Factual framing** — "transmitted to the tool's servers despite a no-share instruction" — **not** "leak".
3. **Exposure counts outbound only** (client→server); server echoes are captured but reported separately.
4. **Headline = planted-secret count** (N of 12, incl. the canary); exposure % is secondary; the sentence-leak metric is **retired** (its unit over-counted header lines).
5. **Report format is free** (IEEE two-column optional — currently using it); include the declaration of originality. No page count required.
6. **Zero-variance results are reported as deterministic observations**, not statistical estimates (std dev 0.0 → the CI is a point, not a significance claim).

## Supervisor-approved directions (23 July 2026 meeting)

Methodology **approved**. Broaden the study where feasible (partial additions welcome — not all required):
- **Test on the desktop too, not Firefox-only** — desktop/system-level clients, needs a system-wide proxy and possibly Frida for pinning (see `docs/Desktop-Capture-Runbook.md`).
- **More tools** — DeepL, an LLM assistant, Avast.
- **Background/idle behaviour & device permissions**; a **USB auto-read** test; a quick **iCloud** check.
- **Read ~20 related papers** (done — ~22 cited; see `docs/Related-Work-Research.md`).
- Possible **Master's-thesis** expansion next semester; classify the **types** of information leaked (Level 1 done; Level 2 = Presidio, planned).

## Status / next

- **Browser phase COMPLETE.** Grammarly **99.0%**, LanguageTool **91.9%**, baseline **0.0%**; **12/12 secrets incl. canary** for both tools; 100% HTTPS; 0 TLS failures; std dev 0.0. Results in `results/`, visualised in `Project-Dashboard.html`.
- **Report** drafted in LaTeX, **IEEE two-column** (`report/main.pdf`), related work grounded in ~22 cited papers.
- **QA audit done (2026-09-05):** all findings fixed (H1–H6 + all Medium/Low) — WebSocket-fragmentation reassembly, all-position coverage, zstd/base64/UTF-16/HTML decode, safe baseline subtraction, no-overwrite re-window, direction-guarded timeline, single-source token list. Tests 10/10 pass. See `docs/Review-Findings-2026-09-05.md`.
- **Analyses added:** information-type breakdown (Level 1) + traffic-over-time figure (`report/figures/`).
- **NEXT (all at the Kali VM):** desktop / system-level pass on Linux — native **LanguageTool desktop**, the **Avast Linux daemon** background/telemetry, **USB auto-read** and **idle/permissions** tests (runbook ready). Then **Level 2 Presidio** PII discovery over decrypted traffic. Capture **Wireshark / Burp / mitmweb / SSLKEYLOGFILE / tcpdump** evidence during the runs. Windows-only apps (Grammarly desktop, DeepL app, iCloud) deferred to a later **Windows-VM phase** (future work).
- **Key operational facts (still true):** tools activate on `http://localhost:8000/test-page.html`, NOT `file://`; paste must be **manual Ctrl+V** (auto-paste registers no input event → fake-clean 0%); each new profile/VM needs proxy + mitmproxy cert + an interception verify before use; verify an extension's publisher before installing (the `/wordtune/` AMO slug was a clone).
- **Instrument:** `capture_addon.py` / `analyze.py` were frozen during collection; the 2026-09-05 hardening is committed and test-guarded. Git from Windows only; `.flow`/`.har`/`Worklog.xlsx`/`credentials.local.txt` stay gitignored.

## How to work with me

- I'm an undergraduate, not a security expert — plain words first, define terms inline.
- Explain reasoning, not just instructions; I push back — listen and re-think rather than defend.
- Decide step by step: one short multiple-choice question at a time, with a concrete example and your recommendation + why.
- Hand me diffs with short commit messages; I run git on Windows.
- Don't refactor the frozen instrument without a test to guard it.

## What I want right now

1. Read the files above.
2. Give an honest status check; flag anything wrong or risky before I collect data.
3. Tell me the single next action to take.
