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

- `docs/QA-Professor.md` — **confirmed decisions** (top) + open questions for the professor
- `docs/Independent-Critical-Review-2026-05-28.md` — methodology/code review (bugs now fixed; read as history)
- `docs/Engineering-Architecture-Review-2026-05-28.md` — code-quality review + refactor backlog
- `docs/Operational-Prompts.md` — P5–P9 setup/capture prompts to run on Kali
- `docs/Capture-Protocol.md`, `docs/Metrics-Definition.md`, `docs/Setup-Guide.md`, `docs/Timeline.md`
- `input-data/test-document.txt`, `input-data/test-page.html`, `input-data/README.md`
- `scripts/capture/capture_addon.py`, `scripts/analysis/analyze.py`, `tests/`

## Confirmed direction (decided 2026-05-28)

1. **3 test documents** (the memo + a long report + a code/structured snippet).
2. **Final tool set: Grammarly + LanguageTool** (two independent automatic grammar checkers) vs a no-extension baseline. ProWritingAid / QuillBot / Wordtune dropped and recorded as limitations (see status below).
3. **Factual framing** — "transmitted to the tool's servers despite a no-share instruction" — **not** "leak".
4. Main runs on the **local practice page**, **plus 1 run each in Gmail and Google Docs** to confirm representativeness.
5. **Simple 95%-CI-overlap** comparison now; a formal pairwise test only if the professor asks.
6. **Exposure counts outbound only** (client→server); server echoes are captured but reported separately.
7. **Headline = planted-secret count**; exposure % is secondary; the sentence-leak metric is dropped.

## Status / next

- **Data collection IN PROGRESS (Kali, live).** Environment set up; P8 validation gate passed. **Grammarly: 5/5 runs — 99.0% exposure, 12/12 secrets incl. canary, every run.** **Baseline (no extension): 3/3 runs — 0.0%, 0/12.** The Grammarly-vs-baseline contrast (99% vs 0%, same setup minus the extension) is locked in.
- **Key operational facts (hard-won):** tools activate on `http://localhost:8000/test-page.html`, NOT `file://`. Paste must be **manual Ctrl+V** — auto-paste (xdotool) fills the box visually but the extension registers no input event and sends `doc_len:0` (a fake-clean 0%). Each new profile needs proxy (127.0.0.1:8080) + mitmproxy cert + an interception verify (`https://example.com`) before use.
- **STATUS (2026-07-10) — rich-editor tools + KEY FINDING.** All 3 remaining profiles configured (proxy + cert; creds in `credentials.local.txt`). **ProWritingAid:** attaches to nothing on the local page (connects to `api.prowritingaid.com` but sends only heartbeats) — inconclusive locally. **Wordtune:** the `/wordtune/` AMO slug is a CLONE (fake, publisher "Akajan Burno"); the real one is `/wordtune-ai-writing-assistant/` (AI21 Labs). Real Wordtune installs and routes through the proxy decryptably, BUT its login/entitlement check loops on a `stigg.io` **403**, so we couldn't drive a rewrite.
- **KEY FINDING (bank it): two exposure classes.** *Automatic/background* transmitters (Grammarly = 99% with no user action beyond pasting) vs *on-demand* transmitters (Wordtune = nothing leaves on a background paste; only sends on Select→Rewrite). Under the study threat model (background + paste), Grammarly **leaks**, Wordtune **does not**. Grammar checkers ≈ automatic; paraphrasers ≈ on-demand. This is a core result, not a failure.
- **UPDATE (2026-07-10) — LanguageTool DONE + Wordtune removed.** LanguageTool (official, by LanguageTooler GmbH, no login needed) is an **automatic/background leaker**: 5 runs, **91.9%, 12/12 incl. canary** (POST `api.languagetool.org/v2/check`), fully interceptable, std dev 0.0. It's the **independent replication partner for Grammarly** — QuillBot had no genuine Firefox extension, so LanguageTool took that slot. **Wordtune REMOVED** from scope (the `/wordtune/` slug was a clone; the real one is on-demand + auth-walled). **Working set now = Grammarly + LanguageTool (automatic leakers) + baseline (0%); ProWritingAid + QuillBot = documented limitations.** Dashboard (`Project-Dashboard.html`) rebuilt. **Remaining:** (1) reconcile the other docs + Makefile (drop Wordtune, add `languagetool` targets), commit the safe files from Windows; (2) optional Gmail/Google-Docs representativeness run; (3) write the report. Always verify an extension's publisher before installing.
- **Code:** third-review bugs fixed; pytest suite + pinned deps added. Instrument (`capture_addon.py`, `analyze.py`) **FROZEN** during collection; structural refactors deferred until after. Uncommitted: `requirements.txt`, Makefile fix, `.gitignore`; `credentials.local.txt` is gitignored and stays local — commit the safe ones from Windows.
- **Professor (deferred by choice):** no meeting until there are results — or if I get stuck, or if he asks. Deferred items (deadlines, IP/publication, metric confirm) in `docs/QA-Professor.md`.

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
