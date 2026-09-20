# Building Agentic AI

Elephant Scale

---

## Pre-requisites and Expectations

* Comfortable with **Python** (functions, packages, virtual environments)

* Comfortable with **API calls and JSON**

* Basic **machine-learning / LLM** familiarity is helpful, not required

* Curiosity!
  - Ask a lot of questions
  - Agents are new — we are all still learning the patterns

* Class will move at the pace of the majority

Notes:

---

## Our Teaching Philosophy

* Emphasis on concepts & fundamentals — patterns outlive frameworks

* Highly interactive (questions and discussions are welcome)

* Hands-on (learn by doing)

* You will *build* an agent on every major framework in production use today

Notes:

---

## Lots of Labs: Learn By Doing

* 15 labs + a team capstone

* Every lab has copy-ready code and a "what a correct run looks like"

* Cloud labs have a **local fallback** — nobody is ever blocked

> We build the pattern by hand first, then let the framework carry it.

Notes:

---

## About You And Me

* About the instructor
* About you
  - Your name
  - Your role (developer, data scientist, lead, PM, ...)
  - Languages / stacks you use every day
  - Agent experience so far (1 - new ... 4 - I ship them)
  - Something non-technical about you!

Notes:

---

## What Is An Agent? (One-Line Version)

* An **LLM in a loop** that can **use tools** to pursue a **goal**

```text
goal -> plan -> act (call a tool) -> observe -> reflect -> decide -> repeat -> answer
```

> A chatbot answers. An agent *acts* — so it needs limits, evaluation, and governance.

Notes:

---

## The Five-Day Map

| Day | You go from... |
|-----|----------------|
| 1 | mental model → a hand-built agent loop (ReAct) + a research assistant |
| 2 | reflection → tools, structured output, MCP, an email assistant |
| 3 | evaluation & debugging → multi-agent + planning-driven agents |
| 4 | frameworks: LangGraph, low-code, Bedrock, DSPy, Claude |
| 5 | voice agents, governance, and the team capstone |

In every module you build a real artifact you can take back to work.

---

## Ground Rules for Building Agents

* **Least privilege** — an agent gets the fewest tools and permissions that work.

* **Human-in-the-loop** for anything that sends, publishes, deletes, buys, or changes records.

* **Log everything** — every plan, tool call, and result is auditable.

* **Evaluate before you trust** — a demo that works once is not a pilot.

* **Treat tool output and retrieved text as untrusted data**, not instructions.

> These five habits separate a useful agent from an expensive incident. We build them in from Lab 1.

Notes:
