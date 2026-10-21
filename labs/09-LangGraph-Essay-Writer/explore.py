# %% [markdown]
# # Lab 9 — LangGraph: State, nodes, and the loop on the edge (interactive)
#
# Open this as a **notebook** (`explore.ipynb`) or run the `.py` cell-by-cell in VSCode with
# **Shift+Enter**. You build the graph up from its parts: the typed State and its reducer, one node
# at a time, then the conditional edge that makes the write/critique cycle a *declared* loop rather
# than a `while`.
#
# Runs with **no key** — `ask()` returns a deterministic `[STUB]` string, so the graph still drives
# end to end and every structural lesson lands. With `OPENAI_API_KEY` you get real essays; with
# `TAVILY_API_KEY` you get live research instead of the local corpus.
#
# Same code as `essay_writer.py`. The CLI is `python essay_writer.py "topic"`.
#
# **How to work through it** — three beats:
# - 🔮 **Predict** — before you run a cell, say what you expect. Then run and compare.
# - 🛠️ **Your turn** — let the critic end the loop early.
# - 🗣️ **Explain** — end by answering the question in your own words.

# %%
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__)) if "__file__" in dir() else os.getcwd()
sys.path.insert(0, HERE)

from essay_writer import (  # noqa: E402
    EssayState, DEFAULT_REVISIONS, MODEL, LLM,
    build_graph, plan_node, research_node, write_node, critique_node,
    should_continue, _local_corpus_search,
)
print("LLM:", f"live {MODEL}" if LLM is not None else "STUB (no OPENAI_API_KEY)")
print("research:", "Tavily (live)" if os.getenv("TAVILY_API_KEY") else "local ./corpus")

# %% [markdown]
# ## 1. The State is the contract
#
# Every node takes State and returns a **partial update dict** — nothing else. `notes` is special:
# `Annotated[list[str], operator.add]` makes it a **reducer**, so updates *append* instead of
# replacing.

# %%
EssayState.__annotations__

# %% [markdown]
# ## 2. 🔮 Predict: reducer vs. replace
#
# Two nodes each return `{"notes": ["..."]}`, and a third returns `{"draft": "..."}` twice. After
# all of that, how many items are in `notes`, and how many drafts are in `draft`? Say it out loud,
# then run.

# %%
import operator
from typing import Annotated, get_args, get_origin

for field, ann in EssayState.__annotations__.items():
    reducer = get_args(ann)[1] if get_origin(ann) is Annotated else None
    print(f"{field:<14} {'APPENDS (reducer: ' + reducer.__name__ + ')' if reducer else 'replaced on update'}")

# %% [markdown]
# ## 3. One node at a time — a node is just a function
#
# No framework magic: call it with a dict, read the dict it hands back.

# %%
state: EssayState = {
    "task": "Why reflection improves agents",
    "plan": "", "notes": [], "draft": "", "critique": "",
    "revisions": 0, "max_revisions": 1,
}
upd = plan_node(state)
print("plan_node returned keys:", list(upd))
print(upd["plan"][:400])

# %% [markdown]
# ## 4. The research node and its fallback
#
# 🔮 **Predict first:** with no `TAVILY_API_KEY`, `research_node` falls back to `./corpus`. Each
# returned note starts with a **bracketed source tag**. Why does that tag matter downstream — what
# does the writer do with it?

# %%
hits = _local_corpus_search("Why reflection improves agents")
for h in hits:
    print("-", h[:150], "...")

# %% [markdown]
# ## 5. The loop lives on the EDGE, not inside a node
#
# `should_continue` reads State and returns a **label**; the mapping in `add_conditional_edges`
# turns that label into the next node. That is the whole reflect/revise cycle.

# %%
import inspect
print(inspect.getsource(should_continue))

for revisions, cap in [(0, 2), (1, 2), (2, 2), (3, 2)]:
    label = should_continue({**state, "revisions": revisions, "max_revisions": cap})
    print(f"revisions={revisions} cap={cap} -> {label:<7} -> {'write' if label == 'revise' else 'END'}")

# %% [markdown]
# ## 6. Compile the graph and look at it

# %%
graph = build_graph()
g = graph.get_graph()
print("nodes:", [n for n in g.nodes])
print("\nedges:")
for e in g.edges:
    label = f"  [{e.data}]" if getattr(e, "data", None) else ""
    arrow = "..>" if getattr(e, "conditional", False) else "-->"
    print(f"  {e.source:<10} {arrow} {e.target:<10}{label}")
print("\n(The two dotted edges out of `critique` are the conditional pair: revise -> write, done -> END.)")
# `g.draw_ascii()` draws this as a picture, but needs the extra `grandalf` package - not in the
# course lockfile. `g.draw_mermaid()` needs nothing and pastes into any Markdown viewer:
print()
print(g.draw_mermaid())

# %% [markdown]
# ## 7. 🔮 Predict, then stream the run
#
# With `max_revisions=2`: how many times does **write** fire, how many times **critique**, and what
# finally stops the loop — the cap, or the critic deciding the draft is good enough? Commit to an
# answer, then run.

# %%
initial: EssayState = {
    "task": "Why reflection improves agents",
    "plan": "", "notes": [], "draft": "", "critique": "",
    "revisions": 0, "max_revisions": 2,
}
config = {"configurable": {"thread_id": "explore-1"}}

for chunk in graph.stream(initial, config):
    for node, update in chunk.items():
        print(f"  -> {node:<9} updated: {list(update)}")

# %% [markdown]
# ## 8. The checkpointer holds State after every node
#
# State is persisted per `thread_id`, which is what makes a run inspectable (and resumable) rather
# than a black box.

# %%
final = graph.get_state(config).values
print("revisions:", final["revisions"], "| notes:", len(final["notes"]))
print("\n--- final draft (first 700 chars) ---")
print(final["draft"][:700])

# %% [markdown]
# ## 9. 🛠️ Your turn — let the critic stop the loop early
#
# Right now the loop *only* ends at the cap: a draft the critic is already happy with gets revised
# anyway. Make the critic able to end it. Two coordinated edits, exactly as in README step 10:
#
# 1. Add to `CRITIQUE_SYS`: *if the draft already meets the rubric, reply with exactly `LGTM` and no
#    bullets.*
# 2. In `should_continue`, after the cap check, return `"done"` when the critique says `LGTM` (or
#    contains no bullet lines).
#
# Below is a scratch version you can run **without editing the module** — patch the router, give it
# a generous cap, and see whether it stops before the cap. *Reference answer in the README
# Teacher's Playbook.*

# %%
import essay_writer

essay_writer.CRITIQUE_SYS = essay_writer.CRITIQUE_SYS + (
    " If the draft already meets the rubric, reply with exactly LGTM and no bullets."
)

def should_continue_v2(state: EssayState) -> str:
    if state["revisions"] >= state["max_revisions"]:
        return "done"                                    # cap still wins
    crit = (state.get("critique") or "").strip()
    if crit.upper().startswith("LGTM") or not [l for l in crit.splitlines() if l.strip().startswith(("-", "*"))]:
        return "done"                                    # critic is satisfied
    return "revise"

essay_writer.should_continue = should_continue_v2
graph2 = essay_writer.build_graph()                      # rebuild so the new router is wired in

for chunk in graph2.stream({**initial, "max_revisions": 4},
                           {"configurable": {"thread_id": "explore-lgtm"}}):
    for node, update in chunk.items():
        print(f"  -> {node:<9} updated: {list(update)}")

st = graph2.get_state({"configurable": {"thread_id": "explore-lgtm"}}).values
print("\nstopped after revisions:", st["revisions"], "of cap 4")
print("last critique:", (st["critique"] or "")[:200])

# %% [markdown]
# ## 10. 🗣️ Explain
#
# In two or three sentences: why is the stop decision a **conditional edge** (a router function)
# instead of an `if` buried inside `critique_node`? What do you gain by keeping it on the edge —
# think about what you can now test, draw, and change without touching a node.
