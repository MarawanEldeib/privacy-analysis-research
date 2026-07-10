# Project Walkthrough — Documentation Map

The walkthrough is split into three focused documents so you can read the one that
matches what you need. Start here, then jump:

| If you want to… | Read | What it is |
|---|---|---|
| **Run the whole study** from a clean machine | [`Reproduction-Guide.md`](Reproduction-Guide.md) | Step-by-step tutorial: exact commands, verified extension links, capture + analysis. |
| **Understand the project** — goal, method, findings, and the dead ends | [`Narrative-Walkthrough.md`](Narrative-Walkthrough.md) | The story as a documented case study (including the fake-Wordtune episode). |
| **Understand the code** — how capture and analysis work | [`Technical-Walkthrough.md`](Technical-Walkthrough.md) | "How it's built": the pipeline, the mitmproxy add-on, the analyzer, the metrics. |

### Supporting reference docs

- [`Capture-Protocol.md`](Capture-Protocol.md) — the locked per-run steps (identical across every run).
- [`Metrics-Definition.md`](Metrics-Definition.md) — exact formulas for exposure %, reproducibility, TLS visibility, secret detection.
- [`ENVIRONMENT.md`](ENVIRONMENT.md) — pinned software versions + how to lock your own environment.
- [`QA-Professor.md`](QA-Professor.md) — the decision log behind scope and methodology.

### The one-paragraph version

Two writing-assistant browser extensions (Grammarly, LanguageTool), running in the
background with no user action beyond pasting, each silently transmitted ~the whole
of a confidential test document — and all 12 planted secrets, including a unique
canary — to their servers. A no-extension baseline transmitted nothing. The method:
paste a synthetic 2,065-character memo into a noise-free page in an isolated Firefox
profile, intercept the HTTPS/WebSocket traffic with mitmproxy, and measure how much
of the document (and which planted identifiers) appears in outbound traffic, against
a subtracted baseline.
