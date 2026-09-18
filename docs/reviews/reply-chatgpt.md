# Reply to ChatGPT

Thank you — this was extremely useful and we are adopting most of it. Answers to your
clarity questions first, then what we are (and aren't) changing.

## Answers to your 11 questions
1. **Responses in T?** No. The scorer skips `http_response` events (`# server echoes …
   not outbound exposure`); only client→server request bodies and client→server WebSocket
   frames are scored. We'll fix the methodology wording that implied otherwise.
2. **Denominator?** The code computes true **character coverage**: each match adds
   `range(start, start+20)` to a covered-index set, and Exposure = |covered| / N. It is not
   window-starts / N, so it can reach 100% and 99.0% is genuine (~1% of characters
   uncovered). We'll correct the printed Eq. (1) to match the code — no recalculation needed.
3. **Run counts?** Table II is correct; Fig. 5's "N=2–3" label was loose. Exact N: Grammarly
   5, LanguageTool 5, baseline 3; Word-AI-on 3, DeepL 3, Edge Copilot 3; Word-AI-off 1,
   Protected View 1; each passive/negative control 1. We'll reconcile every N.
4. **Passive "Runs=1"?** Yes — one USB, one iCloud, one viewer each; we'll split/label them.
5. **Versions/dates.** Host: Windows 11 25H2; Edge 153.0.4234.32; Microsoft 365 CtR
   16.0.20326.20144; DeepL desktop 26.9.1; Grammarly for Windows 1.2.296.1955. Browser: Kali
   VM, Firefox 140.12.0esr, Grammarly ext 8.937.0, LanguageTool ext 11.0.2, mitmproxy 12.2.3.
   Captures 2026-07-02 to 2026-09-15 (browser 2026-09-14). We'll add an environment table.
6. **Office account?** Personal Microsoft account.
7. **Grammarly logged in?** Yes, free tier. LanguageTool account-free every run.
8. **"Accessibility layer" evidence?** None in the captures — they prove transmission to
   `capi.grammarly.com`, not the mechanism. We're removing that mechanism claim.
9. **Byte/request/domain counts available?** Yes, from the archived `.flow`/`.json`. We're
   adding them as an indicators table.
10. **Repo secrets?** We found a now-expired Grammarly token + account ID that leaked into
    some committed JSON previews; we're scrubbing them and rewriting history before any push.
11. **"LLM-integrated" pathway?** Fair — we measure remote transmission, not LLM inference.
    We'll add that caveat and keep the framing to "products offering LLM/AI functionality."

## Adopting
Character-coverage/Eq.(1) wording fix; client→server wording; host phase reframed as a
secondary/exploratory phase; Word result qualified to "the tested M365 configuration" with
the exact setting name; Edge heading fixed ("Invoking Copilot on an opened PDF transmits
content") and the "opening just to read it" line removed; conclusion rewritten to separate
user-initiated (DeepL/Copilot) from incidental; JWT section reframed to a one-line
linkability point; GDPR paragraph reframed (synthetic-data caveat, cite GDPR itself, drop
"Germany stricter" and "deployed compliantly"); Broader Impact cut to a short paragraph;
threat-model wording ("not an adversary") fixed; Permissions/QuillBot trimmed; environment
table + expanded threats-to-validity (construct/internal/external/temporal); indicators,
per-tool confidence, and an RQ-answer table added; figures merged to two; leak/exfiltrate →
transmit; canary language softened; MS "connected experiences" + vendor/Mozilla primary
citations added.

## Not doing (with reason)
- **Re-running the N=1 rows:** we're keeping them single-run but labelling them clearly and
  softening "stops it entirely," rather than re-running.
- **Recalculating percentages / recomputing for responses:** not needed — verified the code
  is already coverage-based and response-excluded (see Q1–Q2).
- **Deleting the repeatability point entirely:** we're softening it (SD=0 within-setup
  repeatability, not "deterministic / CI collapses to points") rather than removing it.
