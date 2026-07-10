# Project Timeline — REVISED

**Final deadline:** October 10, 2026  
**Real working start:** May 23, 2026  
**Original planned start:** April 13, 2026 *(6 weeks lost)*  
**Remaining time:** ~20 weeks  
**Professor updates:** Every 2 weeks

---

## ✅ Status update (2026-07-10)

Data collection is **complete for the final tool set**: **Grammarly** and
**LanguageTool** (two independent automatic grammar checkers) plus a no-extension
baseline. Both transmitted ~the whole document and all 12 planted secrets;
baseline 0%. ProWritingAid, QuillBot, and Wordtune were evaluated and dropped
(recorded as limitations — see `docs/QA-Professor.md`). The phase plan below is the
**original May-23 schedule**, kept for the record; tool-specific rows have been
updated to the final scope. Current entry point for everything: `docs/WALKTHROUGH.md`.

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

### Phase 3 — Analysis (Jul 14 – Aug 10)
- [ ] Python parser for mitmproxy JSON output
- [ ] Exposure % calculation (character-level substring match)
- [ ] Reproducibility (std dev) + traffic visibility as TWO separate numbers (the old multiplicative "confidence %" was rejected — see `docs/Metrics-Definition.md`)
- [ ] Per-tool result tables and comparison charts
- [ ] Per-tool summary statements

📋 **Professor update due: ~Jul 20** — Preliminary results  
📋 **Professor update due: ~Aug 3** — Full analysis complete

---

### Phase 4 — Report Writing (Aug 11 – Sep 14)
- [ ] Introduction and background
- [ ] Methodology section
- [ ] Results section (per tool + comparison)
- [ ] Discussion and limitations
- [ ] Conclusion

📋 **Professor update due: ~Aug 17** — Methodology + intro draft  
📋 **Professor update due: ~Aug 31** — Full draft  
📋 **Professor update due: ~Sep 14** — Revised draft

---

### Phase 5 — Final Polish (Sep 15 – Oct 10)
- [ ] Address final professor feedback
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

## What needs to happen THIS WEEK (May 23–Jun 1)

1. Answer 2 setup questions (browser choice + mitmproxy status)
2. Set up mitmproxy on Kali with SSL interception
3. Create synthetic test document
4. Run first Grammarly capture
5. Have something to show professor immediately after

---

*Last updated: 2026-05-23*
