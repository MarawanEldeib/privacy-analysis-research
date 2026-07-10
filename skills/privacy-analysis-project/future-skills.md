# Future Skills — Create When the Time Is Right

This file lists skills that were *considered* during the planning phase but deliberately deferred. If you (a future Claude session) notice Marawan entering one of the phases below, **proactively suggest creating the relevant skill** rather than improvising.

The rule: skills capture hard-won, project-specific knowledge that would otherwise be re-derived each session. We don't pre-build skills before we know what knowledge will be hard-won.

---

## 1. LaTeX-report skill — create when report writing begins (~early August 2026)

**Triggers that mean "now is the time":**
- Marawan mentions "starting the report" or "writing it up"
- He asks for help with LaTeX templates, BibTeX, citations
- Data collection is complete (all `data/raw/<tool>/run_*.json` files present)
- The Timeline.md milestone "Phase 4 — Report Writing" is current

**What the skill would contain:**
- A canonical LaTeX template (article class) sized for the report's expected length
- A `\includegraphics{results/comparison_chart}` example using the SVG already produced by `analyze.py --chart`
- Section structure aligned with the methodology already locked in:
  - Introduction (threat model recap from `methodology.md`)
  - Methodology (point to `docs/Metrics-Definition.md` for formulas)
  - Setup (point to `docs/Reproduction-Guide.md` and `docs/Capture-Protocol.md`)
  - Results (per-tool conclusion statements + comparison table + chart)
  - Discussion (with limitations from `gotchas.md` — TLS pinning, encoding surprises, etc.)
  - Conclusion
- Citation hints for likely sources: mitmproxy docs, the Grammarly privacy policy as it stood at capture time, prior academic work on browser-extension privacy.

**Why deferred:** Until we have actual numbers and know what the story is, the template is guesswork. Real data shapes the narrative.

---

## 2. Results-narrative skill — create alongside the LaTeX skill

**Triggers:**
- Marawan asks "how should I phrase this finding?"
- He's drafting the results section
- He needs to translate the analyzer's conclusion statements into report prose

**What the skill would contain:**
- A small set of prose templates that turn each analyzer field into a sentence:
  - `median_exposure_pct + ci95_*` → "Grammarly transmitted approximately X% of the document (95% CI [Y, Z])."
  - `reproducibility + stdev_exposure_pct` → "Across 5 runs the result was [highly/moderately/poorly] reproducible (std dev W pp)."
  - `sensitive_tokens_detected` → "Of the 12 planted identifiers, N appeared in captured traffic, including [list]."
- Guidance on when to lead with which number (per `interpretation.md`: sentence count + named example is more impactful than %).
- Templates for the "limitations" subsection covering: cert-pinned traffic, sentence-threshold choice, single test field.

**Why deferred:** Templates without real numbers to fit are abstract. Build them from real Grammarly output.

---

## 3. Professor-meeting-prep skill — create if Marawan ever asks for it

**Triggers:**
- "I have a meeting with the professor on [date]"
- "What should I show him this time?"
- A professor-update milestone in `docs/Timeline.md` is imminent

**What the skill would contain:**
- A simple checklist: results since last update, decisions taken, open questions for him, what to ask about next.
- Pulls from `docs/QA-Professor.md` for current open questions.

**Why deferred:** This is small enough that the current process (open `QA-Professor.md`, scan for `❓`) works fine. Only build if Marawan asks for it.

---

## Skills NOT to build

Recording these here so a future session doesn't reinvent them:

- **Auto-verification agent / capture-debugging agent** — declined during planning. `gotchas.md` covers the common failure modes; an agent that's wrong wastes time. Stick with the troubleshooting docs.
- **Selenium / Playwright browser automation** — anti-bot detection in Grammarly often blocks them. Stay with `xdotool` driving a real Firefox.
- **A generic mitmproxy skill** — the project skill captures what's relevant for this project. A generic skill would duplicate the mitmproxy docs.

---

*Rule of thumb: if a phase is at least 4-6 weeks away, don't build the skill for it yet. If it's "next week" and would save real time, build it.*
