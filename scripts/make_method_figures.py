#!/usr/bin/env python3
"""Generate annotated methodology diagrams (overview + browser phase + host phase +
detection pipeline). Outputs PNG (for review) and PDF (for the report) into
results/figures/ and report/figures/.
"""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ROOT = Path(__file__).resolve().parent.parent
OUT_PNG = ROOT / "results" / "figures"
OUT_PDF = ROOT / "report" / "figures"
OUT_PNG.mkdir(parents=True, exist_ok=True)
OUT_PDF.mkdir(parents=True, exist_ok=True)

LEAK = "#B23A48"; PROXY = "#2E5A6E"; SAFE = "#4C6663"; GREEN = "#2E7D5B"
INK = "#222222"; GREY = "#666666"

def box(ax, x, y, w, h, text, fc="#FFFFFF", ec=INK, tc=INK, fs=9, bold=False):
    p = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.4,rounding_size=2",
                       linewidth=1.3, edgecolor=ec, facecolor=fc, zorder=2)
    ax.add_patch(p)
    ax.text(x+w/2, y+h/2, text, ha="center", va="center", fontsize=fs,
            color=tc, zorder=3, fontweight=("bold" if bold else "normal"))

def arrow(ax, x1, y1, x2, y2, text=None, color=INK, fs=7.5, style="-|>", ls="-"):
    a = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style, mutation_scale=14,
                        linewidth=1.3, color=color, zorder=1, linestyle=ls,
                        shrinkA=2, shrinkB=2)
    ax.add_patch(a)
    if text:
        ax.text((x1+x2)/2, (y1+y2)/2+1.5, text, ha="center", va="bottom",
                fontsize=fs, color=color, style="italic", zorder=3)

def canvas(w=11, h=6):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")
    return fig, ax

def save(fig, name):
    fig.savefig(OUT_PNG / f"{name}.png", dpi=200, bbox_inches="tight")
    fig.savefig(OUT_PDF / f"{name}.pdf", bbox_inches="tight")
    plt.close(fig)
    print("wrote", name)

# ---------- Fig 1: Overview ----------
fig, ax = canvas(11, 6.2)
ax.text(2, 95, "Measurement pipeline (overview)", fontsize=13, fontweight="bold")
box(ax, 2, 66, 24, 20, "Synthetic memo\n12 planted secrets\n+ UUID canary", fc="#F3E9DA")
box(ax, 38, 66, 26, 20, "Tool under test\nbrowser extension /\ndesktop app / Office", fc="#FDECEC", ec=LEAK)
box(ax, 74, 66, 24, 20, "Vendor servers\ncapi.grammarly.com,\naugloop, www2.deepl.com", fc="#FDECEC", ec=LEAK, tc=LEAK)
box(ax, 38, 38, 26, 16, "mitmproxy\n127.0.0.1:8080\nHTTPS + WebSocket", fc="#E4EEF2", ec=PROXY, tc=PROXY, bold=True)
box(ax, 2, 8, 40, 20, "Capture add-on\ndecode gzip/brotli/zstd; match\nplain/base64/UTF-16; 20-char\nwindow + canary check", fc="#EAF2ED", ec=GREEN)
box(ax, 58, 8, 40, 20, "Per-run output\nExposure %, secrets found,\nper-host attribution,\nbaseline-subtracted", fc="#EEF0F0", ec=SAFE)

arrow(ax, 26, 76, 38, 76, "paste / open")
arrow(ax, 64, 76, 74, 76, "TLS")
arrow(ax, 51, 66, 51, 54, "intercept", color=PROXY)
arrow(ax, 51, 66.5, 51, 76, color=PROXY, style="<->", ls=(0,(3,2)))
arrow(ax, 38, 44, 22, 28, "decrypted flows", color=GREEN)
arrow(ax, 42, 18, 58, 18, "scored")
ax.text(51, 60, "CA trusted only in the isolated test profile", ha="center",
        fontsize=7, color=GREY, style="italic")
save(fig, "fig_method_overview")

# ---------- Fig 2: Browser phase ----------
fig, ax = canvas(11, 5.6)
ax.text(2, 95, "Browser phase (isolated Kali Linux VM)", fontsize=13, fontweight="bold")
box(ax, 2, 60, 30, 24, "Local page\nhttp://localhost\nsingle text field,\ncanary memo", fc="#F3E9DA")
box(ax, 40, 60, 26, 24, "Firefox profile\nGrammarly / LanguageTool\n(or no-extension baseline)", fc="#FDECEC", ec=LEAK)
box(ax, 74, 60, 24, 24, "mitmproxy\n127.0.0.1:8080", fc="#E4EEF2", ec=PROXY, tc=PROXY, bold=True)
box(ax, 74, 22, 24, 20, "Vendor servers\n(capi.grammarly.com,\napi.languagetool.org)", fc="#FDECEC", ec=LEAK, tc=LEAK)
box(ax, 8, 20, 46, 22, "Manual paste fires the DOM input event\n-> extension reads the field -> transmits.\nPositive control: example.com loads via proxy.",
    fc="#EEF0F0", ec=SAFE, fs=8.5)
arrow(ax, 32, 72, 40, 72, "paste")
arrow(ax, 66, 72, 74, 72, "HTTPS/WS")
arrow(ax, 86, 60, 86, 42, "out", color=PROXY)
save(fig, "fig_browser_phase")

# ---------- Fig 3: Host phase ----------
fig, ax = canvas(11, 5.8)
ax.text(2, 95, "Host phase (Windows 11)", fontsize=13, fontweight="bold")
box(ax, 2, 58, 30, 30,
    "Applications\nWord (augloop),\nDeepL desktop,\nEdge / Copilot,\nGrammarly desktop", fc="#FDECEC", ec=LEAK)
box(ax, 40, 66, 26, 16, "System proxy\nWinINET + WinHTTP\n-> 127.0.0.1:8080", fc="#E4EEF2", ec=PROXY, tc=PROXY, bold=True)
box(ax, 74, 66, 24, 16, "mitmproxy\n(same add-on)", fc="#E4EEF2", ec=PROXY, tc=PROXY)
box(ax, 74, 40, 24, 18, "Vendor servers\naugloop, capi,\nwww2.deepl.com,\ncopilot.microsoft.com", fc="#FDECEC", ec=LEAK, tc=LEAK)
box(ax, 6, 16, 60, 22,
    "WinHTTP is the key: native apps (Office, Grammarly desktop) bypass a\n"
    "browser-only (WinINET) proxy. Every flow is attributed to its destination\n"
    "host, so a leak is credited to the tool responsible, not to whatever else runs.",
    fc="#EEF0F0", ec=SAFE, fs=8)
arrow(ax, 32, 74, 40, 74)
arrow(ax, 66, 74, 74, 74)
arrow(ax, 86, 66, 86, 58, color=PROXY)
save(fig, "fig_host_phase")

# ---------- Fig 4: Detection pipeline ----------
fig, ax = canvas(11, 4.6)
ax.text(2, 92, "From captured traffic to an exposure number", fontsize=13, fontweight="bold")
box(ax, 1, 40, 20, 30, "Outbound\nrequest /\nresponse /\nWS frame", fc="#E4EEF2", ec=PROXY)
box(ax, 25, 40, 20, 30, "Decompress\ngzip / brotli /\nzstd", fc="#EAF2ED", ec=GREEN)
box(ax, 49, 40, 22, 30, "Decode variants\nplain, base64,\nUTF-16, URL,\nJSON, HTML", fc="#EAF2ED", ec=GREEN)
box(ax, 75, 40, 23, 30, "Match\n20-char window\n+ canary +\n12 secrets", fc="#EAF2ED", ec=GREEN, bold=True)
box(ax, 30, 4, 40, 22, "Exposure % (baseline-subtracted),\nsecrets found (x/12), per host", fc="#FDECEC", ec=LEAK, tc=LEAK)
for x in (21, 45, 71):
    arrow(ax, x, 55, x+4, 55)
arrow(ax, 86, 40, 55, 26, color=INK)
save(fig, "fig_detection_pipeline")

print("done")
