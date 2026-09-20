#!/usr/bin/env bash
# Generate slide-list.txt and, when Elephant Scale slide tooling is available,
# assemble Markdown decks into presentation files.

set -u

cd "$(dirname "$0")"
ls [0-9][0-9]-*.md | sort > slide-list.txt

if [ -n "${ES_HOME:-}" ] && [ -x "$ES_HOME/utils/presentations/slides-assembler.sh" ]; then
  "$ES_HOME/utils/presentations/slides-assembler.sh" slide-list.txt
  if [ -d assembly.out ]; then
    ( cd assembly.out && for f in [0-9][0-9]__*; do
        [ -e "$f" ] || continue
        mv -- "$f" "${f#*__}"
      done )
  fi
else
  echo "slide-list.txt generated. Set ES_HOME to assemble PPTX decks."
fi
