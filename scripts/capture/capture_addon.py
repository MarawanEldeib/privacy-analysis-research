"""
capture_addon.py - mitmproxy addon for default-configuration exposure capture (v3.1)

v3.1 changes over v3:
  - WINDOW_SIZE is now configurable via env var (so the same addon can re-process
    a saved .flow file with a different window without code changes)

Usage (live capture, run from project root):
    TOOL_NAME=grammarly RUN_ID=1 mitmdump -s scripts/capture/capture_addon.py

Usage (offline re-analysis of a .flow file with a different window):
    WINDOW_SIZE=12 TOOL_NAME=grammarly RUN_ID=1 \\
        mitmdump -nr data/raw/grammarly/run_1.flow -s scripts/capture/capture_addon.py

Saves to:
    data/raw/<TOOL_NAME>/run_<RUN_ID>.json   - summarized capture
    data/raw/<TOOL_NAME>/run_<RUN_ID>.flow   - full raw mitmproxy archive
                                               (via run_capture.sh --save-stream-file)
"""

import gzip
import json
import os
import re
import sys
import unicodedata
import urllib.parse
import zlib
from datetime import datetime, timezone
from pathlib import Path

from mitmproxy import http, websocket

# Optional fast multi-pattern matcher
try:
    import ahocorasick
    HAS_AHOCORASICK = True
except ImportError:
    HAS_AHOCORASICK = False

# Optional brotli
try:
    import brotli
    HAS_BROTLI = True
except ImportError:
    HAS_BROTLI = False

# Configuration

PROJECT_ROOT  = Path(__file__).resolve().parent.parent.parent
TEST_DOC_PATH = PROJECT_ROOT / "input-data" / "test-document.txt"

TOOL_NAME = os.environ.get("TOOL_NAME", "unknown_tool")
RUN_ID    = os.environ.get("RUN_ID", "1")

# Sliding window length for substring matching.
# 20 chars avoids false positives from common short words.
# Override via env var to re-analyze a .flow file with a different window:
#   WINDOW_SIZE=12 mitmdump -nr data/raw/grammarly/run_1.flow -s scripts/capture/capture_addon.py
WINDOW_SIZE = int(os.environ.get("WINDOW_SIZE", "20"))

# Per-event body preview cap (bytes of text saved for human inspection).
BODY_PREVIEW_BYTES = 4096

# Sensitive tokens - kept in sync with scripts/analysis/analyze.py and
# docs/Metrics-Definition.md.
SENSITIVE_TOKENS = [
    "Helena Voss",
    "HV-2026-391847",
    "Theodora Baumgartner-Klein",
    "theodora.baumgartner@priv-research-demo.invalid",
    "+49 30 4827-9153",
    "Project Nighthawk-3",
    "XREF-291-ALPHA",
    "NHK3-RES-7741",
    "AC-2026-00293-DELTA",
    "2026-LGL-00847",
    "DE-291-847-3309",
    "CANARY-BC267061-67DC-485B-8E51-6F5494765CAB",
]

# Hosts / suffixes to ignore (background browser noise, not tool traffic).
#
# IMPORTANT — this filter runs at capture time, BEFORE events are recorded.
# Baseline subtraction in analyze.py cannot recover anything filtered here.
# Firefox/Mozilla telemetry hostnames change between versions, so re-verify
# this list at the start of each new capture batch by running:
#   grep -E '"host":' data/raw/baseline/run_1.json | sort -u
# Any unfamiliar Mozilla/Google/cert hosts that recur in all baseline runs
# should be considered for addition here (after which the captures must be
# re-analyzed but NOT re-captured — IGNORE_SUFFIXES is only consulted at
# capture, but the raw .flow files can be re-fed through the addon with the
# updated list).
IGNORE_SUFFIXES = {
    "localhost",
    "127.0.0.1",
    "::1",
    "mitm.it",
    "detectportal.firefox.com",
    "firefox.settings.services.mozilla.com",
    "normandy.cdn.mozilla.net",
    "shavar.services.mozilla.com",
    "push.services.mozilla.com",
    "telemetry.mozilla.org",
    "aus5.mozilla.org",
    "tiles.services.mozilla.com",
    "location.services.mozilla.com",
    "safebrowsing.googleapis.com",
    "ocsp.digicert.com",
    "ocsp.pki.goog",
    "accounts.google.com",
}

# Load test document

if not TEST_DOC_PATH.exists():
    print(f"[ERROR] Test document not found: {TEST_DOC_PATH}", file=sys.stderr)
    sys.exit(1)

TEST_CONTENT = TEST_DOC_PATH.read_text(encoding="utf-8")
TOTAL_CHARS  = len(TEST_CONTENT)
TEST_LOWER   = TEST_CONTENT.lower()

print(f"[INFO] Test document loaded: {TOTAL_CHARS} chars")
print(f"[INFO] Tool: {TOOL_NAME}  |  Run ID: {RUN_ID}  |  Window: {WINDOW_SIZE}")
print(f"[INFO] brotli support:        {HAS_BROTLI}")
print(f"[INFO] Aho-Corasick fast path: {HAS_AHOCORASICK}")

# Build window automaton (fast path)

if HAS_AHOCORASICK:
    WINDOW_AUTO = ahocorasick.Automaton()
    _seen = {}
    for i in range(TOTAL_CHARS - WINDOW_SIZE + 1):
        w = TEST_LOWER[i:i + WINDOW_SIZE]
        if w not in _seen:
            _seen[w] = i
            WINDOW_AUTO.add_word(w, i)
    WINDOW_AUTO.make_automaton()
    print(f"[INFO] Aho-Corasick automaton built ({len(_seen)} unique windows)")
else:
    WINDOW_AUTO = None
    print("[INFO] Using slow O(n*m) window scan - install pyahocorasick for speed")

# Session state

session = {
    "tool":            TOOL_NAME,
    "run_id":          RUN_ID,
    "start_time":      datetime.now(timezone.utc).isoformat(),
    "end_time":        None,
    "test_doc_chars":  TOTAL_CHARS,
    "window_size":     WINDOW_SIZE,
    "tool_version":    os.environ.get("TOOL_VERSION", "unknown"),
    "browser_version": os.environ.get("BROWSER_VERSION", "unknown"),
    "os_info":         os.environ.get("OS_INFO", "unknown"),
    "requests":        [],
    "ws_messages":     [],
    "tls_failures":    [],
    "read_failures":   [],
    "summary":         None,
}

# Full client->server bodies accumulated per host during the session, used for
# the cross-event transcript pass in done(). Kept in memory only (NOT written to
# JSON) so it can hold full bodies without bloating result files or storing
# request headers. Fresh each run (one mitmdump process per run).
PER_HOST_BODIES = {}

# Helpers

def should_ignore(host):
    host = host.lower()
    for suffix in IGNORE_SUFFIXES:
        if host == suffix or host.endswith("." + suffix):
            return True
    return False


def decompress(data, encoding):
    enc = (encoding or "").lower().strip()
    try:
        if enc == "gzip":
            return gzip.decompress(data)
        if enc == "deflate":
            try:
                return zlib.decompress(data)
            except zlib.error:
                return zlib.decompress(data, -zlib.MAX_WBITS)
        if enc in ("br", "brotli") and HAS_BROTLI:
            return brotli.decompress(data)
    except Exception:
        pass
    return data


def bytes_to_text(data):
    for enc in ("utf-8", "latin-1"):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            pass
    return data.decode("utf-8", errors="replace")


# JSON string escapes that show up in real payloads. We unescape them anywhere
# in the text (not only when the whole body is valid JSON) so 20-char windows
# spanning an escaped newline (\n) or em-dash (—) still match. The old code
# did json.loads(f'"{body}"') on the WHOLE body, which threw on any real body
# (they contain " and newlines) — so that variant never actually ran.
_JSON_UXXXX  = re.compile(r'\\u([0-9a-fA-F]{4})')
_JSON_SIMPLE = (('\\n', '\n'), ('\\t', '\t'), ('\\r', '\r'),
                ('\\"', '"'), ('\\/', '/'))


def _json_string_values(obj, out):
    """Recursively collect every string (keys and values) from parsed JSON."""
    if isinstance(obj, str):
        out.append(obj)
    elif isinstance(obj, dict):
        for k, v in obj.items():
            out.append(k)
            _json_string_values(v, out)
    elif isinstance(obj, list):
        for v in obj:
            _json_string_values(v, out)


def _json_unescape(s):
    s = _JSON_UXXXX.sub(lambda m: chr(int(m.group(1), 16)), s)
    for esc, ch in _JSON_SIMPLE:
        s = s.replace(esc, ch)
    return s


def build_search_corpus(raw_text):
    """Return text variants to search. Additive: each variant can only ADD
    coverage, never remove it, so a spurious unescape is harmless."""
    variants = [raw_text]
    seen = {raw_text}

    def add(v):
        if v and v not in seen:
            seen.add(v)
            variants.append(v)

    # Unicode normalization (NFC) so composed/decomposed forms align.
    try:
        add(unicodedata.normalize("NFC", raw_text))
    except Exception:
        pass
    # URL / form-encoded transmission.
    try:
        add(urllib.parse.unquote_plus(raw_text))
    except Exception:
        pass
    # JSON-escaped transmission (1): if the text parses as JSON, pull out every
    # string value — the parser has already unescaped \n and \uXXXX for us.
    try:
        parsed = json.loads(raw_text)
        strings = []
        _json_string_values(parsed, strings)
        for s in strings:
            add(s)
        if strings:
            add("\n".join(strings))
    except Exception:
        pass
    # JSON-escaped transmission (2): when the body isn't cleanly parseable
    # (e.g. it's embedded in a url+headers blob, or is a streamed fragment),
    # unescape JSON-style escapes in place.
    try:
        add(_json_unescape(raw_text))
    except Exception:
        pass
    return variants


def find_covered_positions(text):
    covered = set()
    for variant in build_search_corpus(text):
        variant_lower = variant.lower()
        if WINDOW_AUTO is not None:
            for _, start_idx in WINDOW_AUTO.iter(variant_lower):
                covered.update(range(start_idx, start_idx + WINDOW_SIZE))
        else:
            for i in range(TOTAL_CHARS - WINDOW_SIZE + 1):
                window = TEST_LOWER[i:i + WINDOW_SIZE]
                if window in variant_lower:
                    covered.update(range(i, i + WINDOW_SIZE))
    return covered


def find_tokens_in_text(text):
    found = set()
    for variant in build_search_corpus(text):
        variant_lower = variant.lower()
        for tok in SENSITIVE_TOKENS:
            if tok.lower() in variant_lower:
                found.add(tok)
    return sorted(found)


def make_body_preview(text):
    if not text:
        return ""
    if len(text) <= BODY_PREVIEW_BYTES:
        return text
    return text[:BODY_PREVIEW_BYTES] + f"...[truncated, full length {len(text)} chars]"


def safe_body(message):
    """Return (body_bytes, encoding_to_apply).

    mitmproxy's `.content` is already decompressed, but reading it RAISES
    ValueError when the content-encoding is one it can't handle — and
    `message.content or b""` does NOT catch that, so the event would be lost
    silently. We catch it and fall back to `.raw_content` + the header encoding
    so our own decompress() (with brotli) can try. Read failures are recorded in
    session["read_failures"] so "couldn't read" is never scored as "clean".
    Happy path returns encoding="" because `.content` is already decoded
    (decompress() is then a no-op)."""
    enc = message.headers.get("content-encoding", "")
    try:
        c = message.content                  # decoded; may raise ValueError
        if c is not None:
            return c, ""
    except Exception:
        pass
    try:
        raw = message.raw_content
        if raw:
            return raw, enc                  # still compressed -> decompress() tries
    except Exception:
        pass
    session["read_failures"].append({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "content_encoding": enc,
    })
    return b"", ""


def extract_request_text(flow):
    parts = [flow.request.pretty_url]
    for key, val in flow.request.headers.items():
        parts.append(f"{key}: {val}")
    raw, enc = safe_body(flow.request)
    body = bytes_to_text(decompress(raw, enc))
    if body:
        parts.append(body)
    return ("\n".join(parts), body)


def extract_response_text(flow):
    if not flow.response:
        return ""
    raw, enc = safe_body(flow.response)
    return bytes_to_text(decompress(raw, enc))


def log_event(label, host, covered, tokens, extra=""):
    pct = round(len(covered) / TOTAL_CHARS * 100, 2)
    if covered or tokens:
        tok_note = f" tokens={tokens}" if tokens else ""
        print(f"[! EXPOSURE] [{label}] {host} - {len(covered)} chars ({pct}%){tok_note} {extra}")
    else:
        print(f"[  ok  ] [{label}] {host} {extra}")


# mitmproxy addon

class ExposureTracker:

    def request(self, flow):
        if should_ignore(flow.request.pretty_host):
            return
        search_text, body_only = extract_request_text(flow)
        covered = find_covered_positions(search_text)
        tokens  = find_tokens_in_text(search_text)
        entry = {
            "kind":              "http_request",
            "timestamp":         datetime.now(timezone.utc).isoformat(),
            "host":              flow.request.pretty_host,
            "method":            flow.request.method,
            "path":              flow.request.path,
            "content_length":    len(flow.request.content or b""),
            "tls":               flow.request.scheme == "https",
            "content_encoding":  flow.request.headers.get("content-encoding", ""),
            "covered_positions": sorted(covered),
            "exposure_chars":    len(covered),
            "exposure_pct":      round(len(covered) / TOTAL_CHARS * 100, 2),
            "tokens_found":      tokens,
            "body_preview":      make_body_preview(body_only),
        }
        if body_only:
            PER_HOST_BODIES.setdefault(flow.request.pretty_host, []).append(body_only)
        session["requests"].append(entry)
        log_event("REQ", flow.request.pretty_host, covered, tokens,
                  f"| {flow.request.method} {flow.request.path[:50]}")

    def response(self, flow):
        if should_ignore(flow.request.pretty_host):
            return
        text = extract_response_text(flow)
        if not text:
            return
        covered = find_covered_positions(text)
        tokens  = find_tokens_in_text(text)
        entry = {
            "kind":              "http_response",
            "timestamp":         datetime.now(timezone.utc).isoformat(),
            "host":              flow.request.pretty_host,
            "status_code":       flow.response.status_code if flow.response else None,
            "content_length":    len(flow.response.content or b"") if flow.response else 0,
            "tls":               flow.request.scheme == "https",
            "content_encoding":  flow.response.headers.get("content-encoding", "") if flow.response else "",
            "covered_positions": sorted(covered),
            "exposure_chars":    len(covered),
            "exposure_pct":      round(len(covered) / TOTAL_CHARS * 100, 2),
            "tokens_found":      tokens,
            "body_preview":      make_body_preview(text),
        }
        session["requests"].append(entry)
        if covered or tokens:
            log_event("RSP", flow.request.pretty_host, covered, tokens)

    def websocket_message(self, flow):
        if should_ignore(flow.request.pretty_host):
            return
        msg = flow.websocket.messages[-1]
        if not msg.from_client:
            return
        try:
            text = bytes_to_text(msg.content) if isinstance(msg.content, bytes) else str(msg.content)
        except Exception:
            return
        covered = find_covered_positions(text)
        tokens  = find_tokens_in_text(text)
        entry = {
            "kind":              "websocket_client",
            "timestamp":         datetime.now(timezone.utc).isoformat(),
            "host":              flow.request.pretty_host,
            "frame_type":        "binary" if isinstance(msg.content, bytes) else "text",
            "content_length":    len(msg.content),
            "tls":               flow.request.scheme in ("https", "wss"),
            "covered_positions": sorted(covered),
            "exposure_chars":    len(covered),
            "exposure_pct":      round(len(covered) / TOTAL_CHARS * 100, 2),
            "tokens_found":      tokens,
            "body_preview":      make_body_preview(text),
        }
        PER_HOST_BODIES.setdefault(flow.request.pretty_host, []).append(text)
        session["ws_messages"].append(entry)
        log_event("WS ", flow.request.pretty_host, covered, tokens,
                  f"| {len(msg.content)} bytes")

    def tls_failed_client(self, data):
        try:
            sni = getattr(getattr(data, "conn", None), "sni", None) or "unknown"
        except Exception:
            sni = "unknown"
        if should_ignore(str(sni)):
            return
        session["tls_failures"].append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "side":      "client",
            "sni":       str(sni),
        })
        print(f"[TLS-FAIL] client refused MITM for SNI={sni}")

    def tls_failed_server(self, data):
        try:
            sni = getattr(getattr(data, "conn", None), "sni", None) or "unknown"
        except Exception:
            sni = "unknown"
        if should_ignore(str(sni)):
            return
        session["tls_failures"].append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "side":      "server",
            "sni":       str(sni),
        })
        print(f"[TLS-FAIL] server refused MITM for SNI={sni}")

    def done(self):
        session["end_time"] = datetime.now(timezone.utc).isoformat()
        all_events = session["requests"] + session["ws_messages"]

        union_covered = set()
        union_tokens  = set()
        for ev in all_events:
            union_covered.update(ev["covered_positions"])
            union_tokens.update(ev.get("tokens_found", []))

        # Cross-event ("transcript") pass — built from FULL client->server bodies
        # accumulated during the session, NOT the 4 KB JSON previews (too small to
        # catch chunking past 4 KB). Responses are excluded: this measures data
        # leaving the user, not echoes coming back. Per-host covered positions are
        # stored so analyze.py can union them AFTER baseline subtraction.
        transcript_covered     = set()
        transcript_tokens      = set()
        transcript_cov_by_host = {}
        for host, parts in PER_HOST_BODIES.items():
            if should_ignore(host):
                continue
            joined   = "\n".join(parts)
            host_cov = find_covered_positions(joined)
            if host_cov:
                transcript_cov_by_host[host] = sorted(host_cov)
            transcript_covered.update(host_cov)
            transcript_tokens.update(find_tokens_in_text(joined))

        total_covered = union_covered | transcript_covered
        total_tokens  = union_tokens  | transcript_tokens

        total_events   = len(all_events)
        https_events   = sum(1 for e in all_events if e.get("tls"))
        exposed_events = sum(1 for e in all_events if e["exposure_chars"] > 0 or e.get("tokens_found"))
        unique_domains = len({e["host"] for e in all_events})
        tls_failures   = len(session["tls_failures"])

        https_event_pct = round(https_events / total_events * 100, 2) if total_events else 100.0

        session["summary"] = {
            "total_events":              total_events,
            "http_requests":             sum(1 for e in session["requests"] if e["kind"] == "http_request"),
            "http_responses":            sum(1 for e in session["requests"] if e["kind"] == "http_response"),
            "websocket_messages":        len(session["ws_messages"]),
            "exposed_events":            exposed_events,
            "unique_external_domains":   unique_domains,
            "https_events":              https_events,
            "https_event_pct":           https_event_pct,
            "tls_handshake_failures":    tls_failures,
            "body_read_failures":        len(session["read_failures"]),
            "per_event_covered_chars":   len(union_covered),
            "transcript_covered_chars":  len(transcript_covered),
            "transcript_covered_by_host": transcript_cov_by_host,
            "union_covered_chars":       len(total_covered),
            "union_exposure_pct":        round(len(total_covered) / TOTAL_CHARS * 100, 2),
            "any_exposure":              len(total_covered) > 0 or bool(total_tokens),
            "sensitive_tokens_found":    sorted(total_tokens),
            "sensitive_token_count":     len(total_tokens),
            "window_size_used":          WINDOW_SIZE,
        }

        out_dir  = PROJECT_ROOT / "data" / "raw" / TOOL_NAME
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"run_{RUN_ID}.json"

        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(session, f, indent=2, ensure_ascii=False)

        s = session["summary"]
        sep = "=" * 65
        print("\n" + sep)
        print(f"  SESSION COMPLETE - {TOOL_NAME} / run {RUN_ID} / window {WINDOW_SIZE}")
        print(sep)
        print(f"  HTTP requests:        {s['http_requests']}")
        print(f"  HTTP responses:       {s['http_responses']}")
        print(f"  WebSocket messages:   {s['websocket_messages']}")
        print(f"  Exposed events:       {s['exposed_events']}")
        print(f"  Unique domains:       {s['unique_external_domains']}")
        print(f"  HTTPS events:         {s['https_events']}/{s['total_events']} ({s['https_event_pct']}%)")
        print(f"  TLS handshake fails:  {s['tls_handshake_failures']}  <- missed traffic, if any")
        print(f"  -----------------------------------------")
        print(f"  Per-event exposure:   {s['per_event_covered_chars']} chars")
        print(f"  Transcript exposure:  {s['transcript_covered_chars']} chars (cross-event)")
        print(f"  UNION EXPOSURE:       {s['union_exposure_pct']}%  ({s['union_covered_chars']} / {TOTAL_CHARS} chars)")
        print(f"  Sensitive tokens:     {s['sensitive_token_count']}/{len(SENSITIVE_TOKENS)}  {s['sensitive_tokens_found']}")
        print(f"  Any exposure at all:  {s['any_exposure']}")
        print(f"\n  Saved -> {out_path}")
        print(sep)


addons = [ExposureTracker()]
