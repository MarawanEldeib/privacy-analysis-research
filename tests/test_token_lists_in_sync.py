"""Guard against drift between the three copies of the planted-secret list.

`SENSITIVE_TOKENS` is declared in both scripts/capture/capture_addon.py and
scripts/analysis/analyze.py, and mirrored as the keys of SECRET_TAXONOMY in
scripts/analysis/info_type_breakdown.py. If one is edited but not the others,
detection/grouping breaks silently. We extract each list straight from the source
with `ast` (no imports, so this runs without mitmproxy) and assert they match.

Run from the repo root:  pytest
"""
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _assign_list(path: Path, name: str) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for tgt in node.targets:
                if isinstance(tgt, ast.Name) and tgt.id == name:
                    return [e.value for e in node.value.elts
                            if isinstance(e, ast.Constant)]
    raise AssertionError(f"{name} not found in {path}")


def _taxonomy_keys(path: Path, name: str = "SECRET_TAXONOMY") -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for tgt in node.targets:
                if isinstance(tgt, ast.Name) and tgt.id == name:
                    return [k.value for k in node.value.keys
                            if isinstance(k, ast.Constant)]
    raise AssertionError(f"{name} not found in {path}")


def test_capture_and_analyze_token_lists_identical():
    cap = _assign_list(ROOT / "scripts" / "capture" / "capture_addon.py", "SENSITIVE_TOKENS")
    ana = _assign_list(ROOT / "scripts" / "analysis" / "analyze.py", "SENSITIVE_TOKENS")
    assert cap == ana, (
        "SENSITIVE_TOKENS differ between capture_addon.py and analyze.py:\n"
        f"  only in capture:  {sorted(set(cap) - set(ana))}\n"
        f"  only in analyze:  {sorted(set(ana) - set(cap))}"
    )


def test_info_type_taxonomy_matches_token_list():
    ana = _assign_list(ROOT / "scripts" / "analysis" / "analyze.py", "SENSITIVE_TOKENS")
    tax = _taxonomy_keys(ROOT / "scripts" / "analysis" / "info_type_breakdown.py")
    assert set(tax) == set(ana), (
        "SECRET_TAXONOMY keys differ from analyze.SENSITIVE_TOKENS:\n"
        f"  missing from taxonomy: {sorted(set(ana) - set(tax))}\n"
        f"  extra in taxonomy:     {sorted(set(tax) - set(ana))}"
    )
