#!/usr/bin/env bash
# device_permissions.sh — snapshot what a running desktop tool can actually access.
#
# Vendor-independent evidence for the desktop/system-level phase: for a given
# process, record which sensitive devices and files it currently holds open —
# microphone, camera, USB/removable mounts, and its open file descriptors.
#
# Usage:
#   scripts/capture/device_permissions.sh <process-name-or-pid> [tool_label]
#
# Examples:
#   scripts/capture/device_permissions.sh java languagetool_desktop
#   scripts/capture/device_permissions.sh 12345 avast_linux
#
# Writes a timestamped report to results/permissions/<tool_label>_<pid>.txt
# and also prints it to stdout. Read-only; changes nothing on the system.
set -euo pipefail

ARG="${1:-}"
LABEL="${2:-tool}"
if [[ -z "$ARG" ]]; then
  echo "usage: $0 <process-name-or-pid> [tool_label]" >&2
  exit 1
fi

# Resolve to a PID (accept a numeric pid or a process name).
if [[ "$ARG" =~ ^[0-9]+$ ]]; then
  PID="$ARG"
else
  PID="$(pgrep -n -f "$ARG" || true)"
fi
if [[ -z "${PID:-}" || ! -d "/proc/$PID" ]]; then
  echo "No running process matched '$ARG'." >&2
  exit 1
fi

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
OUT_DIR="$REPO/results/permissions"
mkdir -p "$OUT_DIR"
TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
OUT="$OUT_DIR/${LABEL}_${PID}.txt"

{
  echo "# Device / access permissions snapshot"
  echo "tool_label : $LABEL"
  echo "pid        : $PID"
  echo "process    : $(tr '\0' ' ' < "/proc/$PID/cmdline" 2>/dev/null || echo '?')"
  echo "captured   : $TS (UTC)"
  echo

  echo "## Audio (microphone)"
  # Any fd pointing at an ALSA capture/playback device, and PulseAudio source-outputs.
  if ls -l "/proc/$PID/fd" 2>/dev/null | grep -q '/dev/snd/'; then
    echo "OPEN: process holds an ALSA /dev/snd/* handle:"
    ls -l "/proc/$PID/fd" 2>/dev/null | grep '/dev/snd/' || true
  else
    echo "none: no /dev/snd/* handle held right now."
  fi
  if command -v pactl >/dev/null 2>&1; then
    echo "-- pactl source-outputs (active mic streams system-wide) --"
    pactl list source-outputs 2>/dev/null | grep -E 'Source Output|application.name|application.process.id' || echo "  (none)"
  fi
  echo

  echo "## Camera"
  if ls -l "/proc/$PID/fd" 2>/dev/null | grep -q '/dev/video'; then
    echo "OPEN: process holds a /dev/video* handle:"
    ls -l "/proc/$PID/fd" 2>/dev/null | grep '/dev/video' || true
  else
    echo "none: no /dev/video* handle held right now."
  fi
  echo

  echo "## Removable / USB mounts the process has open"
  # Files open under common removable-media mount points.
  OPEN_MEDIA="$(ls -l "/proc/$PID/fd" 2>/dev/null | grep -E '/media/|/mnt/|/run/media/' || true)"
  if [[ -n "$OPEN_MEDIA" ]]; then
    echo "OPEN: process has file handles under a removable mount:"
    echo "$OPEN_MEDIA"
  else
    echo "none: no open handles under /media, /mnt, or /run/media right now."
  fi
  echo

  echo "## All open file descriptors (regular files + devices)"
  ls -l "/proc/$PID/fd" 2>/dev/null | sed 's/^/  /' || echo "  (unreadable — try sudo)"
  echo

  echo "## Sockets / network endpoints held (for cross-check with capture)"
  if command -v ss >/dev/null 2>&1; then
    ss -tanp 2>/dev/null | grep "pid=$PID," || echo "  (no TCP sockets attributed to this pid via ss)"
  else
    echo "  ss not available"
  fi
} | tee "$OUT"

echo
echo "Saved: $OUT"
