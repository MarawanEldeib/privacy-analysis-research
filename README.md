# Measuring Data Exposure in LLM-Integrated Productivity Tools

University research project — measures how much of a confidential document is silently transmitted to external servers when LLM-integrated writing-assistant browser extensions (Grammarly, LanguageTool) are running by default during normal use.

**Student:** Marawan Eldeib · **Matrikelnummer:** 3764796 · **Deadline:** 2026-10-10

## Research question

> *How does user data exposure differ across LLM-integrated productivity tools during controlled use?*

Concretely: a user receives a confidential file, is told not to share it with AI tools, but has a writing-assistant browser extension running by default in the background. They paste content into a normal text field (email, doc, comment box). The extension silently transmits the content. We measure how much.

## What this repo contains

| Path | What |
|---|---|
| `docs/` | Walkthroughs (reproduction / narrative / technical), capture protocol, metrics, environment, professor Q&A — start at `docs/WALKTHROUGH.md` |
| `input-data/` | Synthetic test document with 12 planted identifiers, controlled test HTML page |
| `scripts/capture/` | mitmproxy addon that captures and scores outbound traffic |
| `scripts/analysis/` | Analyzer (per-tool stats, 95% CIs, info-type breakdown, traffic timeline, comparison chart) |
| `skills/privacy-analysis-project/` | Project knowledge for Claude sessions (auto-loaded) |
| `Makefile` | One-line commands for the capture/analysis cycle |
| `data/raw/` | Capture outputs per tool (one folder per tool) |
| `results/` | Analyzer outputs: per-tool summaries, comparison table, info-type breakdown, chart PNG/SVG |
| `report/` | LaTeX research report (`main.tex` → IEEE two-column PDF) + figures + `refs.bib` |
| `presentation/` | Supervisor progress deck (`build_deck.js` → `Progress-Review.pptx/.pdf`) |
| `tests/` | Pytest regression tests (matching, analysis, token-list-in-sync) |
| `Project-Dashboard.html` | Self-contained results & progress dashboard (open in any browser) |

## Results at a glance

| Condition | Runs | Document exposure | Secrets sent | Canary? | HTTPS | TLS failures |
|---|---|---|---|---|---|---|
| **Grammarly** | 5 | **99.0%** (σ 0.0pp) | **12 / 12** | yes | 100% | 0 |
| **LanguageTool** | 5 | **91.9%** (σ 0.0pp) | **12 / 12** | yes | 100% | 0 |
| Baseline (no extension) | 3 | 0.0% | 0 / 12 | no | — | 0 |

Both writing assistants transmitted essentially the whole document — and every planted
secret, including the unique canary — to their servers on a single paste, perfectly
reproducibly, while the no-extension baseline transmitted nothing. The gap between 99.0%
and 91.9% is formatting/whitespace only; both sent 100% of the sensitive content.

## Documentation

Three focused walkthroughs (index at [`docs/WALKTHROUGH.md`](docs/WALKTHROUGH.md)):

- [`docs/Reproduction-Guide.md`](docs/Reproduction-Guide.md) — run the whole study from scratch (exact commands + verified links).
- [`docs/Narrative-Walkthrough.md`](docs/Narrative-Walkthrough.md) — the project story: goal, method, dead ends, findings.
- [`docs/Technical-Walkthrough.md`](docs/Technical-Walkthrough.md) — how the pipeline, capture add-on, and analyzer are built.

Supporting references:

- [`docs/Metrics-Definition.md`](docs/Metrics-Definition.md) · [`docs/Capture-Protocol.md`](docs/Capture-Protocol.md) · [`docs/ENVIRONMENT.md`](docs/ENVIRONMENT.md) — locked definitions, protocol, and version manifest.
- [`docs/Related-Work-Research.md`](docs/Related-Work-Research.md) — digest of ~22 cited related papers (feeds the report).
- [`docs/Tooling-Landscape.md`](docs/Tooling-Landscape.md) — tools used vs considered (mitmproxy, Wireshark, Burp, Frida, Presidio, …).
- [`docs/Desktop-Capture-Runbook.md`](docs/Desktop-Capture-Runbook.md) — how to extend beyond the browser to desktop/system-level capture (Linux).
- [`docs/Review-Findings-2026-09-05.md`](docs/Review-Findings-2026-09-05.md) — QA audit of the code/methodology and the fixes applied.
- [`docs/Meeting-Notes-2026-07-23.md`](docs/Meeting-Notes-2026-07-23.md) — supervisor feedback and agreed next directions.
- [`CHANGELOG.md`](CHANGELOG.md) — dated log of research milestones.

## Quick start

```bash
# 1. Install dependencies (Kali Linux)
sudo apt install -y python3-pip firefox-esr xclip xdotool jq make
pip3 install --break-system-packages mitmproxy brotli pyahocorasick matplotlib

# 2. Sanity check
make check

# 3. Set up Firefox profiles + mitmproxy cert (see docs/Reproduction-Guide.md)

# 4. Capture (one tool at a time, five runs each)
make page-grammarly        # Terminal 1: open Firefox with the profile
make grammarly-1           # Terminal 2: run capture #1

# 5. Analyze
make analyze               # default strict view
make analyze-lenient       # sensitivity check
make chart                 # write results/comparison_chart.{png,svg} for the report
```

## Methodology in one paragraph

The test document is a synthetic confidential memo (`input-data/test-document.txt`) containing 12 unique fictional identifiers — names, IDs, contact details, and a UUID canary — that don't exist anywhere on the internet. Any match in captured traffic is unambiguously from our input. We use mitmproxy with SSL/TLS interception on Kali Linux, run each tool in an isolated Firefox profile with only that tool's extension active, paste the test document into a controlled local HTML page, and measure how much of the document appears in outbound traffic. Five runs per tool plus three baseline runs (no extension) for background subtraction. The locked protocol lives in `docs/Capture-Protocol.md`.

## Metrics (see `docs/Metrics-Definition.md`)

1. **Exposure %** — fraction of document characters whose 20-char window appears in captured traffic.
2. **Reproducibility** — std dev of exposure % across 5 runs (High <3pp / Medium 3-10pp / Low >10pp).
3. **Traffic visibility** — HTTPS event share + TLS handshake failure count (two separate numbers, never multiplied into a composite).
4. **Sensitive token detection** — N of 12 planted tokens found (the headline metric).

Plus 95% confidence intervals on the mean exposure, an **information-type breakdown**
(the 12 secrets grouped into categories — names, contacts, IDs, financial, legal, etc.),
and a **traffic-over-time** view (the paste spike vs. background transmission). Figures
live in `report/figures/`.

## Project status

Data collection is **complete for the final tool set**: **Grammarly** and **LanguageTool** — two independent automatic grammar checkers — plus a **no-extension baseline**. Across 5 runs each, both tools silently transmitted ~the entire test document (Grammarly **99.0%**, LanguageTool **91.9%**) and **all 12 planted secrets including the canary**; the baseline transmitted **0%**. Per-tool summaries live in `results/`, and `Project-Dashboard.html` gives a self-contained overview.

ProWritingAid, QuillBot, and Wordtune were evaluated but dropped and are recorded as limitations (ProWritingAid didn't attach to the controlled field; QuillBot has no official Firefox extension; the `/wordtune/` Firefox listing was a clone and the genuine tool is on-demand). See `docs/QA-Professor.md` for the reasoning.

The methodology was **approved by the supervisor** (23 July 2026 meeting), who encouraged broadening the study where feasible. The written report is drafted in LaTeX (IEEE two-column, `report/main.pdf`), the related-work section is grounded in ~22 cited papers, and the analysis code has been through a full QA audit (`docs/Review-Findings-2026-09-05.md`).

The Linux desktop / system-level pass is largely complete: native **LanguageTool desktop**
checks on-device and transmits nothing (0%); **Level 2 (Presidio)** PII discovery over the
decrypted traffic surfaced additional transmitted identifiers (e.g. a Grammarly auth token +
session IDs) beyond the 12 planted secrets; an **independent no-proxy capture** confirms the
Grammarly upload goes directly to Grammarly's AWS/CloudFront infrastructure with nothing
intercepting it (rules out proxy-induced behaviour); and an **idle/background test** shows the
extension stays continuously connected to Grammarly's servers (auth, config, experimentation,
telemetry) even with no user action, while transmitting **no document content or secrets**
until text is supplied. Evidence lives in `results/evidence/`.

**Next:** a Windows-VM phase for Windows-only desktop apps (Grammarly desktop, DeepL, iCloud,
free consumer Avast) and the USB auto-read test — see `docs/Desktop-Capture-Runbook.md` and
`docs/Timeline.md`.

## Note on the test document

The document contains realistic-but-fictional personal data (names, emails, phone numbers, etc.). It is **synthetic** — no real person, organization, or system is referenced. If you fork this repository, note that some automated PII scanners may flag the synthetic content despite it being entirely fictional.

## Research artifact and disclaimer

This repository is a **research artifact**, not a maintained product.

- Results reflect tool behavior at the time of capture (the captures themselves are timestamped in each run's JSON). Tool behavior may have changed since then.
- The methodology is intended for transparent measurement of *default-configuration* behavior, not to demonstrate exploits or vulnerabilities. The tested tools are doing what they were designed to do; the research question is whether users understand the scope of that.
- All test data is synthetic. No real personal data was captured or transmitted as part of this study.
- Findings (when finalized) will be shared with the affected vendors under responsible-disclosure norms prior to public release.

## License

MIT — see [`LICENSE`](LICENSE). The code is freely usable, modifiable, and redistributable. The author makes no warranties about fitness for any purpose.

## Citing this work

See [`CITATION.cff`](CITATION.cff) for the citation metadata. If you use the methodology or results, please cite both the software repository and (when available) the accompanying thesis/paper.
