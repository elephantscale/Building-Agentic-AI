# Capstone: Enterprise AI Agent Challenge

Elephant Scale

---

## The Challenge

* In teams, **design a multi-agent system** in one domain:
  - **Finance** · **HR** · **Real Estate** · **Customer Support**
* You have one day: **design → draw → pressure-test → defend**
* It must be a *system*, not a single prompt — agents that **cooperate**
* Everything you learned this week shows up here **at least once**

> You are not writing code today. A design you can defend beats a demo that happens to run.

Notes:

---

## Required Capabilities (all six)

* A passing project shows **every** capability at least once (ref `capstone-rubric.md`):

| Capability | Minimum bar |
|------------|-------------|
| **Reasoning** | An explicit plan / ReAct loop, not one prompt |
| **Tool use** | ≥ 2 real tools with validated schemas |
| **Reflection** | The system self-checks or revises ≥ 1 output |
| **Multi-agent** | ≥ 2 cooperating roles/agents |
| **Evaluation** | 5-8 **named** test cases, incl. one unsafe request |
| **Governance** | A gate on the picture + what gets logged, per step |

> Six checkboxes — and every one of them has to be visible on your picture.

Notes:

---

## Scope It With the Agent Design Canvas

* Fill `agent-design-canvas.md` — **this is the deliverable.** One page, seven boxes:

```text
1. Goal        one sentence + what "done" looks like + out of scope
2. Inputs      trigger, data available, which inputs are UNTRUSTED
3. Tools       name, read/write, safety class (safe/guarded/dangerous)
4. Reasoning   pattern, max steps, budget, memory
5. Reflection  self-check + eval metrics + test cases
6. Guardrails  human gate for send/pay/delete, hard stops, fallback
7. Observ.     what's logged, who owns review/escalation
```

* The **"out of scope"** line is the most valuable thing you'll write today.
* Strong teams have a **longer out-of-scope list than feature list**.

> A finished canvas is a scoped project. A blank canvas is a team still arguing about features.

Notes:

---

## Deliverable 2 — The Picture

* **One diagram**, and it has to carry all six capabilities:

```text
  boxes ............ who does what  (>= 2 roles, genuinely DIFFERENT jobs)
  labelled arrows .. what triggers what - the flow of ONE request
  each tool ........ marked safe / dangerous
  a loop-back ...... reflection: what sends work round again, and on what check
  a STAR + a gate .. the dangerous action, and who approves it
  a log note ....... what is written, at which steps
```

* Draw it **as text** — **boxes and arrows, ASCII** — so it lives inside your canvas
* Pen and paper held up to the camera is also fine. The drawing is not the deliverable; the
  decisions on it are.

> If a capability is not visible on the picture, you have not designed it yet.

Notes:

---

## Run-of-Show

```text
09:30  TEAMS     form teams of 3-4 - pick domain + ONE use case
10:00  DESIGN    canvas 1-3: goal, out of scope, inputs, tools + safety classes
11:00  DRAW      the picture: boxes, arrows, loop-back, the star and the gate
12:30  lunch
13:15  HARDEN    canvas 4-7: memory, reflection, test cases, guardrails, logging
14:15  PRESSURE  swap with another team - each finds 3 holes in the other's design
15:00  REVISE    fix what they found - rehearse the 10 minutes
16:00  PRESENT   ~10 min per team
```

* `starter/agent_scaffold.py` is **reference reading** — use it to check your design is buildable.

> Have the picture drawn by lunch. The afternoon makes it defensible, not makes it exist.

Notes:

---

## The Pressure Test (14:15)

* You hand your canvas + picture to another team. They hand you theirs.
* Each side comes back with **three specific holes** — not "looks good".
* Three questions that find them fast:

```text
1. What is the dangerous action, and what exactly does the approver SEE?
      a gate where the human has no basis to decide is theatre

2. What does this agent REFUSE to do?
      a thin "out of scope" means the scope is still vague

3. Which of your test cases would fail today?
      a team that cannot name one has not thought about failure
```

> Everyone presents having already been attacked once. At 16:00 you defend a design, not read one out.

Notes:

---

## The Presentation (10 min / team)

```text
3 min  the problem, your domain, and the ONE use case you scoped to
4 min  walk your picture - follow a single request from trigger to output
2 min  "here is where it breaks, and here is what we would watch"
1 min  the room pushes back
```

* The **"where it breaks"** slot is required, not optional.
* Naming your own failure modes beats any happy path.

> Don't tell us it works. Tell us how it fails, and show us where the gate stands.

Notes:

---

## How You're Graded (100 pts)

| Dimension | Wt | Full marks |
|-----------|---:|-----------|
| Problem & design | 15 | Clear goal, sane scope, completed canvas |
| Reasoning & planning | 15 | A loop you can trace on the picture; says how it recovers |
| Tools & integration | 15 | Well-specified tools, safety classes, least privilege |
| Reflection & quality | 10 | A named check — and what happens when it fails |
| Multi-agent coordination | 15 | Distinct roles that actually cooperate |
| Evaluation | 15 | 5-8 named cases incl. one unsafe; says what it measures |
| Governance & safety | 10 | Gate on the picture, approver named, logging per step |
| Communication | 5 | Defends the design under pushback |

> Notice the weights: reasoning, tools, multi-agent, and eval are 60 of 100. Depth beats features.

Notes:

---

## Deliverables

* A completed **`agent-design-canvas.md`** — all seven sections, your own copy
* **One picture** carrying all six capabilities
* **5-8 named test cases**, one of them an unsafe request — you name them, you don't run them
* Ten minutes that survive the room

```text
your-team/
  agent-design-canvas.md   all seven sections filled
  the picture              ASCII boxes and arrows, inside the canvas
  test cases               5-8, one of them unsafe
```

> The most valuable line you will write today is "out of scope".

Notes:

---

## Tips

* **One use case, two roles, one dangerous action** — that is the whole scope
* **Nothing dangerous in your tools table?** Then there's no gate and no governance — add a real action
* **Label every arrow** — an unlabelled arrow means "related somehow", which is not a design
* **Name the approver**, not just the gate: who are they, and what do they see?
* **Write "out of scope" early** — it is the fastest way to stop a team arguing
* Reuse the course assets: `help_center.md`, `support_tickets.csv`, the audit schema

> Every hour ask: "if someone senior read this page, what's the first question they'd ask?" Answer it.

Notes:

---

## Common Pitfalls

* **Scope creep** — five domains, zero defended. Pick one use case.
* **Prompt-in-a-trenchcoat** — one box labelled "the agent" is not multi-agent
* **A blind approver** — a gate the human has no basis to decide at
* **No unsafe test case** — the one case that proves you thought about misuse
* **Unlabelled arrows** — a drawing that looks like a design and isn't
* **Governance drawn last** — it's one star and one box; put it in at 11:00

> The failure mode is always the same: too much scope, safety last, and a picture nobody can walk.

Notes:

---

## Gallery — Finance

* **Invoice triage & approval** — extract → validate against PO → flag anomalies → **human gate** to approve payment
* **Expense-policy auditor** — read expense rows, cite the policy clause, escalate the gray areas
* **Earnings-call briefer** — retrieve transcript → summarize → reflect for factuality → cite sources

> Finance = high stakes, clear rules to cite, obvious dangerous action (pay). A natural governance story.

Notes:

---

## Gallery — HR & Real Estate

* **HR**
  - **Onboarding coordinator** — schedule, draft welcome emails, checklist (draft-only, human sends)
  - **Pay-equity analyst** — query aggregates (no raw PII), reflect on the finding, gated report
  - **Policy Q&A** — answer only from the handbook; escalate anything legal
* **Real Estate**
  - **Listing assistant** — draft listings from specs + comps; reflect for compliance wording
  - **Lead qualifier** — score inbound leads, route hot ones, book viewings (gated)
  - **Comps analyst** — pull comparables, compute a range, cite each comp

> HR and Real Estate both live near regulated data — perfect for showing least privilege and gates.

Notes:

---

## Gallery — Customer Support

* **Tier-1 resolver** — answer from `help_center.md`, escalate what it can't ground
* **Refund handler** — verify eligibility from the KB, then a **human gate** before issuing
* **Voice support line** — reuse your Lab 15 agent; add a second agent for account changes
* **Ticket triage swarm** — classifier agent + drafting agent + a QA/reflection agent

> Support has ready-made assets (`help_center.md`, `support_tickets.csv`) — you can be designing by 10:05.

Notes:

---

## Design It — Good Luck

* Go to **`labs/17-Capstone`** — run-of-show, the picture checklist, and the rubric
* One use case. Two roles. One dangerous action. One page and one picture.
* Name the approver. Name what's logged. Name the case that would fail.
* Then defend it — the room gets to push back.

> Monday: a ReAct loop with two read-only tools and a regex. Today: a governed multi-agent system you can defend. The loop never changed — you just know where the gate goes.

Notes:
