# Capture Protocol — Per-Run Checklist

The full spec lives in `docs/Capture-Protocol.md`. This is a condensed checklist for use during data collection.

## Before you start ANY capture session

- [ ] Kali Linux is the active machine (not host OS).
- [ ] You're in the project root: `cd /path/to/Research\ Project\ -\ Privacy\ analysis`.
- [ ] `make check` returns OK for every dependency (no MISSING lines).
- [ ] The mitmproxy CA certificate is installed and trusted in the right Firefox profile.
- [ ] You've verified interception by visiting `https://api.grammarly.com` once and seeing the request in mitmproxy.

## For each run (Makefile version — preferred)

You'll need two terminals.

**Terminal 1 — Firefox setup:**
```bash
# Replace "grammarly" with languagetool or baseline as appropriate
make page-grammarly
```
Wait ~5 seconds for Firefox to settle, then **click into the textarea** to focus it. The cursor should be visibly blinking inside the textarea.

**Terminal 2 — Capture:**
```bash
make grammarly-1   # or grammarly-2 ... 5, or languagetool-N, or baseline-N
```

The Makefile target:
1. Loads `test-document.txt` into the clipboard via xclip.
2. Starts mitmproxy in the background with the addon attached.
3. Pauses and prints `>>> PASTE NOW`.
4. **You paste manually:** switch to Firefox, empty the box (Ctrl+A, Backspace),
   press a real **Ctrl+V**, then return and press Enter. (A scripted xdotool paste
   doesn't fire the DOM input event, so the tool wouldn't ingest the text → false 0%.)
5. Records ~60 seconds for the extension to process and send.
6. Stops mitmproxy (saves the session) and prints the output paths.

**Between runs of the same tool:**
- Empty the textarea (Ctrl+A, Backspace) before the next paste.
- Either way, the next paste should land in an empty textarea.

## Baseline runs

Same protocol, but:
- Use `make page-baseline` (opens the baseline-test profile with NO extensions).
- Run `make baseline-1`, `make baseline-2`, `make baseline-3` (only 3 baseline runs needed).
- These give us the set of background domains to subtract from tool runs.

## After each run, sanity-check

- [ ] `data/raw/<tool>/run_<n>.json` exists.
- [ ] `data/raw/<tool>/run_<n>.flow` exists (the safety net).
- [ ] `data/raw/<tool>/run_<n>.log` exists. Open it and look for `[! EXPOSURE]` lines.
- [ ] `[TLS-FAIL]` lines: if present, note them — those are connections we couldn't decrypt. Should be near-zero for browser extensions. If many, suspect the cert install.

## After all 5 runs of a tool

```bash
make analyze     # default strict view
```
Then look at the per-tool table. Sanity checks:
- All 5 exposure %s should be in the same ballpark (small std dev). If not, see `gotchas.md`.
- HTTPS event share should be near 100%. If much lower, suspect cert issues.
- TLS handshake failures should be 0 or very low.

## After both tools + baseline are done

```bash
make analyze     # final strict analysis with baseline subtraction
make chart       # produces results/comparison_chart.{png,svg}
```

This is the dataset for the report.

## Sensitivity / lenient view

Run this on the first capture set to check if strictness settings are missing real leaks:
```bash
make analyze-lenient
```
If lenient catches a lot more than strict, that's a signal to re-examine the strict settings before committing to them for all runs.

## What you CAN'T change without invalidating prior runs

- The test document file (don't edit after first run).
- The test HTML page (don't edit after first run).
- The 60-second wait.
- The paste method (manual Ctrl+V).

If any of these change, runs before and after the change are not comparable.
