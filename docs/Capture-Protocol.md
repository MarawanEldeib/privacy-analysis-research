# Capture Protocol — Identical for All Runs

**Status:** Locked. Do not vary any step between runs — variance contaminates the reproducibility metric.
**Last updated:** 2026-07-10 (final tool set; manual-paste method)

This document defines exactly what happens during a single capture run.
The protocol must be identical across all main runs (Grammarly ×5, LanguageTool ×5)
and all baseline runs (×3).

---

## Threat model recap

A user receives a confidential document and is told not to share it with AI tools.
They have a writing-assistant browser extension (Grammarly / LanguageTool)
installed and running by default in the background. They go about normal activity —
pasting parts of the document into a normal text field (email, doc, comment box).
The question: does the extension silently transmit that content?

---

## What we test against

A **local HTML page with a single `<textarea>`**. No third-party JavaScript, no
analytics, no other domains involved. The extension's manifest declares it
activates on any `<textarea>` and `[contenteditable]` element, so its behavior
on this page is functionally identical to its behavior in Gmail or Google Docs,
but with zero background noise to filter out.

The page lives at `input-data/test-page.html` and is served over a local HTTP
server (`http://localhost:8000/test-page.html`, started by `make page-<tool>`).
Serving over `http://localhost` rather than a `file://` URL avoids Firefox's
restrictions on extension content scripts running on `file://` pages.

---

## Required tools on Kali

```bash
sudo apt install -y xclip
```

- `xclip` — load the test document into the X clipboard so it's ready for a manual
  paste.

> **The paste is manual, not scripted.** Earlier drafts used `xdotool` to send a
> synthetic Ctrl+V. That fills the textarea visually but does **not** fire the DOM
> `input` event the extensions listen for, so the tool never ingests the text and
> nothing is transmitted — a false 0%. The locked method is a **real Ctrl+V** typed
> by the operator.

---

## Step-by-step protocol (one run)

This is identical for every tool, every run, every baseline. The `Makefile`
wraps it; the steps below are what those targets do.

1. **Open the page in the tool's profile** (starts the local page server and opens
   Firefox with the proxy configured + mitmproxy CA trusted). For baseline runs use
   the `baseline-test` profile (NO extension).
   ```bash
   make page-grammarly        # or page-languagetool / page-baseline
   ```

2. **Click into the text box** so it has keyboard focus — cursor blinking inside it.

3. **Start the recorder** in a second terminal. It loads the document into the
   clipboard, starts mitmproxy with the capture add-on, then pauses for you to paste.
   ```bash
   make grammarly-1           # or languagetool-1 / baseline-1, bump the number per run
   ```

4. **Paste manually** when it prints `>>> PASTE NOW`: switch to Firefox, empty the
   box (**Ctrl+A**, **Backspace**), then press a **real Ctrl+V**. Watch the document
   appear. Return to the recorder terminal and press **Enter**.

5. **Wait ~60 seconds** (the recorder does this) so the extension can process the
   text and send its analysis requests. Watch for a `[! EXPOSURE]` line.

6. **The recorder stops itself**, prints a `SESSION COMPLETE` summary, and saves
   `data/raw/<tool>/run_<id>.json` plus the raw `.flow` archive and `.log`.

7. **Reset for next run:** empty the text box (Ctrl+A, Backspace) before the next
   paste so each run starts identical.

---

## Baseline protocol — same except:

- Use `baseline-test` Firefox profile (no extensions installed).
- Everything else is identical: same wait times, same page, same paste, same 60s wait.
- Run baseline **at least 3 times** (run IDs 1-3) so we have a stable picture of
  background Firefox noise to subtract from tool runs.

---

## What MUST be identical across runs

- The test document file (do not modify after first run).
- The test HTML page (do not modify after first run).
- The wait times (~60s after paste).
- The paste method (a real manual Ctrl+V into a focused, emptied box).
- The Firefox version and the extension version (record these in the run metadata).
- Network conditions (run on the same internet connection, ideally wired).

## What CAN vary between runs

- Time of day (but record it — large patterns may indicate server-side variation).
- Which run is run 1, 2, 3, 4, 5 (but always do them in numerical order).

---

## Future stretch conditions (only if time permits in September)

These are not part of the main runs. Add only as supplementary 1-2 run conditions.

- **Condition G** — same protocol but the test page is a real Gmail compose window.
- **Condition D** — same protocol but the test page is a fresh Google Doc.

These let us spot-check that behavior on a controlled local page matches real-world
sites. If results match, external validity is confirmed.

---

## Why not typing?

Typing fits the scenario of "writing a fresh document." Our scenario is "handling
a document that was sent to you" — which is paste-shaped. Typing would also
require ~2.5 minutes per run at realistic keystroke rates, and would introduce
keystroke-timing variance that contaminates the reproducibility metric.

---

*This protocol is locked. Changing it after data collection has begun invalidates
the consistency of all prior runs.*
