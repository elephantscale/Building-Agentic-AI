# Lab 17 — Capstone: Enterprise AI Agent Challenge

## Goal

In a team, design, build, evaluate, and demo a **multi-agent system** in one
domain — **Finance, HR, Real Estate, or Customer Support** — that shows **all
six required capabilities** from `course-materials/capstone-rubric.md`:
reasoning, tool use, reflection, multi-agent coordination, evaluation, and
governance. This is the whole week in one project. Small scope done well beats
big scope half-built.

## Time

One day (~6 working hours + demos). See the timeline below.

## Tools

- Everything you built this week, plus the `starter/` scaffold in this folder.
- Course materials: Agent Design Canvas, audit-log schema, evaluation rubric,
  safety checklist, capstone rubric.
- Sample data in `labs/assets/`. Model IDs: `gpt-4.1` / `gpt-4o-mini`,
  `claude-sonnet-5`. Keys in `labs/.env`.

## Files in this lab

```text
17-Capstone/
  README.md                this run-of-show
  starter/
    agent_scaffold.py      runnable supervisor + worker + tool-registry + audit log
    requirements.txt       minimal deps (runs offline)
    README.md              how to extend the scaffold
```

## The four domains + project ideas

Pick **one domain and one use case**. Two or three ideas each:

**Finance**
- *Invoice triage & approval* — extract → validate against a PO → flag anomalies
  → **human gate** to approve payment.
- *Expense-policy auditor* — read expense rows, cite the policy clause, escalate
  the gray areas.
- *Earnings-call briefer* — retrieve transcript → summarize → reflect for
  factuality → cite sources.

**HR**
- *Onboarding coordinator* — schedule, draft welcome emails, build a checklist
  (draft-only; a human sends).
- *Pay-equity analyst* — query aggregates only (no raw PII), reflect on the
  finding, gated report (reuse Lab 16's governance).
- *Policy Q&A* — answer only from the handbook; escalate anything legal.

**Real Estate**
- *Listing assistant* — draft listings from specs + comps; reflect for
  compliance wording.
- *Lead qualifier* — score inbound leads, route the hot ones, book viewings
  (gated).
- *Comps analyst* — pull comparables, compute a price range, cite each comp.

**Customer Support** (fastest start — assets are ready)
- *Tier-1 resolver* — answer from `labs/assets/help_center.md`, escalate what it
  can't ground.
- *Refund handler* — verify eligibility from the KB, then a **human gate** before
  issuing (reuse Lab 15).
- *Ticket-triage swarm* — a classifier agent + a drafting agent + a QA/reflection
  agent over `labs/assets/support_tickets.csv`.

## Required capabilities checklist

Tick every box at least once (full detail in `capstone-rubric.md`):

- [ ] **Reasoning** — an explicit plan / ReAct loop, not a single prompt.
- [ ] **Tool use** — ≥ 2 real tools with validated schemas.
- [ ] **Reflection** — the system self-checks or revises ≥ 1 output.
- [ ] **Multi-agent** — ≥ 2 cooperating roles/agents.
- [ ] **Evaluation** — a small **frozen** eval set + before/after scores.
- [ ] **Governance** — an audit log + a human-in-the-loop gate on dangerous acts.

## Timeline (run-of-show)

```text
09:30  Form teams · pick domain + ONE use case
10:00  DESIGN    fill agent-design-canvas.md · agree a 5-8 case eval set
10:45  BUILD     thin end-to-end thread: supervisor + 1 worker + 1 tool + log
12:30  lunch
13:15  BUILD     add 2nd agent · reflection · human gate on the dangerous action
15:00  EVALUATE  run the frozen eval set · record before/after · fix top failure
16:00  POLISH    rehearse the 10-min demo · pick your edge case + gate moment
16:30  DEMOS     ~10 min per team
```

> Hit "end-to-end but ugly" by lunch. Everything after lunch makes it *good*,
> not makes it *work*.

## Phases in detail

**1. Design (before any code).** Fill `course-materials/agent-design-canvas.md`.
The most valuable line is **"out of scope"**. Decide your agents' roles, your
tools and their safety classes, your loop cap and budget, and what a human must
approve. Freeze your eval set now: 5–8 cases covering happy path, missing data,
ambiguous input, and one **unsafe request**.

**2. Build.** Start from `starter/agent_scaffold.py` — it already gives you a
supervisor, a worker, a tool registry with an automatic human gate, and an audit
log. Get one thin thread running first, then add the second agent, reflection,
and your real tools. Cap the loop (max steps + cost) on line one. Fake slow or
expensive integrations with local stubs.

**3. Evaluate.** Score runs with `course-materials/agent-evaluation-rubric.md`
(0–3 on five dimensions; pilot-ready needs Safety = 3 and total ≥ 12/15). Run
the frozen set, record a **before/after** table around one change you make. Read
the **audit log**, not just the final answer — grade the process.

**4. Demo.** Rehearse. Pick the one edge case and the one human-gate moment
you'll show live.

## Starter scaffolding guidance

```sh
cd starter && pip install -r requirements.txt && python agent_scaffold.py
```

It runs offline and writes `audit-log.jsonl`. Map your project onto its pieces
(`starter/README.md` has the table) and grow the `TODO` markers into real
routing, a capped worker loop, a real approver, and real reflection. Reuse the
audit-log schema it already emits, and the course templates for canvas, eval,
and safety sign-off.

## Deliverables

- Repo with runnable code (or a documented low-code flow) + `requirements.txt`.
- Completed `agent-design-canvas.md` **and** `agent-safety-checklist.md`.
- Eval set + a results table (before/after one change).
- A sample **audit log (JSONL)** from a real run.

```text
capstone-<team>/
  README.md                what it does + how to run
  agents/  tools/          the system
  eval/    eval_set.jsonl  results.md
  audit/   run-log.jsonl
  agent-design-canvas.md   agent-safety-checklist.md
```

## Demo format (per team, 10 min)

```text
2 min  problem, domain, and the design canvas
5 min  LIVE demo — include ONE edge case and ONE human-gate moment
2 min  evaluation results + what you'd fix next
1 min  Q&A
```

Show the audit log live. A handled edge case earns more than a flawless happy
path.

## Grading (100 pts, from `capstone-rubric.md`)

| Dimension | Weight |
|-----------|-------:|
| Problem & design | 15 |
| Reasoning & planning | 15 |
| Tools & integration | 15 |
| Reflection & quality | 10 |
| Multi-agent coordination | 15 |
| Evaluation | 15 |
| Governance & safety | 10 |
| Demo & communication | 5 |

A passing project shows **every** required capability at least once.

## Teacher's Playbook

**Before the day.** Have teams of 3–4 pre-picked or pick fast. Pin the four
domains and this timeline where everyone can see them. Make sure everyone can run
`starter/agent_scaffold.py` (a green run = environment is ready). Print the
capstone rubric per team.

**Coaching teams (the moves that save the day).**
- *At 10:45, no canvas yet?* Stop them. Ten minutes on the canvas saves two
  hours of thrashing. The "out of scope" line is where you cut ruthlessly.
- *Scope too big?* Force one use case, one dangerous action, one eval set of
  5 cases. "Finance" is not a project; "invoice anomaly flag with a pay gate" is.
- *Chasing a flaky API at 2 p.m.?* Tell them to stub it. Graders reward the
  *loop, the eval, and the gate* — not a live integration.
- *"It's multi-agent" but it's one giant prompt?* Make the roles do genuinely
  different jobs (e.g., a drafter and a separate QA/reflection agent that can
  reject the draft).
- *Governance being left for last?* It's the cheapest 10 points on the board and
  the scaffold gives it for free — insist the audit log and gate are in the
  thin thread, not bolted on at 4 p.m.

**Time-boxing.** Call the phase transitions out loud (DESIGN → BUILD → EVALUATE
→ POLISH). Give a hard 15-minutes-to-demo warning. Freeze code at demo time.

**Keeping scope sane.** One domain, one use case, two agents, two tools, one
dangerous action, one frozen eval set. Anything beyond that is a bonus, not a
requirement.

**Judging demos.** Score live against the rubric grid; the weights put 60/100 on
reasoning + tools + multi-agent + evaluation, so reward depth over feature count.
Require the live edge case and the gate moment — no slideware. Ask each team the
same closing question: *"what's the single thing you'd fix next, and how would
your eval set prove it worked?"* A team that answers that well understands agents.

**What good looks like.** A scoped problem, a completed canvas, two agents doing
distinct jobs, a capped loop that recovers from one surprise, an honest
before/after eval table, a clean audit log, and one dangerous action caught by a
human gate — demoed live, edge case and all.

**Debrief (10 min after demos).** Pull one pattern from across the teams for each
capability. Close on the through-line: they started the week hand-building a
ReAct loop and ended it shipping a governed multi-agent system.

---
