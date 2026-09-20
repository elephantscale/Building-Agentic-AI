# Lab 8 — Essay Writer Agent with Retrieval + Reflection (LangGraph)

## Goal

Rebuild the reflect-and-revise loop from Day 2 as a real **LangGraph** state graph.
You will assemble a typed `State`, four nodes (**plan -> research -> write -> critique**),
and a **conditional edge** that loops the writer and critic up to *N* times. Research
uses **Tavily** agentic search with a **local corpus fallback**, and a **checkpointer**
makes the run persistent and streamable. By the end you can point to each of the six
LangGraph ideas — State, nodes, edges, conditional edges, checkpointer, streaming — in
running code.

## Time

75 minutes

## Tools

- Python 3.11+
- `langgraph`, `langchain-openai`, `tavily-python`, `python-dotenv`, `rich`
- OpenAI API key in `labs/.env` (works in a STUB mode without one)
- Tavily API key in `labs/.env` (optional — falls back to the local corpus)

## Files in this lab

```
08-LangGraph-Essay-Writer/
├── README.md            # this file
├── requirements.txt
├── essay_writer.py      # the complete LangGraph program
└── corpus/              # local fallback evidence for the research node
    ├── agentic-ai.txt
    ├── reflection.txt
    └── langgraph.txt
```

## Steps

1. **Install.** From the repo root, with your venv active:
   ```sh
   cd labs/08-LangGraph-Essay-Writer
   pip install -r requirements.txt
   ```
2. **Keys.** Ensure `labs/.env` exists (see `labs/SETUP.md`). `OPENAI_API_KEY` is
   recommended; `TAVILY_API_KEY` is optional. With neither, the lab still runs.
3. **Read the State.** Open `essay_writer.py` and find `class EssayState`. Note that
   `notes` is `Annotated[list[str], operator.add]` — a **reducer** so research
   findings accumulate across nodes instead of overwriting.
4. **Trace the nodes.** Each of `plan_node`, `research_node`, `write_node`, and
   `critique_node` takes State and returns a *partial* update dict. Nothing else.
5. **Find the loop.** Read `should_continue` and the `add_conditional_edges("critique",
   ...)` call. This is the reflect/revise cycle, declared as a router + mapping.
6. **Run it.**
   ```sh
   python essay_writer.py "Why reflection improves agents"
   ```
7. **Watch it stream.** The run prints after every node (that is `graph.stream`).
8. **Change the loop cap** and see the difference:
   ```sh
   python essay_writer.py --revisions 1 "Why reflection improves agents"
   ```
9. **Force the fallback.** Temporarily comment out `TAVILY_API_KEY` in `labs/.env`
   (or leave it unset) and confirm the research node uses `./corpus`.

## Starter Code

The State and its reducer — the part students most often get wrong:

```python
from typing import TypedDict, Annotated
import operator

class EssayState(TypedDict):
    task: str
    plan: str
    notes: Annotated[list[str], operator.add]   # APPENDS across nodes
    draft: str
    critique: str
    revisions: int
    max_revisions: int
```

The conditional edge — the reflect/revise loop:

```python
def should_continue(state: EssayState) -> str:
    if state["revisions"] >= state["max_revisions"]:
        return "done"
    return "revise"

builder.add_edge("write", "critique")
builder.add_conditional_edges(
    "critique",
    should_continue,
    {"revise": "write", "done": END},
)
```

Compile with a checkpointer, then stream:

```python
graph = builder.compile(checkpointer=MemorySaver())
config = {"configurable": {"thread_id": "essay-1"}}

for chunk in graph.stream(initial_state, config):
    for node_name, update in chunk.items():
        print(f"-> {node_name} updated: {list(update)}")

final = graph.get_state(config).values   # checkpointer holds final State
print(final["draft"])
```

The research node's fallback (why the lab is never blocked):

```python
def research_node(state):
    if os.getenv("TAVILY_API_KEY"):
        try:
            return {"notes": _tavily_search(state["task"])}
        except Exception:
            pass                                  # fall through
    return {"notes": _local_corpus_search(state["task"])}
```

## What a correct run looks like

With `--revisions 2` and the local corpus (no Tavily key), abridged:

```text
──────────────────── Essay task: Why reflection improves agents ────────────────────
plan: outlining
  -> plan updated: ['plan']
research: gathering evidence
  no TAVILY_API_KEY; using local corpus
  -> research updated: ['notes']
write: drafting (revision 1)
  -> write updated: ['draft', 'revisions']
critique: reviewing draft
  -> critique updated: ['critique']
write: drafting (revision 2)
  -> write updated: ['draft', 'revisions']
critique: reviewing draft
  -> critique updated: ['critique']
──────────────────────────── Final essay ────────────────────────────
Reflection is the pattern where an agent evaluates and revises its own output before
returning it. A first draft from a language model is usually plausible but shallow...
[three to four paragraphs, grounded in the corpus]

revisions: 2  |  research notes: 3
```

Note the **write -> critique -> write -> critique** cycle: the conditional edge sent
control back to `write` once, then stopped at the cap. With a live `TAVILY_API_KEY`
the research line reads `source: Tavily (live search)` and `notes` cite live URLs.

## Deliverable

- A runnable LangGraph essay writer (`essay_writer.py`).
- A saved **streamed transcript** showing the node-by-node run and the write/critique
  loop firing.
- The **final revised essay**.
- A one-line note: how many times did the loop run at `--revisions 2`, and why did it
  stop?

## Troubleshooting

- **`ModuleNotFoundError: langgraph`** — you skipped `pip install -r requirements.txt`
  or the venv is not active.
- **`KeyError: 'notes'`** — you removed the reducer or forgot to seed `notes: []` in
  the initial State. A node reads `state["notes"]` before research runs only if you
  reordered edges.
- **The loop never stops / runs once only** — check `should_continue`: it compares
  `revisions` (incremented in `write_node`) against `max_revisions`.
- **No essay, only `[STUB gpt-4.1] ...`** — `OPENAI_API_KEY` is not set. The graph is
  working; add a key for real prose.
- **Research returns "No corpus match"** — your topic shares no keywords with the
  corpus; the fallback is deliberately simple. Use a topic about agents/reflection, or
  add a `.txt` file to `corpus/`.
- **`get_state` returns empty** — you must pass the same `config` (same `thread_id`)
  you invoked with; State lives per thread in the checkpointer.

## Teacher's Playbook

**The one-sentence framing.** "We already built this loop by hand in Lab 1 with a
`while` and an `if`. Today the `while` becomes the graph and the `if` becomes a
conditional edge — and in return we get streaming, persistence, and a place to bolt on
human approval for free."

**Live-demo script (8 min).**
1. Run once with `--revisions 0` — show it writes a draft and stops (loop never fires).
2. Run with `--revisions 2` — narrate each streamed line; pause on the *second*
   `write: drafting (revision 2)` and say "there is the reflect/revise loop."
3. Open `labs/.env`, remove the Tavily key, rerun — point at
   `no TAVILY_API_KEY; using local corpus`. "No student is ever blocked."

**Worked model answer.** At `--revisions 2` the loop runs the writer **twice** and the
critic **twice**: write(1) -> critique(1) -> [revise] -> write(2) -> critique(2) ->
[done, because revisions (2) >= max_revisions (2)] -> END. It stops on the cap, not
because the critic was satisfied — that distinction is the point.

**Common mistakes + fixes.**
- *Returning full State from a node* instead of a partial dict — works, but teach the
  partial-update habit; it is what makes reducers meaningful.
- *Overwriting `notes`* by dropping the `Annotated[..., operator.add]` reducer — then a
  second research pass would erase the first. Show it by deleting the annotation.
- *Putting the `if` inside a node* instead of a conditional edge — "then the graph
  diagram lies about the control flow." The router keeps the graph honest.
- *Expecting the critic to end the loop* — it can't; only the cap ends it here. Ask the
  class: how would you let the critic say "good enough, stop early"? (Return `"done"`
  from `should_continue` when the critique contains no revision bullets.)

**Debrief Q&A.**
- *Where would a human-approval gate go?* Compile with
  `interrupt_before=["write"]` or add a `publish` node and interrupt before it; the
  checkpointer already makes resume possible.
- *How is this different from LangChain?* LangChain chains are mostly straight lines;
  LangGraph adds first-class cycles and durable state.
- *Why Tavily and not `requests`?* Tavily returns ranked, cleaned, LLM-ready snippets;
  raw HTML would need scraping and is noisy.

**What good looks like.** The student can point at the six LangGraph ideas in the file,
can explain why `notes` needs a reducer, and can state exactly why the loop ran twice.

---
