"""Regression tests for analyze.py.

Locks in the fixes from 2026-05-28: the cross-event transcript coverage must be
folded into the exposure union (it was silently dropped), and the sentence parser
offsets must map back to the document. Per H4 (2026-09-05), transcript coverage is
document content and is counted regardless of host — it is NOT subtracted for
baseline hosts, since the baseline never carries the planted document. No mitmproxy
needed — analyze.py is pure stdlib.

Run from the repo root:  pytest
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts" / "analysis"))

import analyze  # noqa: E402  (path set above)

N = analyze.TOTAL_CHARS


def test_document_anchors_unchanged():
    # If the test document is edited, captured runs are no longer comparable.
    # These anchors make an accidental edit fail loudly.
    assert N == 2065
    assert analyze.TOTAL_SENTENCES == 35


def test_transcript_coverage_is_folded_in():
    # A chunked WebSocket send: every per-event frame is too short to match, so
    # per-event coverage is empty, but the addon's transcript covers everything.
    # The old analyzer reported 0%; it must now report ~100%.
    run = {
        "requests": [],
        "ws_messages": [{"covered_positions": [], "host": "api.grammarly.com"}],
        "summary": {"transcript_covered_by_host": {"api.grammarly.com": list(range(N))}},
    }
    _, pct = analyze.union_exposure_from_run(run)
    assert pct == 100.0


def test_transcript_coverage_counts_even_on_shared_host():
    # H4 (Review-Findings 2026-09-05): transcript coverage is DOCUMENT content.
    # The no-extension baseline never legitimately carries the planted document,
    # so document coverage on a host that also appears in the baseline is a REAL
    # leak, not background — it must NOT be subtracted. (The old rule dropped it,
    # which would erase a genuine leak to a shared CDN.)
    run = {
        "requests": [],
        "ws_messages": [],
        "summary": {"transcript_covered_by_host": {"api.grammarly.com": list(range(N))}},
    }
    _, pct = analyze.union_exposure_from_run(run, baseline_domains={"api.grammarly.com"})
    assert pct == 100.0


def test_mixed_hosts_transcript_all_counts():
    # Both hosts' document coverage counts, even one shared with the baseline (H4).
    run = {
        "requests": [],
        "ws_messages": [],
        "summary": {"transcript_covered_by_host": {
            "api.grammarly.com": list(range(0, 1000)),
            "noise.mozilla.net": list(range(1000, N)),
        }},
    }
    _, pct = analyze.union_exposure_from_run(run, baseline_domains={"noise.mozilla.net"})
    assert pct == 100.0


def test_tls_visibility_defaults_to_100_when_field_absent():
    assert analyze.tls_visibility({"summary": {}}) == (100.0, 0)
    assert analyze.tls_visibility(
        {"summary": {"https_event_pct": 87.5, "tls_handshake_failures": 2}}
    ) == (87.5, 2)


def test_sentence_offsets_map_back_to_document():
    # Guards the parser's start/end arithmetic (no off-by-one).
    for start, end, text in analyze.SENTENCES:
        assert analyze.TEST_CONTENT[start:end] == text


def test_confidence_interval_degenerate_and_normal():
    assert analyze.confidence_interval_95([]) == (0.0, 0.0, 0.0)
    mean, lo, hi = analyze.confidence_interval_95([30.0])
    assert mean == lo == hi == 30.0
    mean, lo, hi = analyze.confidence_interval_95([30.0, 30.2, 29.8, 30.1, 29.9])
    assert lo < mean < hi


def test_response_echo_excluded_from_exposure():
    # Exposure counts OUTBOUND only; a server echo (http_response) carrying the
    # document must NOT inflate the headline % (decided 2026-05-28).
    run = {
        "requests": [
            {"kind": "http_request", "covered_positions": [], "host": "api.grammarly.com"},
            {"kind": "http_response", "covered_positions": list(range(N)), "host": "api.grammarly.com"},
        ],
        "ws_messages": [],
        "summary": {},
    }
    _, pct = analyze.union_exposure_from_run(run)
    assert pct == 0.0
