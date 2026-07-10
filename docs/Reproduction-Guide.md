# Reproduction Guide — Run the Whole Study From Scratch

A complete, do-exactly-this tutorial. If you follow every step in order on a
clean machine, you will end up with the same captures, the same summaries, and
the same headline result the study reports. No prior familiarity with the code
is assumed.

**What you'll produce:** five Grammarly runs, five LanguageTool runs, and three
no-extension baseline runs, then an analysis showing that both extensions
silently transmit the test document (Grammarly ~99 %, LanguageTool ~92 %, all 12
planted secrets) while the baseline transmits nothing.

**Time:** ~30 min setup + ~20 min per tool of capture. Related docs: the exact
per-run steps are also locked in [`Capture-Protocol.md`](Capture-Protocol.md);
exact versions are in [`ENVIRONMENT.md`](ENVIRONMENT.md); metric definitions are
in [`Metrics-Definition.md`](Metrics-Definition.md).

---

## Step 0 — Machine and repository

Use a **Kali Linux** VM so the HTTPS interception is isolated from your real
browsing. The repo can live on the VM directly or on a Windows host shared into
the VM. In the reference setup it lives on Windows at
`F:\Projects\Research Project - Privacy analysis\` and is mounted into Kali via a
VirtualBox shared folder at `/media/sf_privacy_analysis/`.

> If you use the shared-folder layout, keep one rule: **only the host runs git.**
> Kali only runs captures; the `.json`/`.flow` files it writes appear on the host
> instantly. This avoids shared-folder permission and line-ending problems.

For the rest of this guide, "the project directory" means wherever the repo is
inside Kali (e.g. `/media/sf_privacy_analysis/`). Start every terminal with:

```bash
cd /media/sf_privacy_analysis      # adjust to your path
```

---

## Step 1 — Install dependencies

```bash
sudo apt update
sudo apt install -y python3-pip firefox-esr xclip xdotool jq make libnss3-tools
pip3 install --break-system-packages "mitmproxy==12.2.3" "brotli~=1.1" \
    "pyahocorasick~=2.0" "matplotlib~=3.7"
```

What each is for: `firefox-esr` is the browser under test; `xclip` loads the
document into the clipboard; `jq` inspects capture JSON; `make` runs the capture
targets; `libnss3-tools` provides `certutil` (used to trust the proxy cert from
the command line); `mitmproxy` is the interceptor; `brotli`/`pyahocorasick`/
`matplotlib` are used by the capture add-on, the analyzer, and the chart.

Verify the toolchain:

```bash
make check          # prints OK / MISSING for each dependency
mitmdump --version  # expect: Mitmproxy: 12.2.3
```

---

## Step 2 — Generate the mitmproxy CA certificate

mitmproxy needs a certificate authority that your Firefox test profiles will
trust. Generate it by running mitmproxy once:

```bash
mitmdump --listen-host 127.0.0.1 --listen-port 8080
# wait for "HTTP(S) proxy listening at 127.0.0.1:8080"
# then press Ctrl+C
ls ~/.mitmproxy/    # confirm mitmproxy-ca-cert.pem exists
```

---

## Step 3 — Create one Firefox profile per condition

Each condition gets its own isolated profile with (a) the proxy pointed at
mitmproxy and (b) the mitmproxy CA trusted. This script does both from the
command line — run it three times, once per profile name. **Close all Firefox
windows first.**

```bash
for P in grammarly-test languagetool-test baseline-test; do
  DIR="$HOME/.mozilla/firefox/$P"
  firefox -CreateProfile "$P $DIR"
  cat > "$DIR/user.js" <<'EOF'
user_pref("network.proxy.type", 1);
user_pref("network.proxy.http", "127.0.0.1");
user_pref("network.proxy.http_port", 8080);
user_pref("network.proxy.ssl", "127.0.0.1");
user_pref("network.proxy.ssl_port", 8080);
user_pref("network.proxy.share_proxy_settings", true);
EOF
  certutil -A -n mitmproxy -t "C,," \
    -i "$HOME/.mitmproxy/mitmproxy-ca-cert.pem" -d "sql:$DIR"
  echo "configured: $P"
done
```

The `baseline-test` profile deliberately gets **no extension** — it is the
control that proves the browser alone transmits nothing.

---

## Step 4 — Install the extensions (VERIFIED official listings only)

> ⚠️ **Browser stores contain clones that impersonate popular tools.** During
> this study the obvious `/wordtune/` Firefox listing turned out to be a fake by
> publisher *"Akajan Burno"* with a scam support link. **Always confirm the
> publisher** on the add-on page before clicking Add.

| Tool | Official Firefox add-on | Publisher | Account |
|---|---|---|---|
| **Grammarly** | `https://addons.mozilla.org/en-US/firefox/addon/grammarly-1/` | Grammarly, Inc. | Free account, sign in |
| **LanguageTool** | `https://addons.mozilla.org/en-US/firefox/addon/languagetool/` | LanguageTooler GmbH | None needed |

Install Grammarly into its profile and sign in:

```bash
firefox -P grammarly-test --no-remote \
  "https://addons.mozilla.org/en-US/firefox/addon/grammarly-1/" &
# click "Add to Firefox", then sign in to a free Grammarly account
```

Install LanguageTool into its profile (no login required):

```bash
firefox -P languagetool-test --no-remote \
  "https://addons.mozilla.org/en-US/firefox/addon/languagetool/" &
# click "Add to Firefox"
```

Install nothing into `baseline-test`. Only ever one extension per profile.

---

## Step 5 — Verify interception (do this once per profile) ⚠️

This is the single most important check. **A broken MITM looks identical to a
genuine 0 % result**, so never collect data until interception is confirmed.

Start mitmproxy, then in the profile visit `https://example.com`:

```bash
mitmdump --listen-host 127.0.0.1 --listen-port 8080 &
firefox -P grammarly-test --no-remote "https://example.com" &
```

The page must load with **no certificate warning** and appear in the mitmproxy
terminal. A cert warning means the CA import in Step 3 did not take — redo it for
that profile. Repeat for each profile, then stop the background mitmproxy
(`kill %1` or `pkill -f mitmdump`).

---

## Step 6 — Run the captures

The `Makefile` wraps the per-run steps. Each run uses **three terminals**.

Terminal 1 — page server (leave running the whole session):

```bash
make page-grammarly     # serves the test page + opens the grammarly-test profile
```

In the Firefox window that opens, **click inside the text box** so the cursor is
blinking (the extension only reacts to a focused, edited field).

Terminal 2 — the recorder, one run at a time:

```bash
make grammarly-1        # loads the doc to the clipboard, starts recording, then pauses
```

When it pauses and prints `>>> PASTE NOW`, switch to Firefox and:

1. **Ctrl+A** then **Backspace** to empty the box.
2. **Ctrl+V** to paste the document — watch the text appear.
3. Return to Terminal 2 and press **Enter**.

> **Why paste manually?** An automated `xdotool` paste fills the box visually but
> does **not** fire the DOM input event the extension listens for, so nothing is
> transmitted and you get a misleading clean 0 %. A real Ctrl+V is what makes the
> tool ingest the text. (`AUTO=1` exists but is not recommended.)

The recorder waits ~60 s, stops, and prints a `SESSION COMPLETE` summary. Repeat
`make grammarly-2 … grammarly-5`, emptying the box between runs.

Then LanguageTool (five runs) and the baseline (three runs):

```bash
make page-languagetool ; make languagetool-1   # ... through languagetool-5
make page-baseline      ; make baseline-1       # ... through baseline-3
```

The baseline should report **0 %** — that is the point of the control, and it
doubles as proof that interception isn't silently failing.

---

## Step 7 — Analyze

```bash
make analyze            # all tools, baseline-subtracted, comparison table
make chart              # also writes results/comparison_chart.{png,svg}
```

Under the hood these call the analyzer directly, which you can also run per tool:

```bash
python3 scripts/analysis/analyze.py grammarly            # one tool
python3 scripts/analysis/analyze.py grammarly --no-baseline   # raw, no subtraction
python3 scripts/analysis/analyze.py --all --chart        # everything + chart
```

Outputs land in `results/` (`<tool>_summary.json`, `comparison.json`, the chart).
`Project-Dashboard.html` in the repo root shows the same results in a browser.

---

## Step 8 — Read the result

For each tool the analyzer prints, headline first:

- **`SECRETS TRANSMITTED: N/12`** — how many planted identifiers reached the
  servers. `12/12` including the `CANARY-…` token means the whole confidential
  payload left the machine.
- **Exposure %** with median, mean, 95 % CI, and a reproducibility label.
- **HTTPS event share** and **TLS handshake failures** (0 failures = nothing
  hidden by certificate pinning).
- A per-token table and a plain-language conclusion sentence.

Expected shape of the finding: Grammarly ~99 % / 12 of 12, LanguageTool ~92 % /
12 of 12, baseline 0 % / 0.

---

## Troubleshooting

| Symptom | Cause / fix |
|---|---|
| HTTPS shows a cert warning | CA not trusted in that profile — redo Step 3 for it |
| mitmproxy terminal shows no traffic | Profile's proxy prefs didn't apply — confirm `user.js` in the profile dir |
| Capture prints 0 % for a real tool | The paste didn't register an input event — clear the box and do a real **Ctrl+V**, and confirm the extension icon is active |
| `Address already in use` on :8080 or :8000 | A previous proxy/server is still running — `pkill -f mitmdump` / `pkill -f http.server` |
| `[TLS-FAIL]` lines in the log | Some connections used certificate pinning; their contents are unknown, so exposure is a lower bound |
| Inspect what actually happened | `jq '.summary' data/raw/grammarly/run_1.json`, or open the raw flow: `mitmweb -nr data/raw/grammarly/run_1.flow` |

---

## Appendix A — VirtualBox shared-folder setup (optional)

If you run the reference layout (repo on a Windows host, shared into a Kali VM),
set the share up once so the `.json`/`.flow` files Kali writes appear on Windows
instantly.

In VirtualBox Manager on Windows (VM shut down): select the Kali VM → **Settings →
Shared Folders → +**. Set Folder Path to the repo folder
(`F:\Projects\Research Project - Privacy analysis`), Folder Name to
`privacy_analysis` (no spaces), check **Auto-mount** and **Make Permanent**, click
OK, start the VM.

Then inside Kali, once:

```bash
lsmod | grep vboxsf                       # confirm Guest Additions are loaded
# if empty: sudo apt install -y virtualbox-guest-x11 && sudo reboot
sudo usermod -aG vboxsf $USER             # then log out and back in
ls -la /media/sf_privacy_analysis/        # should list README.md, Makefile, docs/, ...
ln -s /media/sf_privacy_analysis ~/privacy-analysis   # optional convenience symlink
```

Keep the discipline from Step 0: **only the Windows host runs git**; Kali only runs
captures. A `.gitattributes` in the repo forces LF line endings on `*.sh`,
`Makefile`, and `*.py` so host-side git doesn't corrupt scripts Kali executes.

## Appendix B — Inspecting a capture with jq

When a run looks off, `jq` queries the JSON without scrolling:

```bash
# every host contacted during a run
jq '.requests[].host' data/raw/grammarly/run_1.json | sort -u

# only events that carried a planted secret
jq '.requests[] | select(.tokens_found | length > 0)' data/raw/grammarly/run_1.json

# just the summary block (exposure %, token count, TLS visibility)
jq '.summary' data/raw/grammarly/run_1.json
```

To replay the full raw traffic of a run, open its `.flow` archive in mitmweb:

```bash
mitmweb -nr data/raw/grammarly/run_1.flow
```

---

*This guide reflects the final method (manual Ctrl+V; Grammarly + LanguageTool +
baseline) and supersedes the older `Setup-Guide.md`. For the story of how the
method got here, see [`Narrative-Walkthrough.md`](Narrative-Walkthrough.md); for
how the code works, see [`Technical-Walkthrough.md`](Technical-Walkthrough.md).*
