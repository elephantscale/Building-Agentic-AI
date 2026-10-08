#!/usr/bin/env bash
# Pre-flight slide check — run BEFORE going to the Mac to build PPTX.
#
# For every slides/NN-*.md it does a throwaway md2pptx conversion in a temp dir and reports:
#   OK       - converts cleanly, all referenced images resolve
#   IMG?     - converts, but one or more ../images/* files are missing
#   CRASH    - the converter raised (e.g. a Notes: line with inline text -> KeyError)
#
# It does NOT build or touch your real decks or slides/assembly.out — Mark builds PPTX on the Mac.
# Exit status is non-zero if any deck CRASHES, so this is CI-friendly.
#
# Usage:  ./scripts/check-slides.sh            # all decks
#         ./scripts/check-slides.sh 00 04      # only decks whose number matches

set -u
cd "$(dirname "$0")/.." || exit 2
REPO="$PWD"
CONV="/home/mark/projects/ES/utils/presentations/md2pptx.py"
[ -f "$CONV" ] || CONV="/media/mark/data1/ES/utils/presentations/md2pptx.py"

if [ ! -f "$CONV" ]; then
  echo "md2pptx.py not found (looked in ES/utils/presentations). Skipping — build on the Mac." >&2
  exit 0
fi

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
mkdir -p "$tmp/slides"
ln -sfn "$REPO/images" "$tmp/images"   # so ../images/* resolves exactly as in slides/

filter="${*:-}"
fail=0; n=0
printf '%-34s %s\n' "DECK" "RESULT"
printf '%-34s %s\n' "----" "------"

for md in slides/[0-9][0-9]-*.md; do
  [ -e "$md" ] || continue
  base="$(basename "$md")"
  if [ -n "$filter" ]; then
    num="${base%%-*}"; match=0
    for want in $filter; do [ "$num" = "$want" ] || [ "${want}" = "$base" ] && match=1; done
    [ "$match" = 1 ] || continue
  fi
  n=$((n+1))
  cp "$md" "$tmp/slides/1.md"
  rm -f "$tmp/slides/"*.pptx
  out="$(cd "$tmp/slides" && python3 "$CONV" ./1.md 2>&1)"
  rc=$?
  if [ $rc -ne 0 ] || printf '%s' "$out" | grep -qi "traceback"; then
    printf '%-34s \033[31mCRASH\033[0m\n' "$base"
    printf '%s\n' "$out" | grep -iE "error|keyerror|traceback" | tail -2 | sed 's/^/    /'
    fail=$((fail+1))
  elif printf '%s' "$out" | grep -qi "not found"; then
    printf '%-34s \033[33mIMG?\033[0m  (missing image ref)\n' "$base"
    printf '%s' "$out" | grep -i "not found" | sed 's#.*/images/#    missing: #'
  else
    printf '%-34s \033[32mOK\033[0m\n' "$base"
  fi
done

echo
if [ "$fail" -gt 0 ]; then
  echo "$fail deck(s) CRASH — fix before the Mac trip."
  exit 1
fi
echo "$n deck(s) checked, no crashes. Safe to build on the Mac."
