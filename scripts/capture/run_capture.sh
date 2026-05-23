#!/usr/bin/env bash
# run_capture.sh — Start a mitmproxy capture session for one tool + run
#
# Usage:
#   ./scripts/capture/run_capture.sh grammarly 1
#   ./scripts/capture/run_capture.sh prowritingaid 2
#   ./scripts/capture/run_capture.sh wordtune 1
#   ./scripts/capture/run_capture.sh baseline 1   ← run with NO extension active
#
# Arguments:
#   $1 = tool name (grammarly | prowritingaid | wordtune | baseline)
#   $2 = run ID (1-5)

set -e

TOOL_NAME="${1:-unknown}"
RUN_ID="${2:-1}"

# Validate tool name so typos don't silently create new data directories
VALID_TOOLS=("grammarly" "prowritingaid" "wordtune" "baseline")
if [[ ! " ${VALID_TOOLS[*]} " =~ " ${TOOL_NAME} " ]]; then
    echo "ERROR: Unknown tool '${TOOL_NAME}'. Valid: ${VALID_TOOLS[*]}" >&2
    exit 1
fi
if ! [[ "$RUN_ID" =~ ^[1-5]$ ]]; then
    echo "ERROR: RUN_ID must be 1-5, got '${RUN_ID}'" >&2
    exit 1
fi

# Move to project root (script is in scripts/capture/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "=============================================="
echo " Starting capture session"
echo " Tool:    $TOOL_NAME"
echo " Run ID:  $RUN_ID"
echo " Proxy:   127.0.0.1:8080"
echo "=============================================="
echo ""
echo "BEFORE starting mitmproxy:"
echo "  1. Open Firefox with the CLEAN profile for this tool"
echo "  2. Make sure ONLY the $TOOL_NAME extension is active"
echo "  3. Have the test document ready to paste:"
echo "     $PROJECT_ROOT/input-data/test-document.txt"
echo ""
echo "Press ENTER when Firefox is ready..."
read -r

echo "Starting mitmproxy... (press q to stop and save)"
echo ""

cd "$PROJECT_ROOT"

# Ensure the per-tool data directory exists so --save-stream-file can write into it.
RAW_DIR="$PROJECT_ROOT/data/raw/$TOOL_NAME"
mkdir -p "$RAW_DIR"
FLOW_PATH="$RAW_DIR/run_$RUN_ID.flow"

TOOL_NAME="$TOOL_NAME" RUN_ID="$RUN_ID" \
    mitmdump \
    --listen-host 127.0.0.1 \
    --listen-port 8080 \
    --ssl-insecure \
    --save-stream-file "$FLOW_PATH" \
    -s scripts/capture/capture_addon.py

echo ""
echo "Capture complete. Results saved to:"
echo "  $RAW_DIR/run_$RUN_ID.json    ← analyzed summary"
echo "  $FLOW_PATH    ← full raw archive (re-analyzable offline)"
echo ""
echo "To re-analyze the raw archive against an updated addon:"
echo "  TOOL_NAME=$TOOL_NAME RUN_ID=$RUN_ID mitmdump -nr $FLOW_PATH -s scripts/capture/capture_addon.py"
