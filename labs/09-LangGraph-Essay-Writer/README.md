# Lab 9 — Essay Writer Agent with Retrieval + Reflection (LangGraph)

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
09-LangGraph-Essay-Writer/
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
   cd labs/09-LangGraph-Essay-Writer
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
6. **🔮 Predict, then run.** Before you run: with the default `--revisions 2`, how many times
   will **write** fire, and how many times **critique**? And what finally stops the loop — the
   cap, or the critic deciding the draft is good enough? Commit to an answer, then:
   ```sh
   python essay_writer.py "Why reflection improves agents"
   ```
7. **Watch it stream.** The run prints after every node (that is `graph.stream`). Check your
   prediction against the `write: drafting (revision N)` lines.
8. **Change the loop cap** and confirm the pattern:
   ```sh
   python essay_writer.py --revisions 1 "Why reflection improves agents"
   ```
9. **Force the fallback.** Temporarily comment out `TAVILY_API_KEY` in `labs/.env`
   (or leave it unset) and confirm the research node uses `./corpus`.
10. **🛠️ Your turn — let the critic stop the loop early.** Right now the loop *only* ends at the
    cap: even a draft the critic is happy with gets revised again. Make the critic able to end it.
    Two small, coordinated edits:
    - In `CRITIQUE_SYS`, add a line: *if the draft already meets the rubric, reply with exactly
      `LGTM` and no bullets.*
    - In `should_continue`, after the cap check, return `"done"` when the critique says `LGTM`
      (or contains no bullet lines).

    Re-run with a generous cap (`--revisions 4`) and a simple topic; a good draft should now stop
    **before** hitting the cap. *Reference answer in the Teacher's Playbook.*
11. **🗣️ Explain.** In one or two sentences: why is this stop decision a **conditional edge** (a
    router function) instead of an `if` buried inside `critique_node`? What do you gain by keeping
    it on the edge?

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


## Explore it interactively (VSCode)

Build the graph up from its parts — open **`explore.ipynb`** (notebook, ships with saved outputs)
or **`explore.py`** (VSCode `# %%` cells, Shift+Enter). Same code as `essay_writer.py`: the typed
State and its reducer, each node called by hand, the router truth-table, the compiled graph's nodes
and edges, then the streamed run and the checkpointer. Runs with **no key** (`ask()` returns a
`[STUB]` string and the graph still drives end to end). (Needs the Python + Jupyter extensions.)
Work the three beats: **🔮 predict** the reducer's effect and the write/critique count, **🛠️ your
turn** let the critic end the loop early (§9 patches the router without editing the module), and
**🗣️ explain** why the stop decision lives on the edge.

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
### Companion exercise — reference answers (`explore.ipynb` / `explore.py`)
- **🔮 Predict (§2):** `notes` **appends** (it is `Annotated[list[str], operator.add]`), so two
  nodes returning one note each leave **2** items. `draft` is **replaced**, so two writes leave
  **1** draft. The reducer is the only reason research findings survive a second research pass.
- **🔮 Predict (§4):** each local-corpus note is prefixed with its source file, e.g.
  `[reflection.txt] ...`. The writer is told to cite that tag verbatim, so the tag is what turns a
  fluent essay into a **checkable** one — it is the same grounding-and-citation contract as Lab 6,
  carried into a graph.
- **§5 router truth-table:** `revisions=0,1 -> revise -> write`; `revisions>=cap -> done -> END`.
  Note the cap is the *only* stop condition in the shipped code — the critic has no vote. That is
  what §9 changes.
- **🔮 Predict (§7):** with `max_revisions=2`, **write fires twice and critique twice**, and the run
  stops at the **cap** — not because the critic was satisfied. Students who predict "it stops when
  the essay is good" have just discovered the missing feature they're about to build.
- **🛠️ Your turn (§9):** with the `LGTM` clause added to `CRITIQUE_SYS` and the router returning
  `done` on `LGTM`/no-bullets, a decent draft stops **before** the cap — in the shipped run it
  stops after **2 revisions of a cap of 4**, with the last critique reading exactly `LGTM`. The
  cap check stays first: the critic can end the loop early but can never extend it past the cap.
  (Note §9 does this by reassigning `essay_writer.should_continue` and **rebuilding** the graph —
  a compiled graph has already captured the old function, so patching without rebuilding does
  nothing. That surprise is itself worth 30 seconds of discussion.)
- **🗣️ Explain (§10):** keeping the decision on the edge means the loop is **declared, not
  implemented**: you can print the graph, unit-test `should_continue` as a pure function over
  State, and change the stopping policy without touching `critique_node`. Buried in the node, the
  control flow becomes invisible to the graph — nothing to draw, and nothing to test in isolation.

**Three-beat companion — reference answers (Steps 6, 10, 11).**
- **🔮 Predict (§6):** at `--revisions 2` the loop runs **write ×2, critique ×2** —
  write(1)→critique(1)→[revise]→write(2)→critique(2)→[done]. It stops on the **cap**, not because
  the critic was satisfied. Students who predict "it stops when the essay is good" have found the
  exact gap Step 10 fixes.
- **🛠️ Your turn (§10):** working early-stop —
  ```python
  CRITIQUE_SYS = (
      "You are a demanding essay critic. Score the draft against this rubric: grounded in "
      "evidence, complete, clear, right length. Return 2-4 specific, actionable revision "
      "instructions as bullets. Be concise. If the draft already meets the rubric, reply with "
      "exactly 'LGTM' and no bullets."
  )

  def should_continue(state: EssayState) -> str:
      if state["revisions"] >= state["max_revisions"]:
          return "done"                                  # hard cap always wins
      crit = state.get("critique", "")
      has_bullets = any(ln.strip().startswith(("-", "*", "•")) for ln in crit.splitlines())
      if "LGTM" in crit or not has_bullets:
          return "done"                                  # critic satisfied -> stop early
      return "revise"
  ```
  Note the cap check stays **first** — the critic can end the loop early but can never override the
  safety cap. That ordering is the teaching point.
- **🗣️ Explain (§11):** keeping the decision on the **edge** means the graph diagram stays honest —
  the control flow (loop vs. end) is visible in the topology, not hidden inside a node. You can swap
  the router, add a human-approval interrupt, or visualize the graph without touching `critique_node`.

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
