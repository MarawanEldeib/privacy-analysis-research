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
# Replace "grammarly" with prowritingaid, wordtune, or baseline as appropriate
make page-grammarly
```
Wait ~5 seconds for Firefox to settle, then **click into the textarea** to focus it. The cursor should be visibly blinking inside the textarea.

**Terminal 2 — Capture:**
```bash
make grammarly-1   # or grammarly-2 ... 5, or prowritingaid-N, etc.
```

The Makefile target:
1. Loads `test-document.txt` into the clipboard via xclip.
2. Starts mitmproxy in the background with the addon attached.
3. Waits 3 seconds for mitmproxy to be ready.
4. Sends `Ctrl+V` to the Firefox window via xdotool.
5. Waits 60 seconds for the extension to process and send.
6. Kills mitmproxy (saves the session).
7. Prints the output paths.

**Between runs of the same tool:**
- Refresh the Firefox page (Ctrl+R or Cmd+R) to clear the textarea.
- Or close and reopen with `make page-<tool>`.
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

## After all three tools + baseline are done

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
- The xdotool paste method.

If any of these change, runs before and after the change are not comparable.
