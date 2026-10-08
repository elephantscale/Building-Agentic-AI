# Multi-Agent Systems & Planning

Elephant Scale

---

## Part III — What We'll Cover

* Why and *when* to use more than one agent — and when not to
* Roles and separation of concerns — the case for specialists
* Multi-agent conversation flows and sequential chatbots
* Orchestration patterns: **supervisor/worker**, **pipeline**, **debate**
* Handoffs and **shared state** — how agents pass work without losing it
* **Planning-driven agents** — plan-then-execute for onboarding and blog generation
* The real risks: **compounding errors** and **cost**
* Lab 8: a planning-driven onboarding assistant

> One good agent beats five that talk past each other. Add agents only when a single loop can't cope.

Notes:

---

## Why Multiple Agents?

* **Separation of concerns** — a researcher, a writer, and a critic each do one thing well
* **Focused context** — each agent carries only the tools and prompt it needs
* **Least privilege** — the agent that *sends email* need not hold the *delete* tool
* **Parallelism** — independent sub-tasks can run at once
* **Testability** — you can evaluate and swap one specialist in isolation

> Multi-agent is modular design for agents. The win is smaller, sharper, safer parts.

Notes:

---

## When NOT to Use Multiple Agents

* A single agent with the right tools already succeeds
* The sub-tasks are **tightly coupled** — constant back-and-forth costs more than it saves
* You need **tight latency or cost** guarantees (each agent = more LLM calls)
* You can't yet **evaluate one agent** — you certainly can't debug five

* Climb the ladder: one prompt < one agent < **many agents**

```text
Start with one agent. Split into roles only when a single loop
can't hold the tools, the context, or the responsibilities.
```

> Every agent you add multiplies cost, latency, and failure surface. Earn the second one.

Notes:

---

## Roles & Separation of Concerns

* Give each agent a **narrow charter**: goal, tools, and what it must *not* do
* Classic role split for content and knowledge work:
  - **Planner** — turns a goal into ordered sub-tasks
  - **Researcher** — gathers grounded facts via tools
  - **Writer** — drafts from the researcher's findings only
  - **Critic / reviewer** — checks against the goal, sends back for revision

* Roles are just **agents with different system prompts and tool sets**

> Name the role, then hand it the fewest tools that role needs. That is the whole design.

Notes:

---

## Multi-Agent Conversation Flows

* Agents collaborate by **passing messages** — one agent's output is another's input
* Keep the transcript **structured** so it's auditable and debuggable
* Decide up front: who speaks, in what order, and who ends the conversation

```text
Planner:    "3 sub-tasks: schedule, welcome email, week-1 checklist."
Researcher: "HR policy: new hires need an IT + a manager 1:1 in week 1."
Writer:     "Draft welcome email + checklist using those facts."
Critic:     "Checklist missing the IT setup. Revise."
Writer:     "Revised."  -> supervisor accepts -> done
```

> Every message an agent receives is untrusted data — even from another agent. Validate at each hop.

Notes:

---

## Sequential Chatbots

* The simplest multi-agent flow: a **fixed chain** of specialists
* Output of stage *N* becomes input of stage *N+1* — no dynamic routing
* Easy to reason about, easy to test, easy to log

```text
user goal
   |
[classify] -> [retrieve] -> [draft] -> [review] -> answer
```

* Use it when the **stages are stable** and always run in the same order

> A sequential chain is a pipeline of chatbots. If the order never changes, don't add a supervisor.

Notes:

---

## Pattern 1 — Supervisor / Worker

* A **supervisor** owns the goal, decides which worker acts next, and assembles the result
* **Workers** are specialists that do one sub-task and report back
* The supervisor holds **shared state** and enforces the step cap

```text
                +--------------------+
                |     SUPERVISOR     |
                |  goal + plan +     |
                |  shared state      |
                +----+----+-----+----+
          route  |    | route |  route
                 v    v       v
          +--------+ +--------+ +--------+
          |RESEARCH| | WRITER | | CRITIC |
          | worker | | worker | | worker |
          +---+----+ +---+----+ +---+----+
              |          |          |
              +----------+----------+
                results back to supervisor
```

> The supervisor is the loop; the workers are the tools. It's the ReAct pattern, one level up.

Notes:

---

## Pattern 2 — Pipeline

* A **fixed sequence** of stages; each transforms and passes forward
* No central router — the graph *is* the control flow
* Great when the steps are known and ordered; cheap to test stage-by-stage

```text
  INPUT
    |
    v
+---------+   +----------+   +--------+   +---------+
| PLAN    |-->| RESEARCH |-->| DRAFT  |-->| REVIEW  |--> OUTPUT
| sub-    |   | grounded |   | from   |   | vs goal |
| tasks   |   | facts    |   | facts  |   | + gate  |
+---------+   +----------+   +--------+   +---------+
```

* Add a **loop-back** from REVIEW to DRAFT for one bounded revision pass

> Pipeline = predictability. Supervisor = flexibility. Pick the least power that fits the task.

Notes:

---

## Pattern 3 — Debate

* Two+ agents argue opposing positions; a judge (or supervisor) decides
* Surfaces errors a single agent would confidently miss
* Useful for high-stakes reasoning, risky claims, or plan review

```text
Proposer: "Ship Friday — tests pass."
Skeptic:  "Load test never ran; Friday deploys have no on-call."
Judge:    "Skeptic wins. Ship Monday with a load test."
```

* **Cost warning**: debate multiplies LLM calls fast — bound the rounds

> Debate buys robustness with tokens. Cap the rounds and make the judge cite the winning point.

Notes:

---

## Handoffs & Shared State

* A **handoff** transfers control *and* the context the next agent needs
* Keep one **shared state** object — the single source of truth for the run:

```json
{
  "goal": "Onboard Priya (Data Engineer, starts Mon)",
  "plan": ["schedule", "welcome_email", "week1_checklist"],
  "done": ["schedule"],
  "artifacts": {"schedule": "packet/schedule.md"},
  "budget": {"steps_left": 4, "cost_usd": 0.006}
}
```

* Pass **references** (a task id, a file path), not giant blobs, to bound context
* On every handoff: record it in the audit log

> Lose the shared state and each agent re-derives the world — badly. State is the memory of the team.

Notes:

---

## Planning-Driven Agents (Plan-Then-Execute)

* Two phases instead of one improvised loop:
  - **Plan** — decompose the goal into ordered, checkable sub-tasks (once)
  - **Execute** — carry out each sub-task with tools, tracking progress
* The **plan is an artifact** — inspectable, testable, and auditable
* Re-plan only on failure, not on every step

```text
GOAL -> [ planner makes a plan ] -> [ execute step 1..N via tools ]
                    ^                              |
                    +----- re-plan on failure -----+
```

> A plan turns "hope the loop converges" into "run a checklist." That is what makes it testable.

Notes:

---

## Plan-Then-Execute vs. ReAct

| | ReAct (Day 1) | Plan-then-execute |
|---|---------------|-------------------|
| Decides next step | every turn | once, up front |
| Best for | open-ended, exploratory | known, multi-part deliverables |
| Auditability | trace of thoughts | an explicit plan + results |
| Failure recovery | improvises | re-plans the failed step |
| Cost | can wander | bounded by the plan |

* Many real systems **combine** them: a plan of steps, each executed ReAct-style

> Use ReAct to explore; use a plan to *deliver*. Onboarding and blog posts are deliverables.

Notes:

---

## Example — Onboarding Assistant

* Goal: onboard a new hire end-to-end, safely
* Planner emits sub-tasks; a supervisor runs each via a tool

```text
PLAN:
  1. propose a first-week meeting schedule   (calendar tool - stub)
  2. draft a welcome email                    (email draft tool)
  3. build a first-week checklist             (HR-policy lookup)
ASSEMBLE -> onboarding packet
GATE     -> a human approves before anything "sends"
```

* Every artifact is a **draft** written to a file; nothing sends without approval

> The plan is the safety story: three named sub-tasks, three tools, one human gate. Lab 8 builds it.

Notes:

---

## Example — Blog-Post Generation

* Same plan-then-execute shape, content-flavored:

```text
PLAN:  outline -> research each section -> draft -> review -> revise once
```

* **Writer drafts only from the researcher's grounded findings** — no free-floating facts
* **Critic** checks the draft against the outline and the sources, then gates publish

> Separation of concerns keeps the writer honest: it can only write what research supplied.

Notes:

---

## Risks of Multi-Agent — Compounding Errors

* Errors **multiply** down a chain: 90% per stage over 4 stages ≈ **66%** end-to-end
* A wrong fact from the researcher becomes a confident lie in the writer
* An unverified handoff lets a bad output masquerade as an input

```text
0.9 x 0.9 x 0.9 x 0.9 = 0.66   <- each "pretty good" stage still compounds
```

* Mitigate: a **critic/gate** between stages, grounding checks, bounded re-tries

> More agents, more joints — and every joint is a place the chain can break. Add a check at each one.

Notes:

---

## Risks of Multi-Agent — Cost & Complexity

* Each agent and each turn is **another LLM call** — cost and latency stack
* A debate or a chatty supervisor can **balloon** token spend silently
* Harder to evaluate, debug, and reason about than a single loop

* Controls:
  - a **global step/turn/cost budget** across the whole team, not per agent
  - **bound** debate rounds and revision passes
  - **log every handoff and tool call** — evaluate the team like one agent

> Budget the *team*, not each member. The failure mode is five agents each politely staying "under budget."

Notes:

---

## Putting It Together

* Add agents for **separation of concerns**, focused context, and least privilege — not for show
* **Supervisor/worker** for flexibility, **pipeline** for predictability, **debate** for robustness
* **Plan-then-execute** turns open-ended loops into testable, checklist-style deliverables
* Keep one **shared state**; treat every handoff as untrusted and log it
* Watch **compounding errors** and **cost** — gate the joints, budget the whole team

> A multi-agent system is a small org. Give it clear roles, a coordinator, a budget, and an audit trail.

Notes:

---

## Lab 8 — Planning-Driven Onboarding Assistant

**Stop here and run Lab 8.**

You will:

1. Fill the **Agent Design Canvas** before writing code.
2. Run a **planner** that decomposes onboarding into ordered sub-tasks.
3. Execute each sub-task via tools: a **calendar stub**, an **email-draft** tool, an **HR-policy lookup**.
4. Have a **supervisor** assemble the results into an onboarding packet.
5. Enforce a **human gate** before anything "sends", and write a **JSONL audit log**.

**Deliverable:** a runnable `onboarding_agent.py` that plans, executes sub-tasks, writes an onboarding packet to files, gates the "send", and emits `audit-log.jsonl`.

**Time:** 60 minutes

Notes:
