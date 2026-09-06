# Desktop / System-Level Capture Runbook (Linux / Kali)

How to extend the study beyond the Firefox browser to **native desktop clients and
system-level behaviour**, entirely inside the existing Kali VM. This satisfies the
supervisor's "test on the desktop too, not Firefox-only" and "measure background
behaviour / permissions" requests, for the tools that have Linux clients.

> **Scope decision (2026-09-06).** Linux/Kali only for now. Windows-only apps
> (**Grammarly desktop, the DeepL app, iCloud**) have no Linux client and are deferred
> to a later Windows-VM phase (framed as future work — the supervisor said partial
> additions are fine). Feasible on Linux now:
> - **LanguageTool standalone desktop** (Java, cross-platform) — a native-desktop parallel to the browser result.
> - **Avast Business Antivirus for Linux** (daemon, v4.7.x on Debian/Ubuntu) — for background/telemetry behaviour; Avast was named by the supervisor.
> - **System-level tests** independent of any one vendor: background/idle capture, device permissions, USB auto-read.

All the safety rules from the browser method still apply: **synthetic data only**,
throwaway/test accounts, the mitmproxy CA trusted **only inside this isolated VM**,
`.flow`/`.har` stay gitignored, git runs on Windows only.

---

## 0. Prerequisites (once)
- Kali VM with mitmproxy ≥ 12 and the capture pipeline already working (browser phase).
- `sudo apt update && sudo apt install -y frida-tools wireshark tcpdump default-jre`
  (frida-tools for pinning; wireshark/tcpdump for packet evidence; JRE for LanguageTool).
- `pip install --break-system-packages frida-tools` if the apt build is old.
- Keep the test document `input-data/test-document.txt` (the 12 planted secrets) as the
  content you paste/translate into each desktop tool — same corpus as the browser runs,
  so results are comparable.

---

## 1. Trust the mitmproxy CA system-wide (VM ONLY)
The browser phase trusted the CA only in a Firefox profile. Desktop apps use the OS trust
store, so add it system-wide **inside the disposable VM only**:

```bash
# mitmproxy writes its CA here on first run
ls ~/.mitmproxy/mitmproxy-ca-cert.cer
sudo cp ~/.mitmproxy/mitmproxy-ca-cert.cer \
        /usr/local/share/ca-certificates/mitmproxy.crt
sudo update-ca-certificates            # adds it to the system bundle
```
Undo later with `sudo rm /usr/local/share/ca-certificates/mitmproxy.crt && sudo update-ca-certificates --fresh`.

> Note: some runtimes ignore the system store — **Java** and some **Electron/Node** apps
> ship their own CA bundle. Sections 3 and 6 handle those.

---

## 2. Route traffic to mitmproxy — two options

### 2a. Explicit proxy (simplest; works for apps that honour proxy settings)
```bash
# terminal 1: start the capture
cd /media/sf_privacy_analysis
TOOL_NAME=languagetool_desktop RUN_ID=1 \
    mitmdump -s scripts/capture/capture_addon.py --listen-port 8080

# terminal 2: launch the app with proxy env vars
export http_proxy=http://127.0.0.1:8080
export https_proxy=http://127.0.0.1:8080
<launch the app from this shell>
```
Good for CLI tools and apps that read `http(s)_proxy`. Many GUI apps ignore these — use 2b.

### 2b. Transparent proxy (for apps that ignore proxy env vars)
```bash
# start mitmproxy in transparent mode
mitmdump --mode transparent --showhost -s scripts/capture/capture_addon.py

# redirect outbound 80/443 from a dedicated test user (or the whole VM) to mitmproxy
sudo iptables -t nat -A OUTPUT -p tcp --dport 80  -j REDIRECT --to-port 8080
sudo iptables -t nat -A OUTPUT -p tcp --dport 443 -j REDIRECT --to-port 8080
# ... run the app, then flush the rules afterwards:
sudo iptables -t nat -F OUTPUT
```
(Alternative: `redsocks` if you prefer a userspace redirector. Scope the iptables rule to a
test user with `-m owner --uid-owner <testuser>` so you don't reroute the whole VM.)

---

## 3. LanguageTool standalone desktop (Java) — the native-desktop case
Java **ignores** both the system CA store and `http_proxy`, so it needs explicit flags.

```bash
# import the mitmproxy CA into the JRE truststore (default password: changeit)
CACERTS=$(dirname $(dirname $(readlink -f $(which java))))/lib/security/cacerts
sudo keytool -importcert -alias mitmproxy -file ~/.mitmproxy/mitmproxy-ca-cert.cer \
     -keystore "$CACERTS" -storepass changeit -noprompt

# launch LanguageTool desktop through the proxy
java -Dhttps.proxyHost=127.0.0.1 -Dhttps.proxyPort=8080 \
     -Dhttp.proxyHost=127.0.0.1  -Dhttp.proxyPort=8080 \
     -jar languagetool.jar
```
Then paste the test document into the desktop UI and let it check. Capture as
`languagetool_desktop`. **Compare to the browser LanguageTool result** — does the native
app transmit the same content to `api.languagetool.org` (or to a different endpoint)?
If LanguageTool is run in **local/offline** mode it should send nothing — worth recording
as a "safe configuration exists" data point.

---

## 4. Avast Business Antivirus for Linux — background / telemetry behaviour
Install per Avast's Linux docs (adds an apt repo + a systemd service). The research
question here is **background transmission with no user action**:

```bash
# capture with NO interaction — just let the service run
TOOL_NAME=avast_linux RUN_ID=1 \
    mitmdump --mode transparent -s scripts/capture/capture_addon.py
# (redirect as in 2b, or point the service's proxy config at 8080)

sudo systemctl restart avast     # trigger its startup/update traffic
# leave it idle 30-60 min; do nothing else
```
Record: which hosts it contacts, definition-update vs telemetry endpoints, whether any
of the planted document (if a USB/file scan runs — see §6) appears. Note that a security
product may **pin** its update channel (see §5) — if so, that itself is a finding
("traffic present but not interceptable"), and Wireshark/tcpdump still prove the
connections happened.

---

## 5. Certificate pinning — when the CA trick isn't enough
If an app rejects the proxy despite the trusted CA, it is pinning. Use **Frida** to
disable pinning at runtime (Linux native processes):

```bash
frida-ps                              # find the running process name/pid
# attach a pinning-bypass script (generic OpenSSL/GnuTLS/BoringSSL hooks)
frida -p <pid> -l frida-scripts/disable-pinning.js
# or spawn under Frida:
frida -f /path/to/app -l frida-scripts/disable-pinning.js --no-pause
```
Notes:
- **Objection** wraps Frida with ready-made bypass scripts but is aimed at Android/iOS;
  for Linux natives, a direct Frida script hooking the TLS verify function is usually
  simpler. Start from a community "frida multiple unpinning" script and adapt the library
  symbols to the target (OpenSSL `SSL_get_verify_result`, BoringSSL, GnuTLS, or Go's
  `crypto/tls`).
- If pinning can't be beaten, **record that as a limitation** and fall back to Wireshark
  (§7) to prove the traffic exists even if the payload stays opaque. This mirrors the
  browser phase's honest "TLS-failure = lower bound" framing.

---

## 6. SSLKEYLOGFILE → Wireshark (independent decrypt, no proxy)
For apps built on OpenSSL/NSS/Node that honour `SSLKEYLOGFILE`, you can skip the proxy
entirely and decrypt the app's *genuine* traffic in Wireshark:

```bash
export SSLKEYLOGFILE=$HOME/tls-keys.log
<launch the app>
sudo tcpdump -i any -w /tmp/app.pcap        # or capture in Wireshark directly
# Wireshark → Preferences → Protocols → TLS → (Pre)-Master-Secret log filename → tls-keys.log
```
This is a *second, independent* method: it proves the leak with the app's own keys and no
man-in-the-middle, which pre-empts the "did the proxy change behaviour?" objection.

---

## 7. Wireshark / tcpdump — packet-level evidence (run LIVE)
Start this **before** you trigger each capture; it records that connections/handshakes
happened even where payloads are pinned/opaque, and produces recognisable screenshots.
```bash
sudo tcpdump -i any -w data/raw/<tool>/run_<n>.pcap host not 127.0.0.1
# open the .pcap in Wireshark afterwards for screenshots
```
Screenshots can be taken later from the saved `.pcap`; only the capture must be live.

---

## 8. System-level experiments (vendor-independent)

### 8a. Background / idle transmission
Start a capture, launch the tool, and **do nothing** for 30–60 min. Any document-bearing
or identifiable traffic in that window is unprompted background transmission. (The
`traffic_timeline.py` figure already visualises paste-spike vs background — reuse it here.)

### 8b. Device permissions
Check what the app can access: microphone via `pactl list source-outputs` / `fuser` on
`/dev/snd/*` while the app runs; filesystem/USB access via `ls -l /proc/<pid>/fd`; camera
via `/dev/video*`. Record which permissions each tool actually exercises.

### 8c. USB auto-read test
Prepare a USB stick containing PDFs seeded with the planted secrets. With a capture
running, plug it in and mount it — **do not open anything**. Watch whether any running
tool/indexer/AV auto-reads the files and transmits:
```bash
# watch file reads on the mount
sudo inotifywait -m -r -e open,access /media/<usb-mount>
# simultaneously watch traffic in mitmproxy / tcpdump
```
A hit here (a tool reading and sending USB PDF contents with no user action) would be a
strong, novel finding.

---

## 9. Analyse the captures
The existing pipeline works unchanged — the addon writes `data/raw/<tool>/run_<n>.json`,
then:
```bash
python scripts/analysis/analyze.py <tool>        # per-tool summary
python scripts/analysis/analyze.py --all --chart # comparison + chart
```
Add each new desktop tool as its own `TOOL_NAME`. The baseline for desktop is a
**no-tool idle capture** of the same VM (mirrors the no-extension browser baseline).

---

## 10. Deferred to the Windows phase (future work)
Stand up a throwaway Windows VM, repeat §1–§9 there (Windows CA store via `certutil`,
proxy via system settings or Proxifier, Frida on the PE binaries), for:
**Grammarly desktop, the DeepL desktop app, consumer Avast, and iCloud for Windows.**
Document as future work if the 10 Oct deadline is tight — the supervisor confirmed partial
additions are acceptable.
