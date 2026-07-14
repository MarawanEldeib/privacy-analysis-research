# Related Work & Methods — Research Digest

A cited synthesis of prior research on how browser extensions (writing assistants
and AI assistants) transmit user data, and the tools/methods available to measure
it. Compiled to feed the report's **related-work** section and **methodology/tools**
discussion. Each claim is tied to a primary source; vendor/marketing material is
labelled and kept separate from independent evidence.

> **Confidence key:** ✅ verified against the primary paper/PDF · ⚠️ verify one
> detail before quoting · 🏷️ vendor/marketing or single-journalist claim — do not
> cite as independent measurement.

---

## Part A — What existing research says about how much these tools transmit

### A.1 Seminal extension-leakage measurement (2017–2018)

The canonical toolkit for measuring extension data exfiltration was established by
four papers, each using a different method. Consistent finding across all: a small
but non-trivial single-digit-% of extensions leak history/PII, and those extensions
collectively have tens-to-hundreds of millions of users.

**Starov & Nikiforakis, "Extended Tracking Powers," WWW 2017.** ✅
First large-scale study of extension privacy leakage. Dynamic analysis of the top
10,000 Chrome extensions with simulated browsing + a differential/mutation trick to
defeat obfuscation, plus string-search of known private values in outgoing requests.
Finding: **618 extensions (~6.3%)** leak browsing/search history; **430** leak
history accidentally via the HTTP `Referer` header to ~2 third parties each.

**Weissbacher et al., "Ex-Ray," ACSAC 2017.** ✅
Content-agnostic detection (catches leaks even when *encrypted/obfuscated*). Network
"counterfactual" analysis: vary the size of simulated history and use linear
regression to find extensions whose outbound traffic volume scales with it. Of
**10,691** extensions, flagged 212, **184 confirmed** history-leaking — including one
using strong encryption on its beacons and one exfiltrating over WebSockets.

**Aggarwal et al., "I Spy with My Little Eye," IEEE EuroS&P 2018.** ✅ (⚠️ one metric)
Analysed **all 43,521** Chrome Web Store extensions; after manual vetting of >1,000
candidates, identified **218 "spying" extensions** stealing history, OSN access
tokens, IP, and geolocation. Method: behavioural traces + an RNN over browser
API-call sequences (recall 93.31% ✅; paired precision ~90% ⚠️ — confirm on the PDF).

**Chen & Kapravelos, "Mystique," ACM CCS 2018.** ✅ (⚠️ venue)
*Note: CCS 2018, not USENIX — cite carefully.* Dynamic **taint tracking** built into
Chromium (taint sources = DOM + extension APIs; sinks = network), plus static
data/control-flow analysis. Largest scale of the era: **181,683 extensions**;
**3,868 (2.13%)** flagged as leaking privacy-sensitive info; the top-10 confirmed
leakers had **>60M** combined users.

### A.2 Recent large-scale studies — on-page *content* (2024)

The field moved from browsing metadata to the actual content on the page.

**Xie, Kasi Murali, Pearce & Li, "Arcanum," USENIX Security 2024.** ✅ — *closest
prior work on content exfiltration.*
Custom instrumented Chromium with **dynamic taint tracking** that can mark specific
DOM elements on real logged-in sites (Amazon, Facebook, Gmail, Instagram, LinkedIn,
Outlook, PayPal) and trace them to network sinks. Findings: **3,028 extensions
(2.68%)** automatically collect sensitive user data, aggregate install base **≈144
million users**; **202 extensions** exfiltrate actual **web-page content** (email
bodies, private social profiles, banking, professional networks). Over 58% of modern
extensions couldn't be analysed by older taint tools — motivating the new system.

**Nayak, Khandelwal, Fernandes & Fawaz, "Experimental Security Analysis of Sensitive
Data Access by Browser Extensions," ACM Web Conference (WWW) 2024.** ✅
Best fit for credential/field access. A PoC data-stealing extension **passed Chrome
Web Store review**; on the **top 10,000 login pages none of the password fields are
protected** from JavaScript; **~1,000 sites store passwords in plaintext in page
source** (incl. Google, Cloudflare). Of 160K+ extensions, **28K have permission to
access sensitive input fields** and **190 actually store password fields**.

### A.3 GenAI assistant audits — the "just viewing" leak (2025)

**Vekaria, Canino, Levitsky, Ciechonski, Callejo, Mandalari & Shafiq, "Big Help or
Big Brother? Auditing Tracking, Profiling and Personalization in Generative AI
Assistants," USENIX Security 2025** (UC Davis / UCL / Reggio Calabria). ✅ (⚠️ 10 vs 9)
*The single most relevant recent study, and the one whose method most resembles
ours.* Audited the ~10 most popular search/AI-assistant extensions (Monica, Sider,
ChatGPT for Google, Merlin, MaxAI, Perplexity, HARPA.AI, TinaMind, Copilot). Method:
**MITM TLS interception + decryption** of the traffic between assistant, first-party
servers, and third-party trackers, driven by a simulated browsing persona across
public and private (logged-in) sites.

Key findings (all ✅ from paper + two university press releases):
- Assistants transmit webpage content — "**often the full HTML DOM and sometimes the
  user's form inputs**" — to their first-party servers; all but one generate
  responses server-side (only one is fully client-side).
- **Merlin exfiltrated a Social Security Number** typed into an IRS web form.
- Collection continued on **health portals** (medical history, diagnoses) with no
  safeguards.
- **Merlin and TinaMind shared raw user queries + IP** with **Google Analytics**.
- **Merlin and Sider kept recording** even in private/authenticated spaces.
- Four (ChatGPT-for-Google, Copilot, Monica, Sider) profiled all five tested
  attributes (location, age, gender, wealth, interests); **Perplexity** did essentially
  no profiling.
- Authors argue some behaviour would violate **HIPAA** and **FERPA**.

⚠️ The paper says "10 most popular" while press names nine — confirm the tenth in the
paper's Table 1 before stating an exact roster.

### A.4 Writing assistants specifically — evidence + the gap you fill

**The 2018 Grammarly bug — cite precisely (it is NOT covert exfiltration). 🏷️/disclosure**
Tavis Ormandy (Google Project Zero), **Feb 2018**, found the Grammarly Chrome/Firefox
extension **exposed users' auth tokens to every website visited** (any site could log
into your Grammarly account with ~4 lines of JS), affecting **~22M** users. This is an
**account-access bug**, patched in ~3 days — *not* proof that Grammarly secretly
sends your text. Use it as context, not as your headline.

**Kolide behavioural analysis of Grammarly (independent, but a security vendor). ⚠️**
Hands-on macOS testing: text entered while the Grammarly widget is visible **is sent
to Grammarly's cloud**; the desktop app uses **Accessibility permissions** to capture
editable text in any foreground app and send it "without any further user
interaction," including **text written before Grammarly was running**; the
"sensitive-field" block is weak (a field labelled *Social Security Number* still
triggered it). Reproducible observations, but Kolide sells device-blocking, so note
the commercial angle.

**Vendor self-statements (confirm text is sent). 🏷️**
Grammarly, QuillBot, Wordtune, and ProWritingAid all state in their own policies that
typed/pasted text is transmitted to their servers for processing. **LanguageTool is
the notable exception** — it offers a genuine **self-hosted/offline** deployment, so
text need not leave the machine (relevant to why it, too, leaked in your test when run
in default cloud mode). LanguageTool + QuillBot are both now owned by **Learneo, Inc.**
(LanguageTool acquired Dec 2024).

**The research gap (your novelty).** No peer-reviewed study performs independent
**network-level measurement quantifying how much text these specific writing
assistants transmit.** Prior work measures the *category* (extensions, AI assistants)
or *capability* (permissions), or audits *AI assistants* (Vekaria). A controlled
mitmproxy + canary measurement of Grammarly/LanguageTool, reporting the *share* of a
document that leaves with per-secret proof, sits in an unfilled space.

---

## Part B — Tools and methods you could use or cite

| Method / tool | What it sees | What it can't see | Cost | Best for |
|---|---|---|---|---|
| **mitmproxy** (scriptable) | full decrypted bodies/headers/URLs on the wire | pinned TLS; in-browser-only flows | low | **your canary search** — cheapest definitive evidence |
| Burp / OWASP ZAP / Fiddler / Charles | same as mitmproxy (CA-injection) | same pinning limit | low–$$ | GUI-driven interception |
| **Taint tracking** — Arcanum (USENIX'24), Mystique (CCS'18) | in-browser data flows; *which* DOM field went where, even if encoded/encrypted; no marker needed | native/opaque code paths; huge build cost, Chromium-version-coupled | high | proving provenance at scale |
| **Static/sandbox** — DoubleX (CCS'21), Fakeium ('24), EmPoWeb (S&P'19) | code-level *potential* flows / capabilities across the whole Web Store | actual runtime volume / real exfiltration | low–med | breadth pre-filter |
| **Traffic/metadata** — Wireshark, tcpdump, TLS/JA3 fingerprinting | endpoints, sizes, timing, SNI, cert chains | the plaintext content itself | low | **fallback when pinned** — bounds volume, can't read text |
| **Mobile/desktop** — system proxy + **Frida**/Objection, emulator | plaintext after **defeating pinning** at runtime | requires root/instrumentation | med–high | extending your approach to pinned apps |

**Where your method sits.** For *unpinned* extension traffic (browser extensions
rarely pin — they ride the browser's normal stack), a **canary-token search over a
mitmproxy-decrypted feed is the single strongest evidentiary method**: when the unique
string appears in a POST body, the leak is undeniable. Its blind spots are (1)
certificate pinning (→ fall back to TLS-metadata bounding, or Frida on desktop/mobile)
and (2) leaks that are transformed/encoded so the raw canary doesn't survive (→ pair
with a taint tool like Arcanum, or a cheap static pre-filter like DoubleX/Fakeium).
Taint tracking sees *more* (in-browser provenance, no marker) but costs far more to
build and maintain; your approach trades that breadth for a cheap, reproducible,
tool-agnostic, and definitive per-secret proof.

---

## Verification flags (read before quoting)

- **Mystique = ACM CCS 2018**, not USENIX. ✅ corrected.
- **"I Spy" precision ~90%** — recall 93.31% is verified; confirm the exact precision
  figure on the PDF before quoting.
- **Starov "6.3% vs 618"** — both appear in the paper; the accidental/intentional
  sub-counts overlap and don't sum to 618. Quote the headline figures, not the sub-sums.
- **Vekaria "10 vs 9"** — paper says 10 analysed; press names 9. Confirm the tenth.
- **Do NOT cite as academic evidence:** LayerX "Enterprise Browser Extension Security
  Report 2025", Incogni's 2026 ranking, and The Register's "287 extensions" story —
  🏷️ vendor marketing / single-journalist claims.
- **Kolide** is a security vendor; its Grammarly observations are reproducible but note
  the commercial angle.

## Sources

- Starov & Nikiforakis, WWW 2017 — https://www.securitee.org/files/extendedtracking_www2017.pdf
- Weissbacher et al., Ex-Ray, ACSAC 2017 — https://mweissbacher.com/publications/acsac_exray.pdf
- Aggarwal et al., I Spy, EuroS&P 2018 — https://people.cs.vt.edu/vbimal/publications/spyingext-euroSP18.pdf
- Chen & Kapravelos, Mystique, CCS 2018 — https://www.kapravelos.com/publications/mystique-CCS18.pdf
- Xie et al., Arcanum, USENIX Security 2024 — https://www.usenix.org/conference/usenixsecurity24/presentation/xie-qinge
- Nayak et al., WWW 2024 — https://www.earlence.com/assets/papers/browsersec-www24.pdf
- Vekaria et al., Big Help or Big Brother?, USENIX Security 2025 — https://www.usenix.org/system/files/usenixsecurity25-vekaria.pdf
- Grammarly 2018 bug (Project Zero #1527) — https://bugs.chromium.org/p/project-zero/issues/detail?id=1527
- Kolide, "Is Grammarly a Keylogger?" — https://www.kolide.com/blog/is-grammarly-a-keylogger-what-can-you-do-about-it
- DoubleX, CCS 2021 — https://publications.cispa.saarland/3464/ · Fakeium — https://arxiv.org/abs/2410.20862 · EmPoWeb, S&P 2019 — https://arxiv.org/abs/1901.03397
- mitmproxy — https://docs.mitmproxy.org/ · Frida — https://frida.re/ · OWASP MASTG interception — https://mas.owasp.org/MASTG/techniques/generic/MASTG-TECH-0120/
