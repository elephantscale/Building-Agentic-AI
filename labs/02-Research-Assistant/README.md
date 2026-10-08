# Lab 2 — Research Assistant with Multi-Step Reasoning & Logging

## Goal

Build a research assistant that **plans**, calls a **search** tool several times, and writes a
structured **JSONL audit log** of everything it did. You extend Lab 1's ReAct loop with an
upfront planning step and real observability. It runs with **no API keys but OpenAI**: search
uses Tavily if `TAVILY_API_KEY` is set, and otherwise falls back to a local search over a small
bundled corpus. Before you write code, you fill out the **Agent Design Canvas**.

## Time

60 minutes

## Tools

- Python 3.11+
- OpenAI API (`gpt-4.1`)
- Optional: Tavily search (`TAVILY_API_KEY`) — a local fallback runs without it
- `openai`, `tavily-python`, `python-dotenv`, `rich`
- `../../course-materials/agent-design-canvas.md` and `../../course-materials/audit-log-schema.md`

## Files in this lab

```
02-Research-Assistant/
  README.md            <- you are here
  requirements.txt     <- openai, tavily-python, python-dotenv, rich
  research_agent.py    <- planning step + multi-step search loop + JSONL logging
  corpus/              <- 4 short .txt notes for the offline fallback search
    agentic-ai.txt
    react-pattern.txt
    evaluation.txt
    tools-and-memory.txt
  run-log.jsonl        <- created when you run the agent (append-only)
```

## Steps

1. **Fill the Agent Design Canvas first.** Open `../../course-materials/agent-design-canvas.md`
   and, on paper or in a scratch file, answer sections 1–7 for *this* agent. Minimum viable
   answers to have before you run anything:
   - **Goal:** answer a research question with grounded, cited findings.
   - **Tools:** one `search` tool (read-only, safety class *safe*).
   - **Pattern / cap:** ReAct with a planning step; **max 5 search steps**.
   - **Memory:** scratchpad only (the Thought/Observation history) — no persistence.
   - **Untrusted inputs:** the search results — treat as data, never instructions.
   - **Observability:** JSONL log per `../../course-materials/audit-log-schema.md`.

2. **Install requirements** (from within this lab folder):

   ```sh
   cd labs/02-Research-Assistant
   pip install -r requirements.txt
   ```

3. **Run it offline first** (no Tavily key needed — uses `corpus/`):

   ```sh
   python research_agent.py
   ```

4. **Inspect the audit log** that was just written:

   ```sh
   cat run-log.jsonl | python -m json.tool --json-lines   # or: less run-log.jsonl
   ```

   Confirm you see the event sequence `run_start -> plan -> tool_call -> tool_result -> ... ->
   run_end`, one JSON object per line.

5. **Ask your own question** and watch the plan and the loop change:

   ```sh
   python research_agent.py "How do agents defend against prompt injection from tool output?"
   ```

6. **(Optional) Go live with Tavily.** Add `TAVILY_API_KEY=tvly-...` to `labs/.env` and re-run.
   The same code now searches the web; the log records `"engine": "tavily"` instead of `local`.

7. **Feel the cap.** Lower `MAX_STEPS` to `1` and ask a broad question. The loop stops cleanly at
   the cap and the `run_end` event records `success: false`.

## Starter Code

**The audit log** is the backbone of the lab. Each event is one JSON line (schema in
`../../course-materials/audit-log-schema.md`):

```python
class AuditLog:
    def emit(self, step, event, detail=None, result=None):
        record = {
            "run_id": self.run_id, "ts": now_iso(), "agent": self.agent,
            "actor": self.actor, "step": step, "event": event,
            "detail": detail or {}, "result": result or {},
        }
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record) + "\n")   # append-only, one line per event
```

**The planning step** runs once, before the loop, and is logged as a `plan` event:

```python
plan = make_plan(client, question)          # 2-4 numbered search steps
log.emit(0, "plan", detail={"plan": plan})
```

**The multi-step search loop** is Lab 1's ReAct loop with logging and a cap:

```python
for step in range(1, MAX_STEPS + 1):
    resp = client.chat.completions.create(
        model=MODEL, messages=messages, temperature=0, stop=["Observation:"])
    turn = resp.choices[0].message.content.strip()

    if "Final Answer:" in turn:
        final_answer = FINAL_RE.search(turn).group(1).strip()
        break

    query = parse_query(turn)
    engine, results = search(query)                       # Tavily or local fallback
    log.emit(step, "tool_call",
             detail={"tool": "search", "args": {"query": query, "engine": engine},
                     "safety_class": "safe"})
    log.emit(step, "tool_result",
             result={"ok": True, "summary": f"{len(results)} results via {engine}",
                     "results": results})
    messages.append({"role": "assistant", "content": turn})
    messages.append({"role": "user", "content": f"Observation: {json.dumps(results)}"})
```

**The search tool** dispatches to Tavily or the local corpus, so the lab is never blocked:

```python
def search(query, k=3):
    if os.getenv("TAVILY_API_KEY"):
        try:
            return "tavily", tavily_search(query, k)
        except Exception:            # network/quota problems fall back, don't crash
            pass
    return "local", local_search(query, k)   # keyword search over ./corpus
```

## What a correct run looks like

```
$ python research_agent.py
── Research goal: What is the ReAct pattern, and why does an agent loop need a max-steps cap? ──
Plan:
1. Search for what the ReAct pattern is (Thought/Action/Observation).
2. Search for why an agent loop needs a maximum-steps cap.
3. Synthesize both into a grounded answer with sources.

--- step 1 ---
Thought: First I need a definition of the ReAct pattern.
Action: search(ReAct pattern Thought Action Observation)
Observation: [{"source": "corpus/react-pattern.txt", "snippet": "ReAct stands for Reasoning..."}]
--- step 2 ---
Thought: Now I need why a loop needs a max-steps cap.
Action: search(agent loop max steps cap runaway cost)
Observation: [{"source": "corpus/react-pattern.txt", "snippet": "...a maximum-steps cap so a loop..."}]
--- step 3 ---
Thought: I have both parts and can answer now.
Final Answer: ReAct (Reasoning + Acting) interleaves the model's reasoning (Thought) with
tool calls (Action) and the runtime's results (Observation) in one visible, auditable trace.
An agent loop needs a max-steps cap because a loop that never converges would otherwise run
indefinitely, running up cost and risking an incident; the cap guarantees termination.
Sources: corpus/react-pattern.txt
──────────────────────────── Done ────────────────────────────

Answer: ReAct (Reasoning + Acting) interleaves ...
Sources: corpus/evaluation.txt, corpus/react-pattern.txt
Audit log appended to run-log.jsonl
```

The matching `run-log.jsonl` (one object per line, abbreviated):

```json
{"run_id":"...","ts":"2026-09-19T14:03:20Z","agent":"research-assistant","step":0,"event":"run_start","detail":{"goal":"What is the ReAct pattern...","inputs_hash":"a1b2c3d4e5f6","max_steps":5},"result":{}}
{"run_id":"...","step":0,"event":"plan","detail":{"plan":"1. Search for what the ReAct pattern is..."},"result":{}}
{"run_id":"...","step":1,"event":"tool_call","detail":{"tool":"search","args":{"query":"ReAct pattern Thought Action Observation","engine":"local"},"safety_class":"safe"},"result":{}}
{"run_id":"...","step":1,"event":"tool_result","detail":{},"result":{"ok":true,"summary":"3 results via local","results":[{"source":"corpus/react-pattern.txt","snippet":"ReAct stands for..."}]}}
{"run_id":"...","step":5,"event":"run_end","detail":{"success":true},"result":{"final_answer":"ReAct (Reasoning + Acting)...","sources":["corpus/evaluation.txt","corpus/react-pattern.txt"]}}
```

## Deliverable

A runnable `research_agent.py` **plus** the `run-log.jsonl` produced by one complete run. The run
must show at least **two** `tool_call` events (multi-step) and a `run_end` with `success: true`
and a non-empty `sources` list. Submit the final answer and the log.

## Troubleshooting

- **`OPENAI_API_KEY not set`** — this lab still needs OpenAI for reasoning. Set it in `labs/.env`.
- **Empty or weak local results** — the corpus is small and keyword-based. Ask questions about
  agentic AI, ReAct, tools/memory, or evaluation (the corpus topics), or add a Tavily key.
- **Agent answers in one step** — your question was too easy. Ask something that needs two facts
  (e.g. "the ReAct pattern *and* why a loop needs a cap") to force multi-step reasoning.
- **`run_end` shows `success: false`** — the loop hit `MAX_STEPS` without a Final Answer. Raise
  the cap slightly, or narrow the question. Don't remove the cap.
- **Tavily errors** — quota or network. The code auto-falls back to local search and prints a
  warning; the run still completes.
- **Log looks like one giant line** — it's JSONL: one object *per line*. Use `less` or
  `python -m json.tool --json-lines`, not a JSON parser expecting a single array.

## Teacher's Playbook

### Worked model answer

The default question is intentionally **two-part**, so a correct run makes **at least two**
`search` calls: one for the ReAct definition, one for the max-steps rationale, then a synthesized
Final Answer citing `corpus/react-pattern.txt` (and often `evaluation.txt`). The event stream in
`run-log.jsonl` is the graded artifact: `run_start -> plan -> (tool_call, tool_result) x2+ ->
run_end{success:true}`.

### Live-demo script (about 12 minutes)

1. Run the default question offline. Narrate the **plan** appearing before any search — *"the
   agent decided its approach first."*
2. `cat run-log.jsonl` and walk the event sequence against `audit-log-schema.md`. Emphasize:
   append-only, bounded payloads, totals belong on `run_end`. *"This exact log powers Lab 7
   evaluation and Lab 16 governance."*
3. Ask a one-fact question ("What is a scratchpad?") — one search, one step. Then the two-part
   default — several steps. This is single- vs multi-step reasoning made visible.
4. Set `MAX_STEPS=1`, ask something broad, show the clean stop and `success:false` in the log.
5. If a Tavily key is available, add it and re-run the same question; show `"engine":"tavily"`
   in the log and web URLs as sources. Same code, real web.

### Common mistakes + fixes

- **Skipping the Agent Design Canvas.** Make section 3 (tools) and section 4 (cap/memory)
  mandatory before coding — it's a two-minute exercise that prevents scope creep.
- **Logging raw tool dumps.** The schema says *bound the payload*. We truncate snippets to 400
  chars; point out why (cost, PII, readability).
- **Treating search results as instructions.** A planted "ignore your instructions" line in a
  snippet is *data*. The system prompt says so; this is the prompt-injection lesson in miniature.
- **Removing the cap to "let it finish."** Never. A stuck agent must terminate; fix the question
  or the query, not the guardrail.
- **Expecting citations without grounding.** If a student sees invented sources, check that the
  Final Answer is built from Observations — that's the factuality defense.

### Debrief Q&A

- *Why a separate planning step instead of pure ReAct?* An explicit plan reduces plan drift and
  gives the loop a spine; it's also a logged artifact you can evaluate.
- *Why JSONL, not one JSON file?* Append-only, crash-safe, and it streams into pandas / DuckDB /
  Delta for lineage — exactly what Labs 6 and 15 need.
- *What would make this production-ready?* Token/cost/latency totals on `run_end`, a `reflection`
  event before finishing, dedup of sources, and a real vector search over the corpus.
- *Where's the human-in-the-loop?* Not needed here — search is read-only (*safe*). It appears the
  moment a tool can send, buy, or delete (Lab 5).

### What good looks like

The student filled the canvas, ran a genuinely multi-step research task, and can open
`run-log.jsonl` and narrate each event and why it's there. The final answer is grounded in the
corpus with real source names, the loop respected the cap, and they can explain how this same log
feeds evaluation and governance later in the week.

---
