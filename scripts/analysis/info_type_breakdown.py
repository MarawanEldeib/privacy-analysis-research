#!/usr/bin/env python3
"""
Level-1 information-type breakdown.

Takes the per-token detection already computed by analyze.py (stored in
results/<tool>_summary.json under "sensitive_tokens_detected") and groups the
12 planted secrets into information *types* (names, contact details, official
IDs, financial codes, legal references, confidential project identifiers, and
the canary proof-token). For each tool it reports, per type, how many of that
type's planted items were transmitted to the tool's servers.

This answers the supervisor's request to "classify the types of information"
that leak, using data we already have — no new captures required.

Outputs:
  results/info_type_breakdown.json   machine-readable
  results/info_type_breakdown.md     human-readable table
  report/figures/info_type_breakdown.{png,pdf,svg}   figure for the report

Run:  python scripts/analysis/info_type_breakdown.py
Stdlib + matplotlib only (matplotlib optional; the figure is skipped if absent).
"""

import json
import sys
from pathlib import Path

# Single source of truth for the token list: import it from analyze.py and assert
# our taxonomy covers exactly those tokens, so a rename in one place can never
# silently make this script report an item as 0/… . See Review-Findings (M1).
sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyze import SENSITIVE_TOKENS  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
RESULTS = REPO / "results"
FIGS = REPO / "report" / "figures"

TOOLS = ["grammarly", "languagetool", "baseline"]
TOOL_LABELS = {
    "grammarly": "Grammarly",
    "languagetool": "LanguageTool",
    "baseline": "Baseline\n(no extension)",
}

# --- The taxonomy: each planted secret -> (information type, plain description) ---
# Order of TYPES controls row order in the table/figure.
TYPES = [
    "Names (direct identifiers)",
    "Contact details",
    "Official / ID numbers",
    "Financial identifiers",
    "Legal / contractual references",
    "Confidential project identifiers",
    "Canary proof-token",
]

SECRET_TAXONOMY = {
    "Helena Voss":                                    ("Names (direct identifiers)",       "Author / compliance officer name"),
    "Theodora Baumgartner-Klein":                     ("Names (direct identifiers)",       "External legal counsel name"),
    "theodora.baumgartner@priv-research-demo.invalid": ("Contact details",                 "Email address"),
    "+49 30 4827-9153":                               ("Contact details",                  "Phone number"),
    "HV-2026-391847":                                 ("Official / ID numbers",            "Employee ID"),
    "DE-291-847-3309":                                ("Official / ID numbers",            "Tax registration number"),
    "XREF-291-ALPHA":                                 ("Financial identifiers",            "Q1 expenditure reference"),
    "NHK3-RES-7741":                                  ("Financial identifiers",            "Reserve fund code"),
    "AC-2026-00293-DELTA":                            ("Financial identifiers",            "Budget approval code"),
    "2026-LGL-00847":                                 ("Legal / contractual references",   "Contract / matter number"),
    "Project Nighthawk-3":                            ("Confidential project identifiers", "Project codename"),
    "CANARY-BC267061-67DC-485B-8E51-6F5494765CAB":    ("Canary proof-token",               "Unique leak-proof marker"),
}

# Fail loudly if the taxonomy drifts out of sync with the canonical token list.
_missing = set(SENSITIVE_TOKENS) - set(SECRET_TAXONOMY)
_extra   = set(SECRET_TAXONOMY) - set(SENSITIVE_TOKENS)
if _missing or _extra:
    raise SystemExit(
        "SECRET_TAXONOMY is out of sync with analyze.SENSITIVE_TOKENS.\n"
        f"  missing from taxonomy: {sorted(_missing)}\n"
        f"  not in token list:     {sorted(_extra)}\n"
        "Update SECRET_TAXONOMY to match analyze.py."
    )


def load_detection(tool):
    """Return {token: times_detected, ...} and num_runs for a tool."""
    f = RESULTS / f"{tool}_summary.json"
    if not f.exists():
        raise SystemExit(
            f"Missing {f.name}. Run:  python scripts/analysis/analyze.py --all  first."
        )
    d = json.loads(f.read_text(encoding="utf-8"))
    detected = d.get("sensitive_tokens_detected", {}) or {}
    return detected, d.get("num_runs", 0)


def build():
    # items per type
    items_by_type = {t: [] for t in TYPES}
    for token, (typ, desc) in SECRET_TAXONOMY.items():
        items_by_type[typ].append(token)

    per_tool = {}
    for tool in TOOLS:
        detected, num_runs = load_detection(tool)
        rows = {}
        for typ in TYPES:
            toks = items_by_type[typ]
            # an item counts as "exposed" if it was detected in >=1 run
            n_exposed = sum(1 for tk in toks if detected.get(tk, 0) > 0)
            rows[typ] = {
                "items_total": len(toks),
                "items_exposed": n_exposed,
                "pct": round(100.0 * n_exposed / len(toks), 1) if toks else 0.0,
            }
        total_items = len(SECRET_TAXONOMY)
        total_exposed = sum(1 for tk in SECRET_TAXONOMY if detected.get(tk, 0) > 0)
        per_tool[tool] = {
            "num_runs": num_runs,
            "by_type": rows,
            "overall_exposed": total_exposed,
            "overall_total": total_items,
        }
    return items_by_type, per_tool


def write_json(items_by_type, per_tool):
    out = {
        "taxonomy": {
            typ: [{"secret": tk, "description": SECRET_TAXONOMY[tk][1]} for tk in toks]
            for typ, toks in items_by_type.items()
        },
        "per_tool": per_tool,
        "note": (
            "An information type counts as exposed for a tool if at least one of "
            "its planted items appeared in that tool's outbound traffic in >=1 run. "
            "Detection data is reused from results/<tool>_summary.json."
        ),
    }
    p = RESULTS / "info_type_breakdown.json"
    p.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"[INFO] wrote {p}")


def write_md(items_by_type, per_tool):
    lines = []
    lines.append("# Level 1 — Information-type breakdown\n")
    lines.append("What *kinds* of information each tool transmitted, grouped from the "
                 "12 planted secrets. A type is \"exposed\" if at least one of its items "
                 "was seen in the tool's outbound traffic (in ≥1 of the runs).\n")
    # summary table
    lines.append("## Exposure by information type\n")
    header = "| Information type | Items | Grammarly | LanguageTool | Baseline |"
    sep = "|---|---|---|---|---|"
    lines.append(header)
    lines.append(sep)
    for typ in TYPES:
        n = per_tool["grammarly"]["by_type"][typ]["items_total"]
        cells = []
        for tool in TOOLS:
            r = per_tool[tool]["by_type"][typ]
            cells.append(f"{r['items_exposed']}/{r['items_total']}")
        lines.append(f"| {typ} | {n} | {cells[0]} | {cells[1]} | {cells[2]} |")
    # overall
    g = per_tool["grammarly"]; l = per_tool["languagetool"]; b = per_tool["baseline"]
    lines.append(f"| **All types (total)** | **{g['overall_total']}** | "
                 f"**{g['overall_exposed']}/{g['overall_total']}** | "
                 f"**{l['overall_exposed']}/{l['overall_total']}** | "
                 f"**{b['overall_exposed']}/{b['overall_total']}** |")
    lines.append("")
    # taxonomy detail
    lines.append("## What is in each type\n")
    for typ in TYPES:
        lines.append(f"**{typ}**")
        for tk in items_by_type[typ]:
            lines.append(f"- {SECRET_TAXONOMY[tk][1]} — `{tk}`")
        lines.append("")
    lines.append("## Reading of the result\n")
    lines.append("Both writing assistants transmitted **every** information type in the "
                 "document — personal names, contact details, official ID numbers, financial "
                 "codes, a legal contract reference, the confidential project codename, and the "
                 "unique canary. The no-extension baseline transmitted none. The leak is therefore "
                 "not limited to a particular class of data (e.g. only free text): structured "
                 "identifiers and regulated personal data are exfiltrated just as readily as prose.\n")
    p = RESULTS / "info_type_breakdown.md"
    p.write_text("\n".join(lines), encoding="utf-8")
    print(f"[INFO] wrote {p}")


def make_figure(per_tool):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.colors import LinearSegmentedColormap
        import numpy as np
    except ImportError:
        print("[INFO] matplotlib not installed; skipping figure. "
              "Install: pip install --break-system-packages matplotlib")
        return

    # matrix: rows = types, cols = tools; value = pct of that type's items exposed
    row_labels = TYPES + ["All types"]
    col_order = ["grammarly", "languagetool", "baseline"]
    col_labels = [TOOL_LABELS[t] for t in col_order]

    mat = []
    annot = []
    for typ in TYPES:
        row_v, row_a = [], []
        for tool in col_order:
            r = per_tool[tool]["by_type"][typ]
            row_v.append(r["pct"])
            row_a.append(f"{r['items_exposed']}/{r['items_total']}")
        mat.append(row_v)
        annot.append(row_a)
    # overall row
    row_v, row_a = [], []
    for tool in col_order:
        o = per_tool[tool]
        pct = round(100.0 * o["overall_exposed"] / o["overall_total"], 1)
        row_v.append(pct)
        row_a.append(f"{o['overall_exposed']}/{o['overall_total']}")
    mat.append(row_v)
    annot.append(row_a)

    mat = np.array(mat)

    # white -> project blue colormap so 100% is the strong brand blue, 0% is white
    cmap = LinearSegmentedColormap.from_list("exposure", ["#FFFFFF", "#4C7AAF"])

    fig, ax = plt.subplots(figsize=(7.4, 4.6))
    im = ax.imshow(mat, cmap=cmap, vmin=0, vmax=100, aspect="auto")

    ax.set_xticks(range(len(col_labels)))
    ax.set_xticklabels(col_labels, fontsize=9)
    ax.set_yticks(range(len(row_labels)))
    ax.set_yticklabels(row_labels, fontsize=9)

    # separate the "All types" summary row visually
    ax.axhline(len(TYPES) - 0.5, color="black", linewidth=1.0)

    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            val = mat[i, j]
            txt_color = "white" if val >= 55 else "#333333"
            ax.text(j, i, annot[i][j], ha="center", va="center",
                    fontsize=9, color=txt_color,
                    fontweight="bold" if i == len(TYPES) else "normal")

    ax.set_title("Information types transmitted, by tool\n"
                 "(planted items exposed / items in type; ≥1 run)", fontsize=11)
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.03)
    cbar.set_label("% of type's items exposed", fontsize=9)

    ax.set_xticks([x - 0.5 for x in range(1, len(col_labels))], minor=True)
    ax.set_yticks([y - 0.5 for y in range(1, len(row_labels))], minor=True)
    ax.grid(which="minor", color="white", linewidth=1.2)
    ax.tick_params(which="minor", length=0)

    fig.tight_layout()
    FIGS.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "pdf", "svg"):
        path = FIGS / f"info_type_breakdown.{ext}"
        fig.savefig(path, dpi=150)
        print(f"[INFO] figure saved: {path}")
    plt.close(fig)


def main():
    items_by_type, per_tool = build()
    write_json(items_by_type, per_tool)
    write_md(items_by_type, per_tool)
    make_figure(per_tool)

    # console summary
    print("\nInformation-type breakdown (items exposed / items in type):")
    print(f"{'Type':<36} {'Gram':>6} {'LT':>6} {'Base':>6}")
    for typ in TYPES:
        g = per_tool['grammarly']['by_type'][typ]
        l = per_tool['languagetool']['by_type'][typ]
        b = per_tool['baseline']['by_type'][typ]
        print(f"{typ:<36} {g['items_exposed']}/{g['items_total']:<4} "
              f"{l['items_exposed']}/{l['items_total']:<4} {b['items_exposed']}/{b['items_total']:<4}")
    print("Done.")


if __name__ == "__main__":
    main()
