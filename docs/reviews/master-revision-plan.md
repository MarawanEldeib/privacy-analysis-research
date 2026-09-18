# Master revision plan — reconciled across Fable 5.1, DeepSeek, ChatGPT

Sources tagged [F]=Fable, [D]=DeepSeek, [C]=ChatGPT, [ALL]=consensus.
Priority: (M) must-fix, (N) nice-to-have, (O) optional.

## 0. Code-verified — resolves top concerns WITHOUT recalculating
- Exposure = |union of covered char indices| / N (true character coverage; can reach 100%).
  99.0% is real, not a window/N ceiling. FIX = correct the printed Eq. (1) to match the code.
  (Downgrades [F][C] "recalculate" to a wording fix.)
- Scorer excludes server responses (client→server only). FIX = correct methodology wording
  "every decrypted outbound request, response, and WebSocket frame" → requests + client→server
  WS frames; responses retained for validation only. (Downgrades [C] "recompute".)
- Baseline hosts are NOT wholesale-subtracted from document coverage. FIX = reword the
  "baseline-subtracted" description; baseline is a negative control. (Downgrades [C] concern.)

## 1. Consensus must-fixes [ALL] (M)
- Restore proposal indicators: outbound bytes, #requests/frames, #external domains per
  condition (new columns or a Table III). Derive from archived .flow/.json.
- Deliver Objective 4: per-tool exposure level + confidence (repeatability + capture
  completeness) as an explicit table/column; single-run rows can't be "High".
- Reconcile every N (Table II vs Fig. 5 vs V-F prose vs Conclusion). Hedge or re-run the
  N=1 rows (Office-AI-off, Protected View).
- Frame the host phase as a secondary/exploratory extension, not an identical-condition
  cross-tool comparison; scope the "compare across tools" claim to the browser phase.
- Cut or condense Broader Impact (Gaza/Lavender/Palantir/rogue-model/memory) to a short
  retention/secondary-use paragraph. [DECISION 1]
- Remove or reframe §V-C JWT (out of scope; "abusable secret" unsupported). [DECISION 2]
- mean/median consistency. [DONE]
- Scope the "complete vs lower-bound" claim (browser complete, host lower-bound). [DONE]
- Fix `[37]`/durumeric citation misuse in Limitations. [DONE]

## 2. Unique-but-valid — ChatGPT [C]
- (M) Directionality wording fix (see §0).
- (M) Soften "deterministic / 95% CI collapse to points" → "high within-setup repeatability
  (SD 0.0 pp); not zero uncertainty across versions/accounts/environments."
- (M) Word result: qualify to "in the tested Microsoft 365 configuration…"; rename Table
  rows "connected experiences analyzing content enabled/disabled" (not "Office AI on/off").
- (M) Edge heading causal fix: "Invoking Copilot on an opened PDF transmits document
  content"; delete "so opening a document just to read it can hand it to the assistant"
  (conflicts with the passive-Edge 0/12 control).
- (M) Conclusion overstatement ("without any step a user would recognise as sharing") —
  untrue for DeepL paste & Copilot invoke; rewrite to separate user-initiated vs incidental.
- (M) Add environment/version table (dates, Firefox, ext versions, Windows build, M365/Word
  version+channel, Edge, DeepL/Grammarly desktop, login state, tier, personal vs work
  account, region). [DECISION: you supply values]
- (M) Expand Limitations into threats to validity: construct / internal / external / temporal.
- (N) Threat model: "a gap is not an adversary" → standard non-adversarial wording.
- (N) Permissions subsection unexpectedly introduces QuillBot (not in study design) — trim
  or move one sentence to Discussion. [DECISION 9]
- (N) "LLM-integrated" caveat: capture proves remote transmission, not LLM inference — add a
  sentence; keep the framing honest.
- (N) Canary wording: drop "unforgeable"/"provably reached" → "high-specificity attribution
  marker" / "strong evidence content was transmitted."
- (N) Cite primary vendor/authority docs: Grammarly privacy, LanguageTool privacy, Mozilla
  host-permission page, Microsoft "Connected experiences in Office" (for the default/setting).
- (O) "The question this project asks is deliberately mundane:" → "We ask the following
  measurement question:".

## 3. Unique-but-valid — Fable [F]
- (M) Correct Eq. (1) definition to coverage (see §0).
- (N) Merge V-B into V-A (all 12/12 → one sentence).
- (N) Add an "answer to the RQ" table: Tool | Trigger (paste/invoke/open) | User action |
  Channel | Recipient | Off-switch available. (Strong — directly answers the RQ.)
- (N) Add a bytes-over-time plot around the paste to support the "single burst" claim.
- (N) Subsection titles written as sentences → noun phrases.
- (N) Related Work "for two representative tools" is now outdated; update.
- (N) Add a one-line mapping of conditions to the proposal's browser/editor/web-interface
  types; note pure web UIs were excluded (submission there is intended use).
- (N) Cite Nissenbaum, "Privacy as Contextual Integrity" (2004) as the frame for the
  default-vs-expectation gap. (Strong.)
- (N) Add limitations: single 2 kB document (long-doc chunking untested); Firefox only; bare
  localhost page vs real allow/deny-listed sites.
- (O) "raised in supervision" → "A natural next step".
- (O) Cite Project Zero's 2018 Grammarly token bug only if any token remark stays; a
  cert-pinning measurement paper (Razaghpanah et al., CoNEXT 2017); Samsung/ChatGPT 2023 for
  the employer angle.

## 4. Unique-but-valid — DeepSeek [D]
- (M) `[37]`/durumeric citation misuse. [DONE]
- (N) Verify whether Word also sent document content to Microsoft endpoints besides augloop;
  state it. (Checkable from captures.)
- (N) Move "Code and data availability" to end of Methodology / before Results.
- (O) Add "accessed" dates for the 2026 web citations.

## 5. Reject / ignore (with reason)
- All DeepSeek "extraction" items (name "Eldieb", garbled www2 footnote, contributions list,
  domain typos, "194.2%", Table I) — PDF text-layer garbling; source is correct.
- [F][C] "recalculate all percentages" — NOT needed; code is character-coverage/N (§0).
- [C] "recompute if responses included" — NOT needed; responses excluded (§0).
- Deleting the CI/repeatability point entirely — prefer softening (keep SD=0 repeatability).

## 6. Security (independent of reviews)
- Scrub the real (now-expired) Grammarly token + account ID (sub REDACTED_ACCOUNT_ID) from 14
  committed run_*.json; rewrite git history; then it's safe to push. [DECISION / pre-push]

## 7. Decisions needed from you
1. Broader Impact: cut to a short paragraph (all 3 urge this) or keep?
2. §V-C JWT: remove (ChatGPT) or reframe to a one-line "linkability" point (Fable)?
3. GDPR paragraph: reframe with the synthetic-data caveat, cite the GDPR itself, drop
   "Germany stricter" + "deployed compliantly"? (all agree soften)
4. N=1 rows: re-run to raise N (needs you at the machine) or hedge the claims?
5. Figures: merge the 4 pipeline diagrams into 2 (setups + scoring)?
6. Permissions subsection incl. QuillBot: trim/remove?
7. Environment details: please supply versions/dates/account tiers/ADP on-off.
8. AI-use disclosure in the Declaration: what do your exam rules require?
9. Add the RQ-answer table and the indicators/confidence tables (build from captures)? (yes/no)

## 8. Round-2 refinements (after replies) — all fold in
- Confidence = TWO columns: Repeatability (High/Med/Low/N-A N=1) + Capture completeness
  (Complete/Lower bound/Incomplete); single-run = "Observation only (N=1)".
- Indicators columns: Payload bytes (app-layer), Outbound messages (HTTP bodies +
  client->server WS frames, NOT "requests"), External hosts (content-bearing vs not),
  Secrets, Exposure (char coverage). Include baseline row.
- Eq.(1) = union coverage; "each position counted at most once"; T = set of decoded
  outbound substrings.
- Copilot run 3 used a DIFFERENT prompt ("interesting facts"); fix "three runs, identical /
  locked protocol" -> "runs 1-2 summary, run 3 interesting-facts; transmitted content
  identical."
- Personal M365: EU Data Boundary / processor agreement are ENTERPRISE commitments, not
  consumer; state we measured a consumer licence; enterprise defaults/policies differ.
- Versions recorded post-hoc (2026-09-18); host apps auto-update over Jul-Sep -> label as
  recorded-after-experiments; browser phase exact (2026-09-14).
- N=1 hedge in ABSTRACT + CONCLUSION too; "configuration choice" -> "indicates"; Word =
  "3 enabled runs vs 1 disabled control; supports attribution, not replicated."
- Scope clauses (DeepSeek exact edits): abstract (browser controlled + host exploratory),
  intro, conclusion, limitations (no Windows all-off baseline; single-run = observations;
  cross-tool comparison valid only in browser phase).
- Conclusion around 3 classes: incidental/background; explicit user-initiated; negative/
  mitigated. LLM-integrated caveat EARLY (Intro/Methodology).
- Word extra-hosts sentence (augloop = only content channel; others telemetry/CDN).
- Protected View attribution sentence (only content host was capi.grammarly.com).
- Report raw AND whitespace-normalized exposure; confirm segmentation by diffing one
  LanguageTool + one Edge payload; name what the passive-Edge 1.8% matched.
- Baseline wording: describe SAFE subtraction precisely (drops only zero-coverage background
  events on baseline hosts; keeps real leaks on shared hosts) — do NOT delete "subtracted".
- JWT -> narrow evidenced linkability line (account identifier present; cross-service linkage
  not tested).
- Figure label: "Exposure % (character coverage)" not "baseline-subtracted".

## 9. Security — BROADENED (Fable) — pre-push
- Committed JSON leaks not just the Grammarly token but the user's real EMAIL, NAME, device
  HOSTNAME (REDACTED_HOST*), and other account identifiers across ~15+ files (system-wide host
  capture). Scrub ALL real PII, not just the token.
- Rewrite git history; note it won't reach forks/clones/GitHub cache -> ask GitHub Support to
  purge dangling commits; sign out Grammarly sessions; add a scrub step to the pipeline and
  mention it in Ethics.

