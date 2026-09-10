#!/usr/bin/env python3
"""
Level 2 — automatic PII discovery over decrypted outbound traffic (Microsoft Presidio).

Goes beyond the 12 planted secrets (Level 1): runs Presidio's PII detector over the
outbound bodies the tools actually transmitted, and reports every personal-data entity it
finds, split into:
  * PLANTED   — matches one of our 12 known secrets (expected)
  * UNPLANTED — anything else Presidio flags (candidates for manual review)

Presidio is statistical, so UNPLANTED hits are candidates, not confirmed leaks — each
should be eyeballed (false positives/negatives are normal). Reads the outbound bodies from
data/raw/<tool>/run_*.json (body_preview of http_request + websocket_client events).

Outputs: results/level2_presidio.{json,md}
"""
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyze import SENSITIVE_TOKENS  # noqa: E402

RAW = REPO / "data" / "raw"
RESULTS = REPO / "results"
TOOLS = ["grammarly", "languagetool"]          # the automatic leakers
OUTBOUND = {"http_request", "websocket_client"}

from presidio_analyzer import AnalyzerEngine                     # noqa: E402
from presidio_analyzer.nlp_engine import NlpEngineProvider       # noqa: E402

_cfg = {"nlp_engine_name": "spacy",
        "models": [{"lang_code": "en", "model_name": "en_core_web_sm"}]}
ANALYZER = AnalyzerEngine(nlp_engine=NlpEngineProvider(nlp_configuration=_cfg).create_engine())

PLANTED_LC = {s.lower() for s in SENSITIVE_TOKENS}


def outbound_bodies(tool):
    bodies = []
    for f in sorted((RAW / tool).glob("run_*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        for e in d.get("requests", []) + d.get("ws_messages", []):
            if e.get("kind") in OUTBOUND:
                bp = e.get("body_preview") or ""
                if bp:
                    bodies.append(bp)
    # de-duplicate identical payloads
    return list(dict.fromkeys(bodies))


def analyze_tool(tool):
    bodies = outbound_bodies(tool)
    by_type = {}          # entity_type -> set of texts
    for text in bodies:
        for r in ANALYZER.analyze(text=text, language="en"):
            frag = text[r.start:r.end].strip()
            if not frag:
                continue
            by_type.setdefault(r.entity_type, {})
            # keep the max score seen for each distinct fragment
            prev = by_type[r.entity_type].get(frag, 0.0)
            by_type[r.entity_type][frag] = max(prev, round(r.score, 2))
    # split planted vs unplanted
    planted, unplanted = [], []
    for etype, frags in by_type.items():
        for frag, score in frags.items():
            is_planted = any(p in frag.lower() or frag.lower() in p for p in PLANTED_LC)
            rec = {"type": etype, "text": frag, "score": score}
            (planted if is_planted else unplanted).append(rec)
    return {"bodies_scanned": len(bodies),
            "planted_hits": sorted(planted, key=lambda x: x["type"]),
            "unplanted_hits": sorted(unplanted, key=lambda x: (x["type"], -x["score"]))}


def main():
    out = {"note": ("Presidio (en_core_web_sm) over outbound bodies. UNPLANTED hits are "
                    "candidates requiring manual review, not confirmed leaks."),
           "planted_secret_count": len(SENSITIVE_TOKENS), "per_tool": {}}
    for t in TOOLS:
        out["per_tool"][t] = analyze_tool(t)

    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "level2_presidio.json").write_text(json.dumps(out, indent=2), encoding="utf-8")

    lines = ["# Level 2 — Presidio PII discovery (outbound traffic)\n",
             out["note"], ""]
    for t in TOOLS:
        r = out["per_tool"][t]
        lines.append(f"## {t}  ({r['bodies_scanned']} outbound bodies scanned)\n")
        lines.append(f"**Planted PII detected (expected):** {len(r['planted_hits'])} entity instances")
        ptypes = sorted({h['type'] for h in r['planted_hits']})
        lines.append(f"- types: {', '.join(ptypes) if ptypes else '(none)'}\n")
        lines.append(f"**UNPLANTED PII candidates (review):** {len(r['unplanted_hits'])}")
        if r["unplanted_hits"]:
            lines.append("| type | detected text | score |")
            lines.append("|---|---|---|")
            for h in r["unplanted_hits"]:
                txt = h["text"] if len(h["text"]) <= 60 else h["text"][:57] + "..."
                lines.append(f"| {h['type']} | `{txt}` | {h['score']} |")
        else:
            lines.append("- none beyond the planted secrets.")
        lines.append("")
    (RESULTS / "level2_presidio.md").write_text("\n".join(lines), encoding="utf-8")

    # console summary
    for t in TOOLS:
        r = out["per_tool"][t]
        print(f"{t}: {r['bodies_scanned']} bodies | planted={len(r['planted_hits'])} "
              f"| unplanted={len(r['unplanted_hits'])}")
    print("Wrote results/level2_presidio.{json,md}")


if __name__ == "__main__":
    main()
