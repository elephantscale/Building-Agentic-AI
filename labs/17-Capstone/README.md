# Lab 17 — Capstone: Enterprise AI Agent Challenge

## Goal

In a team, **design** a multi-agent system in one domain — **Finance, HR, Real
Estate, or Customer Support** — and **defend that design** to the room. You
produce a filled **Agent Design Canvas** and **one picture**, then present for
ten minutes and take the room's pushback.

This is a design review, not a build. It is also what you will actually be
asked to do first at work: come back with something a stakeholder can approve
or reject. The build gets handed to a team; the design is yours.

Your design must show all **six required capabilities** from
`course-materials/capstone-rubric.md`: reasoning, tool use, reflection,
multi-agent coordination, evaluation, and governance.

> You are not writing code today. A design you can defend beats a demo that
> happens to run.

## Time

One day (~5 working hours + presentations). See the run-of-show below.

## Tools

- `course-materials/agent-design-canvas.md` — **the deliverable.** Seven
  sections, all design decisions, no code.
- `course-materials/agent-safety-checklist.md`, `audit-log-schema.md`,
  `agent-evaluation-rubric.md`, `capstone-rubric.md`.
- `starter/agent_scaffold.py` — **read it, don't write it.** See below.
- Sample data in `labs/assets/` if you want concrete inputs to point at.

## Files in this lab

```text
17-Capstone/
  README.md                this run-of-show
  starter/
    agent_scaffold.py      what the build WOULD look like - reference reading
    requirements.txt       minimal deps (runs offline)
    README.md              how the scaffold maps to the six capabilities
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
  finding, gated report (the Lab 16 auditor is your governance story).
- *Policy Q&A* — answer only from the handbook; escalate anything legal.

**Real Estate**
- *Listing assistant* — draft listings from specs + comps; reflect for
  compliance wording.
- *Lead qualifier* — score inbound leads, route the hot ones, book viewings
  (gated).
- *Comps analyst* — pull comparables, compute a price range, cite each comp.

**Customer Support** (fastest start — you have seen the assets)
- *Tier-1 resolver* — answer from `labs/assets/help_center.md`, escalate what it
  can't ground.
- *Refund handler* — verify eligibility from the KB, then a **human gate** before
  issuing (Lab 15 is the shape).
- *Ticket-triage swarm* — a classifier agent + a drafting agent + a QA/reflection
  agent over `labs/assets/support_tickets.csv`.

## Deliverable 1 — the canvas

Fill every section of `course-materials/agent-design-canvas.md`. Copy it into
your own file; don't edit the template.

The most valuable line on the page is **"out of scope"** in section 1. Strong
teams have a longer out-of-scope list than feature list — that is a sign you
know what you are building, not a sign you aimed low.

Two sections carry the most weight:

- **Section 3, Tools.** Every tool gets a **safety class**. If nothing in your
  table is `dangerous`, your scope is too timid — add a real action.
- **Section 5, Evaluation.** Name **5–8 concrete test cases**: happy path,
  missing data, ambiguous input, and at least one **unsafe request**. You will
  not run them. Naming them is the exercise, because a case you cannot name is
  a case you cannot test.

## Deliverable 2 — the picture

One diagram, and it has to carry all six capabilities. Six things must be
visible on it:

| On the picture | Shows |
|----------------|-------|
| **Boxes** — who does what | multi-agent: ≥ 2 roles doing *different* jobs |
| **Labelled arrows** — what triggers what | reasoning: the flow of one request |
| **Tool calls**, each marked safe / dangerous | tool use + least privilege |
| **A loop-back arrow** | reflection: what sends work round again, and on what check |
| **★ on the dangerous action + the gate in front of it** | governance: who approves, and what they see |
| **A note of what is logged, and at which steps** | observability |

If a capability is not visible on the picture, you have not designed it yet.
That is a better test than whether code ran.

**Draw it as text** so it lives inside your canvas — nothing to attach, nothing
to install. Either form is fine:

**ASCII** (works everywhere, no tools):

```text
   [trigger]
       |
       v
  ┌──────────┐      ┌──────────┐
  │ ROLE 1   │ ---> │ ROLE 2   │ ---> (output)
  │ what     │      │ what     │
  └──────────┘      └──────────┘
       |                  ^
       | tool: safe       | reflection: send back if <check fails>
       v                  |
   ( data source )  ------+

  ★ DANGEROUS: <action>   -->  [HUMAN GATE: who approves, what they see]
  LOG at: <which steps>, to <where>
```

Pen and paper held up to the camera is equally fine. **The drawing is not the
deliverable — the decisions on it are**, and nobody is graded on neatness.

If you already know **Mermaid**, use it and paste it into <https://mermaid.live>.
One correction to avoid a wrong impression: Lab 9's `graph.md` was **printed by
the program** (`get_graph().draw_mermaid()`), not typed by anyone. Hand-writing
Mermaid is a different job, and today it buys you nothing that ASCII doesn't:

```text
flowchart TD
    trigger[New claim] --> triage[Triage agent]
    triage --> review[Policy reviewer]
    review -->|fails check| triage
    review --> gate{HUMAN GATE}
    gate -->|approved| pay[issue_payment]
    gate -->|denied| stop[Logged, no action]
```

## Run-of-show

```text
09:30  TEAMS      form teams of 3-4 · pick domain + ONE use case
10:00  DESIGN     canvas 1-3: goal, out of scope, inputs, tools + safety classes
11:00  DRAW       the picture: boxes, arrows, loop-back, the star and the gate, the log
12:30  lunch
13:15  HARDEN     canvas 4-7: memory, reflection, test cases, guardrails, logging
14:15  PRESSURE   swap designs with another team - each finds 3 holes in the other's
15:00  REVISE     fix what the other team found · rehearse the 10 minutes
16:00  PRESENT    ~10 min per team
```

**The 14:15 swap is not optional.** You hand your canvas and picture to another
team, they hand you theirs, and each side comes back with **three specific
holes** — not "looks good". Everyone presents having already been attacked once,
so at 16:00 you are defending a design rather than reading one out.

Three questions that find holes fast — use them on the other team:

1. *What is the dangerous action, and what exactly does the approver see?* A
   gate where the human has no basis to decide is theatre.
2. *What does this agent refuse to do?* If "out of scope" is thin, the scope is
   vague.
3. *Which of your test cases would fail today?* A team that cannot name one has
   not thought about failure.

## Presentation format (per team, 10 min)

```text
3 min  the problem, your domain, and the ONE use case you scoped to
4 min  walk your picture - follow a single request from trigger to output
2 min  "here is where it breaks, and here is what we would watch"
1 min  the room pushes back
```

The **2-minute "here is where it breaks"** slot is required. Naming your own
failure modes is the strongest signal that you understand the system — stronger
than any happy path.

## Grading (100 pts, from `capstone-rubric.md`)

| Dimension | Wt | Full marks |
|-----------|---:|-----------|
| Problem & design | 15 | Clear goal, sane scope, completed canvas, real out-of-scope list |
| Reasoning & planning | 15 | A loop you can trace on the picture; says how it recovers |
| Tools & integration | 15 | Well-specified tools, safety classes, least privilege |
| Reflection & quality | 10 | A named check, and what happens when it fails |
| Multi-agent coordination | 15 | ≥ 2 roles doing genuinely distinct jobs that cooperate |
| Evaluation | 15 | 5-8 named cases incl. one unsafe request; says what it measures |
| Governance & safety | 10 | Gate on the picture, approver named, logging per step |
| Communication | 5 | Defends the design under pushback |

Reasoning, tools, multi-agent and evaluation are **60 of 100**. Depth beats
feature count — one request traced properly through two agents scores higher
than five boxes nobody can explain.

A passing design shows **every** required capability at least once.

## The scaffold — reference reading, not an assignment

`starter/agent_scaffold.py` is what the build of your design would look like:
an `AuditLog`, a `ToolRegistry` that gates dangerous tools automatically, a
`Worker`, and a `Supervisor` that reflects before finishing.

You are not extending it today. Read it for one reason: **to check your design
is buildable.** Open `starter/README.md` and find each of your picture's boxes
in its table. If something on your picture has no home in that table, say so in
your presentation — "this part we would have to build from scratch" is a
legitimate and impressive thing to know about your own design.

If you want to see it run once, `cd starter && python agent_scaffold.py` works
offline and writes `audit-log.jsonl` — the log format your governance section
should describe.

## Teacher's Playbook

**Before the day.** Teams of 3-4, pre-picked or picked fast. Pin the four
domains, the picture checklist, and the run-of-show where everyone can see
them. Print the capstone rubric per team. **ASCII (or paper) is the default** —
do not send a room of fourteen off to learn Mermaid syntax at 11:00. Mermaid is
for the one or two who already use it; note that Lab 9's `graph.md` was emitted
by `draw_mermaid()`, so seeing it that day taught nobody the syntax.

**Framing it so nobody feels short-changed.** Say it straight at 09:30: *"You'd
ship a demo this afternoon, and demos lie. You're doing the thing you'd actually
be asked for first — a design someone can approve or reject."* In their jobs the
design review *is* the deliverable; the build gets handed on. Nobody in a bank
has ever been asked to ship a governed multi-agent system by 4 p.m.

**Coaching teams (the moves that save the day).**
- *At 10:45, no canvas yet?* Stop them — the team is arguing about features. Put
  them on section 1, goal and out of scope, until it is written down.
- *Scope too big?* Force one use case, one dangerous action, two roles.
  "Finance" is not a project; "invoice anomaly flag with a pay gate" is.
- *Nothing dangerous in the tools table?* Then there is no gate, no governance,
  and 10 points are gone. Make them add a real action with consequences.
- *"It's multi-agent" but it's one box labelled "the agent"?* Ask who could be
  fired for the other one's mistake. Distinct jobs, distinct roles.
- *Picture is boxes with unlabelled arrows?* An unlabelled arrow means "related
  somehow". Make them write what travels along it.
- *Governance left for last?* It is the cheapest 10 points on the board, and it
  is one star and one box on a drawing they have already made.

**Running the 14:15 swap.** Pair the teams yourself and keep it strict: three
specific holes, written down, handed back. Use the three questions above as the
prompt if a pair goes quiet. This is the highest-value hour of the day — it
turns six serial presentations into one conversation, and teams fix their own
worst problem before you ever see it.

**Judging presentations.** Score live against the grid. Require the
"where it breaks" slot — a team that skips it has not finished thinking. Ask
every team the same closing question: *"what is the single thing you would build
first, and which of your test cases would prove it worked?"* A team that answers
that well understands agents, whether or not they ever wrote the code.

**What good looks like.** A scoped problem with a real out-of-scope list; two
roles doing genuinely different jobs; one picture where you can follow a single
request from trigger to output and point at the gate; 5-8 named test cases
including an unsafe one; an honest account of what breaks first — and a team
that gets sharper, not defensive, when the room pushes back.

**Debrief (10 min after presentations).** Pull one pattern from across the teams
for each capability. Then close on the through-line: Monday they hand-built a
ReAct loop with two read-only tools and a regex; today they designed a governed
multi-agent system and defended it. The loop never changed. What changed is that
they now know where to put the gate.

---

*Capstone — Building Agentic AI, Elephant Scale.*
