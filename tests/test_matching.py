"""Regression tests for the capture addon's content matching.

Locks in the 2026-05-28 JSON-escape fix: when a tool transmits the document as a
JSON string (escaping newlines as \\n and the em-dash as \\u2014), the 20-char
window matcher must still recover it. The old code's JSON-unescape variant was
dead, costing ~5-8 percentage points of measured coverage.

Requires mitmproxy because capture_addon imports it at module load; the test is
skipped automatically where mitmproxy is unavailable.

Run from the repo root:  pytest
"""
import json
import sys
from pathlib import Path

import pytest

pytest.importorskip("mitmproxy")  # addon does `from mitmproxy import http, websocket`

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts" / "capture"))

import capture_addon as ca  # noqa: E402  (path + importorskip above)

DOC = ca.TEST_CONTENT
N = ca.TOTAL_CHARS
CANARY = "CANARY-BC267061-67DC-485B-8E51-6F5494765CAB"


def _coverage_pct(text: str) -> float:
    return len(ca.find_covered_positions(text)) / N * 100


def test_plaintext_utf8_json_body_is_almost_fully_covered():
    body = json.dumps({"text": DOC}, ensure_ascii=False)
    assert _coverage_pct(body) > 95.0


def test_unicode_escaped_json_body_is_recovered():
    # ensure_ascii=True escapes the em-dash as — and newlines as \n —
    # exactly the case the dead code used to miss.
    body = json.dumps({"text": DOC}, ensure_ascii=True)
    assert _coverage_pct(body) > 95.0


def test_json_unescape_restores_escapes():
    assert ca._json_unescape(r"a—b") == "a—b"
    assert ca._json_unescape(r"line1\nline2") == "line1\nline2"


def test_canary_token_detected_in_json_body():
    body = json.dumps({"text": DOC})
    assert CANARY in ca.find_tokens_in_text(body)


def test_no_false_positives_on_unrelated_text():
    assert ca.find_covered_positions("the quick brown fox " * 50) == set()
    assert ca.find_tokens_in_text("nothing sensitive here at all") == []
