# Q&A for Professor — Open Questions

This file tracks questions that need clarification before we can finalize the project design.
✅ = Confirmed/decided | ❓ = Still open | 🔄 = We decided, confirm with professor later

---

## Confirmed decisions (2026-05-28 — locked with Marawan)

1. **Documents:** use **3** test documents (current memo + a long report + a code/structured snippet), not one — a single document can't support tool-vs-tool comparison.
2. **Tools (FINAL, 2026-07-10):** **Grammarly + LanguageTool** — two independent grammar checkers with genuine Firefox extensions that transmit *automatically in the background* — compared against a **no-extension baseline**. ProWritingAid (did not attach to the controlled field), QuillBot (no official Firefox extension — Chrome-only), and Wordtune (Firefox listing was a clone; the genuine tool is on-demand) were dropped and are recorded as scope limitations. The study measures **automatic/background exposure**; on-demand paraphrasers are out of scope.
3. **Framing:** factual wording — "the tool transmitted the confidential document to its servers under default settings, despite a no-share instruction" — **not** "leak".
4. **Fields:** main runs on the local practice page **plus 1 run each in Gmail and Google Docs** to confirm representativeness.
5. **Stats:** report the simple 95%-CI-overlap comparison; add a formal pairwise test only if the professor requests it.
6. **Exposure counts outbound only** (client→server). Server echoes are captured and reported separately, never added to the headline %.
7. **Headline metric = planted-secret count** ("N of 12 identifiers, incl. the canary, transmitted"); exposure % is secondary; the sentence-leak number is dropped (its unit wrongly counted header lines).

**Professor consultation — DEFERRED, not blocking (decided 2026-05-29):** Do not schedule a meeting now. Proceed with the decided scope; consult the professor only if he asks, once there are results, or if we conclude results aren't achievable. Items to raise then: interim deadlines, open-source/IP permission, and a quick metric confirm.

**Key emerging finding (2026-07-10) — two exposure classes.** Tools split into: (a) **automatic / background transmitters** that send the document to their servers with no user action beyond pasting (Grammarly: 99%, 12/12) — the pure silent-exposure threat; and (b) **on-demand transmitters** that only transmit text the user actively submits (Wordtune: nothing leaves on a background paste; it transmits only on Select → Rewrite). Under the study's exact threat model — extension running in the background, user pastes a document they were told not to share — the automatic class **leaks** and the on-demand class **does not**. This is a meaningful result to report, not a measurement failure. Grammar checkers (Grammarly/ProWritingAid) trend toward class (a); paraphrasers (Wordtune/QuillBot) toward class (b). **Caution logged:** the `/wordtune/` AMO slug is a **clone** (publisher "Akajan Burno", scam support link, echoes text locally, never contacts a server) — the genuine one is `/wordtune-ai-writing-assistant/` by AI21 Labs. Always verify the publisher before installing an extension.

---

## Q1 — Which specific tools should we test?

**Status:** ✅ Decided (revised 2026-07-02 — expanded to 4 tools)  
**Decision:** 4 tools total — all Firefox browser extensions, in two families:

*Grammar/style checkers:*
1. **Grammarly** — professor's own example
2. **ProWritingAid** — replication partner for Grammarly (does the checker finding generalise?)

*Paraphrasers/rewriters:*
3. **Wordtune** — rewriting assistant
4. **QuillBot** — replication partner for Wordtune; the more widely used paraphraser

**Why this set (2×2):** two tools per family gives *within-category replication* — we can say "both grammar checkers and both paraphrasers transmitted the document," which is far stronger than one tool per family. Paraphrasers are especially relevant: rewriting inherently requires uploading the full text to the tool's servers.

**Why all Firefox browser extensions (not GitHub Copilot):** Copilot runs inside VS Code and bypasses Firefox's proxy, making mitmproxy interception unreliable. Keeping every tool a Firefox extension preserves the "same capture protocol for all tools" requirement. QuillBot, like the others, ships a Firefox extension.

**Note:** All four tools are tested in isolated Firefox profiles with the mitmproxy CA certificate installed.

---

## Q2 — What counts as "data exposure percentage"?

**Status:** 🔄 We decided — confirm methodology with professor  
**Decision:** Character-level overlap between input document and captured traffic payloads.

**Formula:**
```
Exposure % = (unique input characters found in any captured payload) / (total input characters) × 100
```

In practice: search all captured and decrypted request bodies/payloads for substrings of the input document (using sliding window of N characters, e.g. N=20 to avoid false positives from common words). Report what fraction of the input was found.

**Also report separately:**
- Whether ANY input content appeared (binary yes/no)
- Volume of outbound data to tool-related domains (bytes)
- Number of requests to tool-related domains
- Number of unique external domains contacted

---

## Q3 — How is "confidence level" defined?

**Status:** 🔄 We decided — confirm with professor  
**Status note:** ❌ REJECTED / superseded — this composite formula was dropped. Reproducibility and traffic-visibility are now reported as two SEPARATE numbers, never multiplied (see "Confirmed decisions" at the top and `methodology.md`). The text below is kept only to record what we moved away from.

**Decision (rejected):** Confidence was originally composed of two factors:

1. **Reproducibility score:** % of repeated runs (out of 5) that showed the same exposure result
   - e.g. 5/5 runs showed exposure → 100% reproducible
2. **Traffic visibility score:** % of total outbound traffic volume that we could actually decrypt and inspect
   - e.g. if 90% of bytes were decryptable → 90% visibility

**Combined confidence:**
```
Confidence % = Reproducibility score × Traffic visibility score
```

Example: 5/5 runs consistent (100%) × 85% of traffic decryptable = **85% confidence**

---

## Q4 — What input data should we use?

**Status:** ✅ Decided  
**Decision:** Synthetic "confidential document" with planted unique identifiers.

The document will contain:
- Unique random phrases not found anywhere on the internet (e.g., "Project Nightingale budget allocation for Q3 fiscal review")
- Fake personal data: names, email addresses, phone numbers, a fake ID number
- A paragraph of normal-looking business text embedding these identifiers

This makes detection in traffic unambiguous — any match is definitely from our input.

---

## Q5 — Active use vs. passive/background exposure

**Status:** ✅ Decided (framing revised 2026-05-23, input method revised again 2026-05-23)
**Decision:** We test **default-configuration exposure when a user handles a confidential document they received**.

Concrete scenario: the user is sent a confidential file, is told not to share it
with AI tools, but has a writing-assistant extension running by default in the
background. They paste content into a normal text field (an email reply,
a Google Doc, a comment form). The extension silently transmits that content.

**Input protocol (locked):**
- Test field: a local HTML page with a single `<textarea>`
  (`input-data/test-page.html`) — chosen for zero third-party noise.
- Method: scripted paste via `xclip` + `xdotool ctrl+v`.
- Wait 60 seconds after paste so the extension has time to process.
- Same protocol for tool runs and baseline runs (baseline uses a no-extension profile).

Why paste, not typing: typing matches a "fresh writing" scenario; the threat
model is "received a document and now handling it." Pasting + wait reproduces
that. Typing would also introduce keystroke-timing variance that would inflate
the std dev metric.

**Stretch (only if time permits):** repeat once in Gmail and once in Google Docs
to confirm the local HTML page is representative of real-world fields.

---

## Q6 — Isolated environment or researcher's real machine?

**Status:** ✅ Decided  
**Decision:** **Kali Linux** (already set up). Each tool tested in a clean browser/editor profile with only that tool's extension active. mitmproxy runs as the system proxy.

Steps per tool:
1. Clean browser profile — no other extensions
2. mitmproxy CA certificate installed in browser
3. Only the target extension installed
4. Run experiment, capture traffic
5. Reset profile before next tool

---

## Q7 — How many repeated trials per tool?

**Status:** ✅ Decided  
**Decision:** **5 runs per tool** (consistent with being enough for reproducibility without excessive time cost).

Each run: fresh mitmproxy capture, same input document, same typing simulation, same duration.

---

## Q8 — Deadline and deliverables

**Status:** ✅ Confirmed  
- **Final deadline:** October 10, 2026
- **Started:** ~May 3, 2026 (3 weeks behind — originally April 13)
- **Professor updates:** Every 2 weeks (next due ~May 17)
- **Deliverables:** Research report + Python analysis code/scripts

Other interim deadlines: to be confirmed with professor as they arise.

---

## Q9 — Handling encrypted/HTTPS traffic (SSL inspection)

**Status:** ✅ Decided  
**Decision:** Yes — we will use mitmproxy's SSL/TLS interception (MITM certificate injection).

Setup: Install mitmproxy's CA certificate into the browser/system trust store on Kali Linux so that HTTPS traffic is decryptable. Without this, we cannot inspect actual content in transit (everything modern uses HTTPS).

Traffic that remains opaque (e.g., certificate pinning) will be logged as a limitation.

---

## Q10 — TLS visibility metric framing

**Status:** 🔄 We decided — confirm with professor
**Decision:** Report TLS visibility honestly as TWO numbers, not one composite:

1. `https_event_pct` — of events the addon actually saw, what % were HTTPS.
2. `tls_handshake_failures` — count of TLS handshakes mitmproxy could not
   complete (e.g., due to certificate pinning). Each failure is a connection
   whose contents we cannot inspect.

The v1/v2 "TLS bytes / total bytes" formula was misleading: cert-pinned
connections never reach the addon's request hook at all, so they were absent
from both numerator and denominator and the metric silently reported high
coverage even when interception was failing. The new framing exposes this
limitation explicitly.

---

## Q11 — Sliding-window granularity & cross-event chunking

**Status:** 🔄 We decided — confirm with professor
**Decision:** Keep the 20-character window for per-event matching, AND add a
per-host concatenated-transcript pass that joins all client-bound bodies from a
single host and scans the joined text. This catches the case where a tool
splits the document across multiple WebSocket frames such that no single frame
contains a 20-char window from the document. Without this pass, chunked sends
would silently understate exposure.

Open sub-question for professor: is a fixed 20-char window appropriate, or
should we also report at a coarser unit (sentence-level)?

---

## Remaining open questions for professor

| # | Question | Priority |
|---|----------|----------|
| Q2/Q3 | Approve the full metric framework: exposure % (20-char window), reproducibility (std dev), traffic visibility (two separate numbers — not one composite), sensitive-token count, sentence-level leak count, mean ± 95% CI. Earlier composite-confidence formula was rejected and replaced. | High — before main data collection |
| Q10 | TLS visibility is reported as two separate numbers (`https_event_pct` + `tls_handshake_failures`). Is this acceptable, or do you want a single coverage number? | Medium |
| Q11 | Matching granularity is 20-char sliding window + per-host concatenated transcript + sentence-level (≥90% covered = leaked) secondary metric. Is this enough, or do you want a different unit (paragraph, token-aware NLP)? | Medium |
| Q12 | Tool comparison currently uses mean ± 95% CI per tool plus a pairwise CI-overlap check. Is this enough, or do you want a formal Welch's t-test with p-values on top? | Medium |
| Q8+ | Any interim submission milestones between now and Oct 10 (e.g., 30% draft by August)? | Medium |

---

*Last updated: 2026-05-23 (re-reviewed; input method, TLS visibility, and chunking framing added; sentence-level + CI metrics implemented; stale rows reworded).*
*Next professor update due: send the email in `docs/Professor-Update-Email.md` after the first Grammarly POC capture.*
