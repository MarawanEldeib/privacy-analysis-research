# Reply to DeepSeek

Thank you — helpful review. One important note first, then answers and what we're changing.

## Several flagged items were PDF text-extraction artifacts, not real
When copied from the compiled PDF the text layer was garbled; the LaTeX source is correct,
so please disregard these (or re-check the source):
- Author name is **"Marawan Eldeib"** (not "Eldieb").
- The `www2` footnote reads correctly ("organizations commonly run hostnames such as
  `www2`…"); "w2 labl / oranions / hostames" was garbling.
- The contributions list is a clean three-item list.
- Hostnames are correct: `www2.deepl.com`, `api.languagetool.org`, `capi.grammarly.com`,
  `augloop.svc.cloud.microsoft`, `copilot.microsoft.com`.
- Tables I and II render as proper columns (e.g. "…Protected View + Grammarly | 1 | 94.2%").

Your substantive points all stand and are being actioned.

## Answers to your questions
1. **Host tools in scope, or an extension?** We're reframing the host phase explicitly as a
   secondary/exploratory extension, and scoping the cross-tool comparison to the browser phase.
2. **Request/volume/domain counts for all conditions?** Yes — available from the archived
   captures; we're adding an indicators table (bytes, requests/frames, external domains).
3. **Per-tool confidence?** We're adding a per-tool exposure + confidence table (repeatability
   from SD/N plus capture completeness); single-run rows are marked "not assessable," not High.
4. **2026 references stable/public?** Yes; we're adding access dates for the web/news ones.
5. **Host-phase baseline?** There was no separate "Windows, all tools off" baseline; we rely
   on per-host attribution plus the passive/negative controls. We'll state this in Limitations.
6. **Did Word send content beyond augloop?** No — `augloop.svc.cloud.microsoft` was the
   content channel; other Microsoft hosts seen (activity.windows.com, arc.msn.com, ecs.office,
   templates CDN, consent.config) carried telemetry/config/CDN, not document content. We'll
   state this.
7. **Protected View attribution to `capi.grammarly.com`?** Per-host attribution: with Office's
   own augloop silent under Protected View, the document coverage was observed on the
   Grammarly host `capi.grammarly.com` (the only content-bearing host in that run).

## Adopting
The `[37]`/durumeric citation fix (done); mean/median consistency (done); browser vs
host lower-bound scoping (done); Confidence column + per-tool summary; indicators table;
condense Broader Impact to a short paragraph; add DeepL 1500-char / Edge-default-PDF /
startup citations or soften; move "Code and data availability" placement; note zero-variance
bars in Fig. 5.

## Not doing (with reason)
- The "extraction" items above (source already correct).
- Re-running conditions: results are stable; we label single-run rows rather than re-run.
