# Project Overview — Measuring Data Exposure in LLM-Integrated Productivity Tools

**Student:** Marawan Eldeib | Matrikelnummer: 3764796  
**Last updated:** 2026-05-03  
**Status:** Planning phase — awaiting professor confirmation on open questions

---

## What This Project Is About

When a colleague sends you a confidential file and asks you not to share it with AI tools,
you might forget that you have extensions or tools running in the background — like Grammarly —
that silently send your content to external servers. This project measures *how much* of your
data these tools expose, and reports a confidence level on that finding.

**Core research question:**  
*How does user data exposure differ across LLM-integrated productivity tools during controlled use?*

**Expected end result (per tool):**  
> "Tool X exposes Y% of the input data. Confidence: Z%."

---

## What We Know (Confirmed)

### Methodology (from proposal)
- Use **mitmproxy** to intercept and inspect outbound network traffic
- Run each tool under **identical controlled tasks** with **identical input data**
- Run a **baseline** (tool disabled) for comparison
- Measure exposure using four indicators:
  1. Whether known input data appears in transmitted content
  2. Volume of outbound data (bytes)
  3. Number of outbound requests
  4. Number of external domains contacted
- Store captured data in **CSV or JSON**
- Analyze with **Python**

### Tools (partially confirmed)
- **Grammarly** — confirmed as the professor's illustrative example (browser extension category)
- Full list of tools: **to be confirmed with professor** (see Q1 in QA-Professor.md)

### Output
- Comparative analysis report (written)
- Python scripts for data capture and analysis
- Per-tool summary: exposure level + confidence assessment

---

## What We Don't Know Yet (Open Questions)

See `docs/QA-Professor.md` for the full list. Key blockers:

| # | Question | Blocks |
|---|----------|--------|
| Q1 | Which tools to test? | Everything |
| Q2 | How is exposure % defined? | Analysis scripts |
| Q3 | How is confidence level defined? | Reporting |
| Q4 | What input data to use? | Experiment design |
| Q5 | Active vs. passive exposure? | Task design |
| Q6 | Environment isolation level? | Setup |
| Q9 | Do we do SSL inspection? | Whether we can see content at all |

---

## Planned Project Structure

```
Research Project - Privacy analysis/
│
├── data/
│   ├── raw/          # Raw mitmproxy captures (HAR or JSON files, one per tool/run)
│   └── processed/    # Cleaned, structured data ready for analysis
│
├── input-data/       # The controlled input document(s) used in all experiments
│
├── scripts/          # Python scripts
│   ├── capture/      # mitmproxy setup and capture helpers
│   ├── analysis/     # Parsing captures, computing metrics
│   └── report/       # Generating summary tables and visualizations
│
├── results/          # Output: tables, charts, per-tool summaries
│
└── docs/
    ├── Project-Overview.md   ← this file
    ├── QA-Professor.md       ← open questions for professor meetings
    └── Data-Exposure-Proposal.pdf
```

---

## Suggested Next Steps (after professor meeting)

1. Finalize tool list
2. Define exposure metric formula
3. Create synthetic input document with planted identifiers
4. Set up mitmproxy with SSL inspection (if approved)
5. Write baseline capture script
6. Run first experiment (Grammarly, if confirmed)
7. Analyze and iterate

---

## Notes & Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-03 | Created project structure | Starting phase |
| 2026-05-03 | Parked tool list & metrics for professor confirmation | Cannot assume — affects all downstream work |

