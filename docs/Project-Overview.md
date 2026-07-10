# Project Overview — Measuring Data Exposure in LLM-Integrated Productivity Tools

**Student:** Marawan Eldeib | Matrikelnummer: 3764796  
**Last updated:** 2026-07-10  
**Status:** Data collection complete for the final tool set — analysis done; report pending.

> **Where things stand:** the pipeline is built and validated, and data collection is
> complete for **Grammarly + LanguageTool + a no-extension baseline**. Both extensions
> silently transmitted ~the whole test document and all 12 planted secrets (Grammarly
> 99.0%, LanguageTool 91.9%); the baseline transmitted 0%. ProWritingAid, QuillBot, and
> Wordtune were evaluated and dropped (recorded as limitations). Remaining: an optional
> Gmail/Google-Docs representativeness run, and the written report. Full entry point:
> `docs/WALKTHROUGH.md`. This overview is kept for background; the earlier "open
> questions" below have been resolved (see `docs/QA-Professor.md`).

---

## What This Project Is About

When a colleague sends you a confidential file and asks you not to share it with AI tools,
you might forget that you have extensions or tools running in the background — like Grammarly —
that silently send your content to external servers. This project measures *how much* of your
data these tools expose, and reports a confidence level on that finding.

**Core research question:**  
*How does user data exposure differ across LLM-integrated productivity tools during controlled use?*

**Result format (per tool):**  
> "Tool X transmitted N of 12 planted secrets (incl. the canary) and ~Y% of the
> document to its servers under default settings." The headline is the planted-secret
> count; exposure % is secondary. (The earlier single "Confidence: Z%" figure was
> rejected — reproducibility and traffic visibility are reported as separate numbers.)

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

### Tools (final)
- **Grammarly** and **LanguageTool** — two independent automatic grammar-checker
  Firefox extensions — versus a **no-extension baseline**. See `docs/QA-Professor.md`
  for why ProWritingAid, QuillBot, and Wordtune were dropped.

### Output
- Comparative analysis report (written)
- Python scripts for data capture and analysis
- Per-tool summary: exposure level + confidence assessment

---

## Open questions — resolved

The planning-phase blockers below have all been decided; the resolutions are recorded
in `docs/QA-Professor.md`.

| # | Question | Resolution |
|---|----------|-----------|
| Q1 | Which tools to test? | Grammarly + LanguageTool + baseline (final) |
| Q2 | How is exposure % defined? | 20-char sliding-window character coverage, baseline-subtracted |
| Q3 | How is confidence defined? | Composite "confidence %" rejected; report std dev + TLS visibility separately, plus 95% CI |
| Q4 | What input data? | Synthetic memo with 12 planted identifiers incl. a UUID canary |
| Q5 | Active vs. passive exposure? | Default-configuration / background exposure on paste |
| Q6 | Environment isolation? | Kali VM, isolated Firefox profile per tool, one extension each |
| Q9 | SSL inspection? | Yes — mitmproxy CA trusted per profile; un-interceptable handshakes counted |

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

## Remaining next steps

1. (Optional) One Gmail and one Google-Docs run to confirm the local page is representative.
2. Write the report — lead with the canary result, not the percentage.
3. Pre-publication gate (see `docs/Timeline.md`): professor approval + vendor disclosure before the repo goes public.

*(Steps 1–7 of the original plan — finalize tools, define metrics, build the document
and scripts, first capture, analyze — are done.)*

---

## Notes & Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-03 | Created project structure | Starting phase |
| 2026-05-03 | Parked tool list & metrics for professor confirmation | Cannot assume — affects all downstream work |
| 2026-05-28 | Locked metrics; rejected composite "confidence %" | Reproducibility and TLS visibility are different kinds of uncertainty — report separately |
| 2026-07-10 | Final tool set = Grammarly + LanguageTool + baseline | ProWritingAid didn't attach; QuillBot has no Firefox extension; Wordtune listing was a clone and the genuine tool is on-demand |
| 2026-07-10 | Data collection complete | Both tools transmit all 12 secrets; baseline 0% |

