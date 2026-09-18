# Reply to Claude Fable 5.1

Thank you — the deepest of the three reviews; we're adopting almost all of it. Answers,
then what we're changing and not.

## Answers to your 8 questions
1. **Baseline subtraction / Windows baseline?** Baseline hosts are used as a negative
   control; document-content coverage is NOT removed just because a host appeared in the
   baseline (the code explicitly keeps it, "dropping it would erase a genuine leak"). The
   browser phase has a 3-run no-extension baseline; the host phase has no all-tools-off
   Windows baseline and relies on per-host attribution. We'll state this.
2. **Text normalized before matching?** Case-folded + Unicode NFC + additive decoded variants
   (URL, JSON, HTML-entity, base64, UTF-16), but **no whitespace normalization**. So the
   99.0/91.9 gap and Edge's 76.9% are coverage/segmentation effects (windows straddling a
   tool's sentence/whitespace segmentation), not "less content" and not "boilerplate." All 12
   secrets were found in every leaking case. We'll fix the explanation and can add a
   whitespace-normalized figure.
3. **Exact N?** Grammarly 5, LanguageTool 5, baseline 3; Word-AI-on 3, DeepL 3, Edge 3;
   Word-AI-off 1, Protected View 1; each passive/negative control 1. We'll reconcile Fig. 5.
4. **Copilot "interesting facts" run?** It was **run 3 of the 3** reported Edge runs.
5. **Grammarly login/tier; Office licence?** Grammarly free + logged in; LanguageTool
   account-free; Office = personal Microsoft 365 (Click-to-Run 16.0.20326.20144). Browser
   phase: Firefox 140.12.0esr, Grammarly ext 8.937.0, LanguageTool ext 11.0.2, mitmproxy
   12.2.3.
6. **Repo: raw flows or scores?** Committed = JSON summaries (results) + code; raw
   `.flow`/`.har`/`.log` are gitignored. A now-expired Grammarly token + account ID had
   leaked into some committed JSON previews — we're scrubbing and rewriting history.
7. **iCloud ADP?** Off. So iCloud content was encrypted in transit but not end-to-end; we're
   correcting that remark. Finding unchanged: 0/12 to the writing tools.
8. **"No direct socket" for USB/iCloud vs Notepad?** We observed no document content on any
   tool host, and Process Monitor showed only indexer/shell metadata for USB; we did not
   positively exclude an unlogged direct socket the way we did for Notepad, so we'll phrase
   these as "no document content observed."

## Adopting
Eq. (1) corrected to coverage; the **RQ-answer table** (Tool | trigger | action | channel |
recipient | off-switch); merge V-B into V-A; **Nissenbaum (contextual integrity)** citation;
JWT → one-line linkability point; loaded verbs → transmit/exposure; "existed … when
captured" (done); move Background method sentences into Methodology; conditions-overview
table; update "two representative tools"; add limitations (single 2 kB document, Firefox
only, bare localhost); noun-phrase subsection titles; "raised in supervision" → "A natural
next step"; considering the Project Zero Grammarly-token, cert-pinning, and Samsung/ChatGPT
citations.

## Not doing (with reason)
- Re-running the N=1 rows: kept single-run but clearly labelled; "stops it entirely" softened.
- Deleting the repeatability/CI point entirely: softened instead (SD=0 within-setup
  repeatability, no determinism/CI-collapse language).
- The `www2` footnote: keeping a brief version (the author found it helpful for
  non-networking readers), though we'll shorten it.
