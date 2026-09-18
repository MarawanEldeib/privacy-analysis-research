# External review — ChatGPT

Overall: would NOT submit this exact version yet. The core browser experiment is strong;
the paper sometimes claims more than the experiment establishes, while failing to report
several measurements the proposal promised. Highest-priority: exposure-% formula may be
mathematically biased; proposal-promised request/domain/volume metrics not reported;
host experiments presented as comparable despite different actions/formats; Fig. 5 vs
Table II disagree on run counts; JWT + GDPR + latter half of Broader Impact drift from
scope; not enough software/version/config info for a reproducible study.

## 1. Proposal alignment
RQ preserved and answered for the browser phase. Alignment table:
- Controlled setup: met (browser). Measure exposure: met. Compare under same conditions:
  met for browser, NOT for host. Per-tool exposure + confidence: partially met (no explicit
  confidence). Detect known input: met strongly. Outbound volume: partial (browser only).
  #requests: missing. #external domains: partial/missing. Baseline: met. Small set across
  integration types: met/exceeded. Observable outbound only: scope drift (later sections).
- [MUST] Restore promised metrics: per browser condition add `Runs | Exposure% | Secrets |
  Outbound payload bytes | Tool-related requests/frames | External domains | Visibility`.
  Derivable from .flow files.
- [MUST] Add explicit per-tool confidence: Repeatability (High/not assessable) +
  Traffic completeness (Complete/lower bound/incomplete), or one "Evidence confidence".
  Don't use the "High<3pp/Med/Low" variation alone as "confidence".
- [MUST] Clarify host phase is NOT identical-condition comparison. Rewrite start of V-F to
  call it a "secondary exploratory host phase … should not be interpreted as direct
  tool-to-tool comparisons."
- Scope drift (remove most): JWT security; mic/camera permissions; detailed GDPR/BDSG;
  persistent memory; model resellers; unreleased-model behaviour; data brokers/defence;
  Gaza/Lavender.

## 2. Add / remove / change
- [MUST] Fix/clarify exposure-% formula. 2065-char doc has 2065-20+1 = 2046 windows; if you
  count valid windows but divide by N=2065, the max is ~99.08% — and Grammarly is 99.0%.
  So 99.0% may mean "every window matched". Inspect the code. Use N-L+1 denominator, or
  better compute true character coverage E_char = |union of covered char indices| / N (can
  reach 100%). If code divides windows by N, recalculate everything.
- [MUST] Clarify traffic direction. "scored every decrypted outbound request, response, and
  WebSocket frame" — a response is inbound. If responses are in T, a backend echo inflates
  exposure. State only client→server request bodies + client→server WS frames were scored;
  responses retained for validation only. If code includes responses, recompute.
- [MUST] Reconsider "baseline-subtracted by host": removing an entire host because it
  appeared in baseline could hide a real transmission. Prefer: baseline as negative control;
  don't exclude hosts wholesale.
- [MUST] Remove "deterministic / 95% CI collapse to points" language. Say "high within-setup
  repeatability (SD=0.0pp); does not imply zero uncertainty across versions/accounts/etc."
- [MUST] Fix Fig. 5 / Table II run-count disagreement; reconcile every N (Fig 5, Table II,
  V-F prose, Conclusion, raw data).
- [MUST] Fix Edge/Copilot causal wording. Heading "Opening a PDF … leaks it" conflicts with
  passive Edge = 0/12. Use "Invoking Copilot on an opened PDF transmits document content."
  Delete "so opening a document just to read it can hand it to the assistant."
- [MUST] Qualify Word result: "In the tested Microsoft 365 configuration, opening the
  document with connected experiences enabled transmitted content to a Microsoft
  connected-experience endpoint." Rename Table rows to "connected experiences analyzing
  content enabled/disabled" rather than "Office AI on/off".
- [MUST] Remove or radically rewrite §V-C (JWT): a token to its own backend over TLS,
  visible only via your MITM, is normal; "directly abusable secret" unsupported + out of
  scope. At most a neutral sentence, or drop.
- [MUST] Rewrite GDPR paragraph: memo is synthetic; fictional names aren't personal data.
  Reframe as "relevant to deployments with real personal data"; cite GDPR itself (Arts 5,
  28); delete "German law … stricter" and "so the same feature can be deployed compliantly".
- [MUST] Cut most of Broader impact (replace with a short "Broader implications" paragraph:
  measures transmission not downstream use; cite staab2024beyond + vekaria2025bighelp only).
  Remove refs [34]–[36].
- [MUST] Fix conclusion overstatement ("without any step a user would recognise as sharing")
  — untrue for DeepL paste and Copilot invoke. Rewrite to distinguish user-initiated vs
  incidental/open-triggered.
- [MUST] Add environment/versions: dates; Firefox; Grammarly/LanguageTool ext versions;
  Windows build; M365/Word version+channel; Edge; DeepL desktop; Grammarly desktop; login
  state; subscription tier; Office account type (personal vs work/school); region/language.
  A compact "Experimental environment" table.
- [MUST] Expand Limitations into threats to validity: construct / internal / external /
  temporal.

## 3. Structure
- Keep high-level sequence.
- Methodology: split into "A. Primary controlled browser experiment" and "B. Secondary
  host-surface probes".
- Results: A primary browser comparison (all promised metrics) / B content-secret coverage /
  C mechanism + proxy-free / D secondary host observations / E mitigation+controls. Remove
  JWT.
- Discussion: 3 subsections (incidental vs user-initiated; surface/config dependence;
  practical/privacy implications). Permissions subsection too weak for its own Results block
  (also unexpectedly introduces QuillBot) — cut or one sentence in Discussion.
- Threat model: "A gap is not an adversary." Use standard language: "We do not assume a
  malicious vendor, compromised endpoint, or network attacker. The threat is unintended
  disclosure of document content to remote providers through enabled integrations."

## 4. Figures & tables
- Over-illustrated for 12 pages. [NICE] Merge Figs 1–4 → two: "Experimental setups"
  (a browser, b host) and "Exposure-scoring pipeline". Frees ~a page.
- Table II: split into Table II (primary browser) + Table III (secondary host probes), or
  expand and drop the yes/no canary column (12/12 implies canary). Suggested browser table:
  `Condition | N | Exposure | Secrets | Payload | Requests/frames | Domains | Repeatability |
  Capture completeness`. Remove long www2 footnote.
- Fig. 5: make full-width; fix N first; neutral legend terms (user-initiated / open-triggered
  incidental / mitigation / no document content observed); mark N=1 exploratory bars (hollow
  or asterisk).

## 5. Citations
- Verified good/recent: vekaria2025bighelp (USENIX Sec '25); privacyparadox2026 (CHI 2026,
  DOI valid); munir2025keystroke (arXiv 2508.19825).
- [MUST] Replace/refine Microsoft [31]: it's asked to support too much. Use MS "Connected
  experiences in Office" and "privacy controls for Microsoft 365 Apps" for the setting/default
  claims.
- [NICE] Cite vendor docs where you say processing is by design: Grammarly privacy; LanguageTool
  privacy.
- [NICE] Cite Mozilla for host-permission semantics ("Access your data for all websites").
- [MUST] Cite or remove product claims: "default state for millions"; Edge default PDF handler;
  DeepL 1500-char; Grammarly desktop "accessibility layer" hook; augloop as specifically
  Copilot/Editor AI; "Grammarly/DeepL launch at startup".
- Weak/remove (with scope cuts): [34] memory, [35] Tom's Hardware, [36] Lavender, probably
  [33] IEEE ethics, and [26] to argue JWT is credential-harvesting risk.
- Legal paragraph: cite GDPR itself + EDPB guidance, not vendor claims.

## 6. Presentation
- Use transmit/transmission/observed exposure; reserve "leak"/"exfiltrate" (imply
  unauthorized). Especially for DeepL/Copilot (user-invoked).
- Intro: "The question this project asks is deliberately mundane:" → "We ask the following
  measurement question:".
- Intended-use: "expected and effectively consented to" → "user-initiated transmission
  because the user explicitly invokes the service on the text."
- Canary: drop "unforgeable" and "provably reached"; use "high-specificity attribution
  marker" and "strong evidence that content was transmitted toward that service."
- "None of these strings exists anywhere on the public internet" → "synthetically generated
  and not intentionally reused elsewhere; exact-string web searches before the experiment
  returned no matches" (only if you did that check).
- Fig. 5 title → "Document-content coverage detected in outbound traffic (%)" unless true
  character coverage is used.
- Declaration page fine.

## 7. Clarity questions
1. Does the scorer include server responses in T, or only client→server?
2. Denominator for the 20-char score: N, N-19, or other?
3. Which run counts are correct: Table II or Fig. 5's N=2–3?
4. Passive row "Runs=1": one USB, one iCloud, one viewer each? Use "1 each" or separate rows.
5. Exact versions/builds and dates for Word/Edge/DeepL/Grammarly desktop, etc.?
6. Office signed into personal vs work/school account?
7. Was Grammarly logged in? LanguageTool account-free every run?
8. Evidence for "Grammarly desktop hooks the text at the accessibility layer"? If none, remove.
9. Do you have request/domain/byte counts for every primary run in the raw captures? If yes,
   add now.
10. Does the public repo contain raw captures, cookies, auth headers, JWTs, or session IDs?
    If yes, scrub. Synthetic document content does not make real credentials synthetic.
11. What makes each product "LLM-integrated" in the measured pathway? Capture proves remote
    transmission, not LLM inference. State the study measures exposure by products offering
    LLM/AI functionality, not that each request reaches an LLM.

## 8. Overall evaluation
Strongest contribution: the browser experiment (controlled synthetic doc, 12 planted IDs,
canary, bare local page, repeated runs, extension-free baseline, HTTPS interception, decoding
passes, proxy-free corroboration). RQ answered convincingly for Grammarly and LanguageTool.
Host phase interesting but weaker (heterogeneous, some single-run, given too much comparative
weight). Largest scientific weakness: the measurement definition (20-char denominator could
explain the 99.0% ceiling; request/response directionality). Largest proposal-alignment
weakness: missing request/domain/volume + explicit per-tool confidence. Largest writing
weakness: overreach (credential theft, GDPR judgments, model training, defence, military).
Not ready as-is but close at project-report level. Fix order:
1. verify/recalculate exposure metric + client→server directionality;
2. reconcile all run counts;
3. add promised bytes/request/domain/confidence;
4. separate primary browser experiment from exploratory host probes;
5. remove JWT, heavily cut/rewrite GDPR + Broader Impact;
6. add versions/config + threats-to-validity;
7. merge redundant figures, tighten wording.
