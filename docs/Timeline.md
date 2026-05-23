# Project Timeline — REVISED

**Final deadline:** October 10, 2026  
**Real working start:** May 23, 2026  
**Original planned start:** April 13, 2026 *(6 weeks lost)*  
**Remaining time:** ~20 weeks  
**Professor updates:** Every 2 weeks

---

## ⚠️ Situation as of May 23

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
| 2. Data Collection | Jun 2 – Jul 13 | 6 weeks | All 3 tools captured (5 runs each) |
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
- [ ] **Tool 1 — Grammarly:** 5 runs + baseline *(Jun 2–15, 2 weeks)*
- [ ] **Tool 2 — ProWritingAid:** 5 runs + baseline *(Jun 16–29, 2 weeks)*
- [ ] **Tool 3 — Wordtune:** 5 runs + baseline *(Jun 30–Jul 13, 2 weeks)*

📋 **Professor update due: ~Jun 8** — Show Grammarly full results  
📋 **Professor update due: ~Jun 22** — Show ProWritingAid results  
📋 **Professor update due: ~Jul 6** — All 3 tools collected (or in progress)

---

### Phase 3 — Analysis (Jul 14 – Aug 10)
- [ ] Python parser for mitmproxy JSON output
- [ ] Exposure % calculation (character-level substring match)
- [ ] Confidence % calculation (reproducibility × visibility)
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
2. **Responsible disclosure to vendors.** Email Grammarly, ProWritingAid, and
   Wordtune with the findings + the methodology, give them at least 90 days to respond
   or fix anything before public release.
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
