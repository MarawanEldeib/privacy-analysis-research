# Locked Methodology — Read Before Suggesting Changes

Every decision below has been considered and locked. Each is paired with the reason and (where relevant) the alternative that was rejected. If you're tempted to suggest a change, find the entry below first.

## Tool selection: Grammarly + LanguageTool + baseline (final, 2026-07-10)

**Decision:** Two automatic grammar-checker Firefox extensions (Grammarly,
LanguageTool) vs a no-extension baseline.
**Why:** Both use the same Firefox/mitmproxy capture path, and both transmit
*automatically in the background* — the exact threat model. Two independent vendors
showing the same behaviour is within-class replication.
**Dropped (recorded as limitations):** ProWritingAid (didn't attach to the controlled
field), QuillBot (no official Firefox extension — Chrome only), Wordtune (the
`/wordtune/` listing was a clone; the genuine tool is on-demand, so it doesn't leak on
a background paste). The original 2×2 plan (adding those three) is superseded — see
`docs/QA-Professor.md`.
**Rejected earlier:** GitHub Copilot — runs inside VS Code and doesn't reliably honour
the Firefox proxy, which would break the "same protocol for all tools" requirement.

## Threat model: "received a doc, handle it normally"

**Decision:** The user has received a confidential file and is handling it (pasting parts into an email, a Google Doc, a comment field). They have a writing-assistant extension running in the background by default. The extension silently sends the pasted content to its servers.
**Why:** This matches the professor's original example. The user wouldn't deliberately paste a doc into Grammarly's own app — they'd paste it into a normal field, where Grammarly silently intercepts.
**Rejected alternative:** "Passive background exposure" was the original framing. It was technically imprecise — Grammarly is doing what it was designed to do. The new framing is more accurate.

## Input method: manual Ctrl+V paste (revised)

**Decision:** `xclip` loads the test document into the clipboard; the operator pastes
with a **real Ctrl+V** into the focused box, then waits 60s.
**Why manual, not scripted (important correction):** the original plan used
`xdotool key ctrl+v`, but a scripted/synthetic paste fills the box **without firing
the DOM `input` event** the extensions listen for — so the tool never ingests the
text and nothing is transmitted (a false 0%). A real keystroke is what makes the tool
receive the document. An opt-in `AUTO=1` xdotool path remains in the Makefile but is
not used.
**Why paste at all (not typing):** matches the "received a document" threat model, and
avoids the keystroke-timing variance that would inflate std dev.
**Rejected:** Selenium / Playwright — anti-bot detection often blocks them; driving a
real Firefox session is safer.

## Test field: local HTML page with one textarea

**Decision:** A static HTML page (`input-data/test-page.html`) with a single
`<textarea>`, served over `http://localhost:8000` (not `file://`).
**Why:** Zero third-party JavaScript and zero third-party network traffic. Whatever the
extension sends is the *only* traffic to interpret. Grammarly and LanguageTool both
activate on standard textareas, so behaviour here matches Gmail or Google Docs. Serving
over `http://localhost` (rather than `file://`) avoids Firefox's restrictions on
extension content scripts running on `file://` pages.
**Stretch (only if time permits in September):** 1-2 supplementary runs in Gmail and Google Docs to confirm the local page is representative of real-world fields.
**Rejected alternative:** Gmail/Google Docs as primary fields — too noisy; baseline subtraction would be much harder.

## Sliding window: 20 characters

**Decision:** A 20-character sliding window over the test document. The analyzer detects which positions in the document have their 20-char window appear somewhere in captured traffic.
**Why:** 20 chars is long enough to avoid false matches from common short words (e.g., "the budget for the"), short enough to catch fragmented sends.
**Tunable:** `--window N` flag in analyze.py for sensitivity analysis. For an authoritative re-window, re-run capture_addon against the `.flow` file with `WINDOW_SIZE=N`.

## Sentence threshold: 90% of characters

**Decision:** A sentence counts as "fully leaked" if at least 90% of its character positions appear in captured traffic.
**Why:** The 10% slack accounts for the final 19 characters of every sentence whose 20-char window extends past the sentence end into trailing punctuation.
**Tunable:** `--sentence-threshold X` flag.

## 5 runs per tool + 3 baseline runs

**Decision:** 5 captures per tool × 2 tools (Grammarly, LanguageTool) = 10 main runs, plus 3 baseline runs (no extension installed).
**Why:** 5 is enough to compute a meaningful std dev and 95% CI without consuming all your time. 3 baseline runs give a stable picture of background Firefox noise to subtract.

## Reproducibility = std dev across 5 runs

**Decision:** Report std dev directly, plus a qualitative label: High (<3pp), Medium (3-10pp), Low (>10pp).
**Why:** Std dev is descriptive — what you saw. No arbitrary normalization constant.
**Rejected alternative:** A single composite "reproducibility %" that combines std dev with something else — would need an arbitrary scaling factor and would conflate things.

## TLS visibility: two separate numbers

**Decision:** Report two numbers, never combined:
1. `https_event_pct` — of events the addon actually saw, what % were HTTPS.
2. `tls_handshake_failures` — count of TLS handshakes mitmproxy could not complete (e.g., cert pinning).
**Why:** The earlier "TLS bytes / total bytes" formula silently hid cert-pinned tunnels (they never reached the addon, so they were absent from both numerator and denominator). The new framing exposes that limitation honestly.
**Rejected alternative:** A composite "confidence %" that multiplied reproducibility × visibility — conflates two distinct kinds of uncertainty and produces a meaningless number.

## Sensitive token detection: 12 planted strings

**Decision:** 12 unique, syntactically realistic but fictional strings planted in the test document. Each is checked individually in every captured event at capture time.
**Tokens:** Helena Voss, HV-2026-391847, Theodora Baumgartner-Klein, theodora.baumgartner@priv-research-demo.invalid, +49 30 4827-9153, Project Nighthawk-3, XREF-291-ALPHA, NHK3-RES-7741, AC-2026-00293-DELTA, 2026-LGL-00847, DE-291-847-3309, CANARY-BC267061-67DC-485B-8E51-6F5494765CAB.
**Why:** Easier to interpret than character %, communicates the privacy violation directly. Any token in traffic = unambiguous leak (none of these exist on the internet).

## Per-host transcript pass (cross-event matching)

**Decision:** After per-event matching, the addon also joins all client-bound bodies per host into one concatenated transcript and re-runs the window matcher.
**Why:** Tools that split text across multiple WebSocket frames could otherwise defeat the per-event window matcher. The transcript pass catches those.

## Reporting per tool, plus side-by-side comparison

**Decision:** A result statement per tool (Grammarly, LanguageTool) + a comparison table with 95% CIs + a visual CI-overlap check.
**Why:** Marawan asked whether tools needed to be compared against each other or reported individually — both. Individual reports per tool are the primary deliverable. The comparison table + CI overlap check is a free bonus that lets the reader spot real differences without formal hypothesis tests.
**Open question for professor (Q12):** Is CI overlap sufficient, or are formal pairwise t-tests required?

## Storage: scan-at-capture + 4 KB body preview + raw .flow archive

**Decision:**
- Per event, scan-at-capture for the 12 tokens and the 20-char windows. Store positions, token list, and a 4 KB body preview.
- Also save the full raw `.flow` file alongside the JSON.
**Why:** Small fast JSON files for analysis. Body preview is for human inspection. `.flow` is the safety net — if Grammarly turns out to use an unexpected encoding (base64, custom compression), we add a decoder and re-analyze the `.flow` files offline without re-capturing.
**Rejected alternative:** Storing full bodies in JSON — files would balloon to 30-50 MB per run for Grammarly. With `.flow` files as safety net, there's no reason to duplicate.

## Final report format: LaTeX

**Decision:** LaTeX (PDF output). Charts saved as both PNG and SVG so they can be `\includegraphics`-ed directly.
**Why:** Marawan's preference. Academic standard.

---

*If you're considering suggesting a change to anything above: re-read the rationale first. If the rationale doesn't address your concern, surface the question to Marawan rather than implementing the change unilaterally.*
