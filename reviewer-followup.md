# Follow-up to reviewers (answers + clarifications)

## Note to DeepSeek — several flagged items are PDF-extraction artifacts, not real
Some "must-fix" items came from a garbled text layer when copying from the compiled PDF.
In the LaTeX source these are all correct, so please disregard them (or re-check against the
source):
- Author name is **"Marawan Eldeib"** (not "Eldieb").
- The `www2` footnote reads correctly ("The `www2` label is not unusual: organizations
  commonly run hostnames such as `www2`…"); "w2 labl / oranions / hostames" was garbling.
- The contributions list is a clean three-item list, not run-together prose.
- Hostnames are correct: `www2.deepl.com`, `api.languagetool.org`, `capi.grammarly.com`,
  `augloop.svc.cloud.microsoft`, `copilot.microsoft.com`.
- Table I and Table II render as proper columns (e.g. "…Grammarly desktop | 1 | 94.2%").

Your substantive points stand and are being actioned: missing promised indicators, the
Objective-4 per-tool confidence verdict, condensing Broader Impact, the `[37]` (durumeric)
citation misuse in Limitations (fixed), and framing the host phase as an extension.

## Answers to clarity questions (both reviewers)

1. **Baseline subtraction / was there a Windows baseline?** We collect the set of hosts seen
   across the no-extension baseline runs and skip those hosts when scoring a tool's exposure.
   The **browser phase** has a 3-run no-extension baseline. The **host phase has no separate
   "Windows, all tools off" baseline**; it relies on per-host attribution plus the passive
   and negative controls (USB, iCloud, Notepad, plain viewers). We will state this explicitly
   and add it to Limitations.

2. **Is text normalized before matching?** Matching is **case-folded (lowercased)** and run
   over additive decoded variants — Unicode **NFC**, URL/form decode, JSON unescape (including
   pulling every JSON string value), HTML-entity unescape, base64 decode, and UTF-16 NUL-strip.
   It does **not** collapse or normalize whitespace/punctuation. Consequently the 99.0% vs
   91.9% gap and Edge's 76.9% are **coverage/segmentation effects** — a tool that splits the
   text into units or alters whitespace leaves some 20-char windows straddling boundaries, so
   they are not matched contiguously — **not** "less content leaving" and **not** "extra
   boilerplate." All 12 planted secrets were recovered in every leaking condition. We will
   correct the report's explanation and can additionally report a whitespace-normalized
   exposure figure.

3. **The exposure measure (Eq. 1).** The implementation computes **character coverage**: for
   each matching 20-char window it marks all characters in `[start, start+20)` as covered, and
   Exposure = covered characters / N. (The paper's Eq. (1) as printed counts window-start
   positions, which understates the ceiling; we will correct the formula to match the code.)

4. **Exact N per condition.** Browser: Grammarly 5, LanguageTool 5, baseline 3. Host:
   Word/Office-AI-on 3, DeepL desktop 3, Edge Copilot 3, Word AI-off 1, Word Protected
   View + Grammarly 1–2, and each passive/negative control (USB, iCloud, Notepad, .md,
   Avast) 1. We will make Table II and Fig. 5 state identical N, and either raise the N=1
   rows or hedge the "one setting stops it entirely" claim.

5. **Copilot "interesting facts" run.** It was observed within the Edge/Copilot captures; we
   will state explicitly whether it is one of the three reported runs or a separate
   observation.

6. **Repo contents.** Committed: the `.json` run summaries (the experimental results), 2 CSVs,
   1 pcap, and all code. Raw `.flow` / `.har` / `.log` are gitignored because they hold
   decrypted tokens. (We found a now-expired Grammarly token + account ID that had leaked into
   some committed JSON previews and are scrubbing it and rewriting history.)

7. **Grammarly login / account tier and Office licence.** Grammarly was **logged in on a
   free account**; LanguageTool ran **account-free** every run; Office used a **personal**
   Microsoft account.

8. **iCloud Advanced Data Protection (ADP) on/off.** **Off** (confirmed on device). So iCloud
   content was encrypted **in transit** but not end-to-end; we will correct the report's
   end-to-end remark accordingly. The finding is unchanged: no document content reached the
   writing tools (0/12).

9. **"No direct socket" for USB/iCloud vs Notepad.** For USB/iCloud we observed no document
   content reaching any tool host, and Process Monitor showed only indexer/shell metadata
   access for the USB case; we did not positively rule out an unlogged direct socket the way
   we caught it for Notepad. We will phrase these as "no document content observed" rather
   than "no socket."

10. **Did Word also hit Microsoft endpoints besides augloop?** Other Microsoft endpoints
    appeared (telemetry / `events.data.microsoft.com`) but were pinned/telemetry, not document
    content; augloop was the content channel. We will verify from the capture and state it.

11. **Stability of 2026 web citations.** They are real; we keep an evidence file with access
    dates and will add "accessed" dates where useful.
