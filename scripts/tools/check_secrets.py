"""Pre-commit guard: refuse commits that add credentials.

Captures record the capture host's own auth traffic, and on 2026-09-14 live
Anthropic, Bitwarden and Google tokens were committed in data/raw and
published. capture_addon.py now redacts on save; this is the second line of
defence for anything that slips past it (older captures, manual edits).

Enabled per clone with:  git config core.hooksPath .githooks
Bypass for a verified false positive:  git commit --no-verify
"""
from __future__ import annotations

import re
import subprocess
import sys

BS = re.escape("\\")
PATTERNS = {
    "Anthropic key/OAuth token": re.compile(r"sk-ant-[a-z]{3}\d{2}-[A-Za-z0-9_\-]{20,}"),
    "OpenAI key": re.compile(r"sk-(?:proj|svcacct|admin)-[A-Za-z0-9_\-]{32,}|sk-[A-Za-z0-9]{40,}"),
    "GitHub token": re.compile(r"(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}"),
    "Google OAuth token": re.compile(r"ya29\.[0-9A-Za-z_\-]{30,}"),
    "JWT": re.compile(r"eyJ[A-Za-z0-9_\-]{10,}\.eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}"),
    "Bearer token": re.compile(r"(?i)bearer\s+(?!\[REDACTED\]|REDACTED)[A-Za-z0-9_\-\.=~+/]{20,}"),
    "OAuth token field": re.compile(
        "(?:access_token|refresh_token|id_token)" + BS + "?\"\\s*:\\s*" + BS + "?\"(?!\\[?REDACTED)[A-Za-z0-9_\\-\\.~+/=]{20,}"),
    "Session cookie": re.compile(r"(?i)(?:sessionKey|__Secure-[A-Za-z\-]+|grauth)=(?!\[REDACTED\])[A-Za-z0-9_\-%\.]{16,}"),
    "Private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |)PRIVATE KEY-----"),
}


def main() -> int:
    diff = subprocess.run(
        ["git", "diff", "--cached", "--no-color", "-U0", "--diff-filter=ACMR"],
        capture_output=True,
    ).stdout.decode("utf-8", "replace")
    findings = []
    path = "?"
    for line in diff.splitlines():
        if line.startswith("+++ b/"):
            path = line[6:]
            continue
        if not line.startswith("+") or line.startswith("+++"):
            continue
        for name, rx in PATTERNS.items():
            for m in rx.finditer(line):
                s = m.group(0)
                findings.append((path, name, s[:10] + "..." if len(s) > 14 else s))
    if not findings:
        return 0
    print("\n[check_secrets] Commit blocked - staged changes contain credentials:\n")
    for path, name, masked in findings[:25]:
        print(f"  {path}: {name} ({masked})")
    if len(findings) > 25:
        print(f"  ... and {len(findings) - 25} more")
    print("\nRedact them (capture_addon.redact_secrets) and re-stage.")
    print("If this is a verified false positive: git commit --no-verify\n")
    return 1


if __name__ == "__main__":
    sys.exit(main())
