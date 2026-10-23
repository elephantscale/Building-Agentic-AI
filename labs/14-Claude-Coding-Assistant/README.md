# Lab 14 — Claude Coding Assistant with Persistent Memory

## Goal

Build a **multi-tool coding assistant** on Anthropic's **Messages API** that can read code,
edit it, and run it — with a **persistent memory** file it carries across sessions. You will see
the native **tool-use loop** end to end, and practice the two disciplines every coding agent
needs: **safety gates** (writing files and running code are `dangerous`) and **context/memory
management** (summarize old turns; keep durable facts in `memory.json`).

The assistant fixes a real bug in the sample `workspace/` project: the tests fail, it reads the
code, runs the tests, proposes a fix, **asks before writing**, applies it, and re-runs to prove
it. Then it **remembers** the decision so the next session starts smarter.

## Time

60 minutes

## Tools

- Python 3.11+, `pip`
- `labs/.env` with `ANTHROPIC_API_KEY`
- `anthropic`, `python-dotenv`
- Concept deck: `slides/11-claude-agents.md`; safety: `course-materials/agent-safety-checklist.md`

## Files in this lab

```text
14-Claude-Coding-Assistant/
├── README.md               # this file
├── requirements.txt        # anthropic, python-dotenv
├── coding_assistant.py     # tool-use loop, gates, memory, summarization
├── memory.json             # created/updated at runtime (persists across sessions)
└── workspace/              # the sandbox the tools operate in
    ├── mathutils.py        # contains one deliberate bug (average divides by len-1)
    └── test_mathutils.py   # runnable test script — fails until the bug is fixed
```

## Steps

1. Install and configure:

   ```sh
   cd labs/14-Claude-Coding-Assistant
   pip install -r requirements.txt
   cp ../.env.example ../.env         # fill in ANTHROPIC_API_KEY
   ```

2. **🔮 Predict, then run Session 1.** First open `workspace/mathutils.py` and
   `workspace/test_mathutils.py` yourself and **predict the bug and the one-line fix** before the
   agent runs. Then give it the one-shot task and approve the write and the runs at the gate — did it
   find what you found?

   Keep it on **one line** — a trailing `\` is a bash continuation and does nothing
   in PowerShell, which would hand the agent an empty task:

   ```powershell
   python coding_assistant.py "The tests in test_mathutils.py fail. Read the code, run the tests, fix the bug, and re-run to prove it. Remember the fix."
   ```

3. Watch the loop: `read_file` -> `run_python` (fails) -> proposes fix -> **[GATE]** on
   `write_file` -> `run_python` (passes). Inspect `memory.json` — the decision was saved.

4. **Session 2** — start a fresh run and confirm the assistant recalls the prior session from
   `memory.json`:

   ```sh
   python coding_assistant.py "What did we work on last time, and what's still open?"
   ```

5. Try **interactive mode** (no argument) to give several tasks in one session and watch the
   `[context] summarized older turns` message fire once the transcript grows.

6. Prove the gate: give a fix task and answer `n`. Confirm `mathutils.py` is **unchanged**.

7. **🛠️ Your turn — design a failing case and watch the loop catch it.**
   - **(a)** Plant a *second* bug the tests already cover: change `is_even` to `return n % 2 == 1`.
     Re-run the Session-1 task. Confirm the agent **reproduces** (test fails), **fixes**, and
     **re-runs green** — you designed the case, the read→run→fix→re-run loop caught it.
   - **(b) Stretch:** the tests never check `average([])`. Add `assert average([]) == 0` (or decide it
     should raise) to `test_mathutils.py` and re-run. Notice the agent only fixes **what the tests
     exercise** — a bug with no test slips straight through. This is the Lab 7 lesson in miniature:
     *your eval set is your safety net; grow it when you find a gap.*

   Reset afterward: `git checkout workspace/` and delete `memory.json`.

8. **🗣️ Explain.** In one or two sentences: why does a good agent **run the tests to see the failure
   before editing**, instead of fixing straight from reading the code? What does the failing test give
   you that the model's inspection alone does not?

## Starter Code

Four tools, each with a **safety class** — reads are `safe`, writing and running are
`dangerous`:

```python
TOOLS = {
    "read_file":  {"safety": "safe",      ...},
    "write_file": {"safety": "dangerous", ...},   # human-gated
    "run_python": {"safety": "dangerous", ...},   # sandboxed + human-gated
    "remember":   {"safety": "safe",      ...},   # updates memory.json
}
```

The **tool-use loop** is the whole agent — one `create` call per turn, capped, ending at
`end_turn`:

```python
for step in range(1, MAX_STEPS + 1):
    r = client.messages.create(model="claude-sonnet-5", max_tokens=2048,
                               system=system_prompt(), tools=tools, messages=messages)
    messages.append({"role": "assistant", "content": r.content})
    if r.stop_reason != "tool_use":
        return messages                      # done
    results = []
    for block in r.content:
        if block.type == "tool_use":
            results.append({"type": "tool_result", "tool_use_id": block.id,
                            "content": json.dumps(dispatch(block.name, block.input))})
    messages.append({"role": "user", "content": results})
```

**Safety lives in `dispatch`, not the prompt** — the model can only *request* a dangerous tool:

```python
def dispatch(name, args):
    spec = TOOLS[name]
    if spec["safety"] == "dangerous" and not human_gate(name, args):
        return {"ok": False, "error": "denied_by_human"}
    return spec["fn"](**args)
```

**`run_python` is sandboxed** — fixed cwd, wall-clock timeout, bounded output; paths for file
tools must resolve **inside `workspace/`** (`_safe_path` rejects `../` escapes).

**Memory & context** — `memory.json` is injected into the system prompt each run and updated via
`remember`; `maybe_summarize` collapses old turns (between completed tasks) to bound the window.

## What a correct run looks like

```text
$ python coding_assistant.py "The tests fail. Fix the bug and prove it. Remember the fix."
Coding assistant on claude-sonnet-5. Sandbox: .../workspace
Loaded memory: {"project": "sample", "conventions": [], "decisions": [], "open_tasks": []}

Claude: I'll read the test and the module, then run the tests to see the failure.
  -> read_file(path=…)  [safe]
  -> read_file(path=…)  [safe]
  -> run_python(code=…)  [dangerous]

  [GATE] dangerous tool: run_python({"code": "exec(open('test_mathutils.py')...})
  Approve? [y/N] y
  -> run_python(code=…)  [dangerous]

Claude: The test fails: average([2,4,6]) returns 6.0, not 4. `average` divides by
(len-1). I'll change it to divide by len(nums).
  [GATE] dangerous tool: write_file({"path": "mathutils.py", "text": "..."})
  Approve? [y/N] y
  -> write_file(path=…, text=…)  [dangerous]

  [GATE] dangerous tool: run_python({"code": "..."})
  Approve? [y/N] y
  -> run_python(code=…)  [dangerous]     # stdout: ALL TESTS PASSED
  -> remember(key=…, value=…)  [safe]

Claude: Fixed. `average` now divides by len(nums); tests pass (ALL TESTS PASSED).
I saved the decision to memory.

Memory saved -> memory.json
```

`memory.json` after the run:

```json
{
  "project": "sample",
  "conventions": [],
  "decisions": ["average() must divide by len(nums), not len(nums)-1"],
  "open_tasks": []
}
```

## Deliverable

- A transcript of **session 1** fixing the bug, showing the gates and `ALL TESTS PASSED`.
- The resulting `memory.json` with the saved decision.
- A transcript of **session 2** where the assistant recalls the prior work from memory.
- A transcript showing a **denied** gate leaving `mathutils.py` unchanged.

> Reset for the next student: `git checkout workspace/mathutils.py` (or restore the `len(nums) - 1`
> bug) and delete `memory.json`.

## Troubleshooting

- **`AuthenticationError`.** Put `ANTHROPIC_API_KEY` in `labs/.env`.
- **The gate never appears / everything is denied.** In a non-interactive shell the gate
  auto-denies (safe default). Run in a real terminal to approve.
- **`path escapes sandbox`.** A tool tried to touch a file outside `workspace/`. That's the guard
  working — keep paths relative to the workspace.
- **`run_python` timeout.** A snippet ran longer than `RUN_TIMEOUT_S` (10s). Intended limit; the
  agent should write terminating code.
- **Tests already pass on first run.** Someone fixed `mathutils.py`. Restore the bug
  (`sum(nums) / (len(nums) - 1)`) and delete `memory.json`.
- **Context never summarizes.** It only triggers after `SUMMARY_AFTER` messages, between tasks —
  use interactive mode and give several tasks.

## Teacher's Playbook

**Three-beat reference answers (Steps 2, 7, 8).**
- **🔮 Predict (§2):** the bug is `average` dividing by `len(nums) - 1`; the one-line fix is
  `return sum(nums) / len(nums)`. A good agent reads both files, **runs the test to see the failure
  first**, changes only that line, and re-runs to `ALL TESTS PASSED`.
- **🛠️ Your turn (§7):** *(a)* breaking `is_even` to `n % 2 == 1` makes the existing `is_even`
  assertion fail; the agent reproduces, flips it back to `== 0`, and re-runs green — a clean
  design-a-case → loop-catches-it. *(b)* adding `average([])` exposes a `ZeroDivisionError` the
  original tests never triggered: the agent will now have to handle the empty case (e.g.
  `return 0 if not nums else sum(nums) / len(nums)`). The point for the room: **the agent is only as
  safe as the tests you give it** — untested paths are invisible to the loop. Ties directly to Lab 7's
  frozen eval set.
- **🗣️ Explain (§8):** running the test first **reproduces the failure as ground truth** — it proves
  the bug exists, pins down exactly what "fixed" means, and lets the re-run *prove* the fix. Editing
  from inspection alone risks "fixing" the wrong thing or introducing a new break with nothing to
  catch it (the "editing before reproducing" mistake below).

**It sometimes skips the reproduce step — use it.** In three keyed runs of the Step-2 task
(2026-10-22, `claude-sonnet-5`), two went `read -> read -> run (fail) -> write -> run (pass)` as
above; **one went straight from reading to `write_file`** without ever running the failing test.
If that happens live, stop and point at it: the §8 question is on the board in front of them, and
the model just made the mistake the Playbook names below. Ask what the skipped run cost it — it
had no proof the bug was the one it read, and no proof the fix was what made the test pass.

**The one big idea.** A coding agent is the most dangerous kind — it edits files and runs code.
The value of this lab is watching capability and control grow together: four tools, but two of
them stop for a human, code runs in a sandbox with a timeout, and the loop is capped. Capability
without those is a demo you can't ship.

**Live-demo script (10 min).**
1. Run session 1; narrate each block: read -> run (fail) -> propose -> **gate** -> write -> run
   (pass) -> remember.
2. `cat memory.json` — "the agent wrote itself a note."
3. Run session 2 ("what did we do last time?") — it answers *from memory.json*, not the model's
   imagination.
4. Run a fix task and **deny** the write — show `mathutils.py` unchanged.
5. In interactive mode, give 3–4 small tasks until `[context] summarized older turns` fires.

**Worked model answer.** The bug is `average` dividing by `len(nums) - 1`. Correct fix is
`return sum(nums) / len(nums)`. A good agent reads both files, runs the test to *see* the failure
before editing, changes only that line, re-runs to confirm `ALL TESTS PASSED`, and records the
decision.

**Common mistakes + fixes.**
- *"Just trust the model to ask first."* Show that the gate is in `dispatch`, not the prompt — a
  prompt is a suggestion, a code gate is a guarantee. Ask a student to try prompt-injecting the
  agent to skip the gate; it can't, because the gate isn't in the model's reach.
- *Editing before reproducing.* Coach the read -> run -> fix -> re-run habit; blind edits are how
  agents make things worse.
- *Unbounded output / no timeout.* Discuss `MAX_OUTPUT_CHARS` and `RUN_TIMEOUT_S`: never dump raw
  output into context, never let code run forever.
- *Memory as a dumping ground.* `memory.json` is injected every run and costs tokens — keep it
  small, structured, reviewable. It's a feature you can audit, not a black box to trust.

**Debrief Q&A.**
- *Why gate `run_python` and `write_file` but not `read_file`?* Side effects and blast radius —
  reads can't corrupt the workspace.
- *Is this a real sandbox?* It's a *limited* one (cwd, timeout, bounded output, no `../` escape).
  Production would add a container, no network, and resource caps — name the gap honestly.
- *Memory vs. context window?* Context is per-session working memory (summarized to stay
  bounded); `memory.json` is durable, external, cross-session state.
- *When would you reach for Opus here instead of Sonnet?* A large multi-file refactor or a
  gnarly bug where Sonnet stalls — otherwise Sonnet is the right default.

**What good looks like.** A student who can (a) run both sessions with memory carrying over, (b)
point to the exact line where the gate lives, (c) explain the sandbox limits on `run_python`, and
(d) articulate the difference between the context window and persistent memory.

---
