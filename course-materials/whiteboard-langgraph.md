# Whiteboard: LangGraph (Day 4 opener)

My drawing sequence for `slides/07-langgraph-tavily.md`. Instructor notes, first person —
the deck has the pieces but states them flat; this is the order I build them on the board so
they arrive as one idea instead of four. Every number below is the **real** behaviour of
`labs/09-LangGraph-Essay-Writer/essay_writer.py`, verified on the class VM 2026-10-21, so the
board matches what their terminals print.

Board plan: I draw **one picture, left to right, adding to it**. By the end the board is the
same graph as deck slide 4 and `labs/09-LangGraph-Essay-Writer/graph.md`. Nothing gets erased
except the `while`.

---

## 0. The bridge — we already wrote this program (two minutes, no drawing yet)

Day 1, Lab 1, we built the agent loop by hand. Put it up as code, not as a picture:

```text
  for step in range(1, MAX_STEPS + 1):
      ...think...
      observation = TOOLS[name](arg)
      messages.append(observation)
      if "Final Answer" in reply: break
```

Ask the room: **what are the three things this code owns?** Let them work it out. I want these
three words on the board, because they are the whole module:

```text
  the DATA        messages
  the WORK        the body of the loop
  the NEXT STEP   the if / break
```

> LangGraph takes all three away from you and asks for them back, separately.

That sentence is the module. Everything after it is detail.

---

## 1. Cross out the `while`

Literally draw a line through `for step in range(...)`. Say: by the end of this hour there
will be **no loop in our code at all** — and the program still loops. That's the thing to be
suspicious about, and we're going to see exactly who runs it.

Expect the objection: *"so I lose control."* Good — write it on the board as a question to
answer at the end. (§7 answers it.)

---

## 2. State — the data, but declared

Draw a box, title it `EssayState`, and write the fields as I say them:

```text
  ┌─ EssayState ──────────────────┐
  │  task          str            │
  │  plan          str            │
  │  notes         list[str]  ★   │
  │  draft         str            │
  │  critique      str            │
  │  revisions     int            │
  │  max_revisions int            │
  └───────────────────────────────┘
```

Star exactly one field: `notes`. Then write next to it:

```text
  notes: Annotated[list[str], operator.add]
                              ^^^^^^^^^^^^ the reducer
```

Say it plainly: **six of these replace, one of them appends.** A field with no reducer takes
the new value and drops the old one. `notes` merges instead.

Draw the two-line comparison — this is worth the thirty seconds:

```text
  draft    "#1"  +  "#2"   ->  "#2"            the first one is gone
  notes    [a]   +  [b,c]  ->  [a, b, c]       nothing is lost
```

> A reducer is the answer to "two nodes both wrote this field — now what?"

Hold it. It pays off in §6, and it is the single thing people miss on first read.

---

## 3. A node is a function

Draw one box with an arrow in and an arrow out:

```text
     State  ──►  ┌────────┐  ──►  {"draft": ..., "revisions": 2}
                 │ write  │
                 └────────┘        a PARTIAL dict - only what changed
```

Say: no base class, no `self`, no globals. State in, a dict of **just the fields you touched**
out. The runtime merges it.

The proof they can hold onto: in the notebook you call `plan_node(state)` yourself, with a
plain dict, before any graph exists. A node doesn't need the framework to run.

---

## 4. The spine — four arrows that never change

Now start the real picture, centre of the board, top to bottom. Solid arrows:

```text
      (start)
         │
         ▼
      ┌──────┐
      │ plan │
      └──────┘
         │
         ▼
      ┌──────────┐
      │ research │
      └──────────┘
         │
         ▼
      ┌───────┐
      │ write │
      └───────┘
         │
         ▼
      ┌──────────┐
      │ critique │
      └──────────┘
```

Say: these four edges are declared once and never reconsidered. `add_edge("plan","research")`
is a fact about the program, not a decision made at runtime. **Static edges are the boring
part, and that is a compliment.**

---

## 5. The fork — where the loop went

Now the payoff. Draw **two dashed arrows** out of `critique`, in a different colour if you
have one: one going down to `(END)`, one curving back up to `write`. Label them `done` and
`revise`.

Then, off to the side, write the router:

```text
  def should_continue(state) -> str:
      if state["revisions"] >= state["max_revisions"]:
          return "done"
      return "revise"

  {"revise": write,  "done": END}     <- the mapping
```

The beat I want to land, said slowly:

> The router never names a node. It returns a **word**. The mapping turns the word into a node.

Why that matters: the function that *decides* and the wiring that *routes* are separate, so
you can rewire the flow without touching the decision — which is exactly the §9 notebook
exercise.

Draw the truth table under it. With `max_revisions = 2` the whole behaviour is four rows:

```text
  revisions  max   returns     next
      0       2    "revise"    write
      1       2    "revise"    write
      2       2    "done"      END
      3       2    "done"      END
```

Point at the board: **that is the `if` from Lab 1.** Same logic. It just lives on the edge now
instead of inside the loop body, which is why it can be printed, drawn, and replayed.

---

## 6. Trace one run — the money shot

The picture is finished. Now walk a real run across it with a tally in the corner. Start it:

```text
  notes 0     draft —     revisions 0      max_revisions 2
```

Walk the arrows and update the tally out loud:

```text
  plan        -> {plan}                notes 0   draft —    rev 0
  research    -> {notes}               notes 3   draft —    rev 0     ★ appended
  write       -> {draft, revisions}    notes 3   draft #1   rev 1
  critique    -> {critique}            notes 3   draft #1   rev 1
     router:  1 >= 2 ?  NO  -> "revise"  -> back up to write
  write       -> {draft, revisions}    notes 3   draft #2   rev 2
     ^ notes STILL 3 (reducer kept them) ... draft #1 is GONE (no reducer)
  critique    -> {critique}            notes 3   draft #2   rev 2
     router:  2 >= 2 ?  YES -> "done"    -> END
```

Then show them the last line their own terminal printed:

```text
  revisions: 2  |  research notes: 3
```

The board and the terminal agree. That line is the whole module in six characters of output.

The second `write` is the beat to slow down on: **the same node ran twice, and the two fields
behaved differently** — `notes` kept everything, `draft` was overwritten. Both rules were
declared back in §2, on the State box, not in the node. Point back at the star.

> You don't write merge logic in your nodes. You declare it once on the field.

---

## 7. Answer the objection from §1

Go back to "so I lose control" and answer it in four words on the board:

```text
  stream      partial progress, node by node
  checkpoint  State saved per thread_id - read it back, or resume
  inspect     the graph prints itself  (draw_mermaid -> graph.md)
  rewire      change the router, rebuild, flow changes - no node touched
```

Say: a hand loop gives you none of these unless you build each one yourself. **That's the
trade.** You stop owning the loop; the runtime starts owning the four things that are tedious
to build around a loop.

If I have the browser up, this is the moment to show `graph.md` on GitHub — the rendered
picture next to my drawing, and say: *"I drew that. This one was printed by the program. They
match because the picture is generated from the compiled graph."*

---

## 8. Hand-off

> Nodes do the work. Edges decide what happens next. State is the memory.

Send them in:

```powershell
cd labs\09-LangGraph-Essay-Writer
python essay_writer.py "Why reflection improves agents"
```

Tell them what to look for: the `revise` line firing once, the citations in brackets, and the
final `revisions: 2 | research notes: 3` — the tally from the board.

Then the notebook, §1–§6 first (nearly free, no waiting, ends on the graph), and §7–§9 if the
room wants streaming, the checkpointer, and the rewire exercise.

---

### Footnotes for me

- **§6 numbers** are from the real VM run on 2026-10-21: `revisions: 2 | research notes: 3`
  with the default `max_revisions = 2`. Three notes because the local corpus search returns
  `k=3`.
- **No Tavily key in class.** `research_node` falls back to `./corpus/*.txt` and prints
  `no TAVILY_API_KEY; using local corpus`. That is expected output, not a failure — say so
  before someone raises a hand. Both paths return the same `[source] text` shape, which is why
  the citation beat works either way.
- **If asked why it's called Mermaid**: nobody documents it. Knut Sveidqvist wrote it in 2014
  to get diagrams out of proprietary binary formats and into text. Mermaid, LangGraph and
  GitHub are three unrelated projects that happen to agree on a text format.
- **The visual version of these notes**, if I want to study it rather than draw it:
  the LangGraph explainer artifact (State, reducer, router, and the §6 trace as a table).
