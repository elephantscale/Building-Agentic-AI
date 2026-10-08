#!/usr/bin/env bash
# validate-course.sh - repository structure check for Building Agentic AI.
set -u
if [ -t 1 ]; then G=$'\e[32m'; R=$'\e[31m'; B=$'\e[1m'; N=$'\e[0m'; else G=; R=; B=; N=; fi
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FAIL=0
ok()  { printf "  ${G}PASS${N}  %s\n" "$1"; }
bad() { printf "  ${R}FAIL${N}  %s\n" "$1"; FAIL=$((FAIL+1)); }
printf "${B}Building Agentic AI - course repo validation${N}\n"

required=(
  README.md outline.md CLAUDE.md
  slides/slide-list.txt slides/gen.sh slides/00-about.md
  labs/SETUP.md labs/verify-setup.sh labs/test-all-labs.sh labs/.env.example
  course-materials/README.md
  course-materials/agent-design-canvas.md
  course-materials/tool-spec-template.md
  course-materials/agent-evaluation-rubric.md
  course-materials/agent-safety-checklist.md
  course-materials/audit-log-schema.md
  course-materials/capstone-rubric.md
)
printf "\n${B}Required files${N}\n"
for f in "${required[@]}"; do [ -f "$ROOT_DIR/$f" ] && ok "$f" || bad "$f missing"; done

printf "\n${B}Slides${N}\n"
while IFS= read -r deck; do
  [ -z "$deck" ] && continue
  [ -f "$ROOT_DIR/slides/$deck" ] && ok "slide deck $deck" || bad "slide deck $deck missing"
done < "$ROOT_DIR/slides/slide-list.txt"

printf "\n${B}Labs${N}\n"
expected_labs=(
  01-Agent-Loop-Setup 02-Research-Assistant 03-Reflective-Summarization
  04-Python-Functions-to-Tools 05-Email-Assistant 06-RAG-Vector-DB
  07-Evaluate-Benchmark 08-Onboarding-Assistant 09-LangGraph-Essay-Writer
  10-Zapier-CustomGPT 11-NoCode-CRM-Agent 12-Bedrock-CRM-Assistant
  13-DSPy-SelfImproving 14-Claude-Coding-Assistant 15-Voice-Support-Agent
  16-HR-Governance-Agent 17-Capstone
)
for lab in "${expected_labs[@]}"; do
  [ -f "$ROOT_DIR/labs/$lab/README.md" ] && ok "$lab README" || bad "$lab README missing"
done

printf "\n${B}Content checks${N}\n"
grep -qi "Building Agentic AI" "$ROOT_DIR/README.md" && ok "README course title" || bad "README course title missing"
grep -qi "Course Outline" "$ROOT_DIR/outline.md" && ok "outline has course outline" || bad "outline course outline missing"
grep -qi "Capstone" "$ROOT_DIR/labs/17-Capstone/README.md" && ok "capstone lab present" || bad "capstone lab missing"

printf "\n"
if [ "$FAIL" -eq 0 ]; then printf "${G}${B}Course repo structure is valid.${N}\n"; exit 0
else printf "${R}${B}%d validation failure(s).${N}\n" "$FAIL"; exit 1; fi
