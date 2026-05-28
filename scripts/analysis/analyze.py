"""
analyze.py - Compute exposure metrics from mitmproxy capture files (v3.1)

v3.1 changes over v3:
  - --window flag re-derives coverage from body_preview at analyze time
    (best-effort; for authoritative re-window, set WINDOW_SIZE=N when
    re-running capture_addon against the .flow file)
  - --sentence-threshold flag tunes how strict 'sentence fully leaked' is
  - Useful for 'lenient first, tighten later' methodology

Usage:
    python scripts/analysis/analyze.py grammarly
    python scripts/analysis/analyze.py --all
    python scripts/analysis/analyze.py --file data/raw/grammarly/run_1.json
    python scripts/analysis/analyze.py grammarly --no-baseline --window 12 --sentence-threshold 0.5
"""

import argparse
import json
import math
import re
import statistics
import sys
from pathlib import Path

PROJECT_ROOT  = Path(__file__).resolve().parent.parent.parent
TEST_DOC_PATH = PROJECT_ROOT / "input-data" / "test-document.txt"
DATA_DIR      = PROJECT_ROOT / "data" / "raw"
RESULTS_DIR   = PROJECT_ROOT / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

TOOLS = ["grammarly", "prowritingaid", "wordtune", "baseline"]

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

if not TEST_DOC_PATH.exists():
    print(f"[ERROR] Test document not found: {TEST_DOC_PATH}", file=sys.stderr)
    sys.exit(1)

TEST_CONTENT = TEST_DOC_PATH.read_text(encoding="utf-8")
TOTAL_CHARS  = len(TEST_CONTENT)
TEST_LOWER   = TEST_CONTENT.lower()


MIN_SENTENCE_CHARS = 25
_SENT_END = re.compile(r'(?<=[\.!\?])\s+|\n+')

def _parse_sentences(text):
    out = []
    pos = 0
    for m in _SENT_END.finditer(text):
        sent = text[pos:m.start()].strip()
        if len(sent) >= MIN_SENTENCE_CHARS:
            sent_start = pos + (len(text[pos:m.start()]) - len(text[pos:m.start()].lstrip()))
            sent_end   = sent_start + len(sent)
            out.append((sent_start, sent_end, sent))
        pos = m.end()
    tail = text[pos:].strip()
    if len(tail) >= MIN_SENTENCE_CHARS:
        sent_start = pos + (len(text[pos:]) - len(text[pos:].lstrip()))
        sent_end   = sent_start + len(tail)
        out.append((sent_start, sent_end, tail))
    return out

SENTENCES = _parse_sentences(TEST_CONTENT)
TOTAL_SENTENCES = len(SENTENCES)


T_CRIT_95 = {
    1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571,
    6: 2.447,  7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228,
    15: 2.131, 20: 2.086, 30: 2.042,
}

def _t_critical_95(df):
    if df < 1:
        return float("inf")
    if df in T_CRIT_95:
        return T_CRIT_95[df]
    keys = sorted(k for k in T_CRIT_95 if k <= df)
    return T_CRIT_95[keys[-1]] if keys else 12.706


def confidence_interval_95(values):
    n = len(values)
    if n == 0:
        return (0.0, 0.0, 0.0)
    mean = statistics.mean(values)
    if n == 1:
        return (mean, mean, mean)
    sd = statistics.stdev(values)
    se = sd / math.sqrt(n)
    t  = _t_critical_95(n - 1)
    return (mean, mean - t * se, mean + t * se)


def sentences_fully_leaked(covered_positions, leak_threshold=0.9):
    leaked = []
    for i, (start, end, text) in enumerate(SENTENCES):
        total = end - start
        if total == 0:
            continue
        covered_in_sentence = sum(1 for p in range(start, end) if p in covered_positions)
        if covered_in_sentence / total >= leak_threshold:
            leaked.append((i, text))
    return leaked


def rederive_covered_positions_from_previews(run_data, window_size):
    """Re-compute covered_positions from each event's body_preview using
    a different window size. Useful for sensitivity analysis without re-capture.

    NOTE: body_preview is capped at 4 KB per event. For an authoritative
    re-analysis with a different window, re-run capture_addon against the
    raw .flow file with the WINDOW_SIZE=N env var.
    """
    if window_size <= 0:
        return set()
    union = set()
    text_lower = TEST_LOWER
    n_total = len(text_lower)
    windows = {}
    for i in range(n_total - window_size + 1):
        w = text_lower[i:i + window_size]
        windows.setdefault(w, i)

    all_events = run_data.get("requests", []) + run_data.get("ws_messages", [])
    for ev in all_events:
        preview = (ev.get("body_preview", "") or "").lower()
        if not preview:
            continue
        for w, start_idx in windows.items():
            if w in preview:
                union.update(range(start_idx, start_idx + window_size))
    return union


def union_exposure_from_run(run_data, baseline_domains=None):
    union = set()
    all_events = run_data.get("requests", []) + run_data.get("ws_messages", [])
    for ev in all_events:
        union.update(ev.get("covered_positions", []))
    # Cross-event ("transcript") coverage: windows that span two outbound frames
    # are invisible to per-event matching. The addon stores per-host transcript
    # coverage computed over FULL client->server bodies; fold it in here, skipping
    # any host that also appears in the baseline (same rule as per-event events).
    summary = run_data.get("summary", {}) or {}
    by_host = summary.get("transcript_covered_by_host", {}) or {}
    for host, positions in by_host.items():
        if baseline_domains and host in baseline_domains:
            continue
        union.update(positions)
    pct = round(len(union) / TOTAL_CHARS * 100, 2) if TOTAL_CHARS else 0.0
    return union, pct


def tls_visibility(run_data):
    s = run_data.get("summary", {}) or {}
    https_pct = s.get("https_event_pct")
    if https_pct is None:
        total = s.get("total_request_bytes", 0)
        tls   = s.get("tls_request_bytes", 0)
        https_pct = round(tls / total * 100, 2) if total > 0 else 100.0
    return float(https_pct), int(s.get("tls_handshake_failures", 0))


def check_sensitive_tokens(run_data):
    all_events = run_data.get("requests", []) + run_data.get("ws_messages", [])
    summary    = run_data.get("summary", {}) or {}

    found_set = set(summary.get("sensitive_tokens_found", []) or [])
    for ev in all_events:
        found_set.update(ev.get("tokens_found", []) or [])

    if not found_set:
        for ev in all_events:
            preview = (ev.get("body_preview", "") or "").lower()
            if not preview:
                continue
            for token in SENSITIVE_TOKENS:
                if token.lower() in preview:
                    found_set.add(token)

    return {token: (token in found_set) for token in SENSITIVE_TOKENS}


def get_baseline_domains(baseline_tool="baseline"):
    baseline_dir = DATA_DIR / baseline_tool
    if not baseline_dir.exists():
        return set()
    domains = set()
    for f in baseline_dir.glob("run_*.json"):
        with open(f, encoding="utf-8") as fp:
            data = json.load(fp)
        all_events = data.get("requests", []) + data.get("ws_messages", [])
        for ev in all_events:
            domains.add(ev.get("host", ""))
    return domains


def analyze_run(run_path, baseline_domains=None,
                window_override=None, sentence_threshold=0.9):
    """Analyze a single run.

    window_override: if set, re-derives coverage from each event's body_preview
        using this window size (best-effort; 4 KB cap per event).
    sentence_threshold: minimum fraction of a sentence's chars that must be
        covered for it to count as "fully leaked".
    """
    with open(run_path, encoding="utf-8") as f:
        run_data = json.load(f)

    if baseline_domains:
        run_data["requests"] = [
            e for e in run_data.get("requests", [])
            if e.get("host", "") not in baseline_domains
        ]
        run_data["ws_messages"] = [
            e for e in run_data.get("ws_messages", [])
            if e.get("host", "") not in baseline_domains
        ]

    if window_override is not None and window_override > 0:
        union_covered = rederive_covered_positions_from_previews(run_data, window_override)
        exposure_pct  = round(len(union_covered) / TOTAL_CHARS * 100, 2) if TOTAL_CHARS else 0.0
    else:
        union_covered, exposure_pct = union_exposure_from_run(run_data, baseline_domains)

    https_pct, tls_failures       = tls_visibility(run_data)
    sensitive_found               = check_sensitive_tokens(run_data)
    s                             = run_data.get("summary", {}) or {}

    all_events = run_data.get("requests", []) + run_data.get("ws_messages", [])

    leaked_sentences  = sentences_fully_leaked(union_covered, leak_threshold=sentence_threshold)
    leaked_sent_count = len(leaked_sentences)

    return {
        "run_id":              run_data.get("run_id"),
        "tool":                run_data.get("tool"),
        "start_time":          run_data.get("start_time"),
        "exposure_pct":        exposure_pct,
        "any_exposure":        (
            len(union_covered) > 0
            or any(sensitive_found.values())
            or leaked_sent_count > 0
        ),
        "covered_chars":       len(union_covered),
        "sentences_leaked":    leaked_sent_count,
        "sentences_leaked_total":   TOTAL_SENTENCES,
        "sentences_leaked_texts":   [t for _, t in leaked_sentences],
        "https_event_pct":     https_pct,
        "tls_handshake_failures": tls_failures,
        "sensitive_tokens_found": {k: v for k, v in sensitive_found.items() if v},
        "total_events":        len(all_events),
        "exposed_events":      sum(
            1 for e in all_events
            if e.get("exposure_chars", 0) > 0 or e.get("tokens_found")
        ),
        "unique_domains":      len({e.get("host") for e in all_events}),
        "total_request_bytes": s.get("total_request_bytes", 0),
        "websocket_messages":  s.get("websocket_messages", 0),
        "baseline_subtracted": baseline_domains is not None,
    }


def analyze_tool(tool_name, subtract_baseline=True,
                 window_override=None, sentence_threshold=0.9):
    tool_dir = DATA_DIR / tool_name
    if not tool_dir.exists():
        print(f"[WARN] No data directory for: {tool_name}")
        return None

    run_files = sorted(tool_dir.glob("run_*.json"))
    if not run_files:
        print(f"[WARN] No run files in: {tool_dir}")
        return None

    baseline_domains = get_baseline_domains() if subtract_baseline else None
    if baseline_domains:
        print(f"[INFO] Subtracting {len(baseline_domains)} baseline domains from {tool_name} runs")
    if window_override:
        print(f"[INFO] Re-deriving coverage with window={window_override} from body_preview "
              f"(best-effort; capped at 4 KB per event)")
    if sentence_threshold != 0.9:
        print(f"[INFO] Sentence-leak threshold = {sentence_threshold}")

    runs = [analyze_run(f, baseline_domains, window_override, sentence_threshold)
            for f in run_files]
    n    = len(runs)

    exposures   = [r["exposure_pct"] for r in runs]
    sent_leaks  = [r["sentences_leaked"] for r in runs]
    https_pcts  = [r["https_event_pct"] for r in runs]
    tls_fails   = [r["tls_handshake_failures"] for r in runs]

    median_exp  = statistics.median(exposures)
    stdev_exp   = round(statistics.stdev(exposures), 2) if n > 1 else 0.0
    mean_exp    = round(statistics.mean(exposures), 2)
    min_exp     = min(exposures)
    max_exp     = max(exposures)

    ci_mean_raw, ci_low_raw, ci_high_raw = confidence_interval_95(exposures)
    ci_low  = max(0.0, round(ci_low_raw, 2))
    ci_high = min(100.0, round(ci_high_raw, 2))
    ci_half_width = round((ci_high - ci_low) / 2, 2)

    median_sentences_leaked = statistics.median(sent_leaks) if sent_leaks else 0

    union_sentences = set()
    for r in runs:
        union_sentences.update(r.get("sentences_leaked_texts", []))

    avg_https_pct  = round(statistics.mean(https_pcts), 2)
    total_tls_fail = sum(tls_fails)

    if stdev_exp < 3:
        repro_label = "High"
    elif stdev_exp < 10:
        repro_label = "Medium"
    else:
        repro_label = "Low"

    all_sensitive = {}
    for r in runs:
        for tok in r.get("sensitive_tokens_found", {}):
            all_sensitive[tok] = all_sensitive.get(tok, 0) + 1

    any_exp   = any(r["any_exposure"] for r in runs)
    tok_count = len(all_sensitive)

    tls_note = (
        f" {total_tls_fail} TLS handshakes could not be intercepted (cert pinning) "
        f"- content for those connections is unknown."
        if total_tls_fail > 0 else ""
    )
    ci_phrase = (
        f"95% CI [{ci_low:.1f}%, {ci_high:.1f}%]"
        if n > 1 else "single run, no CI"
    )
    conclusion = (
        f"{tool_name.title()} transmitted approximately {median_exp:.1f}% of the input document "
        f"to external servers during default-configuration use "
        f"(median across {n} runs, std dev {stdev_exp:.1f}pp, mean {mean_exp:.1f}% {ci_phrase}). "
        f"Reproducibility: {repro_label}. "
        f"At the sentence level, a median of {median_sentences_leaked:.0f} of {TOTAL_SENTENCES} "
        f"sentences leaked fully per run ({len(union_sentences)} unique sentences across all runs). "
        f"Of intercepted events, {avg_https_pct:.1f}% used HTTPS.{tls_note} "
        + (
            f"{tok_count} of {len(SENSITIVE_TOKENS)} planted sensitive tokens were detected in traffic."
            if any_exp else
            "No test document content was detected in outbound traffic."
        )
    )

    summary = {
        "tool":                tool_name,
        "num_runs":            n,
        "baseline_subtracted": baseline_domains is not None,
        "analysis_window_override": window_override,
        "analysis_sentence_threshold": sentence_threshold,
        "exposures_per_run":   exposures,
        "median_exposure_pct": median_exp,
        "mean_exposure_pct":   mean_exp,
        "min_exposure_pct":    min_exp,
        "max_exposure_pct":    max_exp,
        "stdev_exposure_pct":  stdev_exp,
        "ci95_low_pct":        ci_low,
        "ci95_high_pct":       ci_high,
        "ci95_half_width_pp":  ci_half_width,
        "reproducibility":     repro_label,
        "sentences_leaked_per_run":       sent_leaks,
        "median_sentences_leaked":        median_sentences_leaked,
        "total_sentences_in_document":    TOTAL_SENTENCES,
        "unique_sentences_leaked_any_run": sorted(union_sentences),
        "avg_https_event_pct": avg_https_pct,
        "total_tls_handshake_failures": total_tls_fail,
        "any_exposure":        any_exp,
        "sensitive_tokens_detected": all_sensitive,
        "sensitive_token_detection_rate": f"{tok_count}/{len(SENSITIVE_TOKENS)}",
        "avg_events":          round(statistics.mean(r["total_events"] for r in runs), 1),
        "avg_exposed_events":  round(statistics.mean(r["exposed_events"] for r in runs), 1),
        "avg_unique_domains":  round(statistics.mean(r["unique_domains"] for r in runs), 1),
        "avg_request_bytes":   round(statistics.mean(r["total_request_bytes"] for r in runs)),
        "avg_ws_messages":     round(statistics.mean(r["websocket_messages"] for r in runs), 1),
        "runs":                runs,
        "conclusion":          conclusion,
    }

    out_path = RESULTS_DIR / f"{tool_name}_summary.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    return summary


def print_tool_table(s):
    t = s["tool"].upper()
    sep = "=" * 70
    sub = "-" * 57
    print(f"\n{sep}")
    print(f"  {t}  (baseline subtracted: {s['baseline_subtracted']})")
    if s.get("analysis_window_override"):
        print(f"  [analysis: window={s['analysis_window_override']}, threshold={s['analysis_sentence_threshold']}]")
    print(sep)
    print(f"  Runs:                   {s['num_runs']}")
    print(f"  Exposure per run (%):   {[round(e,1) for e in s['exposures_per_run']]}")
    print(f"  Median exposure:        {s['median_exposure_pct']:.1f}%")
    print(f"  Mean exposure:          {s['mean_exposure_pct']:.1f}%  (95% CI [{s['ci95_low_pct']:.1f}%, {s['ci95_high_pct']:.1f}%])")
    print(f"  Std deviation:          {s['stdev_exposure_pct']:.1f} pp")
    print(f"  Min / Max:              {s['min_exposure_pct']:.1f}% / {s['max_exposure_pct']:.1f}%")
    print(f"  Reproducibility:        {s['reproducibility']} (stdev {s['stdev_exposure_pct']:.1f}pp)")
    print(f"  {sub}")
    print(f"  Sentences leaked/run:   {s['sentences_leaked_per_run']}")
    print(f"  Median sentences leaked: {s['median_sentences_leaked']:.0f} of {s['total_sentences_in_document']}")
    print(f"  Unique sentences (any run): {len(s['unique_sentences_leaked_any_run'])} of {s['total_sentences_in_document']}")
    print(f"  {sub}")
    print(f"  HTTPS event share:      {s['avg_https_event_pct']:.1f}% of intercepted events")
    print(f"  TLS handshake failures: {s['total_tls_handshake_failures']}  (missed traffic, if any)")
    print(f"  {sub}")
    print(f"  Sensitive tokens found: {s['sensitive_token_detection_rate']}")
    if s["sensitive_tokens_detected"]:
        for tok, count in s["sensitive_tokens_detected"].items():
            print(f"    [!]  '{tok}' - found in {count}/{s['num_runs']} runs")
    print(f"  {sub}")
    print(f"  Avg outbound events:    {s['avg_events']}")
    print(f"  Avg exposed events:     {s['avg_exposed_events']}")
    print(f"  Avg WS messages:        {s['avg_ws_messages']}")
    print(f"  Avg unique domains:     {s['avg_unique_domains']}")
    print(f"  Avg request bytes:      {s['avg_request_bytes']:,}")
    print(f"  {sub}")
    print(f"  CONCLUSION:")
    print(f"  {s['conclusion']}")
    print(sep)


def print_comparison_table(summaries):
    sep = "=" * 100
    print(f"\n{sep}")
    print("  COMPARISON TABLE  (all values after baseline subtraction)")
    print(sep)
    hdr = (
        "  " + "Tool".ljust(18) + "  " +
        "Median%".rjust(9) + "  " +
        "Mean% (95% CI)".rjust(22) + "  " +
        "Std Dev".rjust(9) + "  " +
        "Sent leak".rjust(11) + "  " +
        "Tokens".rjust(8)
    )
    print(hdr)
    print("  " + ("-" * 98))
    for s in summaries:
        ci = f"{s['mean_exposure_pct']:.1f} [{s['ci95_low_pct']:.1f}, {s['ci95_high_pct']:.1f}]"
        sent = f"{int(s['median_sentences_leaked'])}/{s['total_sentences_in_document']}"
        row = (
            "  " + str(s['tool']).ljust(18) + "  " +
            f"{s['median_exposure_pct']:8.1f}%".rjust(9) + "  " +
            ci.rjust(22) + "  " +
            f"{s['stdev_exposure_pct']:8.1f}pp".rjust(9) + "  " +
            sent.rjust(11) + "  " +
            str(s['sensitive_token_detection_rate']).rjust(8)
        )
        print(row)

    if len(summaries) >= 2:
        print("")
        print("  Pairwise 95% CI overlap (non-overlapping CIs suggest a real difference):")
        for i, a in enumerate(summaries):
            for b in summaries[i+1:]:
                overlap = not (a["ci95_high_pct"] < b["ci95_low_pct"]
                               or b["ci95_high_pct"] < a["ci95_low_pct"])
                if overlap:
                    tag = "overlap (no clear difference)"
                else:
                    tag = "DISJOINT (clear difference)"
                print("    " + str(a['tool']).ljust(15) + " vs " +
                      str(b['tool']).ljust(15) + "  " + tag)
    print(f"{sep}\n")


def make_comparison_chart(summaries, out_dir):
    """Produce a bar chart of mean exposure per tool with 95% CI error bars.
    Saves both PNG (for slides/screenshots) and SVG (for LaTeX inclusion).
    Silently skips if matplotlib is not installed.
    """
    try:
        import matplotlib
        matplotlib.use("Agg")  # no display needed
        import matplotlib.pyplot as plt
    except ImportError:
        print("[INFO] matplotlib not installed; skipping chart. "
              "Install: pip install --break-system-packages matplotlib")
        return None

    if not summaries:
        return None

    tools  = [s["tool"] for s in summaries]
    means  = [s["mean_exposure_pct"] for s in summaries]
    lows   = [s["ci95_low_pct"]  for s in summaries]
    highs  = [s["ci95_high_pct"] for s in summaries]
    # error bars are (mean - low, high - mean) for asymmetric CIs
    err_lo = [m - l for m, l in zip(means, lows)]
    err_hi = [h - m for h, m in zip(highs, means)]

    fig, ax = plt.subplots(figsize=(7, 4.2))
    bars = ax.bar(tools, means, yerr=[err_lo, err_hi], capsize=8,
                  color="#4C7AAF", edgecolor="black", linewidth=0.6)

    for bar, mean in zip(bars, means):
        ax.text(bar.get_x() + bar.get_width()/2, mean + 0.5,
                f"{mean:.1f}%", ha="center", va="bottom", fontsize=10)

    ax.set_ylabel("Exposure (% of document characters)")
    ax.set_title("Default-configuration exposure per tool\n"
                 "(error bars: 95% confidence interval over 5 runs)")
    ax.set_ylim(bottom=0)
    ax.grid(axis="y", linestyle=":", alpha=0.5)
    fig.tight_layout()

    png_path = out_dir / "comparison_chart.png"
    svg_path = out_dir / "comparison_chart.svg"
    fig.savefig(png_path, dpi=150)
    fig.savefig(svg_path)
    plt.close(fig)
    print(f"[INFO] Chart saved: {png_path}")
    print(f"[INFO] Chart saved: {svg_path}  (for LaTeX inclusion)")
    return png_path


def main():
    parser = argparse.ArgumentParser(
        description="Analyze mitmproxy capture data.",
        epilog=(
            "Sensitivity analysis examples:\n"
            "  Strict (default):   python scripts/analysis/analyze.py grammarly\n"
            "  Lenient:            python scripts/analysis/analyze.py grammarly --no-baseline --window 12 --sentence-threshold 0.5\n"
            "  Authoritative re-window (against raw .flow file):\n"
            "    WINDOW_SIZE=12 mitmdump -nr data/raw/grammarly/run_1.flow -s scripts/capture/capture_addon.py"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("tool", nargs="?", help="Tool name (e.g. grammarly)")
    parser.add_argument("--all",   action="store_true", help="Analyze all tools")
    parser.add_argument("--file",  help="Analyze a single run JSON file")
    parser.add_argument("--no-baseline", action="store_true",
                        help="Skip baseline domain subtraction (more lenient)")
    parser.add_argument("--window", type=int, default=None,
                        help="Re-derive coverage with a different window size. "
                             "Best-effort: uses 4 KB body_preview, not full payloads.")
    parser.add_argument("--sentence-threshold", type=float, default=0.9,
                        help="Fraction of a sentence's chars that must appear in coverage "
                             "for it to count as fully leaked (default 0.9; 0.5 = more lenient).")
    parser.add_argument("--chart", action="store_true",
                        help="Save a PNG/SVG comparison chart to results/ (requires matplotlib).")
    args = parser.parse_args()

    if args.window is not None and args.window < 4:
        print(f"[WARN] --window {args.window} is very small; expect false positives", file=sys.stderr)
    if not (0.0 < args.sentence_threshold <= 1.0):
        print(f"[ERROR] --sentence-threshold must be in (0, 1], got {args.sentence_threshold}", file=sys.stderr)
        sys.exit(1)

    subtract = not args.no_baseline
    win = args.window
    sthr = args.sentence_threshold

    if args.file:
        result = analyze_run(Path(args.file),
                             window_override=win, sentence_threshold=sthr)
        print(json.dumps(result, indent=2))

    elif args.all:
        summaries = []
        for tool in TOOLS:
            if tool == "baseline":
                continue
            s = analyze_tool(tool, subtract_baseline=subtract,
                             window_override=win, sentence_threshold=sthr)
            if s:
                summaries.append(s)
                print_tool_table(s)
        if summaries:
            print_comparison_table(summaries)
            out = RESULTS_DIR / "comparison.json"
            with open(out, "w", encoding="utf-8") as f:
                json.dump(summaries, f, indent=2)
            print(f"Comparison saved to: {out}")
            if args.chart:
                make_comparison_chart(summaries, RESULTS_DIR)

    elif args.tool:
        s = analyze_tool(args.tool, subtract_baseline=subtract,
                         window_override=win, sentence_threshold=sthr)
        if s:
            print_tool_table(s)
            if args.chart:
                make_comparison_chart([s], RESULTS_DIR)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
