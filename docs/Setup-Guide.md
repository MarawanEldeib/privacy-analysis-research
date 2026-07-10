# Setup Guide — Kali Linux + Firefox + mitmproxy

Follow these steps **in order** on your Kali Linux machine.
Do this once — then you're ready to run experiments.

The locked capture protocol that you'll follow per run is documented in
`docs/Capture-Protocol.md`. This guide is just about getting the machine
ready to follow it.

---

## Step 0 — Folder topology (one folder, multiple views)

The project files live in **one** location on Windows and are mounted into Kali
via a VirtualBox shared folder. There is no second copy of the folder.

| Where | Path | What you do there |
|---|---|---|
| Windows | `F:\Research Project - Privacy analysis\` | Edit code/docs, run git, push to GitHub, view results, write the report. |
| Kali (shared mount) | `/media/sf_privacy_analysis/` | Run captures. JSON/.flow files written here are instantly visible on Windows. |
| GitHub (private) | repo URL | Off-site backup + sharing with the professor. Updated when you `git push` from Windows. |

**Rules of the road:**

- **Only Windows runs git.** Kali does not touch git, ever. This avoids vboxsf permission/line-ending headaches.
- `.gitattributes` in the repo root forces LF line endings on `*.sh`, Makefile, and `*.py`, so Windows-side git doesn't corrupt them for Kali execution.
- The captures that Kali writes (`.json`, `.flow`) appear on Windows immediately. After each meaningful chunk of work, commit + push from Windows.

### One-time shared-folder setup

In VirtualBox Manager on Windows (Kali VM shut down):

1. Select the Kali VM → **Settings** → **Shared Folders** → click **+**.
2. Folder Path: `F:\Research Project - Privacy analysis`
3. Folder Name: `privacy_analysis` (no spaces).
4. Check **Auto-mount** and **Make Permanent**.
5. Click OK. Start the VM.

Inside Kali (one time):

```bash
# Verify VirtualBox Guest Additions are loaded
lsmod | grep vboxsf
# If empty: sudo apt install -y virtualbox-guest-x11 && sudo reboot

# Add yourself to the vboxsf group (then log out and back in)
sudo usermod -aG vboxsf $USER

# Verify the mount appears
ls -la /media/sf_privacy_analysis/
# Should show: README.md, Makefile, docs/, scripts/, etc.

# Optional: convenience symlink in your home directory
ln -s /media/sf_privacy_analysis ~/privacy-analysis
```

For the rest of this guide, any reference to "the project directory" means
`/media/sf_privacy_analysis/` (or `~/privacy-analysis/` if you made the symlink).

---

## Step 1 — Install dependencies

Open a terminal on Kali and run:

```bash
# Update package list
sudo apt update

# System packages: Firefox, clipboard helper, keystroke simulator, JSON tool, make
sudo apt install -y python3-pip firefox-esr xclip xdotool jq make

# Python packages: mitmproxy + optional speed-ups + matplotlib for the final chart
pip3 install --break-system-packages mitmproxy brotli pyahocorasick matplotlib

# Verify
mitmdump --version
xclip -version
xdotool --version
jq --version
make --version | head -1
python3 -c "import matplotlib; print('matplotlib', matplotlib.__version__)"
```

You should see something like `Mitmproxy: 10.x.x`. `xclip` and `xdotool` are
what the capture protocol uses to load the test document and trigger a paste.

---

## Step 2 — Install the mitmproxy CA certificate in Firefox

This is what allows mitmproxy to decrypt HTTPS traffic.

**2a.** Start mitmproxy in the background:
```bash
mitmproxy --listen-host 127.0.0.1 --listen-port 8080 &
```

**2b.** Open Firefox. Go to **Preferences → Network Settings** and set:
- Manual proxy: `127.0.0.1`, port `8080`
- Check "Use this proxy server for all protocols"
- Click OK

**2c.** In Firefox, navigate to: `http://mitm.it`

You'll see the mitmproxy certificate download page.
Click **Firefox** → download the `.cer` file.

**2d.** In Firefox, go to **Preferences → Privacy & Security → Certificates → View Certificates → Authorities → Import**.
Import the `.cer` file you just downloaded.
Check both: "Trust this CA to identify websites" and "Trust this CA to identify email users".
Click OK.

**2e.** Test it — navigate to `https://example.com` in Firefox.
If the page loads and you see traffic in mitmproxy, the certificate is working.

**2f.** Stop the background mitmproxy (`fg` then Ctrl+C, or `kill %1`).

---

## Step 3 — Create a clean Firefox profile for each tool

We need a separate profile per tool so extensions don't interfere with each other.

```bash
# Open Firefox profile manager
firefox -ProfileManager &
```

In the profile manager, create these profiles:
- `grammarly-test`
- `prowritingaid-test`
- `wordtune-test`
- `baseline-test`

For **each** profile:
1. Open Firefox with that profile
2. Configure the proxy again (Step 2b) — each profile has separate settings
3. Verify the mitmproxy CA cert is trusted (go to `https://example.com`)

```bash
# Open Firefox with a specific profile
firefox -P grammarly-test --no-remote &
```

---

## Step 3b — Verify interception before installing any extension ⚠️

**Do this for each profile before installing any tool.**

With mitmproxy running and the profile's proxy configured:
1. Visit `https://api.grammarly.com` (or any HTTPS site) — it should load without a cert error
2. In the mitmproxy terminal you should see the request appear
3. If you get a cert warning, the CA is not properly installed — repeat Step 2c–2d

**Do not start data collection if interception is not verified.** A failed MITM will silently produce 0% exposure (false negative), not an error.

---

## Step 4 — Install the writing-assistant extensions

Each extension goes into its dedicated profile only. Never install more than one extension per profile.

**4a. Grammarly** (in `grammarly-test` profile):
1. Open Firefox with the `grammarly-test` profile.
2. Visit `https://addons.mozilla.org/en-US/firefox/addon/grammarly-1/`.
3. Click **Add to Firefox**.
4. Sign in to Grammarly (free account is fine).
5. Confirm the Grammarly icon is visible and the extension is enabled.

**4b. ProWritingAid** (in `prowritingaid-test` profile):
1. Open Firefox with the `prowritingaid-test` profile.
2. Visit `https://addons.mozilla.org/en-US/firefox/addon/prowritingaid/`.
3. Click **Add to Firefox**.
4. Sign in to a free ProWritingAid account.
5. Confirm the extension icon is visible.

**4c. Wordtune** (in `wordtune-test` profile):
1. Open Firefox with the `wordtune-test` profile.
2. Visit `https://addons.mozilla.org/en-US/firefox/addon/wordtune-ai-writing-assistant/`  (official, by AI21 Labs — NOT the `/wordtune/` clone).
3. Click **Add to Firefox**.
4. Sign in to a free Wordtune account.
5. Confirm the extension icon is visible.

**4d. baseline-test profile:** install nothing. This is the no-tool control.

In all four profiles: **disable Firefox's own spellcheck** for the test if you want
the cleanest signal (Preferences → General → Language → uncheck "Check your spelling").
Recommended but optional.

---

## Step 5 — Verify the project scripts are ready

```bash
cd "/path/to/Research Project - Privacy analysis"

# Make the run script executable
chmod +x scripts/capture/run_capture.sh

# Check Python dependencies (mitmproxy must be importable)
python3 -c "import mitmproxy; print('mitmproxy OK')"
python3 -c "import ahocorasick; print('Aho-Corasick OK (fast window scan)')" 2>/dev/null \
    || echo "Note: pyahocorasick not installed — addon will use slow path"
python3 -c "import brotli; print('brotli OK')" 2>/dev/null \
    || echo "Note: brotli not installed — addon may miss brotli-compressed traffic"
```

---

## Step 6 — Run your first test capture (Grammarly, Run 1)

This is the proof-of-concept capture. Follow `docs/Capture-Protocol.md` exactly.

In short:

**6a.** In one terminal, open Firefox with the `grammarly-test` profile:
```bash
firefox -P grammarly-test --no-remote &
```
Wait ~10 seconds for Firefox to settle.

**6b.** Open the test page in Firefox via the address bar:
```
file:///absolute/path/to/Research%20Project%20-%20Privacy%20analysis/input-data/test-page.html
```
Click into the textarea so it has keyboard focus.

**6c.** In a second terminal, start the capture:
```bash
cd "/path/to/Research Project - Privacy analysis"
./scripts/capture/run_capture.sh grammarly 1
```
Press ENTER when prompted.

**6d.** In a third terminal, load the test document into the clipboard and paste it
into the focused Firefox window:
```bash
xclip -selection clipboard < input-data/test-document.txt
xdotool key --window "$(xdotool search --name 'Mozilla Firefox' | head -1)" ctrl+v
```

**6e.** Wait 60 seconds without touching anything. Grammarly should be processing.

**6f.** Press **q** in the mitmproxy terminal to stop the capture.

**6g.** Check the output — you should see `[⚠ EXPOSURE]` lines if Grammarly sent any
of the test document content.

---

## Step 7 — Check your results

```bash
# Look at the saved capture
less data/raw/grammarly/run_1.json

# Run the analysis (single tool, even with only 1 run for sanity check)
python3 scripts/analysis/analyze.py grammarly --no-baseline
```

If you see `exposure_pct > 0` and `tokens_found` non-empty, the setup is working.
If you see zero exposure, before concluding "no leak":
1. Did `[TLS-FAIL]` lines appear? Those are connections you couldn't decrypt.
2. Did Grammarly's icon actually activate on the test page? (Look at the icon.)
3. Was the textarea focused before the paste?
4. Look at the `.flow` file in mitmweb to see what really happened:
   ```bash
   mitmweb -nr data/raw/grammarly/run_1.flow
   ```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `mitm.it` not loading | Make sure Firefox proxy is set to 127.0.0.1:8080 |
| HTTPS sites show cert error | CA cert not imported — repeat Step 2c–2d |
| mitmproxy shows no traffic | Firefox proxy settings not saved — check again |
| `import mitmproxy` fails | Run: `pip3 install mitmproxy --break-system-packages` |
| Extension not activating | Make sure you're logged in and the icon is active |
| `xdotool` paste does nothing | Firefox window must be focused. Sometimes the search-by-name returns an old window; close other Firefox windows. |

---

## Quick reference — using the Makefile (recommended)

The Makefile in the project root wraps the multi-step capture and analysis
protocol into one-line commands.

```bash
cd "/path/to/Research Project - Privacy analysis"

# Sanity check: are all dependencies installed?
make check

# Open Firefox with the right profile + test page (do this before each run)
make page-grammarly                # then CLICK INTO the textarea to focus it

# In a second terminal, run the capture (auto: paste + wait 60s + stop)
make grammarly-1
make grammarly-2                   # repeat for runs 2-5 (refresh the page between)
# ... etc

# Baseline (no extension installed in baseline-test profile)
make page-baseline
make baseline-1                    # then baseline-2 and baseline-3

# Analysis - default (strict) and a lenient sensitivity check
make analyze                       # strict defaults
make analyze-lenient               # window=12, threshold=0.5, no baseline subtraction

# Produce the final chart for the report (PNG + SVG for LaTeX)
make chart                         # writes results/comparison_chart.{png,svg}

# Delete everything (CAREFUL - removes data/raw/ and results/)
make clean
```

## Inspecting captures with jq

When something looks off in a run, jq lets you query the JSON without scrolling:

```bash
# All hosts contacted during this run
jq '.requests[].host' data/raw/grammarly/run_1.json | sort -u

# Only events that contained planted tokens
jq '.requests[] | select(.tokens_found | length > 0)' data/raw/grammarly/run_1.json

# Just the summary block
jq '.summary' data/raw/grammarly/run_1.json
```

## Manual fallback — without the Makefile

If you prefer to run captures by hand:

```bash
# Use `bash` invocation (works whether on native Linux or vboxsf shared folder)
bash scripts/capture/run_capture.sh grammarly 1
# Then in a separate terminal: xclip + xdotool paste, wait 60s, press q in mitmproxy
```

See `docs/Capture-Protocol.md` for the manual step-by-step.

After captures, analyze with:
```bash
python3 scripts/analysis/analyze.py grammarly     # single tool
python3 scripts/analysis/analyze.py --all         # all three tools
python3 scripts/analysis/analyze.py --all --chart # also produce the PNG/SVG chart
```

---

*Setup guide version: 2026-05-23 (v4 — adds Makefile, matplotlib, jq, LaTeX-ready chart export).*
