# Independent Critical Review — Privacy Analysis Project

> **STATUS — updated 2026-05-28:** The hard blockers and code concerns below have since been **fixed and tested**, and the methodology/scoping points were **resolved** (decisions logged in `docs/QA-Professor.md`; per-bug fix status in `skills/privacy-analysis-project/SKILL.md`). Kept as the record of what was found and why — read it as history, not a live bug list.

**Reviewer brief:** third independent review, before any data is collected.
**Date:** 2026-05-28. **Reviewed at:** methodology v3.1, scripts v3.1.
**Mandate:** find what the first two reviews missed. Do not defer to locked decisions.

A note on tone: you asked for honesty over validation, so this is blunt. It is blunt because the project is good enough to be worth pushing hard on, not because it's weak. The "what looks genuinely good" section at the end is real, not a courtesy.

The single most important sentence in this review: **right now, your analysis script can report 0% exposure on a capture that actually leaked 100% of the document. I reproduced this.** Details in Blocker 1.

---

## 1. Hard blockers — fix or decide before collection starts

### Blocker 1 — The analyzer throws away the cross-event ("transcript") coverage, so chunked sends silently read as near-zero

This is a real bug, not a theoretical one. I ran it.

Your design has two matchers. The addon (`capture_addon.py`) computes per-event coverage **and** a per-host "transcript" pass that joins bodies and re-scans, specifically to catch a tool that splits the document across many small frames. `gotchas.md` §3 and `methodology.md` both promise this is handled.

But `analyze.py` — the script that actually produces your report numbers — does **not** use the transcript pass. `union_exposure_from_run()` only unions each event's `covered_positions`:

```python
for ev in all_events:
    union.update(ev.get("covered_positions", []))
```

The addon's `transcript_covered`, `union_covered_chars`, and `union_exposure_pct` are never read by the analyzer. So the cross-event coverage is computed, saved to JSON, and then ignored when you run `make analyze`.

Demonstration on your real document (12-char frames, each shorter than the 20-char window):

```
per-event union coverage :   0.0%   <- what analyze.py reports
transcript coverage      : 100.0%   <- what the addon computed and the analyzer dropped
```

Why this matters specifically for you: **Grammarly is WebSocket-based.** WebSocket tools are exactly the ones that fragment text across frames. So the tool most central to your study is the one most likely to trigger this bug. You could capture a run where Grammarly transmitted the entire memo, and `make analyze` would tell you ~0%. You would then either (a) believe Grammarly is safe, or (b) think your capture is broken — and you have no way to tell which.

It gets worse: your per-run `.log` file shows the addon's (transcript-aware) numbers, while `make analyze` shows the analyzer's (per-event-only) numbers. During collection you'll be eyeballing both and they will silently disagree. You'll lose hours to this.

Strictly, the `.flow` files mean you *can* re-analyze later, so this isn't unrecoverable. But your in-flight sanity checks ("are the 5 runs in the same ballpark?", "did this tool leak?") all run through the buggy path. Fix it before you collect, or you'll be making collection decisions on wrong numbers.

**Fix:** compute coverage once, over the full per-host concatenated decoded stream, and use that single number everywhere. Don't maintain two matchers that can disagree. See "What I'd do differently."

### Blocker 2 — The pipeline has never produced a single capture, and two assumptions inside it could make every number invalid

You're about to collect 18 runs on a pipeline that has never once been shown to work end-to-end. Two specific assumptions worry me more than ordinary setup risk:

**(a) Will the extensions even run on a `file://` page?** Your test field is a local HTML file opened via `file://`. Firefox extensions do not automatically get to run content scripts on `file://` URLs — that access is restricted and often off by default. If Grammarly/ProWritingAid/Wordtune don't activate on the local page, you measure 0%, and `gotchas.md` §4 will tell you to check whether you're logged in — sending you down the wrong path, because the real cause is the page origin, not the login. The whole "clean local textarea" design rests on extensions behaving on `file://` exactly as they do on a real site, and that is not safe to assume.

**(b) Does a passive paste actually trigger transmission?** Your threat model is "the extension *silently* transmits in the background." But many of these tools only send text when the user engages the widget — focuses it, edits, clicks the floating button. A paste followed by 60s of no interaction may trigger nothing in some tools. If so, the honest finding isn't "Tool X is safe"; it's "Tool X didn't transmit under a passive paste" — which is a *different and weaker* claim than your thesis, and you need to be ready to report it rather than treat it as a failed run.

**Fix:** before locking anything, run one full Grammarly capture and confirm, by eye, all of: the extension icon activates on the local page; text actually appears in the textarea after the scripted paste; mitmproxy decrypts the traffic (HTTPS event share ~100%, near-zero TLS failures); and the canary string is visible in the `.flow`. Only then is the pipeline trustworthy. Treat this as a gate, not a "proof of concept."

### Blocker 3 — One document means you cannot answer the research question as written; your CIs measure the wrong thing

Your research question is "how much data exposure differ**s** across tools." That's a claim about tool behavior in general. But your entire dataset is **one 2 KB synthetic memo**. Five runs of the same paste of the same document does not sample "documents" — it samples *your measurement pipeline's jitter* (network timing, frame ordering). 

So your 95% confidence interval answers "how reproducibly can I measure this one document?" — not "how much does this tool leak?" Reporting `mean 30.5% [29.5%, 31.9%]` invites every reader (and you) to read it as the second when it's only the first.

This also breaks your tool comparison. Because repeated identical pastes are near-deterministic, within-tool std dev will be tiny, CIs will be razor-thin, and your pairwise check will almost always print "DISJOINT (clear difference)" — even when the real gap is 0.4 percentage points and entirely an artifact of this one document. A Welch's t-test (your Q12) would *not* save you here; it has the same flaw, just with a p-value attached. The problem isn't the test, it's that *n=1 document*.

**Decision you must make before collecting (this is the one to take to your professor):** either
- **(A)** scope every claim explicitly to "for this specific document" — and then drop the inferential CI/t-test machinery, because there's nothing to infer to; or
- **(B)** make *document* the unit of analysis: 3–5 documents of varying length and content type, and report variation across documents. Then "Grammarly exposes more than Wordtune" actually means something.

I'd push for a lighter version of (B). More in Section 4.

---

## 2. Significant concerns — discuss before locking

### 2.1 Encoding/escaping silently undercounts the headline metric, and the code meant to prevent it is dead

Real APIs send text as JSON string values, which escapes newlines (`\n`) and often non-ASCII (`—` for your em-dashes). Your document has ~34 newlines and 7 non-ASCII characters (6 em-dashes + 1 `§`). A 20-char window that spans a newline won't match a body where that newline is `\n`.

Measured on your real document:

```
plaintext UTF-8 in JSON (newlines escaped) : 94.6%
fully \u-escaped JSON (newlines + unicode) : 92.5%
```

So a tool that transmits your document faithfully could score 92–95% instead of ~100%, purely from escaping. That 5–8pp is invisible — it looks like the tool held something back.

You *have* a defense for this — `build_search_corpus()` is supposed to add a JSON-unescaped variant — but it doesn't work. It does `json.loads(f'"{raw_text}"')` on the **entire body**. A real body contains its own quotes and newlines, so wrapping it in one pair of quotes and parsing throws `JSONDecodeError`, the variant is skipped, and you silently fall back to raw matching. I confirmed only 2 variants (raw + URL-decoded) are ever produced for a realistic JSON body.

**Fix:** unescape JSON *string values*, not the whole body — walk the parsed JSON and search each string field, or at minimum `json.loads` the body and recurse. Also normalize Unicode (NFC) on both sides so an em-dash matches regardless of how it's encoded.

### 2.2 The 4 KB `body_preview` cap is load-bearing, but the docs treat it as cosmetic

`methodology.md` says the 4 KB preview is "for human inspection" and the `.flow` file is the safety net. In reality the addon's transcript pass is built from `body_preview` (capped at 4096 bytes), and `analyze.py --window` re-derives coverage from `body_preview`. So your cross-event defense and your sensitivity analysis both silently operate on the first 4 KB of each event only. For Grammarly's large bodies that's a small fraction. (Combined with Blocker 1, the transcript pass is doubly defeated: capped *and* ignored.)

**Fix:** run matching against full decoded bodies inside the addon (you have them at capture time; you only need to store positions, not the bytes). Keep the 4 KB preview purely for eyeballing.

### 2.3 Binary/undecodable frames are silently treated as "searched, found nothing"

`bytes_to_text()` falls back to `latin-1`, which never raises — any bytes become characters. So a genuine binary WebSocket frame (protobuf, compressed, encrypted-at-app-layer) turns into mojibake that matches nothing, and is indistinguishable from "we read it and the document wasn't there." That's the difference between "no leak" and "we couldn't see."

Related, and confirmed against the mitmproxy docs: you read `flow.request.content`, which is **already decompressed** by mitmproxy. Your manual `decompress()` therefore runs on already-decompressed bytes and is dead code — and your `import brotli` try/except gives you a false sense of safety, because mitmproxy (not your addon) is what decompresses. Worse, `.content` *raises* `ValueError` on an encoding mitmproxy can't handle (e.g., a zstd hiccup), and `flow.request.content or b""` does **not** catch that — the exception propagates and that event is silently dropped from the capture.

**Fix:** decide on one path. Either read `raw_content` and decompress yourself (then your brotli handling is real), or keep `.content` but wrap it in try/except and *record* failures. Mark binary frames as `unreadable` in the JSON and surface a count in the summary, so "couldn't read" is never silently scored as "clean."

### 2.4 The HTTPS-share metric probably mislabels encrypted WebSocket traffic

In `websocket_message`, you set `"tls": flow.request.scheme == "wss"`. For WebSocket flows mitmproxy represents the connection as an HTTP flow whose request scheme is typically `"https"`, not `"wss"`. If so, every encrypted WS frame is recorded as non-HTTPS and your `https_event_pct` drops for exactly the tool (Grammarly) that uses WebSockets most. (I couldn't confirm the exact scheme value from docs alone — verify it in your first capture.)

**Fix:** treat `scheme in ("https", "wss")` as TLS, or key off the connection's TLS state rather than a string compare.

### 2.5 The capture mechanics have two silent-failure traps

- **Makefile ordering bug:** in `run_one`, `mitmdump` redirects to `data/raw/$(1)/run_$(2).log` and writes `--save-stream-file data/raw/$(1)/run_$(2).flow` *before* the `@mkdir -p data/raw/$(1)` line. On a fresh checkout where that directory doesn't exist, the shell redirect and the stream-file both fail and the capture is broken — but a PID still gets written, so the run "completes." `run_capture.sh` does the `mkdir` first and is fine; the Makefile is the one you actually use.
- **xdotool paste reliability:** `xdotool key --window <id> ctrl+v` sends a *synthetic* event, which Firefox often ignores for security; the robust pattern is `xdotool windowactivate --sync <id>` then `xdotool key ctrl+v` (real XTEST events). Also `search --name 'Mozilla Firefox' | head -1` can target the wrong window when more than one Firefox is open. And running `make grammarly-1` in a second terminal steals focus away from the textarea you just clicked into. Net effect: the paste can silently land nowhere → empty textarea → 0% → misread as "no leak."

**Fix:** after the paste, verify the textarea actually contains the document (e.g., read it back via `xdotool`/clipboard round-trip or a tiny JS check) and abort the run loudly if it's empty. Add a "paste landed" assertion to the protocol checklist.

### 2.6 "Leak" / "violation" framing overclaims; be honest about consent

You install each extension and **log in**. By doing so you accept a ToS that explicitly says the tool processes your text on its servers. So when the canary appears in traffic, the accurate statement is "the document was transmitted to the vendor's first-party servers as part of the tool's normal, disclosed operation." Calling that a "leak" or "privacy violation" (as `interpretation.md` does) is arguably overclaiming — the data going to Grammarly's servers is the advertised behavior, not a defect.

Your *actual* contribution is sharper and still strong: that this transmission happens **(a) by default, (b) in the background, (c) in a context where the user was explicitly told not to share the document with AI tools, and (d) without an obvious in-the-moment signal.** That's a real and publishable point about informed consent and dark-pattern defaults. Frame it that way. The locked methodology already wisely dropped "passive exposure" as imprecise — extend the same discipline to "leak."

### 2.7 Documentation has drifted and contradicts the locked methodology

If your professor reads `QA-Professor.md` Q3, they'll see the **rejected** composite formula `Confidence % = Reproducibility × Traffic visibility` presented as "we decided." `Timeline.md` Phase 3 also still lists "Confidence % calculation (reproducibility × visibility)." `Metrics-Definition.md` is titled "v2," says "11 planted identifiers" in §4 then lists 12, and Q7 still says "same typing simulation" when you switched to paste. These are the documents you'll hand the professor. Reconcile them before the next update or you'll relitigate settled decisions.

---

## 3. Minor issues — polish

- **"X of 35 sentences" counts label lines as sentences.** Your parser splits on newlines, so "Employee ID: HV-2026-391847", "Canary token: ...", and section headers count among the 35. I verified the parse: 35 units, several are headers, not prose. Either filter label-like lines or just describe the denominator honestly ("35 line-level units").
- **`avg_request_bytes` is always 0.** `analyze.py` reads `total_request_bytes` from the summary, but the addon never writes that key. The comparison table will print a confident "Avg request bytes: 0". Drop it or compute it from `content_length`.
- **Sentence offset math is correct.** You asked me to look for an off-by-one in sentence boundaries; I checked every parsed sentence against the document and all offsets map back exactly. No bug here. (The 90%-threshold *rationale* in the docs is slightly muddled — it's not really about "the trailing 19 characters" — but the 0.9 value itself is fine.)
- **t-table lookup is conservative**, which is the safe direction for n=5. Fine as-is.
- **Baseline subtraction barely affects the exposure metric.** Background telemetry domains don't carry your document, so they contribute ~0 to exposure whether subtracted or not. Baseline's real value is (i) the zero-exposure control — if a no-extension run shows exposure, your pipeline is broken — and (ii) denoising domain/event counts. Describe it as that, not as a correction to the headline %.
- **`sleep 3` before paste** may be too short for a cold mitmproxy start on a VM; poll the log for the "listening" line instead of a fixed sleep, so you never paste into a not-yet-ready proxy.

---

## 4. What I'd do differently if this were mine

I'd cut infrastructure and sharpen the claim. In rough order:

**Lead with the canary, not the percentage.** Your strongest, least-disputable evidence is a string that exists nowhere on Earth showing up in traffic to `*.grammarly.com` over TLS, seconds after a paste, with no user action. That single fact answers the interesting question ("does a confidential document leave the machine to a third party by default?") with a clean yes/no and a named recipient. It needs no confidence interval and no t-test, and no encoding bug can fake it. Make the canary/token result the headline; demote the 20-char exposure % to a supporting "how completely" measure.

**One matcher, one number.** Replace the per-event + transcript + separate-analyzer arrangement with a single function that scans the full per-host concatenated decoded stream and returns covered positions. Compute it once in the addon, store it, and have the analyzer read it rather than recompute. Fewer places to silently disagree (this dissolves Blocker 1 and concern 2.2 at once).

**Make the real field a primary condition.** The local `file://` textarea is a fine *control* for "cleanest possible signal," but the threat model lives in Gmail and Google Docs, which are `contenteditable`/canvas editors that these extensions treat differently. Run at least one real-field condition per tool as a main result, not a September stretch goal. If the local page and the real field agree, you've earned the right to use the clean local numbers. If they disagree, that disagreement is itself a finding.

**Vary the document, lightly.** Three documents — short memo (this one), a long multi-page document, and a code/structured snippet — turn "30% of this memo" into "between X and Y across document types," which is defensible as an answer to your actual research question. This is more valuable than a 4th or 5th repeat of the same paste.

**Spend less on stats, more on truth.** With near-deterministic captures, drop the CI/t-test framing entirely (or report it only as "measurement reproducibility"). Replace "Tool A's CI is disjoint from Tool B's" with effect sizes plus the honest caveat that this is one document. Reviewers respect "here's exactly what we saw and what we can and can't conclude" far more than thin CIs on n=5.

**Store more, trust previews less.** Your input is 2 KB. Storing full request bodies for the tool's own domains for at least one run per tool costs almost nothing and removes every "the preview was capped" caveat. Keep the `.flow` files regardless — that instinct is correct.

None of this throws away the hard parts you've already built (mitmproxy setup, profiles, capture orchestration). It re-points them at a claim you can actually defend.

---

## 5. What looks genuinely good (specific)

- **You killed the multiplicative "confidence" formula and the TLS-bytes ratio.** Recognizing that multiplying reproducibility by visibility produces a meaningless number, and that the bytes ratio silently hid cert-pinned tunnels, is exactly the kind of judgment most projects lack. Reporting two honest numbers instead of one tidy-but-fake one is the right call.
- **The canary/token design is clean and safe.** A UUID canary that exists nowhere, a `.invalid` email (RFC 2606 — can't accidentally hit a real inbox), no real PII, and the "match without the `#`" detail. This is careful, ethical instrument design.
- **Saving raw `.flow` per run.** This is what makes every encoding bug in this review *recoverable without re-collecting*. It's the single best engineering decision in the project.
- **The "0% might be a measurement failure, not a finding" instinct.** `gotchas.md` §1 and the Setup-Guide's "do not start collection if interception isn't verified" show you already understand the most dangerous failure mode in MITM studies — false negatives that look like clean results. Most undergrads (and plenty of grad students) never write that down.
- **Experimental hygiene:** isolated per-tool profiles, a no-extension baseline, scripted paste over Selenium (correctly anticipating anti-bot detection), a fixed wait. Sound controls.
- **The documentation discipline itself.** Locked decisions paired with rationale and rejected alternatives, plus a gotchas file, is better project hygiene than most professional codebases. The drift in §2.7 is worth fixing precisely because the rest is so disciplined that a reader will trust every doc.
- **The responsible-disclosure / publication gate** is thoughtful and ethically correct, and rare to see planned this early.

---

### The one-paragraph version

The engineering instincts are strong and the ethics are sound, but three things must be settled before you collect: fix the analyzer so it stops discarding cross-event coverage (it currently reports ~0% on captures that leaked 100% — I reproduced it); prove the pipeline actually works end-to-end on one real Grammarly capture, including that extensions even run on your `file://` page; and decide honestly whether you're studying *one document* (then drop the CIs) or *documents in general* (then use more than one). Your strongest result isn't a percentage with a confidence interval — it's a unique canary string arriving at a vendor's server, by default, after you were told not to share the file. Build the project around that.
