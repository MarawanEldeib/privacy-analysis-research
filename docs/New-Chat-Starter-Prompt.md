# Starter Prompt — paste at the start of a new Claude session on this project

> Keep this file current with the latest project vision. Whenever decisions, status,
> or scope change, update it so a fresh session is bootstrapped correctly.

You are helping me with my university research project. Read the files listed below
(in order) before doing anything, then give me an honest status check and tell me the
single next action.

## Project in one paragraph

I measure how much of a confidential document is silently transmitted to a writing
tool's servers when an LLM-integrated **browser extension** (Grammarly, ProWritingAid,
Wordtune) is running by default. Scenario: a user is told not to share a document with
AI tools but has the extension active in the background; they paste the document into a
normal text field; the extension transmits it. I capture outbound traffic with
**mitmproxy** (SSL interception) on **Kali**, compare against a no-extension baseline,
and report — **leading with the planted-secret count** (how many of 12 unique fictional
identifiers, including a UUID canary, reached the servers), with exposure % as a
supporting number. Final deadline: **2026-10-10**. (Use today's date from the
environment — this file is not re-dated each session.)

## Workspace

`F:\Research Project - Privacy analysis\` on Windows; mirrored to Kali at
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
2. **3 browser extensions** only (Grammarly, ProWritingAid, Wordtune); a non-browser tool only if the professor later asks.
3. **Factual framing** — "transmitted to the tool's servers despite a no-share instruction" — **not** "leak".
4. Main runs on the **local practice page**, **plus 1 run each in Gmail and Google Docs** to confirm representativeness.
5. **Simple 95%-CI-overlap** comparison now; a formal pairwise test only if the professor asks.
6. **Exposure counts outbound only** (client→server); server echoes are captured but reported separately.
7. **Headline = planted-secret count**; exposure % is secondary; the sentence-leak metric is dropped.

## Status / next

- **Code:** third-review bugs fixed; pytest suite + pinned deps added; safe refactors done. The instrument (`capture_addon.py`, `analyze.py`) is **FROZEN** until after captures. A few structural refactors (logging, state-into-instance, token de-dup) are pending a `pytest` + smoke-capture checkpoint.
- **Not started:** Kali dependency setup, the **P8 pipeline-validation gate** (one Grammarly capture proving the extension fires on the page, the paste lands, traffic decrypts, and the canary appears in the `.flow`), then the capture cycle.
- **Pending the professor:** interim deadlines, publication + university IP rules, and a quick confirm of the metric set (see `docs/QA-Professor.md`).

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
