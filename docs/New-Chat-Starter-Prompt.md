# Starter Prompt — Paste this at the beginning of every new Opus 4.7 session

---

You are helping me with my university research project. Before doing anything else,
read every file listed below in full. Then give me an honest status check and tell me
if anything is wrong, missing, or can be improved before I start collecting data.

## Project in one paragraph

I am measuring how much of a confidential document gets silently transmitted to
external servers when LLM-integrated browser extensions (Grammarly, ProWritingAid,
Wordtune) are running during normal use. I capture outbound network traffic using
mitmproxy with SSL interception on Kali Linux, compare against a no-tool baseline,
and report per tool: exposure % (what fraction of the document was found in traffic),
reproducibility (std dev across 5 runs), and traffic visibility (% of bytes
successfully decrypted). The project is for university — final deadline October 10, 2026.

## My workspace folder

F:\Research Project - Privacy analysis\

## Project-specific skill (read this FIRST)

This project has a dedicated skill at `skills/privacy-analysis-project/`.
Read these four files first — they contain locked decisions, the protocol,
known failure modes, and how to read the analyzer output. They will save
you from re-deriving context:

1. skills/privacy-analysis-project/SKILL.md           — overview + working style notes
2. skills/privacy-analysis-project/methodology.md     — every locked decision + why
3. skills/privacy-analysis-project/protocol.md        — per-run capture checklist
4. skills/privacy-analysis-project/gotchas.md         — known failure modes
5. skills/privacy-analysis-project/interpretation.md  — how to read the analyzer output

## Files to read — read ALL of these before responding

1. docs/Project-Overview.md          — high-level summary and current status
2. docs/QA-Professor.md              — all decisions made and open questions
3. docs/Metrics-Definition.md        — exact metric formulas (v2)
4. docs/Capture-Protocol.md          — per-run protocol (locked)
5. docs/Timeline.md                  — milestones and deadlines
6. docs/Setup-Guide.md               — Kali + Firefox + mitmproxy setup steps (v3)
7. input-data/test-document.txt      — the synthetic confidential document used in all experiments
8. input-data/test-page.html         — the local HTML page we paste into during capture
9. input-data/README.md              — list of planted identifiers in the test document
10. scripts/capture/capture_addon.py — mitmproxy addon (v3)
11. scripts/capture/run_capture.sh   — shell script to start a capture session
12. scripts/analysis/analyze.py      — analysis script (v3)
13. docs/Professor-Update-Email.md   — draft email to professor (not sent yet)

## What happened so far

- The project proposal was submitted. The professor approved it.
- All planning, methodology, scripts, and setup guide were written.
- Two full critical reviews caught and fixed multiple issues: truncated body
  previews invalidating exposure numbers, missing WebSocket hooks, no baseline
  subtraction, bad multiplicative "confidence" formula, broken token detection
  (analyzer read a field the capture script never wrote), misleading TLS-bytes
  visibility metric, missing cross-event chunked-send detection, and an
  unspecified input method that would have contaminated the std-dev reproducibility
  number. These are all fixed in v3 of the scripts.
- GitHub Copilot was dropped from the tool list (VS Code doesn't use Firefox proxy
  reliably) and replaced with Wordtune (browser extension, same capture method).
- The "passive exposure" framing was corrected to "default-configuration exposure
  when a user handles a confidential document they received."
- The capture protocol was locked: scripted paste via xclip + xdotool into a
  local HTML page with a single textarea, 60-second wait. See docs/Capture-Protocol.md.
- No data has been collected yet. The Kali environment has not been set up yet.
- The professor has not been updated since the project started. The email draft
  in docs/Professor-Update-Email.md will be sent after the first Grammarly POC.

## Important rules for working with me

- Never assume anything I haven't confirmed — if something is unclear, ask me.
- If you are unsure about a direction, add the question to docs/QA-Professor.md
  rather than inventing an answer.
- Always update docs/Timeline.md and the memory system when significant decisions
  are made or progress happens.
- Save all final outputs to F:\Research Project - Privacy analysis\
- Today's date is 2026-05-23. I have one week of university holiday to work intensively.

## What I want from you right now

1. Read all the files above.
2. Check everything critically — methodology, scripts, setup guide, metrics, test
   document. Tell me if anything is still wrong or can be improved before I touch
   Kali.
3. Tell me exactly what to do first today on Kali to start getting real data.
4. If everything looks good, say so clearly so I know I can start.

Do not assume the previous review caught everything. Be independently critical.
