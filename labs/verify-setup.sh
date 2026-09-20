#!/usr/bin/env bash
# verify-setup.sh - quick pre-flight for the Building Agentic AI labs.
set -u
if [ -t 1 ]; then G=$'\e[32m'; R=$'\e[31m'; Y=$'\e[33m'; B=$'\e[1m'; N=$'\e[0m'; else G=; R=; Y=; B=; N=; fi
FAIL=0
ok()   { printf "  ${G}PASS${N}  %s\n" "$1"; }
warn() { printf "  ${Y}WARN${N}  %s\n" "$1"; }
bad()  { printf "  ${R}FAIL${N}  %s\n" "$1"; FAIL=$((FAIL+1)); }
LABS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

printf "${B}Building Agentic AI - lab environment check${N}\n\n"

# Python 3.11+
if command -v python3 >/dev/null 2>&1; then
  ver=$(python3 -c 'import sys;print("%d.%d"%sys.version_info[:2])')
  major=${ver%%.*}; minor=${ver#*.}
  if [ "$major" -ge 3 ] && [ "$minor" -ge 11 ]; then ok "python3 $ver"; else bad "python3 $ver (need 3.11+)"; fi
else
  bad "python3 not found"
fi

command -v pip >/dev/null 2>&1 || command -v pip3 >/dev/null 2>&1 && ok "pip present" || bad "pip not found"

# .env
if [ -f "$LABS_DIR/.env" ]; then
  ok ".env present"
  grep -q "OPENAI_API_KEY=sk-" "$LABS_DIR/.env" 2>/dev/null && ok "OPENAI_API_KEY looks set" || warn "OPENAI_API_KEY not set yet"
  grep -q "ANTHROPIC_API_KEY=sk-ant" "$LABS_DIR/.env" 2>/dev/null && ok "ANTHROPIC_API_KEY looks set" || warn "ANTHROPIC_API_KEY not set yet"
else
  warn ".env not found — copy .env.example to .env and add your keys"
fi

printf "\n"
if [ "$FAIL" -eq 0 ]; then printf "${G}${B}Environment looks ready.${N}\n"; exit 0
else printf "${R}${B}%d blocking issue(s). Fix before labs.${N}\n" "$FAIL"; exit 1; fi
