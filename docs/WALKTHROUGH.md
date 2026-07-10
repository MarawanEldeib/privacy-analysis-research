# Project Walkthrough — Measuring Data Exposure in LLM-Integrated Productivity Tools

A complete, follow-along guide to what this project measures, how the measurement
works, and exactly how to reproduce it from a clean machine. Every step gives
copy-paste commands and direct, **verified** download links.

> **Audience:** the supervising professor, an examiner, or anyone who wants to
> re-run or verify the study. No prior familiarity with the codebase is assumed.

---

## 1. What the project shows (in one minute)

**Question:** when a writing-assistant browser extension is running in the
background, how much of a confidential document does it silently send to its own
servers — even if the user was told not to share that document with AI tools?

**Result:** two independent grammar-checker extensions each transmitted **~the
entire document and every planted secret**, automatically, the moment the
document was pasted — no button click required:

| Condition | Runs | Document transmitted | Planted secrets sent | Type |
|---|---|---|---|---|
| **Grammarly** | 5 | **99.0 %** | **12 / 12** (incl. canary) | automatic / background |
| **LanguageTool** | 5 | **91.9 %** | **12 / 12** (incl. canary) | automatic / background |
| **Baseline** (no extension) | 3 | **0.0 %** | 0 / 12 | control |

The only variable that changed between "99 %" and "0 %" is the presence of the
extension. The browser by itself transmits nothing.

---

## 2. The threat model

The scenario we measure — deliberately mundane, because that is the point:

> A user receives a confidential file and is told **not** to share it with AI
> tools. They have a writing-assistant extension installed and enabled (the
> default state for millions of users). They paste the document into an ordinary
> text field — an email reply, a web form, a notes box. Without any further
> action, the extension transmits the content to its servers for analysis.

We are **not** demonstrating an exploit. The tools are doing exactly what they
were designed to do. The research question is whether users understand the scope
of that default behaviour.

---

## 3. How the measurement works

The pipeline has five stages:

1. **Plant secrets.** The test document (`input-data/test-document.txt`) is a
   synthetic 2,065-character "confidential memo" containing **12 unique fictional
   identifiers** — names, an email, a phone number, reference codes, and a UUID
   **canary** (`CANARY-BC267061-…`). None of these strings exist anywhere on the
   internet, so any occurrence in captured traffic is unambiguously ours.
2. **Paste it.** The document is pasted (real Ctrl+V — see the note below) into a
   plain field on a local, noise-free HTML page (`input-data/test-page.html`),
   with exactly one tool's extension active.
3. **Intercept.** [mitmproxy](https://mitmproxy.org/) runs as an HTTPS proxy and
   decrypts the traffic leaving Firefox, using a CA certificate trusted only
   inside the test profile.
4. **Measure.** A mitmproxy add-on (`scripts/capture/capture_addon.py`) scans the
   outbound traffic for (a) sliding 20-character windows of the document and
   (b) each of the 12 planted secrets, and writes a per-run JSON summary.
5. **Compare.** `scripts/analysis/analyze.py` aggregates the runs (median/mean
   exposure, 95 % CI, reproducibility, secret counts) and compares each tool
   against a **no-extension baseline** to subtract ordinary browser background
   traffic.

**Metrics** (full definitions in [`docs/Metrics-Definition.md`](Metrics-Definition.md)):

- **Headline — secret count:** how many of the 12 planted identifiers reached the
  servers. The canary makes this unambiguous.
- **Supporting — exposure %:** fraction of the document's characters found in
  outbound traffic.
- **Reproducibility:** standard deviation of exposure % across 5 runs.
- **Traffic visibility:** share of intercepted events that were HTTPS, plus a
  count of TLS handshakes that could not be intercepted (e.g. certificate
  pinning) — reported as two separate numbers, never merged.

> **Why the paste is manual.** Automated paste (via `xdotool`) fills the box
> visually but does **not** fire the DOM input event the extensions listen for,
> so the tool never ingests the text and nothing is transmitted (a misleading
> "clean" 0 %). A genuine keystroke is what makes the tool receive the document,
> so every capture uses a real Ctrl+V.

---

## 4. Reproduce it from scratch

### 4.0 What you need

- A **Kali Linux** VM (any recent rolling release). A VM is used so the
  interception setup is isolated from your real browsing. See
  [`docs/ENVIRONMENT.md`](ENVIRONMENT.md) for the exact versions used.
- The tools tested need free accounts where noted (Grammarly requires login;
  LanguageTool does not).
- This repository, available inside the VM. In the original setup it lives on a
  Windows host and is shared into the VM at `/media/sf_privacy_analysis/`
  (a VirtualBox shared folder). Adjust paths to wherever you place it.

### 4.1 Install the dependencies

```bash
sudo apt update
sudo apt install -y python3-pip firefox-esr xclip xdotool jq make libnss3-tools
pip3 install --break-system-packages mitmproxy brotli pyahocorasick matplotlib
```

- `mitmproxy` — the intercepting proxy.
- `brotli`, `pyahocorasick` — used by the capture add-on (Brotli decoding, fast
  multi-pattern matching). Optional but recommended.
- `matplotlib` — only needed for `make chart`.
- `libnss3-tools` — provides `certutil`, used to trust the mitmproxy CA inside a
  Firefox profile from the command line.

Sanity check:

```bash
cd /media/sf_privacy_analysis      # or wherever the repo is
make check
```

### 4.2 Generate the mitmproxy CA certificate

Run mitmproxy once so it generates its CA into `~/.mitmproxy/`:

```bash
mitmdump --listen-host 127.0.0.1 --listen-port 8080
# wait for "HTTP(S) proxy listening at 127.0.0.1:8080", then Ctrl+C
ls ~/.mitmproxy/          # should list mitmproxy-ca-cert.pem
```

### 4.3 Create and configure a Firefox profile

Each tool gets its own isolated profile with the proxy set and the mitmproxy CA
trusted. This one-shot script creates and configures a profile (repeat for each
tool, changing the name). Close all Firefox windows first.

```bash
P=grammarly-test; DIR="$HOME/.mozilla/firefox/$P"
firefox -CreateProfile "$P $DIR"
cat > "$DIR/user.js" <<'EOF'
user_pref("network.proxy.type", 1);
user_pref("network.proxy.http", "127.0.0.1");
user_pref("network.proxy.http_port", 8080);
user_pref("network.proxy.ssl", "127.0.0.1");
user_pref("network.proxy.ssl_port", 8080);
user_pref("network.proxy.share_proxy_settings", true);
EOF
certutil -A -n mitmproxy -t "C,," -i "$HOME/.mitmproxy/mitmproxy-ca-cert.pem" -d "sql:$DIR"
echo "configured: $P"
```

Repeat with `P=languagetool-test` and `P=baseline-test` (baseline gets **no**
extension).

### 4.4 Install the tool's extension — use the VERIFIED official listing

> **Important:** browser stores contain clones that impersonate popular tools.
> During this study a fake "Wordtune" (publisher *Akajan Burno*, a scam support
> link) was found squatting the obvious slug. **Always confirm the publisher**
> before installing. The two tools in scope, verified:

| Tool | Official Firefox add-on | Publisher | Account? |
|---|---|---|---|
| **Grammarly** | `https://addons.mozilla.org/en-US/firefox/addon/grammarly-1/` | Grammarly, Inc. | Free account (sign in) |
| **LanguageTool** | `https://addons.mozilla.org/en-US/firefox/addon/languagetool/` | LanguageTooler GmbH | Not required |

Launch the profile, open the link, click **Add to Firefox**, and (for Grammarly)
sign in with a free account:

```bash
firefox -P grammarly-test --no-remote "https://addons.mozilla.org/en-US/firefox/addon/grammarly-1/" &
```

### 4.5 Verify interception (do this once per profile)

With `mitmdump` running, visit `https://example.com` in the profile. It must load
with **no certificate warning** and appear in the mitmproxy terminal. If you get
a cert warning, the CA import in 4.3 did not take. This check matters because a
broken interception looks identical to a genuine 0 % result.

### 4.6 Run a capture

Use **three terminals**:

**Terminal 1 — page server** (serves the test page on localhost):
```bash
cd /media/sf_privacy_analysis/input-data && python3 -m http.server 8000
```

**Terminal 2 — recorder** (the capture add-on; one run at a time, bump `RUN_ID`):
```bash
cd /media/sf_privacy_analysis
TOOL_NAME=grammarly RUN_ID=1 mitmdump --listen-host 127.0.0.1 --listen-port 8080 \
  --save-stream-file data/raw/grammarly/run_1.flow -s scripts/capture/capture_addon.py
```

**Terminal 3 — load the document into the clipboard, then open the page:**
```bash
xclip -selection clipboard < /media/sf_privacy_analysis/input-data/test-document.txt
firefox -P grammarly-test --no-remote "http://localhost:8000/test-page.html" &
```

Then, in Firefox: click the text box → **Ctrl+A, Backspace** to clear → **Ctrl+V**
to paste the document → wait ~60 s while the extension checks it (watch Terminal 2
for a `[! EXPOSURE]` line) → **Ctrl+C** the recorder.

Repeat for `RUN_ID=2 … 5`. (Alternatively, the `Makefile` wraps this:
`make page-grammarly` then `make grammarly-1`.)

### 4.7 Run the baseline

Same as 4.6 but with the `baseline-test` profile (no extension) and
`TOOL_NAME=baseline`, three runs. Expect **0 %** — that's the point of the
control, and it also proves interception isn't silently failing.

### 4.8 Analyze

```bash
# one tool, raw (no baseline subtraction)
python3 scripts/analysis/analyze.py languagetool --no-baseline

# everything, with baseline subtraction + comparison table
python3 scripts/analysis/analyze.py --all

# also write results/comparison_chart.{png,svg} for a report
python3 scripts/analysis/analyze.py --all --chart
```

Outputs land in `results/` (`<tool>_summary.json`, `comparison.json`, and the
chart). `Project-Dashboard.html` presents the same results as a browser page.

---

## 5. Reading the results

For each tool the analyzer reports, in order of importance:

- **`SECRETS TRANSMITTED: N/12`** — the headline. `12/12` including the canary
  means the whole confidential payload reached the servers.
- **Exposure %** with median, mean, 95 % CI, and reproducibility label.
- **HTTPS event share** and **TLS handshake failures** — how much of the traffic
  we could actually see (0 failures = nothing hidden by certificate pinning).
- **Per-token table** — which of the 12 secrets appeared, in how many runs.
- A plain-language **conclusion** sentence suitable for quoting in the report.

---

## 6. What we tested, and what we dropped (the honest trail)

Not every candidate tool fit the controlled Firefox method. Recording this is
part of the methodology, not a gap:

- **Grammarly** ✅ — genuine extension; automatic background transmitter (99 %).
- **LanguageTool** ✅ — genuine extension; automatic background transmitter
  (91.9 %); needs no account, which makes it the cleanest replication.
- **ProWritingAid** ✗ — genuine extension, but it did not attach to the
  controlled test field, so it produced no measurable transmission. Recorded as a
  limitation.
- **QuillBot** ✗ — has **no official Firefox extension** (Chrome-only). Cannot be
  tested under this Firefox-based method.
- **Wordtune** ✗ — the obvious Firefox listing was a **clone**; the genuine tool
  is **on-demand** (it transmits only when the user actively clicks "Rewrite"),
  so it does not leak passively in the background. Dropped from scope.

This yields a clean, defensible design: **two independent automatic grammar
checkers, both leaking, versus a control.**

---

## 7. Caveats & reproducibility notes

- **External services change.** The tested tools are cloud products whose server
  behaviour and extensions auto-update. The *pipeline* reproduces exactly; the
  *numbers* reflect tool behaviour at capture time (each run's JSON is
  timestamped). Expect the method to reproduce even if a specific percentage
  drifts.
- **Verify publishers.** See §4.4 — clones exist. Confirm the publisher before
  installing anything.
- **Interception can fail silently.** Always run the §4.5 verification; a broken
  MITM and a genuine 0 % look identical otherwise.
- **Synthetic data only.** No real personal data is captured. Some automated PII
  scanners may still flag the fictional content.
- For the exact software versions used, see
  [`docs/ENVIRONMENT.md`](ENVIRONMENT.md). For the locked capture protocol, see
  [`docs/Capture-Protocol.md`](Capture-Protocol.md).
