#!/usr/bin/env python3
"""Regenerate the action-spectrum figure (PNG/SVG/PDF) with per-bar run counts (N).

Data source: results/action-spectrum.md. Browser writing-assistant conditions are
5-run means (sigma 0); host/desktop conditions are single-run probes (N=1). Labelling
N per bar prevents equal bar heights from being misread as equal statistical rigor.
"""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

# (label, exposure %, N runs, category)
#   category: "active"=user-invoked leak, "open"=leak on merely opening,
#             "mitigation"=leak switched off by a setting, "passive"=no leak
ROWS = [
    ("DeepL desktop (paste)",              99.6, 3, "active"),
    ("Grammarly (browser, paste)",         99.0, 5, "active"),
    ("Word: open .docx → augloop",    96.8, 3, "open"),
    ("Word: Protected View → Grammarly", 94.2, 2, "open"),
    ("LanguageTool (browser, paste)",      91.9, 5, "active"),
    ("Edge Copilot: PDF (invoked)",        76.9, 3, "active"),
    ("Word: Office AI disabled",            0.0, 1, "mitigation"),
    ("Edge: PDF open (not invoked)",        0.0, 1, "passive"),
    ("PDF in Chrome / Acrobat (open)",      0.0, 1, "passive"),
    (".txt/.md in Notepad (open)",          0.0, 1, "passive"),
    ("iCloud Drive drop (sync)",            0.0, 1, "passive"),
    ("USB inserted / baseline idle",        0.0, 1, "passive"),
]

LEAK = "#B23A48"      # matches \definecolor{leakred} in main.tex (user-invoked leak)
OPEN = "#E08E45"      # amber: leaks on merely opening the file
MITI = "#2E7D5B"      # green: mitigation (leak switched off)
SAFE = "#4C6663"      # muted teal-grey for 0% conditions
_CMAP = {"active": LEAK, "open": OPEN, "mitigation": MITI, "passive": SAFE}

# Horizontal, sorted high->low so leaking conditions stack at the top and the
# zero conditions read as a clean labelled list at the bottom (no empty-bar dead space).
rows = sorted(ROWS, key=lambda r: r[1])   # ascending -> barh draws largest at top
labels = [r[0] for r in rows]
vals   = [r[1] for r in rows]
ns     = [r[2] for r in rows]
colors = [_CMAP[r[3]] for r in rows]

fig, ax = plt.subplots(figsize=(7.2, 4.6))
y = range(len(rows))
ax.barh(list(y), vals, color=colors, edgecolor="black", linewidth=0.6, height=0.72)

for yi, v, n in zip(y, vals, ns):
    if v > 5:
        ax.text(v + 1.2, yi, f"{v:.1f}%  (N={n})", va="center", ha="left",
                fontsize=8.5, fontweight="bold")
    else:
        ax.text(1.2, yi, f"0%  (N={n})", va="center", ha="left",
                fontsize=8, color="#333333")

ax.set_xlabel("Document characters transmitted to external servers (%)")
ax.set_xlim(0, 118)
ax.set_yticks(list(y))
ax.set_yticklabels(labels, fontsize=8.5)
ax.set_title("Exposure by user action", fontsize=11, fontweight="bold", loc="left")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

legend = [Patch(facecolor=LEAK, edgecolor="black",
                label="User-invoked submission to a cloud AI service"),
          Patch(facecolor=OPEN, edgecolor="black",
                label="Leaks on merely opening the file (no submission)"),
          Patch(facecolor=MITI, edgecolor="black",
                label="Word leak with the Office AI setting disabled (mitigation)"),
          Patch(facecolor=SAFE, edgecolor="black",
                label="No document content transmitted (0%)")]
ax.legend(handles=legend, loc="lower right", fontsize=7.5, framealpha=0.95)

fig.text(0.01, 0.005,
         "N = independent capture runs per condition (browser writing assistants 5 runs, "
         "sigma 0; Word/DeepL/Edge-Copilot 2-3 runs; other host probes single-run).",
         fontsize=6.8, color="#555555")

plt.tight_layout(rect=[0, 0.03, 1, 1])

root = Path(__file__).resolve().parent.parent
outs = {
    root / "results" / "action_spectrum.png": dict(dpi=200),
    root / "results" / "action_spectrum.svg": dict(),
    root / "report" / "figures" / "action_spectrum.pdf": dict(),
}
for path, kw in outs.items():
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, bbox_inches="tight", **kw)
    print("wrote", path)
