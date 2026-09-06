#!/usr/bin/env python3
"""
Traffic-over-time figure — the paste spike vs. background transmission.

For each tool we plot, on a common time axis, every captured event as a bar whose
height is its byte size and whose colour says whether it carried our document:
  * blue  = event carried document content (exposure_chars > 0 or a planted token)
  * grey  = other/background traffic (CDN, telemetry, browser update noise)

This visualises the supervisor's request: a single spike at the moment the document
is pasted, versus quiet/irrelevant background traffic the rest of the time. The
no-extension baseline shows background traffic but NO document-bearing (blue) event.

Direction: outbound events (http_request, websocket_client) are what carry data OUT
to a tool's servers — that is where a leak lives. We annotate the document spike with
its outbound byte size.

Uses one representative run per tool (run 1); all runs show the same pattern.

Outputs:
  report/figures/traffic_timeline.{png,pdf,svg}
  results/traffic_timeline.json   (timing of the document spike per tool)

Run:  python scripts/analysis/traffic_timeline.py
Stdlib + matplotlib.
"""

import json
import datetime as dt
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RAW = REPO / "data" / "raw"
RESULTS = REPO / "results"
FIGS = REPO / "report" / "figures"

TOOLS = [
    ("grammarly",    "Grammarly",              "run_1"),
    ("languagetool", "LanguageTool",           "run_1"),
    ("baseline",     "Baseline (no extension)", "run_1"),
]

OUTBOUND_KINDS = {"http_request", "websocket_client"}
BLUE = "#4C7AAF"
GREY = "#BBBBBB"


def load_run(tool, run):
    p = RAW / tool / f"{run}.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    t0 = dt.datetime.fromisoformat(d["start_time"])
    end = dt.datetime.fromisoformat(d["end_time"])
    dur = (end - t0).total_seconds()
    events = []
    for e in d.get("requests", []) + d.get("ws_messages", []):
        ts = dt.datetime.fromisoformat(e["timestamp"])
        off = (ts - t0).total_seconds()
        carries_doc = bool(e.get("tokens_found")) or (e.get("exposure_chars") or 0) > 0
        events.append({
            "t": off,
            "kind": e.get("kind"),
            "host": e.get("host") or "",
            "bytes": e.get("content_length") or 0,
            "exposure_chars": e.get("exposure_chars") or 0,
            "outbound": e.get("kind") in OUTBOUND_KINDS,
            "carries_doc": carries_doc,
        })
    events.sort(key=lambda x: x["t"])
    return d, events, dur


def make_figure():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch

    loaded = [(tool, label, *load_run(tool, run)) for tool, label, run in TOOLS]
    max_dur = max(item[4] for item in loaded)
    xmax = (int(max_dur // 10) + 1) * 10

    fig, axes = plt.subplots(len(TOOLS), 1, figsize=(7.6, 6.2), sharex=True)
    timing = {}

    for ax, (tool, label, d, events, dur) in zip(axes, loaded):
        # A leak is document content going OUT. Only outbound + document-bearing
        # events are coloured blue / eligible to be the annotated spike; an inbound
        # echo (http_response) that happens to contain the document is background,
        # not a "send". See docs/Review-Findings-2026-09-05.md (H6).
        doc_spike = None
        for e in events:
            is_leak = e["carries_doc"] and e["outbound"]
            color = BLUE if is_leak else GREY
            ax.bar(e["t"], e["bytes"], width=0.9, color=color,
                   edgecolor="none", zorder=3 if is_leak else 2)
            if is_leak and (doc_spike is None or e["bytes"] > doc_spike["bytes"]):
                doc_spike = e

        # y-axis in KB for readability
        ax.set_ylabel("Bytes")
        ax.set_xlim(0, xmax)
        ax.grid(axis="y", linestyle=":", alpha=0.4, zorder=0)
        ax.margins(y=0.18)

        # annotate the document spike (or its absence). Place text to the LEFT of
        # the spike so it never collides with the legend or the plot edge.
        if doc_spike is not None:
            ax.annotate(
                f"document sent to {doc_spike['host']}\n"
                f"({doc_spike['exposure_chars']} chars, {doc_spike['bytes']:,} B out)",
                xy=(doc_spike["t"], doc_spike["bytes"]),
                xytext=(doc_spike["t"] + xmax * 0.05, doc_spike["bytes"] * 0.92),
                fontsize=8.5, va="center", ha="left",
                arrowprops=dict(arrowstyle="->", color=BLUE, lw=1.3),
            )
            timing[tool] = {
                "document_spike_at_s": round(doc_spike["t"], 2),
                "outbound_bytes": doc_spike["bytes"],
                "exposure_chars": doc_spike["exposure_chars"],
                "host": doc_spike["host"],
            }
        else:
            ax.text(0.98, 0.80,
                    "no document-bearing traffic\n(background only — 0 chars leaked)",
                    transform=ax.transAxes, ha="right", va="center",
                    fontsize=9, color="#666666")
            timing[tool] = {"document_spike_at_s": None, "outbound_bytes": 0,
                            "exposure_chars": 0}

        ax.set_title(f"{label}", loc="left", fontsize=10, fontweight="bold")

    axes[-1].set_xlabel("Time since capture start (seconds)")
    fig.suptitle("Traffic over time — the paste spike vs. background\n"
                 "(representative run; blue = carried our document, grey = background)",
                 fontsize=11, y=0.99)

    legend = [Patch(facecolor=BLUE, label="Document-bearing traffic (outbound)"),
              Patch(facecolor=GREY, label="Background traffic")]
    axes[0].legend(handles=legend, loc="upper left", fontsize=8, framealpha=0.9)

    fig.tight_layout(rect=[0, 0, 1, 0.96])
    FIGS.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "pdf", "svg"):
        fig.savefig(FIGS / f"traffic_timeline.{ext}", dpi=150)
        print(f"[INFO] figure saved: {FIGS / f'traffic_timeline.{ext}'}")
    plt.close(fig)

    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "traffic_timeline.json").write_text(
        json.dumps({"representative_run": "run_1", "per_tool": timing}, indent=2),
        encoding="utf-8")
    print(f"[INFO] wrote {RESULTS / 'traffic_timeline.json'}")

    # console
    print("\nDocument spike timing (representative run):")
    for tool, label, *_ in [(t[0], t[1]) + (None,) for t in TOOLS]:
        info = timing[tool]
        if info["document_spike_at_s"] is not None:
            print(f"  {label:<26} t={info['document_spike_at_s']:>6}s  "
                  f"{info['outbound_bytes']:,} B out  ({info['exposure_chars']} chars)")
        else:
            print(f"  {label:<26} no document-bearing traffic")


if __name__ == "__main__":
    try:
        import matplotlib  # noqa
    except ImportError:
        raise SystemExit("matplotlib required: pip install --break-system-packages matplotlib")
    make_figure()
    print("Done.")
