# Capstone Rubric — Enterprise AI Agent Challenge

Teams design and demo a multi-agent system in one domain (Finance, HR, Real Estate, or Customer
Support). Score out of 100. A passing project shows **every** required capability at least once.

## Required capabilities (must all be present)

- [ ] **Reasoning** — an explicit plan or ReAct loop, not a single prompt.
- [ ] **Tool use** — at least two real tools with validated schemas.
- [ ] **Reflection** — the system self-checks or revises at least one output.
- [ ] **Multi-agent** — at least two cooperating roles/agents.
- [ ] **Evaluation** — a small frozen eval set + scores (use `agent-evaluation-rubric.md`).
- [ ] **Governance** — an audit log + a human-in-the-loop gate on dangerous actions.

## Scoring

| Dimension | Weight | What earns full marks |
|-----------|-------:|-----------------------|
| Problem & design | 15 | Clear goal, sensible scope, completed Agent Design Canvas |
| Reasoning & planning | 15 | Robust plan/ReAct loop; recovers from surprises |
| Tools & integration | 15 | Well-specified tools; clean error handling |
| Reflection & quality | 10 | Measurable quality lift from self-evaluation |
| Multi-agent coordination | 15 | Roles are distinct and actually cooperate |
| Evaluation | 15 | Frozen eval set, honest metrics, before/after comparison |
| Governance & safety | 10 | Least privilege, human gate, complete audit log |
| Demo & communication | 5 | Clear 10-min demo; team explains tradeoffs |

## Demo format (per team)

1. **2 min** — problem, domain, and design canvas.
2. **5 min** — live demo, including one edge case and one human-gate moment.
3. **2 min** — evaluation results and what you'd fix next.
4. **1 min** — Q&A.

## Deliverables

- Repo with runnable code (or documented low-code flow) + `requirements.txt`.
- Completed `agent-design-canvas.md` and `agent-safety-checklist.md`.
- Eval set + results table.
- Sample audit log (JSONL) from a real run.
