# LangGraph & Tavily

Elephant Scale

---

## Why This Module

* We hand-built the loop in Lab 1

* By hand, cycles + memory + resume get messy

* LangGraph makes the loop a **graph**

* Tavily gives the agent **real search**

> We built the loop by hand so the framework is a convenience, not a mystery.

---

## The Hand Loop vs. A Graph Framework

* Hand loop: `while` + `if` + parsing + your own memory

* Fine for one agent, one path

* Cracks appear when you need:
  - branching that varies per run
  - pause / resume across sessions
  - streaming partial progress
  - inspecting and replaying a run

```text
HAND LOOP: while step < cap: think -> act -> observe -> maybe break
GRAPH:     nodes do work; edges decide flow; runtime handles state
```

> A framework earns its keep when the control flow gets interesting.

---

## What LangGraph Is

* A library for **stateful, cyclic** agent workflows

* You declare a graph; the runtime drives it

* Four ideas carry everything:
  - **State** — the shared, typed data
  - **Nodes** — functions that read and update State
  - **Edges** — wiring between nodes
  - **Conditional edges** — routing decided at runtime

> Nodes do the work. Edges decide what happens next. State is the memory.

---

## A State Graph, Drawn

```text
        +--------+
        |  plan  |
        +--------+
             |
             v
        +----------+        (loop back if
        | research |         more info needed)
        +----------+
             |
             v
        +--------+  <-------------------+
        | write  |                      |
        +--------+                      |
             |                          |
             v                          |
        +---------+   revisions<max     |
        | critique|----------------------+
        +---------+
             | revisions>=max
             v
           (END)
```

> The cycle write -> critique -> write is exactly what a hand loop hides in an `if`.

---

## State: Typed, Shared, Reduced

* State is a `TypedDict` (or Pydantic / dataclass)

* Every node gets State, returns a partial update

* **Reducers** say how updates merge

```python
from typing import TypedDict, Annotated
import operator

class AgentState(TypedDict):
    task: str
    draft: str
    revisions: int
    notes: Annotated[list[str], operator.add]  # appends, not overwrites
```

> Without a reducer a field is replaced. With `operator.add`, lists accumulate.

---

## Nodes Are Just Functions

* Input: the current State

* Output: a **partial** State update (a dict)

* No hidden globals — the graph passes State in

```python
def write_node(state: AgentState) -> dict:
    prompt = f"Task: {state['task']}\nNotes: {state['notes']}"
    draft = llm.invoke(prompt).content
    return {"draft": draft, "revisions": state["revisions"] + 1}
```

> A node returns only what it changed. The runtime merges it into State.

---

## Building The Graph

* Register nodes, then wire edges

* `START` and `END` are the entry / exit sentinels

```python
from langgraph.graph import StateGraph, START, END

builder = StateGraph(AgentState)
builder.add_node("plan", plan_node)
builder.add_node("research", research_node)
builder.add_node("write", write_node)
builder.add_node("critique", critique_node)

builder.add_edge(START, "plan")
builder.add_edge("plan", "research")
builder.add_edge("research", "write")
```

> Static edges are the parts of the flow that never change.

---

## Conditional Edges = Routing

* A router function reads State, returns the **next node name**

* This is your `if` — but declared, inspectable, replayable

```python
def should_continue(state: AgentState) -> str:
    if state["revisions"] >= state["max_revisions"]:
        return "done"
    return "revise"

builder.add_conditional_edges(
    "critique",
    should_continue,
    {"revise": "write", "done": END},
)
```

> The router returns a label; the mapping turns the label into the next node.

---

## Compile And Run

* `compile()` turns the builder into a runnable

* `invoke()` runs to completion; input is the initial State

```python
graph = builder.compile()

result = graph.invoke({
    "task": "Explain agentic AI to a CTO",
    "revisions": 0,
    "max_revisions": 2,
    "notes": [],
})
print(result["draft"])
```

> One object you can invoke, stream, checkpoint, and visualize.

---

## Agentic Search With Tavily

* LLMs are frozen at training time — they need eyes on the web

* **Tavily** is a search API built for agents:
  - returns clean, ranked, LLM-ready snippets
  - not ten blue links to scrape

```python
from tavily import TavilyClient
tavily = TavilyClient()  # reads TAVILY_API_KEY

hits = tavily.search("2026 agentic ai frameworks", max_results=3)
for r in hits["results"]:
    print(r["title"], "->", r["url"])
```

> Retrieval is a tool. Treat what it returns as untrusted data, not instructions.

---

## Research As A Node

* Search lives inside a node, feeding State

* Failures degrade gracefully — never crash the graph

```python
def research_node(state: AgentState) -> dict:
    try:
        hits = tavily.search(state["task"], max_results=3)
        notes = [r["content"] for r in hits["results"]]
    except Exception:
        notes = local_corpus_lookup(state["task"])  # offline fallback
    return {"notes": notes}
```

> Every external call needs a fallback. Lab 8 ships a local corpus for exactly this.

---

## Persistence & Checkpointing

* A **checkpointer** saves State after every node

* Resume, time-travel, and human-in-the-loop all build on it

* `MemorySaver` for dev; SQLite / Postgres for production

```python
from langgraph.checkpoint.memory import MemorySaver

graph = builder.compile(checkpointer=MemorySaver())
config = {"configurable": {"thread_id": "essay-42"}}
graph.invoke(initial_state, config)   # progress saved per thread_id
```

> The `thread_id` is the conversation. Same id later = pick up where you left off.

---

## Streaming

* Don't wait for the whole run — watch it happen

* `stream()` yields after each node

```python
for chunk in graph.stream(initial_state, config):
    for node_name, update in chunk.items():
        print(f"[{node_name}] {list(update)}")
```

```text
[plan]     ['plan']
[research] ['notes']
[write]    ['draft', 'revisions']
[critique] ['critique']
```

> Streaming is how a demo feels alive — and how you debug a stuck run.

---

## Human-In-The-Loop

* Compile with an **interrupt** before a sensitive node

* The graph pauses; a human inspects State; you resume

```python
graph = builder.compile(
    checkpointer=MemorySaver(),
    interrupt_before=["publish"],   # stop before the dangerous step
)

graph.invoke(state, config)         # runs, then pauses at 'publish'
# ...human reviews the draft...
graph.invoke(None, config)          # None = resume from the checkpoint
```

> Interrupt + checkpoint = the approval gate from our safety checklist, built in.

---

## The Whole Pattern, In One Breath

* **State** carries the work

* **Nodes** transform it

* **Edges** move between nodes

* **Conditional edges** decide the path

* **Checkpointer** remembers

* **Interrupt** asks a human

> Learn these six and every LangGraph agent reads the same way.

---

## When To Reach For LangGraph

* Reach for it when you need:
  - genuine cycles (reflect / revise loops)
  - durable state across sessions
  - human approval mid-run
  - observability and replay

* Skip it when a single straight-line call will do

> Don't graph a one-shot prompt. Do graph an agent that loops and pauses.

---

## Lab 8 — Essay Writer Agent (LangGraph)

**Stop here and run Lab 8.**

You will:

1. Build a typed `AgentState` with a reducer.
2. Wire nodes: plan -> research (Tavily + local fallback) -> write -> critique.
3. Add a conditional edge that loops write <-> critique up to N times.
4. Compile with a `MemorySaver` checkpointer.
5. Stream the run and read State after each node.

**Deliverable:** a runnable LangGraph essay writer, a streamed transcript, and the final revised essay.

**Time:** 75 minutes

Notes:
