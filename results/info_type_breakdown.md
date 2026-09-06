# Level 1 — Information-type breakdown

What *kinds* of information each tool transmitted, grouped from the 12 planted secrets. A type is "exposed" if at least one of its items was seen in the tool's outbound traffic (in ≥1 of the runs).

## Exposure by information type

| Information type | Items | Grammarly | LanguageTool | Baseline |
|---|---|---|---|---|
| Names (direct identifiers) | 2 | 2/2 | 2/2 | 0/2 |
| Contact details | 2 | 2/2 | 2/2 | 0/2 |
| Official / ID numbers | 2 | 2/2 | 2/2 | 0/2 |
| Financial identifiers | 3 | 3/3 | 3/3 | 0/3 |
| Legal / contractual references | 1 | 1/1 | 1/1 | 0/1 |
| Confidential project identifiers | 1 | 1/1 | 1/1 | 0/1 |
| Canary proof-token | 1 | 1/1 | 1/1 | 0/1 |
| **All types (total)** | **12** | **12/12** | **12/12** | **0/12** |

## What is in each type

**Names (direct identifiers)**
- Author / compliance officer name — `Helena Voss`
- External legal counsel name — `Theodora Baumgartner-Klein`

**Contact details**
- Email address — `theodora.baumgartner@priv-research-demo.invalid`
- Phone number — `+49 30 4827-9153`

**Official / ID numbers**
- Employee ID — `HV-2026-391847`
- Tax registration number — `DE-291-847-3309`

**Financial identifiers**
- Q1 expenditure reference — `XREF-291-ALPHA`
- Reserve fund code — `NHK3-RES-7741`
- Budget approval code — `AC-2026-00293-DELTA`

**Legal / contractual references**
- Contract / matter number — `2026-LGL-00847`

**Confidential project identifiers**
- Project codename — `Project Nighthawk-3`

**Canary proof-token**
- Unique leak-proof marker — `CANARY-BC267061-67DC-485B-8E51-6F5494765CAB`

## Reading of the result

Both writing assistants transmitted **every** information type in the document — personal names, contact details, official ID numbers, financial codes, a legal contract reference, the confidential project codename, and the unique canary. The no-extension baseline transmitted none. The leak is therefore not limited to a particular class of data (e.g. only free text): structured identifiers and regulated personal data are exfiltrated just as readily as prose.
