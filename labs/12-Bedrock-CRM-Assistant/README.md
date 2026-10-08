# Lab 12 — CRM Assistant on AWS Bedrock

## Goal

Build a **CRM assistant** that looks up and updates customer records through **tool use**,
running on **AWS Bedrock** via the `boto3` **Converse** API. Reads are free; the one write
(`update_customer`) is a **dangerous** action gated behind an explicit human approval.

The exact same agent — same tools, same gate, same audit log — also runs as a **local
fallback** against a direct LLM (Anthropic or OpenAI) with a local SQLite CRM, so **no student
is blocked by an AWS account**. You flip one environment variable to switch:

```text
CRM_BACKEND=BEDROCK   ->  boto3 converse() against Bedrock (cloud)
CRM_BACKEND=LOCAL     ->  anthropic/openai direct + SQLite CRM (works offline of AWS)
                         with NO LLM key, LOCAL auto-uses an offline deterministic
                         stub (no model, no network) — same tools, gate, and audit log
```

> **Fully offline option.** On a locked-down network with no model access, just run the
> `LOCAL` backend without a key: it falls back to a rule-based stub so the governed
> workflow (tools → human gate → audit log) still runs end to end.

Only the transport changes. The tool definitions, the human gate, the max-steps cap, and the
JSONL audit log are shared code — that is the whole lesson: **the agent pattern is portable.**

## Time

60 minutes

## Tools

- Python 3.11+, `pip`
- `labs/.env` with **either** AWS credentials (cloud path) **or** an `ANTHROPIC_API_KEY` /
  `OPENAI_API_KEY` (local path)
- Concepts: `course-materials/tool-spec-template.md`, `agent-safety-checklist.md`,
  `audit-log-schema.md`

## Files in this lab

```text
12-Bedrock-CRM-Assistant/
├── README.md            # this file
├── requirements.txt     # boto3, anthropic, openai, python-dotenv
├── bedrock_crm.py       # runnable agent — BEDROCK and LOCAL backends
└── crm_seed.sql         # sample schema + seed data (auto-seeded by the script)
```

## Steps

1. Install and configure keys:

   ```sh
   cd labs/12-Bedrock-CRM-Assistant
   pip install -r requirements.txt
   cp ../.env.example ../.env        # fill in the keys handed out in class
   ```

2. **Run the local fallback first** (works without AWS):

   ```sh
   CRM_BACKEND=LOCAL python bedrock_crm.py "Who is account GLOBEX-207?"
   ```

3. Run a task that triggers the **dangerous write** and approve it at the gate:

   ```sh
   CRM_BACKEND=LOCAL python bedrock_crm.py \
     "Look up ACME-1042, then set its plan to business."
   ```

4. Run the **same command against Bedrock** (if you have AWS access):

   ```sh
   CRM_BACKEND=BEDROCK python bedrock_crm.py \
     "Look up ACME-1042, then set its plan to business."
   ```

5. Inspect `run-log.jsonl` — every `tool_call`, `tool_result`, and `human_gate` is recorded.

6. Prove the gate works: run a write task and answer `n` at the prompt. Confirm the record is
   **unchanged** and the log shows `decision: "denied"`.

## Starter Code

The tool registry is defined once and reused by every backend — this is the portable core.
Each tool carries a **safety class** (`safe` vs `dangerous`), exactly as in the Tool Spec
Template:

```python
TOOLS = {
    "get_customer":   {"fn": get_customer,   "safety": "safe",      ...},
    "search_customers":{"fn": search_customers,"safety": "safe",     ...},
    "update_customer":{"fn": update_customer,"safety": "dangerous", ...},
}
```

The **human gate** runs before any dangerous tool — a real stop, not a log-after-the-fact:

```python
def dispatch(name, args):
    spec = TOOLS[name]
    if spec["safety"] == "dangerous" and not human_gate(name, args):
        return {"ok": False, "error": "denied_by_human"}
    log("tool_call", tool=name, args=args, safety_class=spec["safety"])
    result = spec["fn"](**args)
    log("tool_result", tool=name, ok=result.get("ok"), summary=str(result)[:200])
    return result
```

The **Bedrock path** is the canonical Converse tool loop — capped, and every `toolUse` block is
dispatched through the shared gate:

```python
resp = client.converse(
    modelId=BEDROCK_MODEL,                       # us.anthropic.claude-sonnet-5-v1:0
    system=[{"text": SYSTEM_PROMPT}],
    messages=messages,
    toolConfig=tool_config,
    inferenceConfig={"maxTokens": 1024, "temperature": 0.2},
)
if resp["stopReason"] == "tool_use":
    for block in resp["output"]["message"]["content"]:
        if "toolUse" in block:
            tu = block["toolUse"]
            result = dispatch(tu["name"], tu.get("input", {}))
            # append a toolResult block, then call converse() again
```

Open `bedrock_crm.py` to read the full loop (Bedrock, Anthropic, and OpenAI backends).

## What a correct run looks like

Local backend, with an approved write:

```text
$ CRM_BACKEND=LOCAL python bedrock_crm.py "Look up ACME-1042, then set its plan to business."
Backend: LOCAL (anthropic)
Task:    Look up ACME-1042, then set its plan to business.

  [GATE] Agent wants to run dangerous tool: update_customer({"account_id": "ACME-1042", "field": "plan", "value": "business"})
  Approve? [y/N] y

=== Answer ===
Account ACME-1042 (Acme Corp) was on the team plan and is now updated to business.

Audit log -> run-log.jsonl
```

Denying the gate:

```text
  [GATE] Agent wants to run dangerous tool: update_customer({...})
  Approve? [y/N] n

=== Answer ===
I did not change ACME-1042 — the update was declined. The account remains on the team plan.
```

A slice of `run-log.jsonl`:

```json
{"run_id":"...","event":"run_start","backend":"LOCAL","task":"Look up ACME-1042..."}
{"run_id":"...","event":"tool_call","tool":"get_customer","args":{"account_id":"ACME-1042"},"safety_class":"safe"}
{"run_id":"...","event":"tool_result","tool":"get_customer","ok":true,"summary":"{'ok': True, 'customer': {...}}"}
{"run_id":"...","event":"human_gate","tool":"update_customer","decision":"approved"}
{"run_id":"...","event":"tool_call","tool":"update_customer","args":{"account_id":"ACME-1042","field":"plan","value":"business"},"safety_class":"dangerous"}
{"run_id":"...","event":"run_end","answer":"Account ACME-1042 ... now updated to business."}
```

## Deliverable

- A terminal transcript of the assistant answering a lookup **and** performing a gated update.
- A terminal transcript showing a **denied** gate leaving the record unchanged.
- The `run-log.jsonl` from at least one run.
- One sentence: what code did you have to change to switch BEDROCK <-> LOCAL? (Answer: only the
  env var — that's the point.)

## Troubleshooting

- **`NoCredentialsError` / `AccessDeniedException` (Bedrock).** Your AWS creds/region aren't set
  or the account lacks `bedrock:InvokeModel`. Use `CRM_BACKEND=LOCAL` — the lab is not blocked.
- **`ValidationException: model ... not found`.** The model isn't enabled in your region, or the
  ID is wrong. Enable it in the Bedrock console (Model access) or set `BEDROCK_MODEL_ID`. List
  ids with `aws bedrock list-foundation-models --region us-east-1`.
- **`AuthenticationError` (local).** Missing `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` in
  `labs/.env`. Switch provider with `LOCAL_PROVIDER=openai`.
- **The gate never appears.** In a non-interactive shell the gate auto-denies (safe default).
  Run in a real terminal to approve.
- **Reset the CRM.** Delete `crm.db`; it re-seeds on the next run (or `sqlite3 crm.db < crm_seed.sql`).
- **The model writes without asking.** It can't — the gate is in `dispatch`, not the prompt. The
  model can only *request* the tool; your code decides whether to run it.

## Teacher's Playbook

**The one big idea.** The tool registry, the safety gate, the step cap, and the audit log are
**backend-independent**. Bedrock's Converse, Anthropic's Messages, and OpenAI's Chat
Completions differ only in the *shape* of the tool-call envelope. Have students diff the three
`run_*` functions and notice how thin the provider-specific code is.

**Live-demo script (8 min).**
1. `CRM_BACKEND=LOCAL python bedrock_crm.py "Who's on the enterprise plan?"` — pure reads, no gate.
2. Run the plan-change task; **approve** it; show the row changed in `sqlite3 crm.db "SELECT * FROM customers"`.
3. Run it again; **deny** it; show the row unchanged and the `denied` log line.
4. If AWS is available, rerun step 2 with `CRM_BACKEND=BEDROCK` — identical behavior, different transport.

**Worked model answer.** For "set ACME-1042 to business," the agent should call `get_customer`
first (confirm the record), then request `update_customer(account_id, "plan", "business")`,
pause at the gate, and on approval report the before/after plan citing the account_id.

**Common mistakes + fixes.**
- *Putting the gate in the system prompt.* A prompt is a suggestion; a code gate is a guarantee.
  Safety lives in `dispatch`, never in wording.
- *Letting the model write SQL.* It only supplies `account_id`/`field`/`value`; the parameterized
  query is ours. Ask: "what if the model passed `plan; DROP TABLE`?" (It can't — we bind params
  and whitelist fields.)
- *No step cap.* Remove `MAX_STEPS` and ask a vague question to show a loop that won't converge —
  then put it back.
- *Unbounded tool output.* We truncate the logged summary to 200 chars; discuss why dumping a
  10k-row query into context is both a cost and a safety problem.

**Debrief Q&A.**
- *Why gate `update` but not `get`?* Reversibility and blast radius — a read can't corrupt state.
- *When would you choose Bedrock over the direct API?* Governance perimeter (IAM, CloudTrail,
  VPC), a multi-model menu, and compliance — not because the model is better.
- *Where would this log go in production?* CloudWatch/S3 for Bedrock, or a Delta table (Lab 13/15)
  for lineage and analytics.

**What good looks like.** A student who can (a) run both backends, (b) show an approved and a
denied write, (c) point to the exact line where the gate lives, and (d) explain that switching
providers changed only one env var.

---
