# Audit Log Schema

Every agent run should emit a structured, append-only log. This is the backbone of evaluation
(Lab 6) and governance (Lab 15). One JSON object per event, one event per line (JSONL).

## Event schema

```json
{
  "run_id": "uuid",
  "ts": "2026-09-18T14:03:22Z",
  "agent": "research-assistant",
  "actor": "user:alice",
  "step": 3,
  "event": "tool_call",
  "detail": {
    "tool": "web_search",
    "args": { "query": "agentic ai eval metrics" },
    "safety_class": "safe"
  },
  "result": { "ok": true, "summary": "3 results returned" },
  "tokens": { "prompt": 812, "completion": 141 },
  "cost_usd": 0.004,
  "latency_ms": 930
}
```

## `event` values

| event | Emitted when |
|-------|--------------|
| `run_start` | A run begins (include goal + inputs hash) |
| `plan` | The agent produces or updates a plan |
| `tool_call` | The agent calls a tool (name, args, safety_class) |
| `tool_result` | A tool returns (ok/error, bounded summary) |
| `human_gate` | A dangerous action pauses for approval (`approved` / `denied`) |
| `reflection` | The agent self-evaluates or revises |
| `run_end` | A run finishes (final output, success flag, totals) |

## Rules

- **Append-only.** Never edit past events; corrections are new events.
- **Bound the payload.** Summarize/truncate large tool results — don't log raw dumps.
- **No secrets.** Redact keys, tokens, PII before writing.
- **Totals on `run_end`.** Sum tokens, cost, latency, and step count for quick dashboards.
- **Queryable.** JSONL loads into pandas, DuckDB, or a Delta table for lineage & analytics.
