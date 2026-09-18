# External review — Claude Fable 5.1

Tags: [M] must-fix, [N] nice-to-have, [O] optional polish.

## 1. Proposal alignment

### (a) Promised but missing or thin
- [M] Three of the four indicators are barely reported. The proposal names four: input found in traffic, outbound volume, number of requests, and number of external domains. Only the first is reported properly. Volume appears once as prose ("roughly 6 kB… about two tool-related hosts", V-D), request counts never appear, and the host phase has none of the three. Fix: add columns to Table II, or a new Table III, giving outbound bytes, requests, and distinct non-baseline hosts per condition.
- [M] Objective 4 is not delivered. The proposal promised, per tool, "a clear statement describing the level of data exposure… together with a confidence assessment based on the consistency and completeness of the observations." IV-F defines High/Medium/Low reproducibility labels, but they are never applied to any tool. Fix: end Results with a "Per-tool summary" table with columns Tool | Exposure level | Consistency (SD, N) | Completeness (failed TLS handshakes / pinned hosts) | Confidence. Single-run rows cannot be rated "High".
- [M] The 95% CIs promised in IV-F are never reported. Either report them or delete the paragraph. With N=3 and N=1 the "non-overlapping intervals" argument does not work anyway, so I would replace it with min–max across runs.
- [N] No "web interface" tool. The proposal names browser-based, editor-based, and web interfaces. You cover extensions, desktop apps, Office, and a browser sidebar. Add one sentence mapping your conditions to the three types and state that pure web UIs were dropped because submission there is intended use by definition.
- [N] "Same conditions" holds only in the browser phase. Host conditions differ in action (paste, open, invoke) and format (.docx, PDF), so the percentages are not like-for-like. State that cross-phase comparison rests on the secret count, not on exposure %.

### (b) Drift beyond scope
- [M] VI-B Broader impact. Lavender/Gaza, Palantir, a "rogue" OpenAI model, Claude memory, and data brokers have no connection to "observable outbound data exposure". This is the paragraph most likely to cost you credibility. Cut it to three or four sentences on retention and secondary use.
- [M] V-C transmitted credential. This is out of scope and also technically wrong (see §2).
- [N] V-G permissions audit and the Avast result. Neither measures outbound document exposure, and Avast is not an LLM tool. Move them to a short appendix or reduce them to two sentences.
- [N] VI-A GDPR/BDSG. Acceptable as a single paragraph with your disclaimer, but do not let it grow.
- Process Monitor and the USB/iCloud conditions are defensible if you explicitly call them negative controls.

### (c) Framing mismatch
- The research question is never explicitly answered. The RQ asks how exposure differs across tools, but the report's message is that it does not differ (everything leaks roughly 100%). The differences you did find are the trigger (paste / invoke / merely open), the channel, the recipient, and whether an off-switch exists. Say this in one paragraph and add a table (see §4).
- The meaning of "LLM-integrated" is never stated. LanguageTool is largely rule-based and Grammarly's core checker is not obviously an LLM. Define the term in II-A and justify each tool in one line.

## 2. Add / remove / change

### [M] Internal contradictions
1. Complete figures vs lower bounds. V-A says "the reported figures are complete, not lower bounds", but VII says "every reported figure is a lower bound". Fix VII to read: "Browser-phase figures are complete (zero failed handshakes); host-phase figures are lower bounds."
2. Scope of the proxy CA. VII says "The proxy CA is trusted only in the isolated test profile", but IV-E says the CA was "trusted in the Windows certificate store". The host phase therefore decrypted system-wide traffic on a real laptop with real accounts (iCloud, Microsoft, Grammarly). The Ethics claim that "no real personal data was captured" needs qualifying. State what was discarded, and that the CA was removed afterwards. Check that the archived raw captures in the public repo do not contain your Grammarly JWT or account identifiers.
3. Notepad + Grammarly desktop. VII reports this case as "unmeasured rather than zero" because of a direct socket. V-F and Table II nevertheless fold Notepad into a 0.0% passive row. Split that row and mark the Notepad case "unmeasured".
4. Run counts. Table II gives N=1 for both "Office AI off" and "Protected View + Grammarly", while Fig. 5 gives "N=2–3" for each. Give the exact N everywhere. "Disabling a single Office setting stops it entirely" rests on one run if the table is right. Run it twice more or hedge the claim.
5. Mean vs median. The text uses "median 99.0%" while Table II uses "mean". Pick one.
6. Permissions claim (V-G). You say the tools hold "read and change all your data on all websites". You then say Grammarly's declared permissions "look modest… so declared permissions understate actual data access". These two statements contradict each other. Check the manifest and delete the second one.

### [M] Wrong or overclaimed
- V-C. A client sending its own JWT to its own backend over TLS is ordinary authentication. It is visible only because you installed the man-in-the-middle proxy. "leaking a directly abusable secret" and "widens the attack surface" are incorrect. Delete the subsection. At most keep: "Presidio also flagged Grammarly's session token and client IDs in the same channel, meaning transmitted text is linkable to an account; LanguageTool's requests carried no account identifier." That version is a real and relevant finding about linkability.
- V-D: "The ∼8 percentage-point gap… reflects how much surrounding boilerplate each includes". Extra boilerplate in the traffic cannot lower the fraction of document characters found in it. The gap is almost certainly a matching artefact, such as newline or whitespace normalisation, JSON segmentation, or windows straddling chunk boundaries. Diff the LanguageTool payload against the memo, state the actual cause, and ideally report a whitespace-normalised exposure figure as well. The same applies to Edge's 76.9%.
- Passive Edge result. "matched only 1.8%… incidental boilerplate" undermines your claims that 20-character windows avoid false matches and that the strings are unique. Identify what actually matched, for example the filename or title metadata.
- Eq. (1). There are N−19 windows, not N, so as written the measure can never reach 100%. Define the measure as coverage: "character i is covered if any matching 20-char window contains it; Exposure = covered / N".
- Remove the Claude anecdote in V-F. It is uninstrumented, and "on occasion did not honour a later request" is unsupported. Keep the Copilot observation, which is good. Clarify whether that run was one of the three reported runs or a fourth.
- "None of these strings exists anywhere on the public internet." This has not been true since you published the repo. Change it to "existed… at the time of capture".
- Loaded verbs. "silently observe", "exfiltrates", "leak", and "watching" conflict with "this is not an exploit… behaving as designed". Use "transmit" and "exposure" throughout, and keep "leak" only for the canary test.

### [M] Missing reproducibility details
- Extension, app, and Office versions and the Office licence type.
- Firefox version.
- Account tiers, and whether Grammarly was logged in.
- Windows build.
- Capture dates.
- Whether a host-phase baseline existed. Host subtraction on Windows is risky because Microsoft hosts appear in both the baseline and the tool traffic. Describe how you handled that overlap.

### [M] Other
- VIII is titled "Responsible Disclosure" but describes no disclosure. Either state why none was needed (the behaviour is documented) or retitle the section "Ethics".
- Declaration of originality. If any AI tools were used for drafting, code, or the figures, the "no aids other than those indicated" statement requires you to list them. Check your examination rules.

### [N] Other improvements
- Add to limitations: a single 2 kB document (chunking/truncation of long documents untested); Firefox only; a bare localhost page whereas real sites may be allow/deny-listed by the tools.
- Replace IV-A's "We measure three conditions" with an overview of all nine conditions.
- Update the Related Work line "for two representative tools", now outdated.
- Give numbers for the tcpdump corroboration (bytes, destination IPs or ASN).
- Show evidence for the "single outbound burst" claim.

## 3. Structure
Overall order is fine. Suggested changes:
- II-B: the last three sentences describe method; move them to IV.
- Add a IV-0 "Conditions overview" table (condition, phase, user action, input format, N).
- Split V-F (over a page of run-in headings) into "Active submission", "Opening a file", "Negative controls".
- Merge V-B into V-A. All results are 12/12, so it needs one sentence.
- Add V-last "Per-tool summary and answer to the RQ".
- Merge VII and VIII. Cut VI-B.
- Rewrite the contributions list. Bullet 3 mixes two unrelated items; use three parallel items (method, cross-surface result, mitigation + negative controls).

## 4. Figures and tables
- [M] Figs. 1–4 are four diagrams of one pipeline. Reduce to two: a setup figure with both phases side by side, and the scoring pipeline (Fig. 1 and Fig. 4 are redundant). Remove the titles embedded in the images. Use vector graphics in a restrained style (current ones look like slide clip-art).
- [M] Fix the N values in Fig. 5, and add a lower-bound or pinned-host marker to Table II.
- [M] Add an indicators table and a per-tool verdict table (see §1).
- [N] Add an "answer" table: Tool | Trigger (paste/invoke/open) | User action required | Channel | Recipient | Off-switch available.
- [N] Add a small bytes-over-time plot around the paste, to support the burst claim.
- [O] Show the actual synthetic values in Table I.

## 5. Citations
Under-cited claims: "the default state for millions of users" (store install counts); "both vendors document that they process user text" (both privacy policies); DeepL's 1,500-char free limit; Edge as the default PDF handler; Protected View and Mark-of-the-Web; connected experiences on by default (cite Microsoft "Connected experiences in Office" / privacy-controls page rather than the Copilot page [31]); GDPR and BDSG as legal sources if VI-A stays; tcpdump and Process Monitor.
Weak citations to remove: [34],[35],[36] go with VI-B. Cannot verify [26] or [35]; [26] carries three separate claims, confirm each. Check the [25] DOI. [14] and [11] have incomplete author lists. [36] has capitalisation errors.
Citations to add: Nissenbaum, "Privacy as Contextual Integrity" (2004); Project Zero's 2018 Grammarly auth-token bug (Ormandy), if you keep any token remark; a certificate-pinning measurement paper (e.g. Razaghpanah et al., CoNEXT 2017); the 2023 Samsung/ChatGPT incident, for the employer angle.

## 6. Presentation
- Abstract. Before: "even when the user has been told not to share it with any AI tool". After: "in a scenario where the user has not chosen to share it with any AI tool".
- Inline glosses ("a range the true average is likely to fall in", "a Sysinternals tool that logs…") read as tutorial material. Keep only if your supervisor wants that level.
- Subsection titles written as sentences ("The channel is text, not the microphone") read like blog headings. Use noun phrases.
- The www2 footnote is unnecessary; delete.
- Report the traffic-visibility metric per host condition, not only for the browser phase.
- "raised in supervision" should become "A natural next step".

## 7. Clarity questions
1. How exactly are baseline hosts subtracted, and was there a Windows baseline?
2. Is the text normalised (whitespace, newlines) before window matching?
3. What are the exact N values for every host condition?
4. Was the Copilot "interesting facts" run one of the three reported runs?
5. Was Grammarly logged in during the captures, and was the account free or premium? Which Office licence was used?
6. What is in the public repo: raw flows, or only scores?
7. Was Advanced Data Protection (ADP) enabled on iCloud? If not, the end-to-end-encryption remark does not apply.
8. How was "no direct socket" established for the USB/iCloud conditions, given the Notepad case?

## 8. Overall evaluation
Strengths: clean canary design; genuine care about false zeros (manual-paste finding, interception verification, tcpdump corroboration, WinHTTP point); a memorable result (Word-open finding + one-switch control + Protected View); the Copilot "declines in chat, but the text was already sent" observation. For a research project, the measurement is solid.
Weaknesses: modest novelty (tools do what they document; contribution is quantifying it + the surface framing); one short document, one browser, tiny N on host conditions; metric sensitive to normalisation; write-up undermined by internal contradictions, one technically wrong finding (V-C), and an off-topic advocacy section; does not deliver two things the proposal promised.
Not ready to submit as-is. Fix order: (1) indicators table + per-tool exposure/confidence verdicts (proposal objectives 2–4); (2) resolve contradictions (lower bounds, CA scope, Notepad, N values); (3) delete/reframe V-C, cut VI-B, remove Claude anecdote; (4) correct the 8pp/76.9% explanations and Eq. (1); (5) add versions/dates/host baseline; (6) audit repo for real tokens. About a day or two of editing plus a few re-runs; no new experiments beyond raising the N=1 rows.
