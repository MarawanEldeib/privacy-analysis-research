# Capture Protocol — Identical for All Runs

**Status:** Locked. Do not vary any step between runs — variance contaminates the reproducibility metric.
**Last updated:** 2026-05-23

This document defines exactly what happens during a single capture run.
The protocol must be identical across all 15 main runs (3 tools × 5 runs) and all baseline runs.

---

## Threat model recap

A user receives a confidential document and is told not to share it with AI tools.
They have a writing-assistant browser extension (Grammarly / ProWritingAid / Wordtune)
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

The page lives at `input-data/test-page.html` and is opened via `file://` URL.

---

## Required tools on Kali

```bash
sudo apt install -y xclip xdotool
```

- `xclip` — load the test document into the X clipboard.
- `xdotool` — simulate the Ctrl+V keystroke to paste into the focused window.

---

## Step-by-step protocol (one run)

This is identical for every tool, every run, every baseline.

1. **Open Firefox** with the tool's clean profile (e.g., `grammarly-test`),
   proxy already configured to 127.0.0.1:8080, mitmproxy CA already trusted.
   For baseline runs, use the `baseline-test` profile with NO extensions installed.
   ```bash
   firefox -P grammarly-test --no-remote &
   ```

2. **Wait 10 seconds** for Firefox to settle (startup pings, addon load).

3. **Open the test page** in Firefox:
   ```
   file:///path/to/Research%20Project%20-%20Privacy%20analysis/input-data/test-page.html
   ```

4. **Click into the textarea** so it has keyboard focus.
   Verify the textarea has the cursor blinking inside it before continuing.

5. **Start mitmproxy capture** in a separate terminal:
   ```bash
   ./scripts/capture/run_capture.sh grammarly 1
   ```

6. **Load the test document into the clipboard:**
   ```bash
   xclip -selection clipboard < input-data/test-document.txt
   ```

7. **Trigger the paste** into Firefox:
   ```bash
   xdotool key --window "$(xdotool search --name 'Mozilla Firefox' | head -1)" ctrl+v
   ```

   The document should now be visible in the textarea.

8. **Wait 60 seconds** without touching anything. This gives the extension time
   to process the pasted text and send any analysis requests.

9. **Stop mitmproxy** by pressing `q` in its terminal.
   The capture script saves the JSON file and the raw `.flow` archive.

10. **Reset for next run:** clear Firefox's tab history (Ctrl+Shift+Del → last hour)
    or restart Firefox cleanly so the next run starts identical.

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
- The wait times (10s startup, 60s after paste).
- The paste method (xdotool ctrl+v on a focused textarea).
- The Firefox version and the extension version (record these in the run metadata).
- Network conditions (run on the same internet connection, ideally wired).

## What CAN vary between runs

- Time of day (but record it — large patterns may indicate server-side variation).
- Which run is run 1, 2, 3, 4, 5 (but always do them in numerical order).

---

## Future stretch conditions (only if time permits in September)

These are not part of the main 15 runs. Add only as supplementary 1-2 run conditions.

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
