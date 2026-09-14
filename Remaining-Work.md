# Remaining Work — Privacy Analysis Project

**Deadline:** 2026-10-10 · **As of:** 2026-09-13

> **Tonight (2026-09-13, non-experiment write-up — DONE):** read + cited all 5 new sources
> (Microsoft Copilot docs, CHI 2026, Unit 42, CSA, Cyberhaven); tightened the abstract;
> added the clipboard/F1 OS-level note; built a reproducible action-spectrum figure generator
> with N-per-bar labels; augloop defined + JWT elevated (already done). Report rebuilds clean,
> 11 pages, 0 undefined citations. **Left for the together-review pass (need your eye / not
> experiments):** headline de-duplication, delivery-channel↔action-spectrum merge, dashboard +
> slide-deck sync. **TOMORROW = EXPERIMENTS ONLY** (see below; Grammarly-active Word run first,
> and verify each browser tool's LOGIN state before its run — flagged 2026-09-13).
**Done:** Browser phase (Grammarly 99.0%, LanguageTool 91.9%, baseline 0%) — captured, analysed,
report drafted (IEEE), QA'd. Linux desktop phase (idle transmission + analysis). Host-capture
harness built & proven; DeepL desktop captured (F2); Windows Cloud Clipboard finding (F1).

Windows/desktop phase is the supervisor-approved broadening — **partial is acceptable**;
feasible apps first, pinned/hard ones documented as limitations.

**Supervisor constraints (confirmed):**
- **~3 tools is enough.** We already have **Grammarly + LanguageTool (browser) + DeepL (desktop) = 3**, so the tool-count requirement is essentially **MET**. More tools are not needed.
- **No two-weekly update cadence.** Professor does not want scheduled biweekly updates — send one only if there's a result genuinely worth sharing.

---

## ⭐ PRIORITY ORDER (do in this sequence — prove the important thing first)

**Principle:** the browser phase is already a complete, defensible study. Broadening should
prove the ONE most valuable new claim rigorously and integrate it — not chase many tools.
**P1 → P3 is the whole thesis;** everything after is rigor, housekeeping, or optional flavor.

- **P1 — Prove the headline: PASSIVE exposure** ("received a file, just opened it" → does it
  leak, and to whom?). Section B. The novel claim; valuable either way (leak = headline;
  no-leak = clean bound). **Must-do. USB auto-read is the #1 channel — do it first.**
- **P2 — Lock the active-entry axis cleanly** (small, high-certainty): browser "viewed, no
  field → 0%" control; DeepL one file-upload run + one repeat for a σ. Sections A0/A.
- **P3 — Analyze + write into the report**: analyzer, tables/chart, two-axis section
  (active tools vs passive system actors) + clipboard finding + limitations, rebuild PDF.
  Sections C + D. *This is what makes it a finished thesis.*
- **P4 — Housekeeping**: dashboard/deck sync. (No biweekly professor update — supervisor
  doesn't want the cadence; send one only if a result is worth it.) Section F.
- **P5 — Bonus, do LAST only if time (kept by choice):** Grammarly *desktop* capture ·
  iCloud & Avast as *standalone* captures (beyond their passive-test role in P1) · DeepL
  file-upload/drag-drop run.
  **CUT entirely (not doing):** extra LLM apps (Perplexity/Kimi/MiniMax/Antigravity/Zed/Ollama) ·
  extra DeepL σ reruns · biweekly professor updates.
- **End — Teardown** (Section G) whenever the study wraps.

If time runs short: **P1, P3, teardown** alone = a complete submission.

---

## 📅 Sprint to self-deadline: WED SEP 16 (true external deadline Oct 10; travel Sep 30–Oct 6)

- **Sat–Sun Sep 13–14: P1 passive test** (the only new experiment). Run the **USB auto-read
  test FIRST** (the priority), then Downloads / iCloud Drive; background actors on; per-host attribution.
- **Mon Sep 15 (AM): analysis.** Run analyzer on P1 + existing data; tables/chart; write up
  per-host attribution + the action-spectrum result.
- **Mon Sep 15 (PM): report.** Integrate the two-axis section + clipboard finding (F1) +
  limitations into the existing IEEE draft; rebuild PDF.
- **Tue Sep 16: slides + polish + teardown + submission-ready.** Update deck; consistency pass
  (report ↔ dashboard ↔ deck); machine teardown; final PDF.
- **Tue Sep 16 (hand-off):** send report + slides to the professor for review AND **propose
  live-presentation dates** with him + the team — target **Sep 17–29**, flag the travel
  blackout **Sep 30–Oct 6**. (Coordination, not a status update — this one he needs.)
- **P5 bonus items only if slack remains.**

Reality check: report = already a drafted IEEE paper; deck + dashboard already exist; 3-tool
requirement already met. The only genuinely new *experiment* is P1 — everything else is write-up.

---

## 🔬 TOMORROW (2026-09-14) — EXPERIMENT RUN SHEET (experiments only)
Ordered for efficiency: grouped by app so the setup isn't toggled back and forth, hardest/messiest
install (Avast) last. **Apply the verification protocol (below) to EVERY run** — especially: confirm
mitmdump listening + proxy ON + a positive control before each, and record who received content
(`transcript_covered_by_host`) after each. Save JSON + Procmon CSV per run. Detailed rationale for
each item lives in sections B2/B3 further down; this is the do-order.

**PRE-FLIGHT (once, before any run)**
- [ ] `proxy-toggle.ps1 on` → confirm `status` shows ProxyEnable 1 + mitmdump True (positive control: some traffic flows).
- [ ] Confirm the test files are staged and correct: the 12-secret `.docx`, the planted PDFs (USB + Downloads), all listed not assumed.
- [ ] Confirm Claude/Anthropic bypass still in ProxyOverride so this session isn't disrupted.

**BLOCK 1 — Word / Office (highest value; do the whole block while Word is set up)**
- [ ] **1a. Grammarly-ACTIVE Word run** *(the one you asked to start with)*. Precondition GATE: Grammarly signed in AND its indicator visible in Word AND it actually produced a suggestion — verify the login state first (see the browser/tool-login note in the protocol; a signed-out Grammarly = false 0%). Q: does `*.grammarly.com` receive the doc **in addition to** Microsoft `augloop`?
- [ ] **1b. Word Protected-View nuance** — open the `.docx` fresh (arrives via USB/Downloads → opens read-only). Does the augloop leak fire **before** clicking "Enable Editing" (true "just opened") or only after? Record the Procmon/capture timestamp proving when it fired.
- [ ] **1c. Word (F6) reproducibility ×3** — 3 confirmatory clean runs so the host headline isn't n=1 (browser phase was n=5). Compute a σ.
- [ ] **1d. Mitigation / causation** — disable Office intelligent services (Editor/Copilot "connected experiences"), re-open the same `.docx`. If the augloop leak vanishes → proves causation AND gives users a concrete, documented mitigation (pairs with the Microsoft-docs citation). Re-enable after.

**BLOCK 2 — Cloud sync passive ("dropped in a synced folder, never opened")**
- [ ] **2a. OneDrive auto-sync** — save/drop the file into a OneDrive-synced folder (Desktop/Documents), do NOT open → does it upload to Microsoft with zero open? (M365 machine → likely positive.)
- [ ] **2b. iCloud Drive auto-sync** — drop the file into the iCloud Drive folder, do NOT open → does Apple auto-upload? (TLS likely pinned → connection-level evidence + limitation if opaque.)

**BLOCK 3 — Browser viewer (quick)**
- [ ] **3a. Edge PDF** — open the PDF in Edge (built-in Copilot / read-aloud / translate); we did Chrome + Comet, not Edge. Edge Copilot may be a positive. Confirm which app actually opened it.

**BLOCK 4 — DeepL reproducibility**
- [ ] **4a. DeepL (F2) reproducibility ×2–3** — confirmatory paste runs for a σ (current DeepL result is a single clean run). *(File-upload/drag-drop delivery = P5 bonus, only if slack.)*

**BLOCK 5 — LAST, only if time (messiest install)**
- [ ] **5a. Avast** — install last; test AV cloud file-scan on the USB/open scenario (does the AV upload the file?). Expect pinning → connection-level + limitation.
- [ ] **5b. Opaque-upload size check** — add a "large outbound upload to an unexpected host" size heuristic to the detector so a compressed-PDF binary exfil can't slip past a text matcher; consider tcpdump/Wireshark on pinned channels for size+destination corroboration.

**AFTER THE RUNS (same day if time, else Mon Sep 15 AM)**
- [ ] Run `analyze.py` on each new capture; apply consistent host attribution; regenerate tables + the action-spectrum figure (generator: `scripts/make_action_spectrum.py`); add any new positives as their own bars/rows.
- [ ] `proxy-toggle.ps1 off` + internet restored at end of day (full teardown only when the whole study wraps — Section G).

> **P5 bonus (do LAST only if time, kept by choice):** Grammarly *desktop* capture · iCloud/Avast as *standalone* tool captures (beyond their passive role above) · DeepL file-upload/drag-drop run.
> **CUT (not doing):** extra LLM apps · extra DeepL σ beyond a quick 2–3 · biweekly professor updates.

---

## ✅ Verification protocol — "confirm, don't assume" (apply to EVERY run)
Every prior mix-up (Grammarly inactive, wrong browser, proxy-on-without-mitmdump, a broken
capture that looks like a clean 0%) came from assuming a condition instead of checking it.
So each experiment explicitly verifies its own preconditions and its result:

**Before the run — confirm the setup is really in the intended state:**
- [ ] mitmdump is listening AND the system proxy is actually ON (`proxy-toggle.ps1 status` → ProxyEnable 1, mitmdump True).
- [ ] The **file under test is the right one, in the right place** (drive letter, path, correct format) — list it, don't assume.
- [ ] The **actor under test is genuinely in the intended state** and record how you know:
  - Grammarly "active" = signed in AND its indicator is visible in the app AND it actually produced a suggestion/score (not merely installed).
  - Office AI "enabled/disabled" = verified in Word options, not assumed.
  - Correct default app / browser = confirm which app actually opened the file (we confirm from traffic markers too).
  - **Browser-extension / tool LOGIN state (flagged 2026-09-13):** not all tools in my browsers are actually signed in — some may be freshly added but NOT logged in. A signed-out extension can look "installed and running" yet transmit nothing (a false 0% negative). BEFORE each browser-tool run, confirm the specific extension is signed in and shows its active indicator, and record the login state in the run notes. A 0% from a signed-out tool is "was never actually exercised," not "did not leak."
- [ ] **Positive control**: some traffic is flowing through mitmdump, so a quiet result can't be a broken capture masquerading as 0%.

**After the run — confirm the result is real, not an artefact:**
- [ ] The capture recorded a non-trivial number of events (0 events = broken setup, not a finding).
- [ ] Read `transcript_covered_by_host` to see **who actually received content** — never infer the culprit; confirm it.
- [ ] For a **0% (negative)**: confirm it's a *true* negative — capture was live and the actor really did the thing — i.e. distinguish "did not leak" from "was never actually exercised."
- [ ] TLS-failure count noted (pinned = lower bound), evidence saved (JSON + Procmon CSV), proxy toggled OFF, internet restored.

Record the confirmed conditions alongside each result in `Host-Capture-Findings.md`.

## A. Host / desktop app captures (current phase)
Protocol per app: clean baseline (have `baseline/run_2`) → capture with the 12-secret test doc →
per-host attribution → ideally repeat for reproducibility (browser phase used 5 runs; fewer OK
for this optional phase, but ≥2–3 for a σ).

- [x] **DeepL desktop** — 1 clean run (run_2): 100%, 12/12 to `www2.deepl.com`. (Extra σ reruns **CUT** — one clean run stands.)
- [ ] **Grammarly desktop** — **P5 bonus, do last if time** (browser Grammarly already covers it; 3-tool count met).
- [ ] **iCloud for Windows** — role = **passive-test actor (P1/B)**: drop a planted file into iCloud Drive, watch for auto-sync; TLS likely pinned → connection-level + limitation. Standalone tool capture = **P5 bonus**.
- [ ] **Avast Free** — install LAST; role = **passive-test actor (P1/B)** (cloud file-scan). Standalone telemetry capture = **P5 bonus**. Expect pinning → limitation.
- ~~Additional LLM apps (Perplexity, Kimi, MiniMax, Antigravity, Zed, Ollama)~~ — **CUT** (3-tool requirement already met).
- [ ] Decide clipboard handling per run (disable Windows Cloud Clipboard, or rely on per-host attribution) so F1 never contaminates a tool result.

### A0. Delivery method as an explicit variable (methodology refinement — raised 2026-09-12)
The way the document reaches the tool is itself a variable and must be recorded per run.
Prefer **non-clipboard** delivery (avoids the F1 clipboard-sync confound and better models
"document opened/loaded, not pasted").
- [ ] **Paste-into-editable-field** — the correct/only trigger for the browser writing-assistant extensions (already done for Grammarly/LanguageTool; they act only on editable fields).
- [ ] **Browser "just opened/viewed" control** — open the test doc in a plain browser tab (no editable field) → expect **0% exposure** → documents that *viewing* is safe and bounds the finding to editable-field entry.
- [ ] **File open / drag-drop** — DeepL "Translate a file" — **P5 bonus, do last if time** (passive test already covers "loaded, not pasted").
- [ ] **Passive load / sync (no paste, no action)** — iCloud Drive file-drop auto-sync + USB auto-read. The purest "loaded, not pasted" vector.
- [ ] Record the delivery method as a field on every capture and report exposure per delivery method.

## B. PASSIVE EXPOSURE — "someone sent me a file and I just opened it" (headline scenario)
This is the professor's core question: the user *receives* a file and does nothing but open it —
no copy, no paste, no submitting. Does it leak anyway, and to whom? Measures **system/OS actors**
(cloud sync, antivirus cloud-scan, indexer), NOT the writing tools (which need active entry).
- [ ] **Realistic receipt channels** (priority order): **① USB stick — THE priority test** (planted PDFs already staged), **② Downloads** (as from an email attachment), **③ iCloud Drive** (synced folder).
- [ ] With normal background tools running (iCloud, Avast once installed, Windows Search indexer), start capture, **place/open the file, then do nothing** for ~2–5 min.
- [ ] Variant: (a) file just *sits* in the folder (no open) vs (b) double-click to *open* in its default app — compare. [DONE: F3 insert=silent, F4 open-in-Acrobat=Adobe telemetry only, Notepad=silent]
- [ ] **Viewer variants of "opened" (NEXT — 11 PM session, high value, in-scope):** the leak is *surface-dependent* — it happens only where an LLM integration is watching.
  - **Open PDF in a browser (Edge/Chrome):** local render, but page-reading AI extensions already installed (**Monica** `api.monica.im`, **Perplexity**) may scrape the rendered content — could leak MORE than Acrobat. Zero setup. Do FIRST.
  - **Open a .docx in Word with the Grammarly/Office add-in:** the add-in likely reads + transmits the doc text. Needs a `.docx` of the test doc + Word + the add-in. Do if time.
  - Framing for the report: Notepad/Acrobat (no LLM hook) = silent; a monitored field / add-in / page-reading extension = leak. Same mechanism as the browser writing-assistant phase.
- [ ] Measure: does the canary/tokens leave? To which host (iCloud? Avast? indexer?). Use mitmproxy + **Sysinternals Process Monitor** (which process reads the file).
- [ ] A hit here (content transmitted with zero user action beyond opening) = the strongest, most novel finding of the study.
- [ ] Frame results on the **action spectrum**: never-touched (sync/AV) → opened/viewed → pasted/typed (tools). Report exposure at each level.

### B1. ⭐ USB AUTO-READ = the single most important test in the project
Insert the stick (planted PDFs already on it), **open NOTHING**, and watch whether any
tool / Windows Search indexer / antivirus **auto-reads and transmits** the files —
mitmproxy/tcpdump for the network side + **Process Monitor** filtered on the USB path for
the file reads. A hit here (content sent with zero user action) is the headline finding.
Do this channel FIRST.
- [ ] Planted-secret PDFs already staged on the USB stick.
- [ ] With Grammarly / Avast / iCloud running + Windows Search indexer on + capture live, **insert the USB and open nothing**.
- [ ] Watch for any tool/indexer/AV that **auto-reads and transmits** the files — network (mitmproxy/tcpdump) + **Sysinternals Process Monitor** (filter on USB path) for file reads.
- [ ] A hit here = strongest, most novel finding. Write it up.

## B2. Likely-new-positive experiments to try (explore mindset, added 2026-09-12)
Ranked by likelihood of revealing something new. All use the same harness + planted files.
- [ ] **Word Protected View nuance** — a `.docx` from USB/internet opens in Protected View (read-only sandbox). Determine whether the augloop/Office leak (F6) fires *before* clicking "Enable Editing" or only after. Sharpens the "just opened it" headline. Cheap, do first.
- [ ] **OneDrive auto-sync** — machine is M365; save/drop the file into a OneDrive-synced folder (Desktop/Documents), do NOT open → does it upload to Microsoft with no open at all? Realistic, likely positive.
- [ ] **iCloud Drive auto-sync** — drop the file into the iCloud Drive folder (iCloud installed but only tested as background actor so far) → does Apple auto-upload? Pending.
- [ ] **Microsoft Edge PDF** — open the PDF in Edge (built-in Copilot / read-aloud / translate); we did Chrome + Comet, not Edge. Edge Copilot may be a positive.
- [ ] **Avast** — NOT installed yet; install last, test AV cloud file-scan on the USB/open scenario (does the AV upload the file?). Messiest install → do last.
- [ ] **Reproducibility of host positives** — Word (F6) and DeepL (F2) are single runs; do 2–3 confirmatory runs each so the host headline matches the browser phase's rigor.
- [ ] **PDF-binary / opaque-upload check** — detector matches text; add a "large outbound upload to an unexpected host" size check so a compressed-PDF binary exfil can't slip past. Consider tcpdump/Wireshark on pinned channels (Defender/Adobe/MS telemetry) for connection-level (size+destination) corroboration.

## B3. Supervisor-review action items (from privacy-professor-review, 2026-09-12)
The single biggest lever: harden the Word/Office headline (reproduce it, nail "just opening," show it can be switched off).

### Rigor & validity (MAJOR — do these)
- [ ] **Reproducibility of host positives** — 2–3 confirmatory runs each of Word (F6) and DeepL (F2); host headline is currently n=1 vs browser's 5.
- [ ] **Word Protected-View** — does the augloop leak fire *before* clicking "Enable Editing" (true "just opening") or only after? Resolve before the report leans on "merely opening."
- [ ] **Grammarly-active re-check in Word** — prior Word/Notepad runs had Grammarly INACTIVE, so they don't test Grammarly's role. Re-open the `.docx` with Grammarly genuinely active (signed in, indicator visible in Word) and see whether `*.grammarly.com` receives the doc *in addition to* Microsoft `augloop`. (Notepad/PDF re-checks low value — Grammarly doesn't hook those surfaces.)
- [ ] **Consistent baseline handling** — browser numbers are baseline-subtracted; host numbers were per-file. Either apply a host baseline or state explicitly that host attribution is by-host (so subtraction isn't needed) — don't leave methods asymmetric/unexplained.
- [ ] **Word-upload causation rebuttal** — mirror the Grammarly no-proxy tcpdump argument: show/argue the Word→augloop upload is default M365 behaviour, not proxy-induced.

### Mitigation / causation experiment (HIGH value)
- [ ] **Disable Office intelligent services (Editor/Copilot) → re-open Word** — if the leak vanishes, it both proves causation AND gives users a concrete mitigation (examiners love this).

### Presentation & consistency (MINOR — polish, do in the together-review pass)
- [ ] De-duplicate the headline (restated ~6× across abstract/results/discussion/conclusion). *(Left for together-review — needs the whole-paper eye; risky to prune blind.)*
- [x] Split/tighten the abstract — trimmed 2026-09-13 (~290→~255 words; removed redundant clauses, kept all numbers/framing). Build clean.
- [ ] Merge overlap: "Delivery channel (LanguageTool desktop)" subsection vs new action-spectrum subsection. *(Reviewed 2026-09-13: they make distinct points — same-tool browser-vs-desktop vs passive-vs-active surfaces — and the delivery-channel subsection already forward-references sec:action-spectrum. Overlap judged minor; leave the structural merge for together-review.)*
- [x] Give the JWT credential finding a touch more weight — done (subsection retitled "a transmitted credential", elevated).
- [ ] **Sync dashboard + slide deck** with the host findings (surfaces currently disagree). *(Dashboard partially mentions DeepL/Word/host already; full deck rebuild via presentation/build_deck.js + cross-surface number reconciliation left for together-review pass — better with the user's eye. Effort chip currently blank — fix during that pass.)*
- [x] Clipboard→Microsoft (F1) — DECIDED to include: added as a one-line OS-level "Incidental: the operating system itself" note in the action-spectrum subsection (framed as a controlled confound, not a tool behaviour). 2026-09-13.

### Vague points to clarify / visualise
- [x] Define **"augloop / Augmentation Loop"** in one sentence — done (Office Editor/Copilot cloud backend, defined inline in the Word finding + backed by Microsoft's own docs citation). *(Tiny Word→WebSocket→augloop TikZ diagram deferred to together-review — optional flavour, needs tikz package added.)*
- [x] Action-spectrum figure: label **N per bar** (browser=5, host=1) — done 2026-09-13. New reproducible generator `scripts/make_action_spectrum.py`; every bar labelled N=5/N=1, caption explains N, figure regenerated (PNG/SVG/PDF), PDF rebuilt clean.
- [ ] If claiming "leaks on open," include the Procmon/capture timestamp proving it fired before any click. *(EXPERIMENT-dependent — tomorrow, with the Word/Protected-View run.)*

### Likely examiner questions to be ready for
Open-vs-Enable-Editing · n=1 determinism · proxy-induced? · augloop = free Editor or licensed Copilot? · can users prevent it? · how much do pinned channels hide (lower-bound size)? · single doc/machine generalisability · disclosure posture for naming Microsoft/Grammarly defaults.

## C. Analysis of the new captures
- [ ] Run `analyze.py <tool>` for each new tool; `analyze.py --all --chart` for the comparison.
- [ ] Apply baseline subtraction using the clean host baseline.
- [ ] Add each app as its own TOOL_NAME to the comparison table + info-type breakdown.
- [ ] Regenerate `results/` tables + comparison chart (PNG/SVG).

## D. Report integration (`report/main.tex`)
- [ ] New section: host/desktop phase — method (host mitmproxy, CA, safe proxy toggle) + results.
- [ ] Add DeepL (and any other) results; add **F1 clipboard leak** as an incidental OS-level finding.
- [ ] Update **Limitations**: host vs isolated-VM, clipboard confound + mitigation, cert-pinning (iCloud/Avast/some DeepL asset conns), single machine/OS.
- [ ] Update related work if new tool categories need it.
- [x] **New sources read + cited (2026-09-13):** added 5 refs to refs.bib and wired citations into main.tex — Microsoft Copilot privacy docs (`microsoft2026copilotprivacy`, next to Word/augloop finding: documents default-on cloud content processing + the user-disable control + EU Data Boundary/GDPR → strengthens the "default M365, not proxy-induced, mitigation exists" argument); CHI 2026 "Privacy Paradox of LLMs" (`privacyparadox2026`, Related Work, perception-vs-reality framing — cited at title/venue level only, NO fabricated findings, since full text was JS-blocked; author list flagged in bib note to verify before submission); Unit 42 (`unit42genai2026`, Related Work industry corroboration — 18 high-risk GenAI productivity extensions that read email as composed + intercept prompts); CSA + Cyberhaven (`csa2026extensions`, `cyberhaven2026`, corroboration: DLP-invisible extensions + data pasted from personal/unmonitored accounts). PDF rebuilt clean, 0 undefined citations.
- [ ] Rebuild the IEEE PDF; proofread.

## E. QA & consistency
- [ ] Reproducibility runs (σ) for the new tools; sanity-check per-host attribution.
- [ ] Re-run the QA audit style of `Review-Findings-2026-09-05.md` on the new captures.
- [ ] Reconcile numbers across report ↔ `Project-Dashboard.html` ↔ progress deck.

## F. Deliverables & communication
- [ ] Update `Project-Dashboard.html` with host-phase results (effort chip already synced to 44h30m).
- [ ] Update supervisor progress deck (`presentation/`) if presenting.
- [ ] (Optional) professor update ONLY if a result warrants it — **no fixed biweekly cadence** (supervisor doesn't want it).
- [ ] Check `docs/QA-Professor.md` "Remaining open questions" and close them.

## G. Teardown at end of study (from Host-Capture-Change-Log.md)
- [ ] `proxy-toggle.ps1 off` (done) + clear leftover ProxyServer/Override strings.
- [ ] Remove mitmproxy CA from **both** stores: `certutil -delstore Root mitmproxy` (admin) + `certutil -user -delstore Root mitmproxy`.
- [ ] Delete `%USERPROFILE%\.mitmproxy`.
- [ ] `pip uninstall -y mitmproxy pyahocorasick` (+ frida-tools if added).
- [ ] KEEP: Grammarly (pre-existing), DeepL, iCloud/Apple software (user uses them).
- [ ] If Avast was installed: uninstall + run `avastclear`.

## H. Final polish & submission (by 2026-10-10)
- [ ] Final proofread of report, figures, references.
- [ ] Update `docs/Reproduction-Guide.md` to include the host phase.
- [ ] Produce final PDF and submit.
- [ ] Keep worklog + dashboard current throughout.

### ✅ Citation-integrity check — ALL VERIFIED IN-BROWSER 2026-09-13 (was ⚠️, now cleared)
All five 2026 citations were confirmed against their primary sources in the browser and the bib
entries corrected to real metadata. Nothing citation-related is left open.
- [x] **CHI 2026 `privacyparadox2026`** — VERIFIED on ACM DL. Real paper, open access. Authors **Shuai Cheng, Haitao Xu, Shu Meng, Shuai Hao, Chuan Yue, Zhao Li**; CHI '26, **Article 1638, 25 pp.**; DOI **10.1145/3772318.3791809**; published 13 Apr 2026. Abstract confirms both a large-scale PII-leakage evaluation (email/phone extractable at high rates) AND the perception-vs-reality / "privacy cynicism" framing (20 interviews + 204 survey). Bib updated with real authors/articleno/DOI; placeholder removed. Our citation stays at the framing level — accurate.
- [x] **CSA `csa2026extensions`** — VERIFIED. Real CSA research note "AI Browser Extensions: The DLP-Invisible Enterprise Attack Surface," 11 Apr 2026 (labs.cloudsecurityalliance.org). Confirms DLP failure is architectural + GenAI-extension permission stats. URL + date added to bib.
- [x] **Cyberhaven `cyberhaven2026`** — VERIFIED. Real "2026 AI Adoption & Risk Report," Cyberhaven Labs (shadow-AI personal accounts, sensitive data into AI tools). Title corrected to the 2026 edition; author "Cyberhaven Labs"; URL added.
- [x] **Unit 42 `unit42genai2026`** — VERIFIED on the live page. Authors **Shresta Bellary Seetharam, Nabeel Mohamed, Billy Melicher, Oleksii Starov, Qinge Xie, Fang Liu**; published **30 Apr 2026**; 18 high-risk GenAI extensions (surveil email as composed, intercept ChatGPT prompts, exfiltrate passwords). Bib already matched — confirmed correct.
- [x] **Microsoft `microsoft2026copilotprivacy`** — verified earlier against live Microsoft Learn (default-on connected experiences, disable control, EU Data Boundary). *(Only residual: re-check URL resolves at final submission time — MS relocates docs.)*

### Housekeeping loose ends (non-experiment, added 2026-09-13)
- [ ] **Dashboard effort chip is BLANK** (`Project-Dashboard.html` "Effort logged:" has no value) — populate it and reconcile with the worklog during the together-review/deck-sync pass.
- [ ] **Worklog** — log this 2026-09-13 non-experiment write-up session's hours in `Worklog.xlsx`.
- [ ] **Optional TikZ diagram** Word → WebSocket → augloop (needs `tikz` package added to preamble) — nice-to-have for the Word finding; deferred to together-review.
