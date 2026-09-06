# Tooling Landscape — related tools & why we chose what we chose

A reference note for the **methodology** and **related-work** sections. It records the
open-source tools adjacent to this project: what each does, whether we use it, and
why our mitmproxy-based pipeline is the right fit. None of these would *replace* our
approach; some save setup time, some add depth, and some are good to *show* because
readers recognise them.

Last reviewed: 2026-09-05.

---

## What we use (and why)

### mitmproxy — our core capture tool *(in use)*
Interactive HTTPS/WebSocket proxy. Intercepts, inspects, and replays TLS-protected
traffic; scriptable in Python (our `capture_addon.py`). Chosen because it is
transparent, scriptable, reproducible, and standard in privacy-measurement research.

- **HAR export (use this):** mitmproxy can export captured flows to **HAR**
  (`File > Export` in mitmweb, or `mitmdump ... --set hardump=out.har` /
  `mitmdump -nr run.flow -w har:out.har` depending on version). HAR is a portable
  JSON format that other tools (Fluxzy, Proxyman, browser devtools, custom scripts)
  can re-open. Value for us: hand a single run to a second analyzer for a sanity
  check, or attach a HAR as a reproducible artifact without shipping the raw `.flow`
  (which must stay gitignored — it can hold decrypted auth tokens).

### Microsoft Presidio — Level 2 PII discovery *(planned)*
Open-source PII detector (patterns + a small NLP model). We use it in **Level 2** to
auto-discover *unplanted* personal data in decrypted traffic (names, emails, IBANs,
device/account IDs, telemetry) — beyond our 12 planted secrets. Output is statistical,
so it needs manual review of false positives/negatives. Best run after desktop/background
captures exist. Free; no external model key required. See task: *Level 2 — automatic
PII discovery (Presidio)*.

### Frida + Objection — desktop certificate-pinning bypass *(planned)*
For the desktop/system-level phase, pinned apps reject our proxy CA, breaking the
classic "install CA + intercept" method. **Frida** is a dynamic instrumentation
toolkit; **Objection** wraps Frida with ready-made SSL-pinning-bypass scripts.
Start from **Objection** rather than hand-writing Frida hooks — it saves real time.
Caveat: most published guides target mobile apps, so expect some adaptation for
desktop binaries. See task: *Desktop / system-level testing setup*.

### HTTP Toolkit — pretty viewer for screenshots *(adopted as a viewer)*
Open-source interception UI with a much nicer request/response view than mitmproxy's
terminal/mitmweb. We use it **as a display layer over our own captures**, not as a new
measurement: export an existing run to HAR (`scripts/capture/export_har.sh`), then
**Import** the HAR into HTTP Toolkit and screenshot the clean request/response view
(e.g. the document text visibly going to Grammarly's servers). Notes:
- **HAR import may require HTTP Toolkit Pro** (free tier intercepts live but appending
  an imported HAR is a Pro feature). Free alternative: do a quick *live* interception in
  HTTP Toolkit just for screenshots — its auto-CA setup makes that a 2-minute job.
- **Caption honestly:** "the same capture rendered in HTTP Toolkit." It is presentation,
  not independent corroboration (unlike Wireshark, which is a different layer).
- **Token hygiene:** the HAR holds decrypted auth tokens — keep it local (gitignored)
  and redact tokens in screenshots.
- Optional: HTTP Toolkit ships an MCP server (`httptoolkit-mcp`) that can be added to
  Claude Code to drive it programmatically.

### Wireshark — packet-level evidence & recognisable visuals *(planned, in use for figures)*
Deep packet analyzer, one level *below* HTTP. Even when a payload is encrypted or a
desktop app is pinned and we cannot decrypt it, Wireshark still shows **that** the app
opened connections and performed TLS handshakes to a tool's servers — useful fallback
evidence, and a clean way to visualise the paste-spike vs. background traffic at the
packet level. We also include Wireshark screenshots deliberately because it is one of
the most widely recognised tools in the field; showing it (even where it duplicates a
point mitmproxy already made) adds credibility and familiarity for readers. See task:
*Add Wireshark capture + screenshots*.

### Burp Suite (Community) — polished proxy GUI for screenshots *(adopted)*
Ships with Kali. Same job as mitmproxy (intercepting HTTPS) but with a clean GUI that
makes a leak obvious in a screenshot: the request to the tool's server with the document
text visible in the body. Use it as a *presentation* surface alongside mitmproxy, not a
second measurement. Community edition is free.

### mitmweb — mitmproxy's own web UI *(adopted)*
We already run mitmproxy; `mitmweb` gives it a browser-based UI (flow list + request
detail) that screenshots far better than the terminal. Zero extra install. Good for
quickly grabbing a clean image of a specific captured request.

### tcpdump — headless packet capture *(adopted)*
CLI packet capture (`tcpdump -i any -w run.pcap`). Use it for the background/idle and
desktop experiments where we just need to record that connections happened (and to what
hosts) without a GUI — e.g. leaving a tool running with no user action. Complements
Wireshark (which can open the resulting `.pcap`).

### SSLKEYLOGFILE → Wireshark — decrypt TLS *inside* Wireshark *(adopted)*
**What it is and why it matters:** normally Wireshark only sees *encrypted* bytes — it
can show that Firefox talked to `capi.grammarly.com` over TLS, but not what was said.
Our mitmproxy setup decrypts by sitting in the middle as a proxy with its own CA. The
`SSLKEYLOGFILE` technique is a *different, cleaner* way to see the plaintext: you set the
environment variable `SSLKEYLOGFILE=/path/keys.log` before launching Firefox, and Firefox
writes the per-session TLS keys to that file. Point Wireshark at that key log
(Preferences → Protocols → TLS → *(Pre)-Master-Secret log filename*) and Wireshark uses
the keys to **decrypt the capture itself** — no proxy, no injected CA, no man-in-the-middle.

**The difference it makes for us:**
- It's a *second, independent* way to prove the leak. mitmproxy proves it by intercepting;
  SSLKEYLOGFILE + Wireshark proves it by decrypting the browser's own real traffic with the
  browser's own keys. Two different methods reaching the same conclusion is much harder to
  dismiss than one.
- It removes the "maybe the proxy/CA changed the tool's behaviour" objection entirely,
  because nothing is in the middle — you're watching Firefox's genuine, unaltered TLS
  session and just decrypting it after the fact.
- It produces a very credible Wireshark screenshot: the actual decrypted HTTP/2 request
  carrying the document, in the tool the field expects.
Caveat: it only works for apps that honour `SSLKEYLOGFILE` (Firefox/Chrome and anything
using their TLS libraries do; many native desktop apps do **not** — those still need
mitmproxy + Frida). Keep the key log local; it can decrypt the captured traffic.

---

## Considered / good to cite (not adopted)

### OpenWPM — the reference web-privacy measurement framework
Firefox + Selenium framework built to crawl thousands to millions of sites for privacy
studies; the framework most of our related-work papers build on. We deliberately did
**not** use it: our question is targeted depth (does *this* tool leak *this* document,
proven byte-for-byte) rather than large-scale breadth. Naming OpenWPM and explaining
that trade-off *strengthens* our methodology section.

### Privacy Pioneer (privacy-tech-lab)
A browser extension + companion crawler that detects data collection/sharing in web
traffic — same spirit as our work, at crawl scale. Good to cite and contrast.

### Postman / Insomnia — NOT applicable
These are **API request *builders*** — you hand-craft a request and send it to see the
response. They do **not** passively capture what a browser extension or desktop app
sends on its own, which is the entire point of this project. (Postman has a limited
"capture" proxy add-on, but it is far weaker than mitmproxy/Wireshark for this.) Skip
both — they solve a different problem.

### ProxyKit
Commercial-ish proxy that can flag PII with plain-English rules, but needs your own
model key. Presidio does the equivalent for free, so we use Presidio instead.

---

## One-line summary for the report
> We use **mitmproxy** for scriptable, reproducible HTTPS/WebSocket capture (with **HAR
> export** for interchange), **Wireshark** for packet-level corroboration and recognisable
> figures, **Presidio** for automatic PII discovery beyond our planted secrets, and
> **Frida/Objection** to reach pinned desktop apps. We cite **OpenWPM** and **Privacy
> Pioneer** as the large-scale-crawl alternatives whose breadth-vs-depth trade-off our
> targeted design deliberately inverts.

## Sources
- OpenWPM — https://github.com/openwpm/OpenWPM
- Privacy Pioneer — https://github.com/privacy-tech-lab/privacy-pioneer
- HTTP Toolkit — https://httptoolkit.com/
- mitmproxy — https://www.mitmproxy.org/
- Microsoft Presidio — https://github.com/microsoft/presidio
- Frida — https://frida.re/ · Objection — https://github.com/sensepost/objection
- Wireshark — https://www.wireshark.org/
