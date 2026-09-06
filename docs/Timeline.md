# Project Timeline — REVISED

**Final deadline:** October 10, 2026  
**Real working start:** May 23, 2026  
**Original planned start:** April 13, 2026 *(6 weeks lost)*  
**Remaining time:** ~20 weeks  
**Professor updates:** Every 2 weeks

---

## ✅ Status update (2026-09-06)

**Browser phase complete and analysed; report drafted; QA done.** Grammarly **99.0%**,
LanguageTool **91.9%**, baseline **0.0%**; **12/12 secrets incl. canary** for both tools;
std dev 0.0. The methodology was **approved by the supervisor (23 July 2026)**, who asked
to broaden the study where feasible (desktop/system-level, more tools, background
behaviour). Since then: LaTeX report drafted (IEEE two-column), related work grounded in
~22 cited papers, information-type + traffic-over-time figures added, and a full QA audit
completed with all findings fixed (`docs/Review-Findings-2026-09-05.md`).

**Now entering the desktop / system-level phase (Linux first)** — see
`docs/Desktop-Capture-Runbook.md`. Windows-only apps deferred to a later Windows-VM phase.
The original May-23 schedule is kept below for the record. Entry point for everything:
`docs/WALKTHROUGH.md`; dated log in `CHANGELOG.md`.

---

## ⚠️ Situation as of May 23 *(historical — original plan)*

- 6 weeks behind original plan
- No data collected yet
- No technical setup done yet
- First professor update is overdue (was due May 17)
- **Action:** Get mitmproxy + first Grammarly capture done ASAP — this is the proof of concept we need to show the professor

---

## Revised Phase Overview

| Phase | Dates | Duration | Goal |
|-------|-------|----------|------|
| 1. Setup & first capture | May 23 – Jun 1 | 10 days | mitmproxy working, test doc ready, Grammarly POC done |
| 2. Data Collection | Jun 2 – Jul 13 | 6 weeks | Final tool set captured: Grammarly + LanguageTool (5 runs each) + baseline |
| 3. Analysis | Jul 14 – Aug 10 | 4 weeks | Metrics computed, results per tool |
| 4. Report Writing | Aug 11 – Sep 14 | 5 weeks | Full report written and revised |
| 5. Final Polish | Sep 15 – Oct 10 | ~4 weeks | Final review, submission |

---

## Detailed Milestones

### Phase 1 — Setup & First Capture (May 23 – Jun 1) 🔴 URGENT
- [ ] mitmproxy installed and running on Kali
- [ ] CA certificate installed in browser (Firefox or Chromium)
- [ ] Grammarly extension installed in clean browser profile
- [ ] Synthetic test document created
- [ ] First Grammarly passive capture run (proof of concept)
- [ ] Baseline capture run (no extension)
- [ ] Verify we can see Grammarly traffic in mitmproxy

📋 **Overdue professor update — send ASAP once POC works**
*Show: methodology decisions, mitmproxy working, first Grammarly capture screenshot*

---

### Phase 2 — Data Collection (Jun 2 – Jul 13)
- [x] **Tool 1 — Grammarly:** 5 runs + baseline — **done** (99.0%, 12/12 secrets)
- [x] **Tool 2 — LanguageTool:** 5 runs + baseline — **done** (91.9%, 12/12 secrets)
- [~] **ProWritingAid / QuillBot / Wordtune:** evaluated and **dropped** (didn't attach / no Firefox extension / clone + on-demand) — recorded as limitations

📋 **Professor update:** send only when there are results to show (consultation is
deferred by decision — see `docs/QA-Professor.md`).

---

### Phase 3 — Analysis (Jul 14 – Aug 10) ✅
- [x] Python parser for mitmproxy JSON output
- [x] Exposure % calculation (character-level substring match)
- [x] Reproducibility (std dev) + traffic visibility as TWO separate numbers (the old multiplicative "confidence %" was rejected — see `docs/Metrics-Definition.md`)
- [x] Per-tool result tables and comparison charts
- [x] Per-tool summary statements
- [x] Information-type breakdown (Level 1) + traffic-over-time figure (added 2026-09-05)
- [x] Full QA audit of code + methodology; all findings fixed (2026-09-05)

---

### Phase 3b — Desktop / system-level pass (Sep 2026) ⏳ CURRENT
- [ ] Linux native **LanguageTool desktop** capture (Java truststore + proxy)
- [ ] **Avast Linux daemon** — background/telemetry behaviour (no user action)
- [ ] **USB auto-read** test + **idle/permissions** checks
- [ ] Level 2 — **Presidio** PII discovery over decrypted traffic
- [ ] Wireshark / Burp / mitmweb / SSLKEYLOGFILE / tcpdump evidence during runs
- [ ] (Later) Windows-VM phase: Grammarly desktop, DeepL app, iCloud

---

### Phase 4 — Report Writing (Aug 11 – Sep 14) — draft complete, iterating
- [x] Introduction and background
- [x] Methodology section
- [x] Results section (per tool + comparison)
- [x] Discussion and limitations
- [x] Conclusion
- [x] Related work (~22 cited papers) + IEEE two-column layout
- [ ] Fold in desktop-phase results when available; title page + declaration of originality

---

### Phase 5 — Final Polish (Sep 15 – Oct 10) ⏳
- [ ] Address final supervisor feedback
- [ ] Final proofreading
- [ ] Package code + data for submission
- [ ] Submit

📋 **Professor update due: ~Sep 28** — Near-final version
🎯 **SUBMISSION: October 10, 2026**

---

## Post-submission: open-source publication gate

The repository is **prepared** for open-source publication (MIT LICENSE, CITATION.cff,
disclaimer block in README — all already in place) but **MUST NOT BE MADE PUBLIC**
until all three of the following are confirmed:

1. **Professor approval.** Marawan must show the professor the repo + the disclaimer
   and get explicit "yes, you may publish this." Check whether the university has
   IP rules that affect publication.
2. **Responsible disclosure to vendors.** Email the tested vendors (Grammarly and
   LanguageTool) with the findings + the methodology, give them at least 90 days to
   respond or fix anything before public release.
3. **Final results stable.** No re-captures planned that would change the headline numbers.

Until all three hold, the GitHub repo stays **private**. This gate is not optional.

---

## What needs to happen next (from 2026-09-06)

1. Desktop / system-level pass on the Kali VM — start with the **Avast Linux daemon
   idle/background capture** and the **USB auto-read** test (highest-value, no Windows
   needed); then **LanguageTool desktop**. Follow `docs/Desktop-Capture-Runbook.md`.
2. Run **Level 2 (Presidio)** over the decrypted captures for unplanted PII.
3. Fold desktop results into the report; add the title page + declaration of originality.
4. (Optional, time permitting) Windows-VM phase for Grammarly desktop / DeepL / iCloud.
5. Keep `CHANGELOG.md`, `README.md`, and this timeline updated as milestones land.

---

*Last updated: 2026-09-06*
