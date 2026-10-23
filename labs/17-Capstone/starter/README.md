# Capstone Starter Scaffold

A minimal, runnable multi-agent skeleton.

> **For the capstone design review, this is reference reading — you are not
> extending it today.** Use it for one thing: to check your design is
> buildable. Find each box on your picture in the table below. Anything with no
> home there is something you would have to build from scratch — worth saying
> out loud in your presentation.

## What's here

- `agent_scaffold.py` — the skeleton: `AuditLog`, `ToolRegistry` (with an
  automatic **human gate** on dangerous tools), `Worker`, `Supervisor`.
- `requirements.txt` — runs offline (`python-dotenv`); add your own deps.

## Run it

```sh
pip install -r requirements.txt
python agent_scaffold.py            # writes audit-log.jsonl, no API key needed
```

You'll see a 2-agent support demo: an **analyst** looks up the KB (safe tool),
a **communicator** sends a reply (dangerous tool → gated), and the
**supervisor** reflects before finishing. Every step lands in `audit-log.jsonl`.

## How it maps to the six required capabilities

| Capability | Where in the scaffold | What building it would take |
|------------|-----------------------|----------|
| Reasoning | `Worker.run` (one step) | Grow it into a **capped ReAct loop** |
| Tool use | `ToolRegistry.register/call` | Add ≥ 2 real tools with validated args |
| Reflection | `Supervisor.reflect` | Replace with a real quality check / LLM judge |
| Multi-agent | `Supervisor([...workers])` | Give workers **distinct** roles that cooperate |
| Evaluation | *(not in scaffold)* | Add `eval/eval_set.jsonl` + a scorer (Lab 6) |
| Governance | `AuditLog` + human gate | Keep it; set a **real approver** for your channel |

## Extension points

The `TODO` markers are where a real build would pick up — read them as the
distance between a skeleton and a system:

- **Real routing** — the supervisor runs workers in a fixed order; make it
  choose based on the goal (a plan, a DAG, or an LLM router).
- **Real worker loop** — `Worker.run` does one step; parse the model's output
  into tool calls and loop with a **max-steps cap**.
- **Real approver** — `ToolRegistry` auto-approves in the demo; wire a genuine
  human gate (CLI prompt, Slack, or the spoken confirmation from Lab 14).
- **Real reflection** — swap the placeholder for schema validation, an LLM
  judge, or an eval-set score.

## Reuse the course assets

- `course-materials/agent-design-canvas.md` — fill it **before** coding.
- `course-materials/audit-log-schema.md` — the log this scaffold already emits.
- `course-materials/agent-evaluation-rubric.md` — score your run.
- `course-materials/agent-safety-checklist.md` — sign off before the demo.
- `labs/assets/help_center.md`, `labs/assets/support_tickets.csv` — sample data.
