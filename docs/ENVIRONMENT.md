# Environment & Reproducibility Reference

The exact software environment the captures were produced in, plus commands to
(a) recreate a compatible environment and (b) lock *your* exact versions
alongside your data. This is the reproducibility appendix to
[`WALKTHROUGH.md`](WALKTHROUGH.md) — the walkthrough tells you *what to do*; this
file pins *what it ran on*.

> **Why this matters.** The results depend on version-specific behaviour of
> mitmproxy (HTTP `.content` decoding and WebSocket scheme handling both had to
> be worked around). A capture is only reproducible if the version manifest
> travels with the data. Treat a `pip freeze` taken on the capture machine as
> part of the dataset.

---

## 1. Reference environment (what the study ran on)

| Component | Version used | Role |
|---|---|---|
| Host OS | Windows (host) + VirtualBox | Repo lives on host, shared into the VM |
| Guest OS | **Kali Linux** (rolling, 2026 branch) | Isolated capture environment |
| Python | **3.13** (Kali system Python; project requires ≥ 3.10) | Runs the addon + analyzer |
| **mitmproxy** | **12.2.3** (verified working 2026-07-02) | HTTPS interception + capture hooks |
| Firefox | **firefox-esr ~140** | Browser under test (per-tool profiles) |
| brotli (py) | **~1.1** | Decode `Content-Encoding: br` bodies |
| matplotlib | **~3.7** | `make chart` output only |
| pyahocorasick | **~2.0** (optional) | Fast multi-pattern window matching |
| libnss3-tools | **2:3.124-1** | Provides `certutil` for the CA import |
| xclip / xdotool / jq / make | distro current | Clipboard load, focus, JSON, orchestration |

The two tools under test were their then-current auto-updating extensions
(Grammarly by Grammarly, Inc.; LanguageTool by LanguageTooler GmbH). Because both
auto-update, pin the **capture date** (already stamped in every run's JSON)
rather than an extension version string — see §4.

---

## 2. Recreate a compatible environment

On a fresh Kali VM:

```bash
sudo apt update
sudo apt install -y python3-pip firefox-esr xclip xdotool jq make libnss3-tools
pip3 install --break-system-packages \
    "mitmproxy==12.2.3" "brotli~=1.1" "matplotlib~=3.7" "pyahocorasick~=2.0"
```

Confirm the toolchain is complete:

```bash
cd /path/to/repo
make check          # prints OK / MISSING for each dependency
mitmdump --version  # expect: Mitmproxy: 12.2.3
python3 --version
```

The pinned constraints also live in [`requirements.txt`](../requirements.txt), so
`pip3 install --break-system-packages -r requirements.txt` is equivalent.

---

## 3. mitmproxy version sensitivity (do not skip)

The capture add-on was written against **mitmproxy 12.x** and relies on behaviour
that differs across major versions:

- **HTTP body decoding** — the addon reads `flow.request.content` expecting
  mitmproxy to have already decompressed gzip/deflate; Brotli is handled
  explicitly via the `brotli` package. Older/newer mitmproxy may change this.
- **WebSocket scheme handling** — grammar checkers stream over WebSockets; the
  addon normalizes `ws://` / `wss://` message capture in a way that assumes 12.x
  message structure.

If you upgrade mitmproxy, re-run a **baseline (0 %)** and a **known-leaker
(Grammarly, ~99 %)** capture as a smoke test before trusting new numbers. A
silent decoding regression looks like a lower exposure %, not an error.

---

## 4. Lock YOUR exact versions with the data

After installing, snapshot the precise environment on the capture machine and
keep it beside the run outputs:

```bash
# exact Python package versions
pip3 freeze > results/pip-freeze.$(date +%F).txt

# exact system package versions of the interception-critical tools
dpkg -l firefox-esr libnss3-tools mitmproxy 2>/dev/null \
    | awk '/^ii/{print $2, $3}' > results/apt-versions.$(date +%F).txt

# mitmproxy + python one-liners for the record
{ mitmdump --version; python3 --version; } > results/toolchain.$(date +%F).txt
```

Every capture already records its own timestamp in `data/raw/<tool>/run_N.json`,
so the freeze files above plus those timestamps fully pin the environment a given
result was produced in.

---

## 5. Verified download sources

All installs above come from the distro repositories (`apt`) and PyPI (`pip`).
The **browser extensions** must come from their official listings — clones exist
(see [`WALKTHROUGH.md`](WALKTHROUGH.md) §4.4). Confirm the publisher before
installing:

| Tool | Official Firefox add-on | Publisher |
|---|---|---|
| Grammarly | `https://addons.mozilla.org/en-US/firefox/addon/grammarly-1/` | Grammarly, Inc. |
| LanguageTool | `https://addons.mozilla.org/en-US/firefox/addon/languagetool/` | LanguageTooler GmbH |
| mitmproxy (CA docs) | `https://docs.mitmproxy.org/stable/concepts-certificates/` | mitmproxy project |
