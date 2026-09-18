# External review — DeepSeek

> NOTE: several of DeepSeek's "must-fix" items (author name "Eldieb", garbled `www2`
> footnote, garbled contributions list, domain typos, "194.2%", Table I rendering) are
> PDF text-extraction artifacts. The LaTeX source is correct on all of them. Kept below
> for completeness but marked as N/A.

## 1. Proposal alignment
- Objective 1 (controlled setup): met (IV.A–IV.E).
- Objective 2 (measure exposure): met (V.A–V.F).
- Objective 3 (compare under same conditions): **partial** — browser phase compares
  Grammarly/LanguageTool/baseline under identical paste; host phase is not same-task
  (Word opened, Copilot invoked, DeepL pasted, passive controls). Restrict the
  "compare across tools" claim to the browser phase, or add a same-task host condition.
- Objective 4 (per-tool exposure + confidence): **under-delivered** — Table II has no
  confidence column; High/Med/Low defined but never assigned. Add a Confidence column
  and a per-tool summary.
- Indicators: volume mentioned in prose only; request count and external-domain count
  not systematically reported. Add a small table (volume, requests, domains per
  condition) or justify omission.
- Scope drift: host/system phase goes beyond "small set of LLM-integrated tools under
  identical tasks" — frame as supplementary/exploratory extension.
- Broader-impact §VI.B drifts far beyond measured data (Gaza, Lavender, Palantir, rogue
  model). Remove or condense to a short retention/model-training paragraph.

## 2. Add / remove / change
### Must-fix
1. [N/A — extraction] Name "Eldieb" → source already "Marawan Eldeib".
2. [N/A — extraction] "Broken contributions list" → source list is clean; still, make the
   three bullets parallel.
3. [N/A — extraction] Garbled `www2` footnote → source is correct.
4. Add confidence column to Table II (Grammarly High, LanguageTool High, DeepL High/Med,
   Word-AI-on High, Word-AI-off High, Edge Copilot Medium, Protected View Medium (1 run),
   passive High-for-zero but single run).
5. Fix citation misuse: Limitations "we report the raw traffic unmodified [37]" — [37] is
   Durumeric (HTTPS interception), not about reporting raw traffic. Replace with [30]
   (mitmproxy) or remove. [FIXED]
6. Remove or heavily condense §VI.B Broader impact.
7. Inconsistent mean/median: V.A "median 99.0%" vs Table II "mean". Make consistent. [FIXED]
8. [N/A — extraction] Domain typos (`deep1`, capitalisation) → source correct.

### Nice-to-have
- Add "Per-tool summary and confidence" subsection after V.F (Objective 4).
- Add network-indicator table (volume kB, request count, domains) per condition.
- Add a host-phase baseline (Windows, no tools) or explain why passive controls serve.
- In Fig. 5 note zero-variance conditions have no error bars; state runs per bar.
- Remove the anecdotal Claude observation in V.F unless instrumented.

### Optional polish
- Consistent hyphenation ("LLM-integrated", "large-language-model").
- Check Table I rendering.
- Rewrite abstract to mention both browser and host phases in the first sentence.

## 3. Structure
- Flow (Intro→Background→Related→Method→Results→Discussion→Limitations→Ethics→Conclusion)
  is standard; keep.
- Add V.G "Per-tool summary and confidence".
- Move "Code and data availability" to end of Methodology / before Results.
- Consider splitting Results into "Browser phase" / "Host phase".
- Remove §VI.B or move to a brief "Broader implications" paragraph.

## 4. Figures & tables
- Figs 1–4 clear; keep.
- Fig. 5: add note on zero variance and run counts.
- Table I: check formatting.
- Table II: add Confidence column; consider splitting browser vs host, or add a separate
  volume/request/domain table.
- Missing: per-tool summary table (Exposure level, Confidence, Evidence basis).

## 5. Citations
- Under-cited: DeepL 1500-char free tier; Edge default PDF handler; Grammarly/DeepL launch
  at startup; Avast CyberCapture.
- Misused: [37] in Limitations → [30] or remove. [FIXED]
- Weak/tangential: [35] (Tom's Hardware rogue model) not needed if broader-impact cut.
- Add: mitmproxy docs; Windows WinINET/WinHTTP docs; Office privacy settings [31] is good.

## 6. Presentation
- Fix garbled footnote/contributions [N/A — extraction].
- Clarify V.A "complete, not lower bounds" applies to browser phase; host may be lower
  bounds due to pinning. [FIXED]
- Formula (1): define T as a set of substrings present in traffic, not "traffic" itself.
- Fix extraction garbling ("organizations", "hostnames") [N/A — source correct].

## 7. Clarity questions
1. Host-phase tools within approved scope, or present as extension?
2. Do you have request counts and outbound volume for all conditions?
3. Confidence level per tool — define High/Med/Low and assign each.
4. Are the 2026 references stable/public?
5. Did you run a host-phase baseline without tools?
6. For the Word leak, did you verify content wasn't also sent to other Microsoft endpoints?
7. For Grammarly desktop in Protected View, how attributed to `capi.grammarly.com`?

## 8. Overall evaluation
Strong measurement study; clear threat model; reproducible canary; browser phase rigorous
and answers the RQ for Grammarly and LanguageTool. Host phase valuable but less controlled
and beyond proposal scope. Main weaknesses: (1) missing promised indicators + per-tool
confidence, (2) scope drift into host/OS and societal impact, (3) presentation/citation
issues. Not quite ready. Top fixes: confidence column + per-tool summary; add/explain
volume/request/domain indicators; remove/condense broader impact; fix extraction-era items;
fix [37] citation. After these, ready — core contribution (quantifying default exposure +
surface-dependent leakage) is solid.
