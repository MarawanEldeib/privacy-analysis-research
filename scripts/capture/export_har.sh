#!/usr/bin/env bash
#
# export_har.sh — convert every captured mitmproxy .flow into a .har file.
#
# WHY: HAR is a portable JSON format that other tools (HTTP Toolkit, Fluxzy,
# Proxyman, browser devtools) can open. We use it to view our EXISTING captures
# in HTTP Toolkit's nicer UI for report/slide screenshots — same data, prettier
# rendering. It is a presentation/viewer step, NOT a new measurement.
#
# WHERE TO RUN: inside the Kali VM where mitmproxy 12.x is installed and the
# .flow files live (repo mounted at /media/sf_privacy_analysis). Do NOT run on
# Windows — mitmdump is only in the VM.
#
# SECURITY: the .har files contain DECRYPTED traffic including auth tokens, exactly
# like the .flow files. They are gitignored (data/raw/*/run_*.har and *.har).
# Keep them LOCAL. Redact tokens before putting any screenshot in the report.
#
# USAGE:
#   bash scripts/capture/export_har.sh            # convert all .flow -> .har
#   bash scripts/capture/export_har.sh grammarly  # only one tool's folder
#
set -euo pipefail

REPO="$(cd "$(dirname "$0")/../.." && pwd)"
RAW="$REPO/data/raw"

if ! command -v mitmdump >/dev/null 2>&1; then
  echo "ERROR: mitmdump not found. Run this inside the Kali VM (mitmproxy installed there)." >&2
  exit 1
fi

echo "mitmproxy: $(mitmdump --version 2>&1 | head -1)"

# Optional first arg = tool subfolder filter (e.g. grammarly, languagetool, baseline)
FILTER="${1:-}"
if [[ -n "$FILTER" ]]; then
  search_root="$RAW/$FILTER"
else
  search_root="$RAW"
fi

count=0
while IFS= read -r -d '' flow; do
  har="${flow%.flow}.har"
  echo "  $flow  ->  $har"
  # -n: no proxy server, -r: read flows, -q: quiet; hardump writes the HAR on exit.
  mitmdump -q -n -r "$flow" --set hardump="$har"
  count=$((count + 1))
done < <(find "$search_root" -type f -name '*.flow' -print0 | sort -z)

echo "Done. Converted $count flow file(s) to HAR."
echo "Reminder: .har files hold decrypted tokens — keep them local, redact before screenshots."
