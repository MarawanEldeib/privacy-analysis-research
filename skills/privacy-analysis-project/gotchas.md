# Known Gotchas — Read Before "Fixing" Anything

These are real failure modes that have caused (or could cause) silently wrong results. If you see symptoms below, the cause is probably one of these.

## 1. Silent zero exposure due to bad cert install

**Symptom:** Capture runs cleanly, no errors, but `exposure_pct = 0` and `tokens_found = []` across all events. HTTPS event share also low (or 0).

**Likely cause:** The mitmproxy CA certificate is NOT properly installed in the Firefox profile being used. Firefox is silently using direct HTTPS (bypassing mitmproxy) or refusing to trust the proxy.

**Diagnosis:**
1. With mitmproxy running, open Firefox with that profile and visit `https://example.com`.
2. If you see a certificate warning page → CA is not trusted.
3. If the page loads but no traffic appears in mitmproxy → proxy not set in this profile's network settings.

**Fix:** Re-do Steps 2c-2d of `docs/Setup-Guide.md` (import the `mitmproxy-ca-cert.cer` file into the Authorities tab of that specific profile).

**Important:** Do NOT report "Grammarly leaked 0%" if you suspect this. It's a measurement failure, not a finding.

## 2. Cert pinning — silent missing traffic

**Symptom:** `tls_handshake_failures > 0` in the JSON summary, but exposure looks normal otherwise.

**Cause:** Some servers (rare in browser extensions, common in mobile/desktop apps) use certificate pinning — they refuse to trust ANY CA except a specific one they expect. mitmproxy's MITM cert is rejected, the connection becomes an opaque CONNECT tunnel, and the addon never sees the contents.

**What this means:** The exposure result is a *lower bound*. The tool may have sent more, but we can't see it.

**Report this honestly:** "N TLS handshakes could not be intercepted; their content is unknown." Already in the conclusion statement.

**Workaround:** For Grammarly specifically, the browser extension does not pin certs (its desktop app does). Should not be a problem here. If it appears, note the SNI hosts in the log and flag them.

## 3. Chunked WebSocket frames defeating the window matcher

**Symptom:** `per_event_covered_chars` is much smaller than `transcript_covered_chars` in the summary. (Or: exposure looks small in per-event matching but jumps when the cross-event transcript is included.)

**Cause:** The tool sent the document split across multiple WebSocket frames. Each individual frame is too short to contain a 20-char window from the doc, but joined together they do contain it.

**This is handled** by the per-host concatenated-transcript pass in capture_addon. If you see a big gap between per-event and transcript numbers, that's confirmation it's working — the cross-event pass is catching what per-event missed.

## 4. Extension not actually active

**Symptom:** Zero events from `api.grammarly.com` (or the relevant tool's domains) even though the test page was pasted.

**Likely cause:**
- Not logged into the tool's account in that profile.
- Extension is installed but disabled.
- Extension was installed in the wrong profile.

**Diagnosis:**
1. Open the test page in the relevant Firefox profile.
2. Look at the extension icon in the toolbar — is it colored/active? If grey, it's not running.
3. Type a single character in the textarea — does Grammarly show a suggestion underline? If no, the extension is not seeing the textarea.

**Fix:** Open the extension's settings, log in, enable on the test page.

## 5. The body_preview bug (already fixed in v3, don't re-introduce)

**Background:** In v2 of the scripts, `analyze.py` looked for tokens in a `body_preview` field that `capture_addon.py` never wrote. Every token detection silently returned 0/12.

**Fix in v3:** `capture_addon.py` now scans for tokens AT capture time and stores `tokens_found` per event. `analyze.py` reads this field directly.

**If you're ever editing the addon or analyzer:** keep the `tokens_found` field name consistent. Don't move token detection logic from the addon to the analyzer without checking that body content is actually available.

## 6. Encoding surprise — base64 or custom encoding

**Symptom:** Exposure % much lower than expected; you can see in `body_preview` that some payload contains long base64-looking strings, but no tokens are detected.

**Cause:** The tool encoded the text before sending. The current addon checks raw, URL-decoded, and JSON-unescaped variants. If the tool uses base64 or something custom, those variants miss it.

**Fix path:** Don't re-capture. Open the `.flow` file in mitmweb to inspect the bytes. If you find an encoding pattern (base64 in a specific JSON field, etc.), add a decoder to `build_search_corpus()` in capture_addon.py, then re-run the addon offline against the `.flow` file:
```bash
WINDOW_SIZE=20 TOOL_NAME=grammarly RUN_ID=1 \
    mitmdump -nr data/raw/grammarly/run_1.flow -s scripts/capture/capture_addon.py
```
This is exactly why we save the `.flow` files.

## 7. Background browser noise overwhelming the signal

**Symptom:** Many unrelated hosts in the JSON (Mozilla telemetry, Google safe-browsing, etc.), exposure % artificially inflated.

**Cause:** The `IGNORE_SUFFIXES` list in `capture_addon.py` filters known noise, but not perfectly.

**Fix:** Run baseline. Baseline subtraction in `analyze.py` removes domains seen in the baseline. If unwanted domains still appear, add them to `IGNORE_SUFFIXES` (and re-run analysis on the existing JSONs — no re-capture needed).

## 8. Std dev too high (Low reproducibility)

**Symptom:** `stdev_exposure_pct > 10pp` for one tool. Labeled "Low" reproducibility.

**Likely causes (in order of probability):**
1. The protocol varied between runs (different wait time, different paste timing). Re-check Capture-Protocol.md.
2. The tool itself behaves non-deterministically (e.g., randomly samples a fraction of input to send). This is a real finding.
3. Network conditions varied (cellular vs wired, different times of day).
4. Cert was working in some runs and not others.

**Don't average over Low reproducibility data.** Report it as a finding ("Tool X showed Low reproducibility, std dev Y pp — results are unstable") and consider doing 5 more runs to see if a pattern emerges.

## 9. Exposure > 100% (shouldn't happen, but...)

If you ever see exposure > 100%, it's a bug. The math is `len(covered_positions) / TOTAL_CHARS * 100` where TOTAL_CHARS is `len(test-document.txt)`. If TOTAL_CHARS changes between capture and analysis (because the doc was edited), the numbers don't make sense.

**Don't edit `test-document.txt` after capture starts.** If you must regenerate it, also wipe `data/raw/` and start over.

## 10. Selenium / Playwright triggering anti-bot detection

If you ever consider replacing xdotool with browser-automation libraries: Grammarly's anti-bot detection often flags those tools and disables itself. xdotool driving a real Firefox session is what works. Stay with it.

---

*If symptoms don't match anything above, fall back to first principles: look at the `.flow` file in mitmweb (`mitmweb -nr data/raw/<tool>/run_N.flow`) and see what the browser actually sent. Don't trust the JSON summary alone when something looks weird.*
