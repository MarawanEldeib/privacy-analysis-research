# Operational Prompts — Paste into Claude Code on Kali, one phase at a time

These are self-contained prompts for the data-collection phases. Each is written
for a **fresh Claude Code session on Kali** (it can't see this conversation), so
each one re-establishes context by pointing at the skill files.

**How to use:** run them in order, P5 → P9. Each prompt ends by telling Claude to
**stop and report** so you stay in the loop between phases. Don't paste the next
one until the previous phase is confirmed working.

**Ground rules baked into every prompt:**
- Project on Kali is at `/media/sf_privacy_analysis/` (VirtualBox shared folder).
- **Never run git on Kali.** You commit `.json` results + `results/` from Windows.
  `.flow` archives stay local only (now gitignored — they hold decrypted auth tokens).
- GUI steps (cert import, profile creation, extension install, logging in) are
  manual — Claude Code can't automate the Firefox UI. It guides and verifies.
- The code was fixed on 2026-05-28 (4 commits). The transcript bug, JSON-escape
  undercount, `.content` crash, WS TLS-flag, and Makefile `mkdir` are all fixed.

---

## P5 — Install dependencies + dependency sanity check

```text
You are helping with my university privacy-research project on Kali Linux. Read these
files first for full context (do not skip — they contain the locked protocol and known
failure modes), then do the task:

  /media/sf_privacy_analysis/skills/privacy-analysis-project/SKILL.md
  /media/sf_privacy_analysis/skills/privacy-analysis-project/protocol.md
  /media/sf_privacy_analysis/skills/privacy-analysis-project/gotchas.md
  /media/sf_privacy_analysis/docs/Independent-Critical-Review-2026-05-28.md

SKILL.md is the source of truth. Treat "locked"/"all fixed" wording in methodology.md
or the starter prompt as stale; the review and the recent fixes are the current state.

TASK (Phase 5 — environment setup):
1. cd /media/sf_privacy_analysis/
2. Install system packages:
     sudo apt update
     sudo apt install -y python3-pip firefox-esr xclip xdotool jq make
3. Install Python packages:
     pip3 install --break-system-packages mitmproxy brotli pyahocorasick matplotlib
4. Run `make check` and show me the full output.
5. If any line says MISSING (other than optional ones), tell me exactly which and how
   to fix it. brotli and pyahocorasick are optional but recommended; matplotlib is
   needed for the final chart.

Do NOT run git. Do NOT start any capture yet.
STOP after `make check` and report the result. Wait for me to confirm before Phase 6.
```

---

## P6 — Install + verify the mitmproxy CA certificate (mostly manual GUI)

```text
Fresh session. Read for context first:
  /media/sf_privacy_analysis/skills/privacy-analysis-project/SKILL.md
  /media/sf_privacy_analysis/skills/privacy-analysis-project/gotchas.md
  /media/sf_privacy_analysis/docs/Setup-Guide.md   (Step 2 covers this exactly)

TASK (Phase 6 — make HTTPS interception work). Most of this is Firefox GUI that I do by
hand; your job is to give precise click-by-click instructions and then verify it worked.

1. Tell me how to start mitmproxy listening on 127.0.0.1:8080.
2. Walk me through, in Firefox: set the manual proxy to 127.0.0.1:8080 (all protocols),
   open http://mitm.it, download the Firefox cert, and import it under
   Settings → Privacy & Security → Certificates → Authorities → Import, ticking
   "Trust this CA to identify websites."
3. Verify interception two ways and have me report what I see:
     - https://example.com loads with NO certificate warning, and the request shows up
       in the mitmproxy window.
     - https://api.grammarly.com is intercepted (request visible in mitmproxy).
4. CRITICAL (from gotchas.md #1): if a cert warning appears or no traffic shows in
   mitmproxy, the CA is not trusted / proxy not set. A broken MITM produces silent 0%
   exposure later — a false negative, not an error. So do not move on until BOTH checks
   above pass.

Note: the proxy + cert must be set up SEPARATELY in each Firefox profile (Phase 7).
Do NOT run git. STOP and report the two verification results. Wait before Phase 7.
```

---

## P7 — Create the four Firefox profiles + install extensions (manual GUI, then verify)

```text
Fresh session. Read for context first:
  /media/sf_privacy_analysis/skills/privacy-analysis-project/SKILL.md
  /media/sf_privacy_analysis/docs/Setup-Guide.md   (Steps 3-4)

TASK (Phase 7 — isolated profiles). I create the profiles and install extensions by hand
in the Firefox GUI; you give exact steps and then verify the setup is clean.

1. Guide me to create four profiles via `firefox -ProfileManager`:
     grammarly-test, prowritingaid-test, wordtune-test, baseline-test
2. For EACH of the four profiles: set the proxy to 127.0.0.1:8080 and confirm the
   mitmproxy CA is trusted (re-do the example.com check per profile — proxy/cert are
   per-profile in Firefox).
3. Install exactly ONE extension per tool profile (and log into a free account):
     grammarly-test → Grammarly,  prowritingaid-test → ProWritingAid,
     wordtune-test → Wordtune.   baseline-test → NOTHING (it's the control).
4. Verify per profile and have me confirm: only the intended extension is present, it's
   enabled, the icon is active/colored, and I'm logged in.

Heads-up from the review (this matters): the test field is a local file:// page. Firefox
restricts extension content scripts on file:// URLs. We confirm the extension ACTUALLY
activates on the local page in Phase 8 — if it doesn't, that's a real blocker, not a
config typo. Just be aware now.

Do NOT run git. Do NOT capture yet. STOP and report per-profile status. Wait before P8.
```

---

## P8 — PIPELINE VALIDATION GATE (one Grammarly capture). HARD precondition, not a demo.

```text
Fresh session. Read these in full first — this phase decides whether the whole pipeline
measures what we think it does:
  /media/sf_privacy_analysis/skills/privacy-analysis-project/protocol.md
  /media/sf_privacy_analysis/skills/privacy-analysis-project/gotchas.md
  /media/sf_privacy_analysis/skills/privacy-analysis-project/interpretation.md
  /media/sf_privacy_analysis/docs/Independent-Critical-Review-2026-05-28.md  (Blocker 2)

TASK (Phase 8 — ONE Grammarly capture, then verify FOUR things). This is a gate: if any
of the four fails, we STOP and debug. Do not treat a clean run as success until all four
hold.

Run the capture (two terminals, per protocol.md):
  Terminal 1:  cd /media/sf_privacy_analysis/ && make page-grammarly
               then CLICK INTO the textarea so the cursor blinks in it.
  Terminal 2:  cd /media/sf_privacy_analysis/ && make grammarly-1

Then verify ALL FOUR and report each explicitly:
  (a) EXTENSION ACTIVE ON THE file:// PAGE — was the Grammarly icon colored/active on the
      test page, and did a suggestion underline appear? If grey/inactive, the extension
      isn't running on file:// → STOP (this is the Blocker 2 risk; gotchas.md #4).
  (b) PASTE LANDED — did the full test document actually appear in the textarea after the
      scripted paste? If empty, the xdotool synthetic paste failed (gotchas: try
      `xdotool windowactivate --sync <id>` then `xdotool key ctrl+v`, and close other
      Firefox windows). A blank textarea = 0% for the wrong reason.
  (c) WE COULD SEE THE TRAFFIC — open data/raw/grammarly/run_1.json and report from the
      summary: https_event_pct (should be ~100%), tls_handshake_failures (should be ~0),
      body_read_failures (should be 0). low https% or failures → cert/profile problem
      (gotchas #1/#2). [https_event_pct now counts WebSocket events correctly after the
      2026-05-28 fix.]
  (d) THE CANARY LEFT THE MACHINE — grep the raw flow for the unique canary:
        grep -a "CANARY-BC267061-67DC-485B-8E51-6F5494765CAB" \
            data/raw/grammarly/run_1.flow
      If it appears, the confidential string provably reached Grammarly's servers — the
      strongest, cleanest finding in the project. If it does NOT appear, tell me; it may
      mean (a) didn't fire, the tool chunked/encoded it (check run_1.json
      summary.transcript_covered_by_host and union_exposure_pct), or it genuinely wasn't
      sent — we need to know which before trusting any number.

Also run, as a cross-check:
  python3 scripts/analysis/analyze.py grammarly --no-baseline
and report exposure_pct, sentences_leaked, and sensitive_tokens_found. Note whether the
transcript fold-in (cross-event coverage) contributed — i.e. union exposure is sensible,
not stuck at 0 from chunking.

Do NOT run git. Do NOT proceed to the full 18-run cycle. STOP and report all four checks
plus the analyzer output. We only move to P9 after all four pass AND I've cleared scope
with my professor.
```

---

## P9 — The 18-run cycle (ONLY after P8 passes AND professor sign-off)

```text
Fresh session. Read first:
  /media/sf_privacy_analysis/skills/privacy-analysis-project/protocol.md
  /media/sf_privacy_analysis/skills/privacy-analysis-project/gotchas.md
  /media/sf_privacy_analysis/skills/privacy-analysis-project/interpretation.md

PRECONDITIONS — confirm with me before running anything:
  1. Phase 8 passed all four checks.
  2. Scope is already decided (3 documents; 3 browser extensions — see docs/QA-Professor.md).
     No professor sign-off is required first: by my decision, the professor is consulted only
     if he asks, once there are results, or if we conclude results aren't achievable.
  NOTE: the full cycle spans 3 documents + a Gmail and a Google Docs spot check. That needs
     multi-document support added first (the addon currently loads one fixed test document);
     P8 above validates the pipeline on the existing memo (document 1).

TASK (Phase 9 — full collection): 15 tool runs + 3 baseline runs.
  For each tool (grammarly, prowritingaid, wordtune):
    make page-<tool>     # click into the textarea
    make <tool>-1        # then refresh the page (Ctrl+R) between runs
    make <tool>-2 ... make <tool>-5
  Baseline (no extension):
    make page-baseline
    make baseline-1 ; make baseline-2 ; make baseline-3

  After each TOOL's 5 runs, sanity-check (interpretation.md + gotchas.md):
    - the 5 exposure %s are in the same ballpark (low std dev). If std dev > 10pp,
      stop and diagnose (cert working in some runs but not others? paste timing?
      genuine tool non-determinism?).
    - https_event_pct ~100%, tls_handshake_failures ~0, body_read_failures 0 each run.

  After ALL tools + baseline:
    make analyze         # strict, baseline-subtracted
    make analyze-lenient # sensitivity check
    make chart           # writes results/comparison_chart.{png,svg}

Then tell me what to commit. Reminder: I commit from WINDOWS, not Kali. We commit the
.json files and results/ ; the .flow archives stay local (gitignored — auth tokens).

STOP after each tool's 5 runs and report the sanity-check before continuing. Do NOT run
git on Kali.
```

---

## After P9

When collection is done and the numbers are stable, the next phases are the report
(LaTeX) and — per the publication gate in `docs/Timeline.md` — vendor disclosure before
the repo goes public. Lead the writeup with the canary result, not the percentage.
