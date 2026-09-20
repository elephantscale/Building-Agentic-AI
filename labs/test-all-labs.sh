#!/usr/bin/env bash
# Quick structural check that every lab guide exists and is non-trivial.
set -u
LABS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fail=0
for d in "$LABS_DIR"/[0-9][0-9]-*/; do
  f="$d/README.md"
  if [ -f "$f" ] && [ "$(wc -l < "$f")" -gt 20 ]; then
    echo "PASS  $(basename "$d")"
  else
    echo "FAIL  $(basename "$d") (missing or too short)"; fail=1
  fi
done
exit $fail
