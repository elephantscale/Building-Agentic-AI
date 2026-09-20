# Lab 1 — Environment Setup & Your First Agent Loop (ReAct)

## Goal

Get your lab environment working, then **hand-build a minimal ReAct agent** against the OpenAI
API — no framework. You will register two tools, run the Thought / Action / Observation loop
yourself, enforce a max-steps cap, and print the full trace. By the end you will understand,
concretely, what every agent framework in this course is doing under the hood.

## Time

45 minutes

## Tools

- Python 3.11+
- OpenAI API (`gpt-4.1`)
- `openai`, `python-dotenv`, `rich`

## Files in this lab

```
01-Agent-Loop-Setup/
  README.md          <- you are here
  requirements.txt   <- openai, python-dotenv, rich
  agent_loop.py      <- a complete, runnable ReAct loop with two tools
```

## Steps

1. **Create the environment** (once for the whole course). From the repo root:

   ```sh
   python3 -m venv .venv
   source .venv/bin/activate            # Windows: .venv\Scripts\activate
   python -m pip install --upgrade pip
   ```

2. **Add your keys.** Copy the template and paste in the key handed out in class
   (see `labs/SETUP.md`). This lab only needs `OPENAI_API_KEY`.

   ```sh
   cp labs/.env.example labs/.env
   # edit labs/.env, set OPENAI_API_KEY=sk-...
   ```

3. **Verify the machine:**

   ```sh
   ./labs/verify-setup.sh
   ```

   You want `PASS python3 3.11+`, `PASS pip present`, and `OPENAI_API_KEY looks set`.

4. **Install this lab's requirements:**

   ```sh
   cd labs/01-Agent-Loop-Setup
   pip install -r requirements.txt
   ```

5. **Read `agent_loop.py` top to bottom.** Find the three jobs your code does every turn:
   **parse** the model's `Action`, **dispatch** it to a tool, **paste back** the `Observation`.
   Find the `MAX_STEPS` cap and the `stop=["Observation:"]` guard.

6. **Run the default question** (a two-step problem: look up the price, then multiply):

   ```sh
   python agent_loop.py
   ```

7. **Run your own question** and watch the loop adapt:

   ```sh
   python agent_loop.py "What is the refund window, and what is 30 * 24 hours?"
   ```

8. **Break it on purpose** to feel the guardrails: lower `MAX_STEPS` to `1`, re-run, and see the
   loop stop cleanly instead of running forever.

## Starter Code

The heart of the lab is the loop. Read this alongside `agent_loop.py` — it is the same code:

```python
for step in range(1, MAX_STEPS + 1):
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0,
        stop=["Observation:"],          # the model never writes its own Observation
    )
    turn = response.choices[0].message.content.strip()

    # 1) Did the model finish?
    final = FINAL_RE.search(turn)
    if final:
        return final.group(1).strip()

    # 2) Otherwise parse and dispatch the Action.
    parsed = parse_action(turn)
    if parsed is None:
        observation = "ERROR: no Action or Final Answer found."
    else:
        name, arg = parsed
        observation = (TOOLS[name](arg) if name in TOOLS
                       else f"ERROR: unknown tool {name!r}.")

    # 3) Paste the turn AND the observation back into the conversation.
    messages.append({"role": "assistant", "content": turn})
    messages.append({"role": "user", "content": f"Observation: {observation}"})
```

Two things make this reliable, and both are easy to miss:

- **`stop=["Observation:"]`** — without it the model happily *hallucinates* the tool result and
  never actually calls your tool. This one line forces it to stop and wait for the real runtime.
- **`MAX_STEPS`** — the `for` range is the cap. A loop with no cap is a runaway bill and an
  incident. Every agent you build this week keeps a cap.

The tools themselves are ordinary Python functions in a registry:

```python
TOOLS = {
    "calculator": calculator,   # safe arithmetic only
    "lookup": lookup,           # a small local fact table (becomes web search in Lab 2)
}
```

## What a correct run looks like

```
$ python agent_loop.py
──────── Goal: We are buying 17 seats on the Team plan. What is the total monthly cost? ────────
--- step 1 ---
Thought: I need the per-seat price of the Team plan before I can compute a total.
Action: lookup(seat price team plan)
Observation: The Team plan costs $42 per seat per month.
--- step 2 ---
Thought: The Team plan is $42 per seat. For 17 seats I multiply 17 by 42.
Action: calculator(17 * 42)
Observation: 714
--- step 3 ---
Thought: 17 seats at $42 each is $714 per month. I can answer now.
Final Answer: The total monthly cost for 17 seats on the Team plan is $714 (17 × $42).
──────────────────────────── Done ────────────────────────────

Final Answer: The total monthly cost for 17 seats on the Team plan is $714 (17 × $42).
```

Note the shape: **one tool call per step**, the runtime supplies each `Observation`, and the
agent **stops** as soon as it can answer. That is ReAct.

## Deliverable

A runnable `agent_loop.py` that solves a **multi-step** question and prints a ReAct trace ending
in a `Final Answer`. Paste your terminal trace for one run into the class channel.

## Troubleshooting

- **`OPENAI_API_KEY not set`** — you skipped step 2, or `.env` is in the wrong place. It must be
  `labs/.env` (not the lab folder). Re-run `./labs/verify-setup.sh`.
- **The model writes its own fake `Observation:` line** — you removed the `stop=["Observation:"]`
  argument. Put it back; it is what forces a real tool call.
- **Loop never finishes / hits max steps** — usually the model isn't following the format. Keep
  `temperature=0`, and check the system prompt still shows the exact `Thought/Action` template.
- **`unknown tool` in an Observation** — the model invented a tool name. That's fine: the error
  goes back as an Observation and the model recovers. Don't crash the loop on tool errors.
- **`calculator` returns an ERROR** — it only allows arithmetic (that's least privilege by
  design). `lookup` handles words; `calculator` handles numbers.

## Teacher's Playbook

### Worked model answer

The default question is deliberately **two-step**: the price isn't in the prompt, so the agent
*must* `lookup` first, then `calculator`. A one-tool agent can't answer it — that's the point.
The expected trace is the one under "What a correct run looks like": lookup → 42, calculator →
714, Final Answer $714. Total three model turns.

### Live-demo script (about 10 minutes)

1. Run `python agent_loop.py` and narrate the three jobs as each step scrolls: *"the model
   proposed an Action, our code ran the tool, we pasted the Observation back."*
2. Comment out `stop=["Observation:"]`, re-run. The model now fabricates `Observation: 714`
   without ever calling the tool. Ask: *"did it actually compute anything?"* Restore the line.
3. Set `MAX_STEPS = 1`, re-run. It stops at the cap with no Final Answer. *"This is the line
   between a demo and an incident."* Restore it.
4. Run `python agent_loop.py "What is 12345 * 6789?"` — one-step, one `calculator` call. Contrast
   single- vs multi-step reasoning (sets up Lab 2).

### Common mistakes + fixes

- **Students edit `agent_loop.py` before reading it.** Make step 5 mandatory; the loop is short.
- **Someone hard-codes the price into the prompt** to "help" the agent — now it's single-step and
  the lesson is lost. Keep the price only in the `lookup` table.
- **Confusing who writes the Observation.** Reinforce: the *model* writes Thought + Action; the
  *runtime* writes Observation. That boundary is the whole safety story.
- **Treating a tool result as a command.** Point out the "untrusted data" line in the system
  prompt — it's the seed of prompt-injection defense we build on all week.

### Debrief Q&A

- *Why `temperature=0`?* Deterministic, format-following behavior; agents want reliability, not
  creativity, in the control loop.
- *What if two tools are needed at once?* ReAct does one per turn by design — simpler to parse,
  log, and audit. Parallel tool calls come later.
- *Where would web search go?* Replace `lookup` with a real search tool — exactly Lab 2.
- *How do we know it's safe?* Sandboxed `calculator`, least-privilege tool set, a step cap, and
  every result treated as data. Those four scale to every later lab.

### What good looks like

A student can point at any line of the loop and say what it does; can explain why `stop=` and
`MAX_STEPS` matter; and has a printed multi-step trace that ends in a correct Final Answer with
the tools actually invoked (not hallucinated).

---
