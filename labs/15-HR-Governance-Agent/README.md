# Lab 15 — HR Governance Agent (audit agent activity)

## Goal

Build the agent that **watches the other agents**. It ingests an append-only
activity log (JSONL, per `course-materials/audit-log-schema.md`), runs
deterministic **policy checks**, produces a **compliance report**, and writes
findings to a **Delta-style table** (Parquet locally; Unity Catalog / Delta on
Databricks). This is governance made concrete: not a slide about accountability,
but code that catches an ungated refund, an SSN in a log, and a runaway loop.

The checks are **deterministic on purpose** — an auditor must be reproducible,
not "vibes". An optional LLM step *narrates* the findings for a non-technical
reviewer, but never *decides* them.

## Time

60 minutes

## Tools

- Python 3.11+ with `pandas` and `pyarrow`
- `hr_governance_agent.py` (this lab)
- `sample_activity_log.jsonl` — a seeded log with planted violations
- `OPENAI_API_KEY` in `labs/.env` — **optional** (only for `--narrate`)

## Files in this lab

```text
15-HR-Governance-Agent/
  README.md                  this guide
  requirements.txt           pandas, pyarrow, python-dotenv (openai optional)
  hr_governance_agent.py     the runnable auditor
  sample_activity_log.jsonl  4 runs, with planted violations
```

Running the agent produces `findings.parquet` and `compliance_report.md` — your
deliverables.

## Steps

1. Install deps: `pip install -r requirements.txt`.
2. Skim `sample_activity_log.jsonl` — 4 runs of a fictional `hr-analytics` agent.
   Only **run-1001** is clean; the others hide problems.
3. Audit it: `python hr_governance_agent.py`.
4. Open `compliance_report.md`. Match each finding back to the exact log line
   that caused it (use the `run` + `step` columns).
5. Open `findings.parquet` to confirm the Delta-style table:
   `python -c "import pandas as pd; print(pd.read_parquet('findings.parquet'))"`.
6. **Tune a policy.** Lower `RUN_COST_CAP` or `REPEAT_CAP` at the top of the
   script and re-run — watch findings change. Governance thresholds are policy.
7. *(Optional)* `python hr_governance_agent.py --narrate` to add an LLM summary
   for a non-technical reviewer (needs `OPENAI_API_KEY`).

## Starter Code

**Two gate checks in one pass — ungated vs. bypassed:**

```python
def check_gates(run_events):
    findings, gate_state_for = [], {}
    for ev in run_events:
        if ev.get("event") == "human_gate":
            gate_state_for[_tool(ev)] = _gate_state(ev)      # remember approval
            continue
        if ev.get("event") == "tool_call" and _safety_class(ev) == "dangerous":
            state = gate_state_for.get(_tool(ev))
            if state == "approved":
                continue                                     # compliant
            rule = "denied_but_proceeded" if state == "denied" else "ungated_dangerous"
            findings.append(_finding(ev, rule, "critical", ...))
    return findings
```

**PII check — report the type, never re-log the value:**

```python
PII_PATTERNS = {"ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
                "email": re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b"),
                "phone": re.compile(r"\b\d{3}[-.]\d{3}[-.]\d{4}\b")}

def check_pii(run_events):
    findings = []
    for ev in run_events:
        blob = json.dumps({"detail": ev.get("detail"), "result": ev.get("result")})
        hits = [name for name, rx in PII_PATTERNS.items() if rx.search(blob)]
        if hits:
            findings.append(_finding(ev, "pii_in_log", "high",
                f"raw PII in log payload: {', '.join(hits)} (value redacted)"))
    return findings
```

**Write the Delta-style table (local Parquet):**

```python
def write_delta_table(df, path):
    df.to_parquet(path, engine="pyarrow", index=False)
    # On Databricks the same findings go to a governed Delta table:
    #   spark.createDataFrame(df).write.format("delta").mode("append") \
    #        .saveAsTable("governance.audit_findings")
    # Unity Catalog then governs read access and tracks lineage on that table.
```

## What a correct run looks like

```text
$ python hr_governance_agent.py
Ingesting sample_activity_log.jsonl ...
  30 events across 4 runs
Policy checks complete: 8 findings (2 critical).
Wrote findings.parquet and compliance_report.md

Top findings:
  [critical] run-1002 step 3: dangerous tool 'email_report' ran with no approved human_gate
  [critical] run-1004 step 4: dangerous tool 'delete_records' ran AFTER its human_gate was denied
  [high]     run-1002 step 2: raw PII in log payload: ssn (value redacted)
  [high]     run-1003 step 14: run reached 14 steps (cap 12)
  [medium]   run-1003 step 14: run cost $2.34 exceeds cap $1.00
```

`compliance_report.md` (excerpt):

```text
| Severity | Run      | Step | Rule                 | Finding |
| critical | run-1002 |    3 | ungated_dangerous    | dangerous tool 'email_report' ran with no approved human_gate |
| critical | run-1004 |    4 | denied_but_proceeded | dangerous tool 'delete_records' ran AFTER its human_gate was denied |
| high     | run-1002 |    2 | pii_in_log           | raw PII in log payload: ssn (value redacted) |
| medium   | run-1003 |   14 | runaway_loop         | tool 'query_salaries' called 12 times with identical args |

## Per-run verdict
| run-1001 | user:alice      | 0 | PASS   |
| run-1002 | user:bob        | 3 | REVIEW |
| run-1003 | agent:scheduler | 4 | REVIEW |
| run-1004 | user:carol      | 1 | REVIEW |
```

Every planted violation is caught, and the one clean run (**run-1001**) passes.

## Deliverable

- `findings.parquet` and `compliance_report.md` from the sample log.
- For each **critical** finding, the exact `run_id` + `step` in the source log
  that triggered it.
- One sentence: which finding would you escalate to the HR director first, and
  why? (Hint: severity + what data was exposed.)

## Troubleshooting

- **`pyarrow` won't install.** On the class VM `pip install pyarrow` works; if
  not, swap `to_parquet` for `df.to_csv("findings.csv")` — the checks are
  unchanged, only the sink differs.
- **Zero findings on the sample.** You edited the log or the thresholds; the
  shipped sample must yield 8 findings (2 critical). Restore it from git.
- **`ungated_dangerous` not firing.** A tool is dangerous only if its
  `tool_call` has `detail.safety_class == "dangerous"`. Check the log field.
- **PII check misses a value.** It only knows SSN/email/phone shapes — add a
  pattern to `PII_PATTERNS` (e.g., credit-card) and re-run.
- **`--narrate` does nothing.** It needs `OPENAI_API_KEY`; without it the report
  is still complete, just without the plain-English paragraph.

## Teacher's Playbook

**What good looks like.** A student can (1) name all five policy checks, (2)
point to the log line behind each critical finding, and (3) explain why the
checks are deterministic while the *narrative* is the only LLM step. Bonus: they
change a threshold and predict the new finding count before re-running.

**Live-demo script (5 min).** Run the audit. Open the report next to the log
side by side. For `run-1004`, read step 3 (`human_gate ... denied`) then step 4
(`delete_records` ran anyway) — "the gate said no and the agent did it anyway;
that's the worst kind of finding." For `run-1002`, show the SSN sitting in a
`tool_result` summary — "the agent logged raw PII; that's a breach in the log
itself."

**The one big idea.** Governance is reconstruction after the fact. The auditor
never trusts the final answer — it grades the *process* recorded in the log.
That only works if the upstream agents logged honestly (tie back to Labs 1, 5,
14: log every plan, tool call, result, and gate).

**Common mistakes + fixes.**
- *"I'll just ask an LLM if the run was compliant."* → non-reproducible and
  ungradable. Deterministic checks first; LLM only to *explain* them.
- *"PII check re-logs the SSN in the finding."* → report the *type* and redact;
  an auditor that copies the PII into its own report is now the violation.
- *"Runaway loop missed."* → two signals: absolute step count **and** repeated
  identical calls. Show both on `run-1003`.
- *"Everything is critical."* → severities let a reviewer triage; keep
  ungated/bypassed = critical, PII = high, loops/cost lower.

**Debrief Q&A.**
- *Where does Databricks fit?* Delta stores the findings table (ACID, history);
  Unity Catalog governs who reads it and tracks lineage; MLflow tracing produces
  the upstream log; a dashboard runs these same checks as SQL.
- *Retention?* Map to policy (Module 12): e.g., audit findings retained 13
  months, then archived — who owns review, who can read the table.
- *How would you run this continuously?* Stream new JSONL into the table (Auto
  Loader), run the checks on a schedule, alert on any `critical`.

**Time-box.** 10 min read the sample log · 15 min run + trace findings to lines
· 15 min tune a threshold / add a PII pattern · 5 min optional `--narrate` · 15
min debrief.

---
