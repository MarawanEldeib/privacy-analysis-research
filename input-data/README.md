# Input Data

## test-document.txt

A synthetic "confidential" document used as the controlled input for all experiments.

**Planted unique identifiers** (any of these appearing in captured traffic = confirmed exposure).
These are the canonical 12 tokens checked by `scripts/analysis/analyze.py` and listed in `docs/Metrics-Definition.md`. Token strings must match these exactly (case-insensitive).

| # | Token | Type |
|---|-------|------|
| 1 | Helena Voss | Fake person name |
| 2 | HV-2026-391847 | Fake employee ID |
| 3 | Theodora Baumgartner-Klein | Fake person name |
| 4 | theodora.baumgartner@priv-research-demo.invalid | Fake email |
| 5 | +49 30 4827-9153 | Fake phone number |
| 6 | Project Nighthawk-3 | Fake project codename |
| 7 | XREF-291-ALPHA | Fake document reference |
| 8 | NHK3-RES-7741 | Fake reserve fund code |
| 9 | AC-2026-00293-DELTA | Fake approval code |
| 10 | 2026-LGL-00847 | Fake contract ID (matched without the `#` prefix) |
| 11 | DE-291-847-3309 | Fake tax registration number |
| 12 | CANARY-BC267061-67DC-485B-8E51-6F5494765CAB | UUID canary (fully unique) |

**Why these work:** All identifiers are syntactically realistic but completely fictional.
None exist on the internet. Any match in captured traffic is unambiguously from our input.

**Note on the contract ID:** the test document contains `#2026-LGL-00847` (with `#`).
The analyzer searches for `2026-LGL-00847` (without `#`) so it still matches if a tool
strips the `#` during transmission. Both forms are still detectable.

**Do not modify this file** once experiments begin — all runs must use identical input.
If the test document is ever regenerated, update both `analyze.py::SENSITIVE_TOKENS` and
`docs/Metrics-Definition.md` so they stay in sync with this file.
