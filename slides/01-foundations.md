# Foundations of Agentic AI

Elephant Scale

---

## Part I — What We'll Cover

* What Agentic AI *is* — and what it is not
* From prompt-based AI to agents that act
* OpenAI's guidance: **when** to use an agent vs. a plain workflow
* Design principles: autonomy, reasoning, reflection, planning, safety
* The canonical **agent loop** and the **ReAct** pattern
* Tools and memory — how an agent reaches the world
* Two labs: hand-build a ReAct loop, then a logged research assistant

> Today's goal: a correct *mental model* first, then a working agent you built by hand.

Notes:

---

## What Is Agentic AI?

* An **LLM in a loop** that pursues a **goal** by **using tools**
  - not one prompt, one answer — many steps
  - the model decides *what to do next* each turn
* Three ingredients:
  - a **goal** (what "done" means)
  - **tools** (search, code, APIs, databases)
  - a **loop** (act, observe, decide, repeat)

```text
goal -> plan -> act (call a tool) -> observe -> reflect -> decide -> repeat -> answer
```

> Agentic ≠ a bigger model. It's a control loop wrapped around a model.

Notes:

---

## Agent vs. Chatbot vs. Workflow

| | Chatbot | Fixed workflow | Agent |
|---|---------|----------------|-------|
| Steps | one turn | pre-wired, fixed | model chooses at runtime |
| Tools | none / one | called in fixed order | called as needed |
| Adapts to input | no | little | yes |
| Predictable | very | very | less — needs guardrails |

* A chatbot **answers**. A workflow **executes a script**. An agent **decides**.

> More autonomy buys flexibility and costs predictability. You pay for it with evaluation and governance.

Notes:

---

## From Prompt-Based AI to Autonomous Agents

* **Prompt** — one instruction in, one completion out
* **Prompt chain** — you wire step 2 to step 1 (you are the loop)
* **Tool-use / function calling** — the model can *request* an action
* **Agent** — the model runs its own loop: plan, call tools, observe, revise
* **Multi-agent** — several agents specialize and collaborate (Day 3)

```text
prompt  ->  chain  ->  tool use  ->  agent loop  ->  multi-agent
 (you drive) ....................... (the model drives) .........
```

> The shift is *who holds the loop*. In an agent, the model does — that is the whole idea.

Notes:

---

## OpenAI's Agentic Guidance — When to Build an Agent

* Reach for an agent when a task has **all three**:
  - **Complex, branching decisions** — many "it depends" paths
  - **Rules too messy to hard-code** — brittle or ever-changing logic
  - **Heavy reliance on unstructured input** — language, documents, tickets
* Good fits: triage, research, multi-step support, document workflows

> If a flowchart would capture it cleanly, write the flowchart — not an agent.

Notes:

---

## When NOT to Use an Agent

* The task is **deterministic** — same input, same steps every time
* You need **hard guarantees** on cost, latency, or output shape
* A **single prompt** or a short **script** already does the job
* Errors are **expensive and hard to catch** with no human in the loop

* Prefer the simplest thing that works:
  - one prompt  <  prompt chain  <  fixed workflow  <  agent

> Start at the lowest rung of autonomy. Climb only when the task forces you to.

Notes:

---

## Design Principles

* **Autonomy** — the agent decides next steps, within limits you set
* **Reasoning** — it thinks *before* it acts (make the thinking explicit)
* **Reflection** — it checks its own work and revises (Day 2)
* **Planning** — it breaks a goal into ordered sub-steps
* **Safety** — least privilege, human gates, everything logged, a step cap

> These five are not features you add later. They are the shape of the agent from Lab 1.

Notes:

---

## The Canonical Agent Loop

```text
        +-----------------------------------------------+
        |                                               |
        v                                               |
   +---------+   +--------+   +--------+   +----------+  |
   |  INPUT  |-->|  PLAN  |-->|  ACT   |-->| REFLECT  |--+
   |  goal   |   | decide |   | call a |   | good     |  |
   | context |   | next   |   | tool   |   | enough?  |  loop until
   +---------+   | step   |   +---+----+   +----+-----+  done OR cap
                 +--------+       |             |
                                  v             | yes
                            +-----------+       v
                            |  OBSERVE  |   +--------+
                            |  result   |   | OUTPUT |
                            +-----------+   | answer |
                                            +--------+
```

* Every loop ends one of two ways: **done**, or **max steps hit**.

> Input -> Plan -> Act -> Reflect -> Output. Memorize this — every framework this week is a variation of it.

Notes:

---

## Anatomy of the Loop

* **Input** — the goal plus available context and inputs
* **Plan** — pick the next action (or decide you're done)
* **Act** — call exactly one tool with concrete arguments
* **Observe** — read the tool result (treat it as **untrusted data**)
* **Reflect** — is the answer good enough, or loop again?
* **Output** — the final answer, ideally with sources

* The **step cap** is not optional — it's what stops a loop that never converges.

> No cap, no ship. A runaway loop is a bill and an incident waiting to happen.

Notes:

---

## The ReAct Pattern

* **ReAct = Reasoning + Acting**, interleaved in one trace
* The model emits a fixed cycle until it can answer:

```text
Thought:  what do I know, what do I need next?
Action:   tool_name(arguments)
Observation: <result the runtime pastes back>
... repeat ...
Final Answer: <the response to the goal>
```

* Your code **parses** each turn, **dispatches** the Action, **pastes back** the Observation
* Simple, transparent, framework-free — you'll build it by hand in Lab 1

> ReAct makes the reasoning *visible and auditable*. That's why we teach it first.

Notes:

---

## ReAct — A Worked Trace

Goal: *"What is the total cost if we buy 17 seats at $42/seat?"*

```text
Thought: I need to multiply 17 by 42. I'll use the calculator tool.
Action: calculator("17 * 42")
Observation: 714
Thought: 17 seats at $42 each is $714. I can answer now.
Final Answer: The total cost is $714 (17 x $42).
```

* Notice: **one action per step**, and the model **stops** once it has enough.
* The runtime — not the model — produces each `Observation`.

> The loop is dumb and reliable; the intelligence lives in Thought and in the tools.

Notes:

---

## Single- vs. Multi-Step Reasoning

* **Single-step** — one tool call answers the goal
  - "Convert 90F to Celsius" -> one `calculator` call -> done
* **Multi-step** — the answer depends on earlier results
  - "Compare the two most-cited ReAct follow-up papers" ->
    - search -> read -> search again -> synthesize

```text
single:  goal --> act --> answer
multi:   goal --> act --> observe --> act --> observe --> ... --> answer
```

* Multi-step needs a **scratchpad** (what have I learned so far?) and a **cap**.

> Most real tasks are multi-step. Lab 2 is where that becomes real.

Notes:

---

## Tools — Giving the Agent Hands

* A tool is a **function the model may call**: a name, a description, typed args
* The model picks the tool and the arguments; **your code runs it**
* Examples across this course: `calculator`, `web_search`, email, CRM query, code exec

```text
model says:   Action: web_search("react agent eval metrics")
your code:    result = TOOLS["web_search"](query="...")
model reads:  Observation: <bounded summary of result>
```

* **Least privilege**: give the fewest tools, narrowest scopes, that still work.
* **Untrusted output**: a tool result is *data*, never new instructions.

> The model proposes; your code disposes. That boundary is where safety lives.

Notes:

---

## Memory — What the Agent Remembers

* **No memory** — each run starts blank (simplest, safest default)
* **Scratchpad (this run)** — the running Thought/Observation trace in context
* **Persistent (across runs)** — stored notes, vectors, a DB (Day 4+)

* Memory is context, and context has a **budget** — summarize, don't hoard
* More memory = more capability *and* more attack surface

> Start with a scratchpad. Add persistent memory only when the task can't succeed without it.

Notes:

---

## Motivating Example — A Support / Research Assistant

* Goal: *"A customer asks why their invoice doubled this month. Explain it."*

```text
Thought: I need this customer's recent invoices.
Action: crm_lookup(account="ACME-1042")
Observation: Aug $420 (7 seats), Sep $840 (14 seats)
Thought: Seat count doubled. Confirm the per-seat price.
Action: pricing_lookup(plan="team")
Observation: $60 / seat / month
Thought: 14 x $60 = $840. The increase is 7 added seats.
Final Answer: Your Sep invoice rose from $420 to $840 because seats
went from 7 to 14 at $60/seat. Sources: CRM, pricing table.
```

> Same loop, real tools, cited sources — a demo the business actually recognizes.

Notes:

---

## Safety From Line One

* **Max-steps cap** in the loop — always
* **Human-in-the-loop** for anything that sends, buys, deletes, or changes records
* **Least privilege** — minimal tools and scopes
* **Log everything** — plan, tool call + args, result, final output (JSONL)
* **Treat tool/retrieved text as untrusted** — data, not instructions

> A demo that works once is not a pilot. We build the guardrails in from the first lab, not after.

Notes:

---

## Putting It Together

* An agent = **model + tools + a capped loop** pointed at a **goal**
* Use one only when the task is complex, messy, and language-driven
* **ReAct** makes the loop visible: Thought / Action / Observation / Final Answer
* Real tasks are **multi-step** — they need a scratchpad and a step cap
* Safety and logging are part of the design, not an afterthought

> You now have the mental model. Next you build it — by hand, no framework.

Notes:

---

## Lab 1 — Environment Setup & Your First Agent Loop (ReAct)

**Stop here and run Lab 1.**

You will:

1. Verify your Python env and `labs/.env` keys (`./labs/verify-setup.sh`).
2. Register two tools: a `calculator` and a local `lookup`.
3. Build a ReAct loop against the OpenAI API — Thought / Action / Observation / Final Answer.
4. Parse each step, dispatch the action, and paste back the observation.
5. Enforce a **max-steps cap** and print the full trace.

**Deliverable:** a runnable `agent_loop.py` that solves a multi-step question and prints a ReAct trace ending in a Final Answer.

**Time:** 45 minutes

Notes:

---

## Lab 2 — Research Assistant with Multi-Step Reasoning & Logging

**Stop here and run Lab 2.**

You will:

1. Fill the **Agent Design Canvas** before writing code.
2. Add a planning step, then loop a `search` tool multiple times (Tavily or local fallback).
3. Enforce a max-steps cap and treat every result as untrusted data.
4. Write a structured **JSONL audit log** (`run_start`, `plan`, `tool_call`, `tool_result`, `run_end`).
5. Synthesize a final answer **with sources**.

**Deliverable:** a runnable `research_agent.py` plus a `run-log.jsonl` from one complete run.

**Time:** 60 minutes

Notes:
