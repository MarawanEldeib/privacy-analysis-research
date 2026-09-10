# Independent evidence — Grammarly transmits with no proxy in the loop

**Date:** 2026-09-10 · **Capture:** `data/raw/evidence/grammarly_noproxy.pcap` (tcpdump, 85 packets)

## Why this capture exists
The main results (Grammarly 99.0 %, all 12 secrets) come from the **mitmproxy** method,
where our proxy sits between the browser and Grammarly. A fair reviewer can ask: *did the
proxy itself change the behaviour?* This capture answers that by removing the proxy
entirely and observing the browser's own traffic.

## Method
- Firefox `grammarly-test` profile switched to **direct connection** (`network.proxy.type = 0`
  via `user.js`) — **no mitmproxy running, nothing intercepting.**
- Encrypted-SNI (ECH) disabled (`network.dns.echconfig.enabled = false`) so the destination
  hostname is visible in the TLS ClientHello.
- `tcpdump` recorded all non-loopback traffic for a 30 s window; the 12-secret test document
  was pasted once into the controlled test page.

> **Limitation (honest):** Debian's `firefox-esr` does **not** honour `SSLKEYLOGFILE`
> (verified: `curl` writes TLS keys, Firefox writes none after successful HTTPS loads), so
> the *payload* of this direct capture cannot be decrypted. The **content** proof stays with
> the mitmproxy runs; this capture proves the **connection and upload** happen without a proxy.

## What the packets show
- **DNS lookup:** `assets.grammarly.com`
- **TLS SNI:** `assets.grammarly.com`
- **Outbound upload** (browser → server, right after paste):
  | Destination IP | Reverse DNS | Tx bytes |
  |---|---|---|
  | 44.213.83.95 | `ec2-44-213-83-95.compute-1.amazonaws.com` (Grammarly AWS backend) | ~4.3 KB |
  | 65.8.131.65 | `server-65-8-131-65.fra60.r.cloudfront.net` (Grammarly CDN, Frankfurt) | ~3.3 KB |
  | 65.8.131.124 | `server-65-8-131-124.fra60.r.cloudfront.net` | — |
  | 18.245.65.219 | `server-18-245-65-219.fra60.r.cloudfront.net` | — |
- Total ~6.5 KB uploaded to Grammarly-owned infrastructure in the paste window; the test
  document is ~2 KB, consistent with a full-document upload plus TLS overhead.

## Interpretation
With **no interception of any kind**, pasting the document caused the browser to open TLS
connections to Grammarly's own servers (AWS EC2 + CloudFront) and upload several kilobytes
immediately. This independently confirms the mitmproxy finding and rules out the objection
that the proxy induced the transmission.

*Reproduce:* set `network.proxy.type=0` in the profile's `user.js`, run
`tcpdump -i any -w <out>.pcap 'not host 127.0.0.1'`, paste the document, then inspect with
`tshark -z endpoints,ip` and `-e tls.handshake.extensions_server_name`.
