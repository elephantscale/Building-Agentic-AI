# Governance with Databricks

Elephant Scale

---

## Part IV O–P — What We'll Cover

* Why agent governance — **autonomy creates accountability**
* Tracking every agent action; **data lineage**
* **Audit logs** as the backbone (ref `audit-log-schema.md`)
* Access control and **least privilege**
* Databricks tools, conceptually: **Unity Catalog, MLflow tracing, Delta, dashboards**
* A worked **HR-analytics** governance example
* Mapping controls to **policy** — who reviews, how long we keep it
* Then you build the auditor — Lab 15

> A chatbot answers; an agent *acts*. The moment it acts, someone must be able to answer for it.

Notes:

---

## Why Governance — Autonomy ⇒ Accountability

* An agent that can **send / pay / delete / change records** can cause real harm
* "It's just the AI" is not an answer to an auditor, a regulator, or a customer
* Governance answers five questions **after the fact**:

```text
WHO   ran the agent, on whose behalf?
WHAT  did it do — every tool call and result?
WHEN  did each step happen?
WHY   what plan / input led to the action?
WAS   a human required to approve — and did they?
```

> Governance is not paperwork. It's the ability to reconstruct exactly what happened, and prove it.

Notes:

---

## Tracking Agent Actions

* Every run emits a structured, **append-only** trace
* One event per line (JSONL), one object per event (see `audit-log-schema.md`)

```json
{"run_id":"a1b2","ts":"2026-09-18T14:03:22Z","agent":"hr-analytics",
 "actor":"user:alice","step":3,"event":"tool_call",
 "detail":{"tool":"query_salaries","args":{"dept":"eng"},"safety_class":"guarded"},
 "result":{"ok":true,"summary":"142 rows"},"cost_usd":0.004,"latency_ms":930}
```

* Log: `run_start`, `plan`, `tool_call`, `tool_result`, `human_gate`, `reflection`, `run_end`
* **Bound payloads**, **redact secrets/PII**, put **totals on `run_end`**.

> If it isn't in the log, it didn't happen — and you can't prove it did.

Notes:

---

## Data Lineage — Where Did This Come From?

* **Lineage** = the path from source data → agent → output/action
* Answers: *which tables did the agent read to make that decision?*
* Needed for: audits, incident response, GDPR/CCPA requests, debugging plan drift

```text
salaries table ──┐
                 ├─> query_salaries tool ─> agent plan ─> "pay-equity report"
headcount table ─┘                                          │
                                                            └─> emailed to HRBP (gated)
```

* Lineage links the **audit log** to the **actual data assets** touched.

> Lineage turns "the agent said so" into "here is every table that produced this number".

Notes:

---

## Access Control and Least Privilege

* The agent gets its **own identity**, not a human's admin token
* Grant the **fewest** tables/tools with the **narrowest** scope that works
* **Read-only first** — observe and draft before it can change anything
* Column/row-level controls: the agent sees aggregates, **not raw PII**

```text
BAD:   agent runs as `admin`, full read/write on all HR tables
GOOD:  agent runs as `svc-hr-analytics`, SELECT on hr.salary_agg only,
       no PII columns, no write; changes go to a human queue
```

> Least privilege is the cheapest incident-limiter you have. Scope the agent before you trust it.

Notes:

---

## Databricks, Conceptually

| Databricks piece | Governance job |
|------------------|----------------|
| **Unity Catalog** | Central permissions + **data lineage** across tables/models |
| **MLflow Tracing** | Capture each agent run: prompts, tool calls, latency, cost |
| **Delta tables** | Store the **audit log** — ACID, append-only, time-travel |
| **Dashboards / SQL** | Query the log: violations, cost, volume, who-did-what |

* You don't need Databricks to learn this — the **shapes** are portable.
* Local fallback (Lab 15): JSONL log → **Parquet** "Delta" table → pandas queries.

> Unity Catalog = who + lineage. MLflow = the trace. Delta = the ledger. Dashboards = the answers.

Notes:

---

## The Log → Delta → Dashboard Flow

```text
   AGENT RUNS
   (voice, HR, CRM, ...)
        |
        | emit JSONL events (append-only)
        v
  +--------------+     ingest / stream      +------------------+
  | audit log    | -----------------------> |  DELTA TABLE     |
  | *.jsonl      |   (Auto Loader / COPY)   |  audit_events    |
  +--------------+                          |  (ACID, history) |
                                            +---------+--------+
                                                      |
                     Unity Catalog: permissions       | SQL / policy checks
                     + lineage on every asset          v
                                            +------------------+
                                            |  DASHBOARD /     |
                                            |  COMPLIANCE      |
                                            |  REPORT          |
                                            +------------------+
```

* Same pipeline locally: `jsonl → pandas → parquet → query + markdown report`.

> Logs are the raw ledger. Delta makes them queryable. The dashboard is where governance becomes visible.

Notes:

---

## Worked Example — HR Analytics Agent

* Goal: an agent answers HR questions ("pay gap by level?", "attrition in sales?")
* It reads sensitive tables, so governance is **not optional**

```text
Agent:  hr-analytics
Tools:  query_salaries (guarded, aggregates only)
        query_attrition (guarded)
        email_report (dangerous -> human gate)
Identity: svc-hr-analytics  (SELECT on hr.*_agg, no PII, no write)
```

* Every question = one logged run. Every emailed report = a `human_gate` event.

> High-value questions over sensitive data are exactly where an ungoverned agent gets you fired.

Notes:

---

## What the Auditor Looks For

* **Ungated dangerous actions** — a `send/pay/delete` with no approved `human_gate`
* **Missing human approval** — action proceeded after a `denied` gate (or no gate at all)
* **PII in the logs** — raw emails, SSNs, salaries in `detail` / `result`
* **Runaway loops** — step counts or repeated identical calls past a threshold
* **Cost spikes** — a run's `cost_usd` far above the norm

```text
VIOLATION  run=7fa3  ungated_dangerous  email_report sent, no human_gate
VIOLATION  run=7fa3  pii_in_log         result contains an SSN pattern
```

> The auditor doesn't read the final answer. It reads the *process* — the log — and flags the exceptions.

Notes:

---

## Mapping Controls to Policy

* A control with no owner is a control that won't hold. Write it down:

| Question | Policy answer (example) |
|----------|-------------------------|
| Who reviews failures? | Named owner per agent; HRBP for HR-analytics |
| Who approves dangerous actions? | Role-based approver in the human gate |
| How long do we retain logs? | Audit log retained **13 months**, then archived |
| Who can read the logs? | Compliance + agent owner; Unity Catalog grant |
| What triggers escalation? | Any ungated dangerous action → incident review |

> Every checkbox in the safety checklist should map to a person and a retention rule — or it's theater.

Notes:

---

## Putting It Together

* Autonomy ⇒ accountability — governance lets you **reconstruct and prove** what happened
* **Log everything** (append-only JSONL), **redact PII**, totals on `run_end`
* **Lineage** ties decisions back to the data that produced them
* **Least privilege + own identity** limits the blast radius
* Databricks shape: **Unity Catalog + MLflow + Delta + dashboards** — portable locally
* Map every control to an **owner, an approver, and a retention rule**

> You built agents that act. Governance is how you stay allowed to run them.

Notes:

---

## Lab 15 — HR Governance Agent (Audit Agent Activity)

**Stop here and run Lab 15.**

You will:

1. **Ingest** an agent activity log (JSONL, per `audit-log-schema.md`).
2. Run **deterministic policy checks**: ungated dangerous actions, missing approval, PII in logs, runaway loops, cost spikes.
3. Produce a **compliance report** (Markdown) with one row per finding.
4. Write findings to a **Delta-style table** — Parquet via pandas/pyarrow (note the Unity Catalog equivalent).
5. *(Optional)* Add an **LLM narrative** summarizing the audit for a non-technical reviewer.

**Deliverable:** a runnable `hr_governance_agent.py` that turns `sample_activity_log.jsonl` into `findings.parquet` + a Markdown compliance report.

**Time:** 60 minutes

Notes:
