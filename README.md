# Measuring Data Exposure in LLM-Integrated Productivity Tools

University research project — measures how much of a confidential document is silently transmitted to external servers when LLM-integrated browser extensions (Grammarly, ProWritingAid, Wordtune) are running during normal use.

**Student:** Marawan Eldeib · **Matrikelnummer:** 3764796 · **Deadline:** 2026-10-10

## Research question

> *How does user data exposure differ across LLM-integrated productivity tools during controlled use?*

Concretely: a user receives a confidential file, is told not to share it with AI tools, but has a writing-assistant browser extension running by default in the background. They paste content into a normal text field (email, doc, comment box). The extension silently transmits the content. We measure how much.

## What this repo contains

| Path | What |
|---|---|
| `docs/` | Methodology, capture protocol, setup guide, metrics, professor Q&A |
| `input-data/` | Synthetic test document with 12 planted identifiers, controlled test HTML page |
| `scripts/capture/` | mitmproxy addon that captures and scores outbound traffic |
| `scripts/analysis/` | Analyzer (per-tool stats, 95% CIs, sentence-leak count, comparison chart) |
| `skills/privacy-analysis-project/` | Project knowledge for Claude sessions (auto-loaded) |
| `Makefile` | One-line commands for the 18-run capture/analysis cycle |
| `data/raw/` | Capture outputs per tool (one folder per tool) |
| `results/` | Analyzer outputs: per-tool summaries, comparison table, chart PNG/SVG |

## Quick start

```bash
# 1. Install dependencies (Kali Linux)
sudo apt install -y python3-pip firefox-esr xclip xdotool jq make
pip3 install --break-system-packages mitmproxy brotli pyahocorasick matplotlib

# 2. Sanity check
make check

# 3. Set up Firefox profiles + mitmproxy cert (see docs/Setup-Guide.md)

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
4. **Sensitive token detection** — N of 12 planted tokens found.

Plus 95% confidence intervals on the mean exposure and a sentence-level leak count as a more interpretable secondary metric.

## Project status

Methodology and scripts locked at v3.1 after two critical reviews. Kali environment setup and data collection are the next steps. See `docs/Timeline.md` for milestones.

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
