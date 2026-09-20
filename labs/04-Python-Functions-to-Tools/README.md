# Lab 4 — Convert Python Functions to Agentic Tools

## Goal

Take three plain Python functions and promote them into **agentic tools** the model can call:

- `get_order_status(order_id)` — a read-only order lookup
- `lookup_help_center(query)` — a read-only search over `assets/help_center.md`
- `calc(expression)` — safe arithmetic (AST-based, no `eval`)

For each, you add the three things a model needs — a **description**, a **JSON Schema**, and a
**safety class** — then run the full **tool-calling round-trip** with OpenAI: the model proposes
a call, your code **validates** the args against the schema, checks the safety class, dispatches
the function, and pastes the structured result back. A `MAX_STEPS` cap guarantees termination.

## Time

50 minutes

## Tools

- Python 3.11+
- OpenAI API (`gpt-4.1` by default; `gpt-4o-mini` also works)
- `jsonschema` for argument validation
- `labs/.env` with `OPENAI_API_KEY` (see `labs/SETUP.md`)
- Shared asset: `../assets/help_center.md`

## Files in this lab

- `tools.py` — the three functions, their JSON Schemas, their safety classes, and the
  registry that renders them to OpenAI (and Anthropic) tool specs.
- `tool_agent.py` — the tool-calling loop: validate -> safety check -> dispatch -> repeat.
- `requirements.txt` — `openai`, `python-dotenv`, `jsonschema`, `rich`.

## Steps

1. Install and confirm your key:
   ```sh
   cd labs/04-Python-Functions-to-Tools
   pip install -r requirements.txt
   ```
2. Read `tools.py`. For each tool, note the **description** (when to use / when not to), the
   **schema** (types, `enum`, `pattern`, `additionalProperties: false`), and the **safety
   class** (`safe`/`guarded`/`dangerous`).
3. Run the agent on the default multi-part question:
   ```sh
   python tool_agent.py
   ```
4. Watch the trace: each `call` is validated against its schema before the `result` runs. The
   model chooses which tools to call and in what order.
5. Try your own questions, including ones that force multiple tools:
   ```sh
   python tool_agent.py "How do I export invoices, and what's the status of order 88124?"
   python tool_agent.py "What is 240 * 3 minus a 30-day refund?"
   ```
6. **Break it on purpose** to see validation and safety in action:
   - Ask about order `9` (fails the `^[0-9]{4,6}$` pattern -> `bad_args`, model recovers).
   - Ask it to "send an email" — there's no such tool, and any `dangerous` call is refused
     (that's Lab 5).

## Starter Code

A tool is a function plus metadata. The registry keeps all three parts in one place
(`tools.py`):

```python
TOOLS = {
    "get_order_status": {
        "fn": get_order_status,
        "safety": "safe",
        "description": "Look up the current status of a customer order by its ID. "
                       "Use when the user references an order number. Read-only.",
        "schema": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string", "pattern": "^[0-9]{4,6}$"},
            },
            "required": ["order_id"],
            "additionalProperties": False,
        },
    },
    # ... lookup_help_center, calc ...
}
```

Validate **before** you execute — reject bad args, don't coerce them (`tool_agent.py`):

```python
def dispatch(name, args):
    if name not in toolmod.TOOLS:
        return {"ok": False, "error": "unknown_tool", "tool": name}
    ok, err = validate_args(name, args)          # JSON Schema check
    if not ok:
        return {"ok": False, "error": "bad_args", "detail": err}
    if toolmod.TOOLS[name]["safety"] == "dangerous":
        return {"ok": False, "error": "human_approval_required", "tool": name}
    return toolmod.TOOLS[name]["fn"](**args)
```

Tool results go back as **data, not instructions** — note the wrapper key:

```python
messages.append({"role": "tool", "tool_call_id": tc.id,
                 "content": json.dumps({"tool_result_data": result})})
```

**Anthropic variant.** The schema is identical; only the envelope differs. `tools.py` also
ships `anthropic_tool_specs()` (uses `input_schema` instead of `function.parameters`), and the
loop reads tool calls from `response.content` blocks of `type == "tool_use"` with model
`claude-sonnet-5`. The validation, safety-class, and dispatch logic are unchanged.

## What a correct run looks like

Wording varies; the round-trip shape does not.

```text
─────────────────────────────── Goal: What is the refund policy for annual plans, and
what is the status of order 88123? Also, what would a refund of 3 duplicate charges of
$80 each total? ───────────────────────────────
--- step 1 ---
call lookup_help_center({"query": "refund annual plan"})
result {"ok": true, "query": "refund annual plan", "matches": 2, "snippet": "Annual plans:
full refund within **14 days** of purchase; pro-rated after that.\nDuplicate charges are
refunded within **5 business days** once confirmed."}
call get_order_status({"order_id": "88123"})
result {"ok": true, "order_id": "88123", "status": "shipped_twice", "items": 2,
"total_usd": 240.0, "note": "Duplicate shipment detected; eligible for refund of one charge."}
call calc({"expression": "3 * 80"})
result {"ok": true, "expression": "3 * 80", "result": 240}
--- step 2 ---
──────────────────────────────── Done ────────────────────────────────

Final Answer: Annual plans get a full refund within 14 days of purchase (pro-rated after),
and duplicate charges are refunded within 5 business days once confirmed. Order 88123 shipped
twice and is eligible for a refund of one charge. Three duplicate charges of $80 total $240.
```

Bad-args recovery looks like this:

```text
call get_order_status({"order_id": "9"})
result {"ok": false, "error": "bad_args", "detail": "'9' does not match '^[0-9]{4,6}$'"}
--- step 2 ---
call get_order_status({"order_id": "88123"})   # model corrected itself
```

## Deliverable

A runnable `tool_agent.py` + `tools.py` that:

1. exposes the three functions as tools with descriptions, JSON Schemas, and safety classes,
2. validates every model-proposed call against its schema before executing,
3. refuses any `dangerous` call (human approval required),
4. completes a multi-tool question and prints the full round-trip trace ending in a final
   answer, and
5. enforces a `MAX_STEPS` cap.

## Troubleshooting

- **`OPENAI_API_KEY not set`.** Copy `labs/.env.example` to `labs/.env` and add your key.
- **`ModuleNotFoundError: tools`.** Run from inside the lab folder so `import tools` resolves.
- **`help_center_missing`.** Run from the lab folder; the path is `../assets/help_center.md`
  relative to `tools.py` (it uses an absolute resolved path, so cwd shouldn't matter — but a
  moved file will).
- **Model answers without calling a tool.** Strengthen the system prompt ("prefer a tool over
  guessing") and keep `tool_choice="auto"`. For math especially, tell it to use `calc`.
- **`bad_args` every time.** Your schema is stricter than the model expects — check the
  `pattern`/`enum`. That's the schema doing its job; make sure the constraint is intentional.
- **Loop hits max steps.** Usually a tool keeps erroring and the model keeps retrying. Read the
  `result` lines; fix the tool or loosen an over-strict schema.

## Teacher's Playbook

**Worked answer / what good looks like.** A complete submission calls `lookup_help_center` and
`get_order_status` and `calc` on the default question, returns them as `tool_result_data`, and
produces a grounded final answer citing the tool outputs. The student can point to (a) where
validation happens, (b) where the safety class is checked, and (c) why the result is wrapped as
data. Bonus points for demonstrating the `bad_args` self-correction and explaining the
Anthropic variant is the *same schema, different envelope*.

**Live-demo script (6–8 min).**
1. Open `tools.py`. "These are ordinary functions. The only thing that makes them *tools* is
   the description, the schema, and the safety class." Point at each.
2. Run `python tool_agent.py`. Narrate the trace: "The model chose three tools, in an order we
   never hard-coded. That's the agent deciding at runtime."
3. Run the order-`9` example. "The model sent junk; our schema caught it *before* any code ran;
   the model read the error and fixed itself. Validation is a safety layer, not a formality."
4. Show `dispatch`: the `dangerous -> human_approval_required` branch. "No dangerous tool here.
   In Lab 5 that branch becomes a real human gate for sending email."
5. Show the `{"tool_result_data": ...}` wrapper. "We label tool output as data. A malicious
   help-center line that says 'ignore your rules' is just... data."

**Common mistakes + fixes.**
- *Forgetting `additionalProperties: false`* -> the model sneaks in extra args. Fix: lock the
  schema.
- *Coercing bad args instead of rejecting* -> hides bugs and injection. Fix: validate and
  return a structured `bad_args` error the model can recover from.
- *Not appending the assistant tool-call turn before the tool result* -> API error about
  mismatched `tool_call_id`. Fix: append `msg` first, then each tool message.
- *Returning a giant string* -> context bloat. Fix: return bounded, structured dicts;
  `lookup_help_center` caps output with `max_chars`.
- *No `MAX_STEPS`* -> a stuck loop bills forever. Fix: keep the cap; tie back to Day 1.

**Debrief Q&A.**
- *Q: Why JSON Schema instead of just trusting the model?* A: The model is probabilistic; the
  schema is the deterministic contract your code enforces. It's also your first injection
  defense.
- *Q: Safe vs. guarded vs. dangerous — who decides?* A: You do, at design time, per
  `tool-spec-template.md`. When unsure, class up, not down.
- *Q: Can the model call two tools at once?* A: Yes — modern APIs return parallel tool calls;
  the loop handles a list. We still validate and gate each one.
- *Q: What changes for Anthropic?* A: `input_schema` vs. `function.parameters`, and you read
  `tool_use` blocks. Validation, safety, and dispatch are identical — the pattern is portable.

---
