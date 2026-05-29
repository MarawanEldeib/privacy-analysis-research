# Metric Definitions — Data Exposure Study (v2)

**Status:** Draft — confirm with professor at next meeting  
**Last updated:** 2026-05-23  
**Changes from v1:** Removed multiplicative confidence formula; added baseline subtraction; fixed reproducibility metric; added sensitive token detection.

---

## 1. Exposure Percentage

**Definition:** The fraction of the input document's characters whose 20-character context window appears anywhere in outbound network traffic during one experiment run, after removing domains that also appear in the baseline (tool-disabled) run.

**Formula:**
```
Exposure % = |union of all covered positions across all captured events| / total input chars × 100
```

Where a "covered position" is any character index i in the test document such that the 20-character window starting at i appears as a substring in any captured and decrypted outbound payload (HTTP request body, HTTP response body, or WebSocket client message).

**Baseline subtraction:** Before computing exposure, any network events destined for domains that also appeared in the baseline (no-tool) run are removed. This filters out background browser traffic.

**Encoding variants searched:** plain text, URL-decoded, JSON-string-unescaped. If a tool URL-encodes or JSON-escapes the document before sending, matches are still detected.

**What counts as a "captured payload":**
- HTTP request bodies (decompressed from gzip/deflate/brotli if needed)
- HTTP response bodies (tools may echo content back)
- WebSocket client→server frames (critical for tools like Grammarly that use WS)

---

## 2. Reproducibility

**Definition:** The standard deviation of exposure % across the 5 repeated runs for a tool.

**Interpretation:**
- Std dev < 3 pp → High reproducibility (results are consistent)
- Std dev 3–10 pp → Medium reproducibility
- Std dev > 10 pp → Low reproducibility (results are unstable)

**Why not a single "reproducibility %" number:** Collapsing stdev into a percentage would require an arbitrary normalisation constant. Reporting stdev directly is more transparent and interpretable.

---

## 3. Traffic Visibility — reported as TWO numbers

Earlier drafts used a single "TLS-intercepted bytes / total bytes" formula.
This was silently broken: cert-pinned connections never reach mitmproxy's
request hook at all, so they're absent from both numerator and denominator,
and the metric could read 100% even when meaningful traffic was being missed.

The honest framing uses two numbers, reported separately:

```
https_event_pct       = HTTPS events seen / total events seen × 100
tls_handshake_failures = count of TLS handshakes mitmproxy could NOT complete
```

- `https_event_pct` describes the events we did see — what share were encrypted.
- `tls_handshake_failures` counts connections where the client (browser or
  extension) refused our MITM certificate. Each failure is a connection whose
  contents we cannot inspect. If this number is non-zero, the exposure result
  is a lower bound, not the full picture.

**Why reported separately, not multiplied with reproducibility:** Reproducibility
is a statistical property of the measurement; visibility is a coverage property
of the instrumentation. Multiplying them into a single number conflates two
different kinds of uncertainty and produces a figure with no clear interpretation.

---

## 4. Sensitive Token Detection

**Definition:** A binary check for each of the 12 planted identifiers in the test document. A token is "detected" if it appears verbatim (case-insensitive) in any captured payload across any of the 5 runs.

**Token list (12 tokens — canonical; kept in sync with `analyze.py::SENSITIVE_TOKENS` and `input-data/README.md`):**

| # | Token | Type |
|---|-------|------|
| 1 | Helena Voss | Fake person name |
| 2 | HV-2026-391847 | Fake employee ID |
| 3 | Theodora Baumgartner-Klein | Fake person name |
| 4 | theodora.baumgartner@priv-research-demo.invalid | Fake email |
| 5 | +49 30 4827-9153 | Fake phone number |
| 6 | Project Nighthawk-3 | Fake project codename |
| 7 | XREF-291-ALPHA | Fake document reference |
| 8 | NHK3-RES-7741 | Fake fund code |
| 9 | AC-2026-00293-DELTA | Fake approval code |
| 10 | 2026-LGL-00847 | Fake contract ID (matched without `#` prefix) |
| 11 | DE-291-847-3309 | Fake tax registration number |
| 12 | CANARY-BC267061-67DC-485B-8E51-6F5494765CAB | UUID canary (fully unique) |

**Why this matters:** Exposure % captures what fraction of the document was transmitted. Sensitive token detection answers whether the *specifically sensitive* parts (names, IDs, contact details) were transmitted — which is the question users actually care about.

---

## 5. Sentence-Level Exposure (secondary, easier to interpret)

The exposure % above is character-level. As a more interpretable supplementary
metric, we also report **how many full sentences were leaked**.

The test document is parsed into "sentence-like" units (≥ 25 characters, split
at `. ! ?` or hard line breaks). A sentence is considered **fully leaked** in
a run if at least 90% of its character positions appear in covered_positions
(the 10% slack accounts for the 19 final characters of every sentence whose
20-char window extends past the sentence end into trailing punctuation).

Reported per tool:

- `sentences_leaked_per_run`: list of N integers (one per run).
- `median_sentences_leaked`: median across the 5 runs.
- `unique_sentences_leaked_any_run`: the worst-case observed — every distinct
  sentence that leaked in *any* of the 5 runs.

This gives the report a sentence like:
> "A median of 4 of 35 sentences leaked fully per run; 7 unique sentences
> leaked across all runs combined."

Easier for a reader to interpret than "32.4% of characters leaked".

---

## 6. Confidence Intervals on Exposure

In addition to mean / median / std dev, we report a **95% confidence interval
on the mean exposure** using a t-distribution with n-1 degrees of freedom.

For n=5 runs (df=4) the t-critical for a two-sided 95% interval is 2.776.
We do not depend on scipy — a hardcoded t-table covers df = 1..30 conservatively.

```
CI = mean ± t_critical × (stdev / √n)
```

We use the CI for two things:

1. **Per-tool report** — "Grammarly mean 30.5% (95% CI [28.9%, 32.1%])".
2. **Pairwise comparison** — if two tools' CIs do not overlap, that is
   evidence (informal) of a real difference between them.

For a more formal claim like "Tool A leaks significantly more than Tool B",
a Welch's t-test would be appropriate; we have not implemented this yet
because it depends on a question to the professor about how formal the
statistical claims need to be (Q12 in QA-Professor.md).

---

## 7. Per-Tool Result Statement Format

> "[Tool name] transmitted approximately **X%** of the input document to external servers
> during default-configuration use (median across 5 runs, std dev **Y pp**,
> mean **X̄%** 95% CI [**lo%**, **hi%**]).
> Reproducibility: **[High/Medium/Low]**.
> At the sentence level, a median of **N** of **35** sentences leaked fully
> per run (**U** unique sentences across all runs).
> Of intercepted events, **Z%** used HTTPS; **F** TLS handshakes could not
> be intercepted (cert pinning).
> **K/12** planted sensitive tokens were detected in captured traffic."

---

## 8. Open questions for professor

- Is the combination of 20-char window + sentence-level + sensitive-token detection
  sufficient, or do you want a different granularity?
- Should sensitive tokens be weighted differently (e.g., email > plain text > code reference)?
- Is reporting mean + std dev + 95% CI sufficient, or do you want a formal
  pairwise statistical test (e.g., Welch's t-test between tools)?

---

*To be confirmed with professor before finalising analysis scripts.*
