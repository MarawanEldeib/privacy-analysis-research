# Professor Update Email — May 2026

**To:** [Professor's email]
**Subject:** Project Update — Measuring Data Exposure in LLM-Integrated Productivity Tools

---

Dear Professor [Name],

I want to apologise for not sending updates at the two-week intervals we agreed.
I underestimated how much time the planning and methodology phase would take,
and I should have communicated earlier instead of waiting until everything was
fully ready. From this point forward I will send an update every two weeks
regardless of whether I have new results, so you always know where the project
stands.

Here is where things are:

**What has been completed**

The methodology and experimental design are now defined. I have finalised the
three tools to test: Grammarly, ProWritingAid, and Wordtune. All three are
browser extensions running in Firefox under mitmproxy interception, which keeps
the capture protocol identical across tools. I originally planned to include
GitHub Copilot but dropped it because it runs inside VS Code and does not
reliably honour the Firefox system proxy — mixing it with the browser-based
tools would have broken the "same capture protocol for all tools" requirement.

The framing of the research question has also been sharpened. Rather than
calling it "passive" exposure, I now describe it as **default-configuration
exposure during routine writing**: the tool is installed and active in its
default state, the user types the test document into a normal text field, and
I measure what is transmitted. This is more accurate — the tool is doing
exactly what it was designed to do — and the underlying question is how much
of that transmission is something the user may not be aware of.

I have created a synthetic confidential test document containing twelve planted
unique identifiers (fake names, employee IDs, contact details, project codes,
and a UUID canary). None of these strings exist outside this project, so any
match found in captured traffic is unambiguously from our input.

I have written the mitmproxy capture addon (handling HTTP requests, HTTP
responses, and WebSocket frames, with gzip/deflate/brotli decompression and
URL/JSON encoding variants) and a separate Python analysis script that computes
the metrics described below. The setup guide for Kali Linux is complete and I
am beginning the environment setup this week.

**How I am measuring exposure**

Three measurements per tool, reported separately rather than collapsed into one
number:

- **Exposure %** — the fraction of the test document's characters whose
  20-character context window appears anywhere in decrypted outbound traffic,
  after subtracting domains seen in a no-tool baseline run.
- **Reproducibility** — the standard deviation of exposure % across the 5
  repeated runs. Reported as a number (pp) and a qualitative label.
- **Traffic visibility** — the fraction of outbound bytes mitmproxy could
  actually decrypt. Reported as a separate coverage metric, not multiplied
  into a single "confidence" number.

Additionally, I check each of the twelve planted sensitive tokens individually:
the report will state how many of them appeared in captured traffic across
the 5 runs.

I changed away from a single multiplicative "confidence %" because combining
reproducibility (a property of the measurement) with TLS visibility (a property
of the instrumentation) into one number obscures what is being claimed. Keeping
them separate makes the limitations of each result legible.

**What I would value your feedback on**

1. Is the 20-character sliding window the right granularity for exposure, or
   would you prefer a coarser unit (sentence-level matching, or weighting by
   data type)?
2. Is reporting reproducibility as a standard deviation sufficient, or do you
   want a formal statistical test (e.g. confidence intervals from a small
   number of trials)?
3. Are there interim submission deadlines I should plan around before
   October 10?

I am happy to send the methodology document and metric definitions in full
ahead of our next meeting if that would be useful.

**Next step**

I am completing the Kali + mitmproxy environment this week and aim to have
the first Grammarly proof-of-concept capture ready by [DATE]. I will send
the next update with that result, regardless of outcome.

Thank you again for your patience.

Best regards,
Marawan Eldeib
Matrikelnummer: 3764796
