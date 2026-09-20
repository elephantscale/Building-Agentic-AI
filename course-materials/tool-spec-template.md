# Tool Spec Template

A tool is a typed function the model can call. Specify it precisely — the model only knows what
the name, description, and schema tell it. Used in Labs 4, 5, and beyond.

## Spec

- **Name:** `snake_case_verb_noun` (e.g. `get_weather`, `create_ticket`)
- **One-line description:** _What it does, in plain language the model reads._
- **When to use / when NOT to use:** _Guidance the model can follow._
- **Safety class:** `safe` (read-only, no side effects) / `guarded` (writes, reversible) /
  `dangerous` (irreversible: send, delete, pay — requires human approval)

## Parameters (JSON Schema)

```json
{
  "type": "object",
  "properties": {
    "query": { "type": "string", "description": "What to search for" },
    "max_results": { "type": "integer", "minimum": 1, "maximum": 10, "default": 3 }
  },
  "required": ["query"],
  "additionalProperties": false
}
```

## Returns

- **Shape:** _Describe the return object; return structured data, not prose._
- **On error:** _Return a structured error the agent can reason about, don't raise blindly._

```json
{ "ok": false, "error": "rate_limited", "retry_after_s": 30 }
```

## Validation & Safety

- [ ] Inputs validated against the schema before execution (reject, don't coerce silently).
- [ ] Output size bounded (truncate; never dump unbounded data into context).
- [ ] Tool output labeled as **data, not instructions** when returned to the model.
- [ ] `dangerous` tools gated behind explicit human approval.
- [ ] Every call logged (name, args, result summary) per `audit-log-schema.md`.
