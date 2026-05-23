# Interpreting the Analyzer's Output

Plain-language guide to what each number means and when to be suspicious.

## The conclusion statement (per tool)

After 5 runs of a tool, `make analyze` prints a paragraph like:

> "Grammarly transmitted approximately **30.5%** of the input document to external servers during default-configuration use (median across 5 runs, std dev **0.8pp**, mean **30.7%** 95% CI [**29.5%**, **31.9%**]). Reproducibility: **High**. At the sentence level, a median of **4** of **35** sentences leaked fully per run (**6** unique sentences across all runs). Of intercepted events, **100.0%** used HTTPS. **2** of 12 planted sensitive tokens were detected in traffic."

Read it left-to-right:

- **"approximately 30.5%"** — the median exposure across 5 runs. This is the headline number for the report.
- **"std dev 0.8pp"** — how spread out the 5 runs were. Small means consistent.
- **"mean 30.7% 95% CI [29.5%, 31.9%]"** — best estimate plus the range we're 95% confident the true mean lies in.
- **"Reproducibility: High"** — qualitative label based on std dev.
- **"median of 4 of 35 sentences leaked fully per run"** — easier-to-grasp version of the headline. Half the document's sentences were transmitted whole.
- **"6 unique sentences across all runs"** — worst-case across runs. If you union all sentences leaked in any of the 5 runs.
- **"100% used HTTPS"** — of what we saw. Doesn't account for cert-pinned connections we couldn't decrypt.
- **"2 of 12 planted sensitive tokens"** — the concrete privacy violation count.

## Reproducibility labels

Based on the std dev of exposure % across the 5 runs:

| Label | Std dev | Meaning |
|---|---|---|
| High | < 3pp | Tool's behaviour is consistent. Numbers are trustworthy. |
| Medium | 3-10pp | Some variance. Results are usable but explain the spread in the report. |
| Low | > 10pp | Tool is unstable across runs. Either the protocol drifted between runs, or the tool itself is non-deterministic. **Don't average without explaining why.** |

If Low: look at the gotchas first (cert issues across runs, paste timing variation), then consider that the tool genuinely doesn't behave the same way every time and report it.

## When CI overlap means something

The comparison table prints lines like:
> `grammarly vs prowritingaid    DISJOINT (clear difference)`
> `grammarly vs wordtune         overlap (no clear difference)`

- **DISJOINT** = the two tools' 95% CIs don't overlap. Strong informal evidence that they actually differ in exposure. You can say "Grammarly leaks notably more than ProWritingAid" with confidence.
- **overlap** = CIs overlap. The difference (if any) is too small to claim with statistical confidence. You can still report the medians side-by-side, but don't claim one is "significantly more" without a formal t-test.

This is a visual check, not a formal hypothesis test. If the professor specifically asks for "is the difference statistically significant?", we'd need to add a Welch's t-test on top.

## Strict vs lenient analysis comparison

`make analyze` uses strict defaults: 20-char window, 0.9 sentence threshold, baseline subtraction.
`make analyze-lenient` uses: 12-char window, 0.5 sentence threshold, no baseline subtraction.

**Use the comparison like this:**

- If both views give similar numbers → strict settings are not missing real leaks. Use strict for the report.
- If lenient finds way more than strict → strict may be too conservative. Look at the difference: is it noise (random text matching by chance) or real (fragments of the doc that strict's stricter rules dismissed)?
- If strict finds more than lenient → impossible. If you see this, there's a bug. (`--no-baseline` could explain it if baseline adds rather than subtracts — check.)

## Sentence-leak count is more meaningful than %

For the written report, often this:
> "4 of 35 sentences containing the test document leaked fully to Grammarly's servers, including the sentence stating Helena Voss's authority to sign expenditures."

...is more impactful than this:
> "30.5% of the document leaked."

When you can, lead with the sentence count + a named example, then back it with the % for completeness.

## Exposure pct nuances

- It's the **union** across all events in a run, then averaged across 5 runs. So if Run 1 leaked positions 0-200 and Run 2 leaked positions 200-400, each run individually shows ~10% but they're catching different parts of the doc.
- The metric counts each character position once even if it leaked multiple times. That's the right metric.
- "Exposure %" is character-level. "Sentence leak count" is sentence-level. Token detection is token-level. All three are reported because each illuminates something different.

## The 12 sensitive tokens

These are the strongest evidence in the report. Each is unique, fictional, and not findable on the internet. If any appears in captured traffic, that's an unambiguous privacy violation. Use them in the report:

> "Of the 12 planted sensitive identifiers — including Helena Voss's name, her fictional employee ID, her phone number, and a unique UUID canary — N appeared in Grammarly's captured traffic."

The UUID canary is the most diagnostic: if `CANARY-BC267061-67DC-485B-8E51-6F5494765CAB` appears anywhere, the leak is certain.

## When numbers don't add up — first thing to check

1. Are `data/raw/baseline/run_*.json` files present? If not, baseline subtraction does nothing.
2. Is the `[TLS-FAIL]` count > 0 in the .log files? Some traffic was opaque to us.
3. Did Grammarly's icon actually activate in the relevant profile? (Open the .log: are there any requests to `grammarly.com` domains?)
4. Did the paste actually land in the textarea? (Open the test page during the run and watch for the text appearing.)

When in doubt, open the `.flow` file in mitmweb to see exactly what bytes the browser sent.
