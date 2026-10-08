# Building Agentic AI

© Elephant Scale

---

## Agenda

| Module | Topic |
|--------|-------|
| 1 | Foundations of Agentic AI |
| 2 | Reflection & Self-Evaluation |
| 3 | Tools, Structured Output & MCP |
| 4 | RAG & Vector Databases |
| 5 | Evaluation, Error Analysis & Debugging |
| 6 | Multi-Agent Systems & Planning |
| 7 | LangGraph & Tavily |
| 8 | Low-Code Agentic Design |
| 9 | Agentic on AWS Bedrock |
| 10 | DSPy & Databricks |
| 11 | Agentic with Claude |
| 12 | Voice Agents with Google ADK |
| 13 | Governance with Databricks |
| 14 | Capstone: Enterprise AI Agent Challenge |

Notes:

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

* API — no need to learn anything by heart

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

## Analogy: Learning To Fly...

<img src="../images/learn-to-fly.png" style="width:80%;"/> <!-- {"left" : 0.66, "top" : 2.06, "height" : 4.89, "width" : 8.93} -->

Notes:

---

## Introductions

<img src="../images/classroom-instruction.png" style="width:70%;"/> <!-- {"left" : 0.6, "top" : 2.06, "height" : 4.96, "width" : 9.04} -->

Notes:

---

## + Flight Time

<img src="../images/cockpit.png" style="width:70%;"/> <!-- {"left" : 0.61, "top" : 2.06, "height" : 4.95, "width" : 9.04} -->

Notes:

---

## This Will Take A Lot Of Practice

<img src="../images/practice.png" style="width:70%;"/> <!-- {"left" : 0.69, "top" : 2.06, "height" : 5.63, "width" : 8.87} -->

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

<img src="../images/hiking-3.jpg" style="width:18%;"/> &nbsp; <!-- {"left" : 1.08, "top" : 6.08, "height" : 1.99, "width" : 2.25} --><img src="../images/ice-cream-3.png" style="width:25%;"/> &nbsp; <!-- {"left" : 3.36, "top" : 6.1, "height" : 1.92, "width" : 3.54} --><img src="../images/biking-1.jpg" style="width:18%;"/> &nbsp; <!-- {"left" : 6.92, "top" : 6.08, "height" : 1.99, "width" : 2.25} -->

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
