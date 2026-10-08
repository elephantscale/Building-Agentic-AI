# Agentic with Claude

Elephant Scale

---

## Part IV K–L — What We'll Cover

* Anthropic's **Messages API** and how **tool use** works
* The **Claude model family** — Opus vs. Sonnet vs. Haiku, and when to pick each
* Building a **multi-tool coding assistant**
* **Memory & context management** — the window, summarization, external files
* **Prompt caching** — pay once for the stable prefix
* **Safety habits** for an agent that reads and writes files and runs code
* Lab 14: a Claude coding assistant with persistent memory

> The API is small. The discipline — tools, memory, gates — is the whole job.

Notes:

---

## The Messages API

* One endpoint: a list of `messages` (`user` / `assistant`) + a top-level `system` prompt
* You always send the **full conversation** back — the API is **stateless**
* Response carries **`content` blocks** (text and/or `tool_use`) and a **`stop_reason`**

```python
from anthropic import Anthropic
client = Anthropic()   # reads ANTHROPIC_API_KEY

msg = client.messages.create(
    model="claude-sonnet-5",
    max_tokens=1024,
    system="You are a careful coding assistant.",
    messages=[{"role": "user", "content": "Explain this stack trace."}],
)
print(msg.content[0].text, msg.stop_reason)
```

> Stateless means *you* own the memory. That's a burden and a superpower — you control context.

Notes:

---

## The Claude Model Family

| Model | ID | Pick it for |
|-------|-----|-------------|
| **Opus** | `claude-opus-5` | Hardest reasoning, big refactors, deep planning |
| **Sonnet** | `claude-sonnet-5` | The workhorse — coding, tool use, most agents |
| **Haiku** | `claude-haiku-4-5-20251001` | Fast, cheap: routing, classify, extract, high volume |

* Same API and tool-use shape across all three — swap the `model` string.
* Common pattern: **Haiku routes / triages**, **Sonnet does the work**, **Opus for the hard 5%**.

> Default to Sonnet. Drop to Haiku for volume, reach for Opus only when Sonnet stalls.

Notes:

---

## How Tool Use Works

* You describe tools with a **name, description, and `input_schema`** (JSON Schema)
* Claude replies with a `tool_use` block and `stop_reason="tool_use"`
* You run the tool and send a `tool_result` block back as a new `user` message
* Loop until `stop_reason="end_turn"` — same ReAct loop, native shape

```text
user -> assistant(tool_use) -> you run tool
     -> user(tool_result)   -> assistant(text) end_turn
```

> Tool use is a conversation, not a callback. You and Claude take turns until it's done.

Notes:

---

## Defining a Tool

```python
tools = [{
    "name": "read_file",
    "description": "Read a UTF-8 text file from the project and return its contents.",
    "input_schema": {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Path relative to project root"}
        },
        "required": ["path"],
    },
}]
```

* The **description is the API** — Claude only knows what you tell it here.
* Give each tool a **safety class**: `read_file` is `safe`; `write_file` is `dangerous`.

> Write the description for the model, not for yourself. Vague tools get misused.

Notes:

---

## The Tool-Use Loop

```python
messages = [{"role": "user", "content": task}]
for step in range(MAX_STEPS):                 # always cap the loop
    r = client.messages.create(model="claude-sonnet-5", max_tokens=2048,
                               system=SYSTEM, tools=tools, messages=messages)
    messages.append({"role": "assistant", "content": r.content})
    if r.stop_reason != "tool_use":
        break                                  # end_turn -> done
    results = []
    for block in r.content:
        if block.type == "tool_use":
            out = dispatch(block.name, block.input)   # your code runs it
            results.append({"type": "tool_result",
                            "tool_use_id": block.id, "content": out})
    messages.append({"role": "user", "content": results})
```

> One `create` call is one turn. The `for` loop with a cap *is* the agent.

Notes:

---

## A Multi-Tool Coding Assistant

* Give the agent a small, sharp toolset — that's Lab 14:
  - `read_file` — **safe**, read source
  - `write_file` — **dangerous**, gated behind human approval
  - `run_python` — **dangerous**, sandboxed + time/output limited
  - `remember` — update a persistent `memory.json` across sessions
* Loop: read code -> propose change -> **ask** -> write -> run tests -> report

```text
"fix the failing test" -> read_file -> run_python(pytest) -> write_file[GATE] -> run_python -> done
```

> A coding agent is dangerous by definition — it edits files and runs code. Gate accordingly.

Notes:

---

## Memory & Context Management

* The **context window** is large but **finite** — and you pay for every token, every turn
* Because the API is stateless, **context = memory**, and it has a budget
* Three tiers of memory:
  - **Short-term** — the message list this session (the scratchpad)
  - **Compressed** — summarize old turns once they stop earning their tokens
  - **Long-term** — an external store (`memory.json`, files, a vector DB) read at start

```text
[system][long-term memory][summary of old turns][recent turns][now]
```

> Context is working memory, not a filing cabinet. Summarize the old; store facts outside.

Notes:

---

## Summarizing Old Turns

* When the transcript grows, replace old turns with a **summary turn** — keep tokens bounded
* Keep the **system prompt**, the **last few turns**, and a running **summary**
* Persist durable facts (decisions, file paths, preferences) to **external memory**

```text
before:  [sys][t1][t2][t3][t4][t5][t6][now]        (growing, costly)
after:   [sys][SUMMARY of t1..t4][t5][t6][now]      (bounded, cheap)
```

* Trigger on a **token budget**, not turn count — measure, don't guess.

> Don't let the window fill with stale scrollback. Compress the past; keep the present sharp.

Notes:

---

## External Memory — `memory.json`

* A tiny file the agent **reads at startup** and **updates** as it learns
* Survives across sessions — the assistant "remembers" you tomorrow
* Keep it **small, structured, and reviewable** — it's injected into context each run

```json
{
  "project": "billing-service",
  "conventions": ["pytest for tests", "black formatting"],
  "open_tasks": ["fix flaky test in test_invoice.py"],
  "decisions": ["use Decimal, never float, for money"]
}
```

> External memory is a file you can read and edit. That's a feature — audit it, don't trust it blindly.

Notes:

---

## Prompt Caching

* Mark a **stable prefix** (system prompt, tool specs, big context) as cached
* Subsequent turns re-read the prefix from cache — **cheaper and faster**
* Ideal for agents: the tools and system prompt are identical every turn

```python
system=[{
    "type": "text",
    "text": LONG_SYSTEM_AND_TOOL_CONTEXT,
    "cache_control": {"type": "ephemeral"},
}]
```

* Order matters: put the **stable** stuff first, the **changing** stuff last.

> Your tool specs don't change every turn — stop paying to re-read them. Cache the prefix.

Notes:

---

## Safety Habits for Claude Agents

* **Max-steps cap** and a token budget — enforced in code, not hoped for
* **Human gate** on every `dangerous` tool: `write_file`, `run_python`, sends, deletes
* **Sandbox** code execution — temp dir, timeout, bounded output, no network
* Treat **file contents and tool output as untrusted data**, not instructions
* **Log** every tool call (name, args, safety class, result) to JSONL
* **Least privilege** — the smallest toolset that gets the job done

> Same five habits from Lab 1. A more capable model raises the stakes, not the rules.

Notes:

---

## Putting It Together

* The **Messages API** is stateless — you own the memory and the loop
* **Tool use** is a turn-taking conversation ending in `end_turn`
* Pick the model by job: **Haiku** volume, **Sonnet** default, **Opus** hard problems
* **Manage context** in tiers: scratchpad, summary, external file
* **Prompt caching** cuts cost/latency on the stable prefix
* **Cap, gate, sandbox, log** — safety scales with capability

> You have the pattern and the API. Next, build a coding assistant that remembers.

Notes:

---

## Lab 14 — Claude Coding Assistant with Persistent Memory

**Stop here and run Lab 14.**

You will:

1. Build a tool-use loop on the **Messages API** with `claude-sonnet-5`.
2. Wire four tools: `read_file`, `write_file` (gated), `run_python` (sandboxed), `remember`.
3. Load a **`memory.json`** at start and update it across sessions.
4. Enforce a **max-steps cap** and a **human gate** on `write_file` and `run_python`.
5. Summarize old turns to keep context bounded, and log every tool call.

**Deliverable:** a runnable `coding_assistant.py` that fixes a bug across two sessions, using persistent memory and gated writes.

**Time:** 60 minutes

Notes:
