"""
Lab 15 - HR Governance Agent (audits agent activity logs).

This agent does NOT act on HR data. It AUDITS other agents' behavior. It ingests
an append-only activity log (JSONL, per course-materials/audit-log-schema.md),
runs deterministic policy checks, writes findings to a Delta-style table
(Parquet via pandas/pyarrow), and emits a Markdown compliance report. An
optional LLM step narrates the findings for a non-technical reviewer.

Policy checks (deterministic - governance must be reproducible, not vibes):
  1. ungated_dangerous   a dangerous tool ran with no approved human_gate
  2. denied_but_proceeded a dangerous tool ran AFTER its gate was denied
  3. pii_in_log          raw SSN / email / phone found in a logged payload
  4. runaway_loop        step count or repeated identical calls over a cap
  5. cost_spike          a run (or single event) over the cost cap

Run:
    pip install -r requirements.txt
    python hr_governance_agent.py                         # audits the sample log
    python hr_governance_agent.py --log some_other.jsonl
    python hr_governance_agent.py --narrate               # add an LLM summary

Outputs (in this folder):
    findings.parquet        one row per finding (the "Delta table")
    compliance_report.md    the human-readable report
"""

import os
import re
import json
import argparse
from pathlib import Path
from collections import defaultdict

import pandas as pd
from dotenv import load_dotenv

LAB_DIR = Path(__file__).resolve().parent
ENV_PATH = LAB_DIR.parents[0] / ".env"
load_dotenv(ENV_PATH)

# --- Policy thresholds (make governance limits explicit and editable) --------

STEP_CAP = 12            # a single run should not exceed this many steps
REPEAT_CAP = 5           # identical (tool, args) calls beyond this = loop
RUN_COST_CAP = 1.00      # USD per run
EVENT_COST_CAP = 0.50    # USD for any single event

# PII patterns. We report the TYPE and a redacted marker - never re-log the value.
PII_PATTERNS = {
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "email": re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b"),
    "phone": re.compile(r"\b\d{3}[-.]\d{3}[-.]\d{4}\b"),
}


# --- Ingest ------------------------------------------------------------------

def load_events(path: Path) -> list[dict]:
    """Read a JSONL activity log into a list of event dicts (skip blank lines)."""
    events = []
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError as exc:
            print(f"  ! skipping malformed line {i}: {exc}")
    return events


def group_by_run(events: list[dict]) -> dict[str, list[dict]]:
    runs = defaultdict(list)
    for e in events:
        runs[e.get("run_id", "UNKNOWN")].append(e)
    for evs in runs.values():
        evs.sort(key=lambda e: e.get("step", 0))
    return runs


# --- Helpers -----------------------------------------------------------------

def _safety_class(ev: dict) -> str:
    return (ev.get("detail") or {}).get("safety_class", "unspecified")


def _gate_state(ev: dict) -> str:
    d = ev.get("detail") or {}
    # accept a couple of shapes: detail.state / detail.decision / result.approved
    if "state" in d:
        return d["state"]
    if "decision" in d:
        return d["decision"]
    res = ev.get("result") or {}
    if "approved" in res:
        return "approved" if res["approved"] else "denied"
    return "unknown"


def _tool(ev: dict) -> str:
    return (ev.get("detail") or {}).get("tool", "")


def _finding(ev: dict, rule: str, severity: str, message: str) -> dict:
    return {
        "run_id": ev.get("run_id"),
        "step": ev.get("step"),
        "ts": ev.get("ts"),
        "agent": ev.get("agent"),
        "actor": ev.get("actor"),
        "rule": rule,
        "severity": severity,
        "message": message,
    }


# --- The five policy checks (each takes one run's events) --------------------

def check_gates(run_events: list[dict]) -> list[dict]:
    """ungated_dangerous + denied_but_proceeded.

    A dangerous tool_call is compliant only if a human_gate for the SAME tool
    reached state 'approved' earlier in the run. A gate that was 'denied'
    followed by the action is a worse violation (a bypass).
    """
    findings = []
    gate_state_for = {}       # tool -> last gate state seen so far
    for ev in run_events:
        if ev.get("event") == "human_gate":
            gate_state_for[_tool(ev)] = _gate_state(ev)
            continue
        if ev.get("event") == "tool_call" and _safety_class(ev) == "dangerous":
            tool = _tool(ev)
            state = gate_state_for.get(tool)
            if state == "approved":
                continue                      # compliant
            if state == "denied":
                findings.append(_finding(
                    ev, "denied_but_proceeded", "critical",
                    f"dangerous tool '{tool}' ran AFTER its human_gate was denied"))
            else:
                findings.append(_finding(
                    ev, "ungated_dangerous", "critical",
                    f"dangerous tool '{tool}' ran with no approved human_gate"))
    return findings


def check_pii(run_events: list[dict]) -> list[dict]:
    """pii_in_log - raw PII in any logged detail/result payload."""
    findings = []
    for ev in run_events:
        blob = json.dumps({"detail": ev.get("detail"), "result": ev.get("result")})
        hits = [name for name, rx in PII_PATTERNS.items() if rx.search(blob)]
        if hits:
            findings.append(_finding(
                ev, "pii_in_log", "high",
                f"raw PII in log payload: {', '.join(sorted(hits))} (value redacted)"))
    return findings


def check_runaway(run_events: list[dict]) -> list[dict]:
    """runaway_loop - too many steps, or the same call repeated too often."""
    findings = []
    max_step = max((e.get("step", 0) for e in run_events), default=0)
    if max_step > STEP_CAP:
        findings.append(_finding(
            run_events[-1], "runaway_loop", "high",
            f"run reached {max_step} steps (cap {STEP_CAP})"))
    counts = defaultdict(int)
    for ev in run_events:
        if ev.get("event") == "tool_call":
            key = (_tool(ev), json.dumps((ev.get("detail") or {}).get("args"),
                                         sort_keys=True))
            counts[key] += 1
    for (tool, _args), n in counts.items():
        if n > REPEAT_CAP:
            findings.append(_finding(
                run_events[-1], "runaway_loop", "medium",
                f"tool '{tool}' called {n} times with identical args "
                f"(cap {REPEAT_CAP}) - likely a loop with no progress"))
    return findings


def check_cost(run_events: list[dict]) -> list[dict]:
    """cost_spike - run total or a single event over the cost cap."""
    findings = []
    total = sum(float(e.get("cost_usd", 0) or 0) for e in run_events)
    if total > RUN_COST_CAP:
        findings.append(_finding(
            run_events[-1], "cost_spike", "medium",
            f"run cost ${total:.2f} exceeds cap ${RUN_COST_CAP:.2f}"))
    for ev in run_events:
        c = float(ev.get("cost_usd", 0) or 0)
        if c > EVENT_COST_CAP:
            findings.append(_finding(
                ev, "cost_spike", "low",
                f"single event cost ${c:.2f} exceeds cap ${EVENT_COST_CAP:.2f}"))
    return findings


CHECKS = [check_gates, check_pii, check_runaway, check_cost]


def audit(runs: dict[str, list[dict]]) -> pd.DataFrame:
    findings = []
    for run_events in runs.values():
        for check in CHECKS:
            findings.extend(check(run_events))
    cols = ["run_id", "step", "ts", "agent", "actor", "rule", "severity", "message"]
    return pd.DataFrame(findings, columns=cols)


# --- Outputs -----------------------------------------------------------------

def write_delta_table(df: pd.DataFrame, path: Path):
    """Write findings to Parquet - the local stand-in for a Delta table.

    On Databricks this is:
        spark.createDataFrame(df).write.format("delta").mode("append") \\
             .saveAsTable("governance.audit_findings")
    Unity Catalog then governs who may read it and tracks its lineage.
    """
    df.to_parquet(path, engine="pyarrow", index=False)


SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


def write_report(df: pd.DataFrame, runs: dict, path: Path, narrative: str | None):
    lines = ["# Agent Activity Compliance Report", ""]
    lines.append(f"- Runs audited: **{len(runs)}**")
    lines.append(f"- Events audited: **{sum(len(v) for v in runs.values())}**")
    lines.append(f"- Findings: **{len(df)}**")
    if not df.empty:
        by_sev = df["severity"].value_counts().to_dict()
        sev_str = ", ".join(f"{k}: {by_sev[k]}" for k in
                            sorted(by_sev, key=lambda s: SEVERITY_ORDER.get(s, 9)))
        lines.append(f"- By severity: {sev_str}")
    lines.append("")

    if narrative:
        lines += ["## Summary for reviewers", "", narrative, ""]

    lines += ["## Findings", ""]
    if df.empty:
        lines.append("No policy violations detected. All runs compliant.")
    else:
        ordered = df.sort_values(
            by=["severity", "run_id", "step"],
            key=lambda col: col.map(SEVERITY_ORDER) if col.name == "severity" else col)
        lines.append("| Severity | Run | Step | Rule | Finding |")
        lines.append("|----------|-----|-----:|------|---------|")
        for _, r in ordered.iterrows():
            lines.append(f"| {r.severity} | {r.run_id} | {r.step} | "
                         f"`{r.rule}` | {r.message} |")
    lines.append("")
    lines.append("## Per-run verdict")
    lines.append("")
    lines.append("| Run | Actor | Findings | Verdict |")
    lines.append("|-----|-------|---------:|---------|")
    for run_id, evs in runs.items():
        n = int((df["run_id"] == run_id).sum()) if not df.empty else 0
        verdict = "PASS" if n == 0 else "REVIEW"
        lines.append(f"| {run_id} | {evs[0].get('actor','?')} | {n} | {verdict} |")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def narrate(df: pd.DataFrame) -> str | None:
    """Optional: a short plain-English summary via the LLM (if a key is set)."""
    if df.empty or not os.getenv("OPENAI_API_KEY"):
        return None
    try:
        from openai import OpenAI
        client = OpenAI()
        table = df[["run_id", "severity", "rule", "message"]].to_dict("records")
        msg = [
            {"role": "system", "content":
                "You are a compliance analyst. Summarize these audit findings in "
                "3-4 sentences for a non-technical HR director. State the biggest "
                "risk first and one recommended action. Do not invent findings."},
            {"role": "user", "content": json.dumps(table)},
        ]
        r = client.chat.completions.create(model="gpt-4.1", messages=msg,
                                           temperature=0)
        return r.choices[0].message.content.strip()
    except Exception as exc:
        print(f"  ! narration skipped ({exc})")
        return None


# --- Main --------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="Audit an agent activity log.")
    ap.add_argument("--log", default=str(LAB_DIR / "sample_activity_log.jsonl"))
    ap.add_argument("--narrate", action="store_true",
                    help="add an LLM natural-language summary (needs OPENAI_API_KEY)")
    args = ap.parse_args()

    log_path = Path(args.log)
    print(f"Ingesting {log_path} ...")
    events = load_events(log_path)
    runs = group_by_run(events)
    print(f"  {len(events)} events across {len(runs)} runs")

    df = audit(runs)
    print(f"Policy checks complete: {len(df)} findings "
          f"({(df['severity'] == 'critical').sum()} critical).")

    narrative = narrate(df) if args.narrate else None

    parquet_path = LAB_DIR / "findings.parquet"
    report_path = LAB_DIR / "compliance_report.md"
    write_delta_table(df, parquet_path)
    write_report(df, runs, report_path, narrative)
    print(f"Wrote {parquet_path.name} and {report_path.name}")

    if not df.empty:
        print("\nTop findings:")
        for _, r in df.sort_values(
                by="severity",
                key=lambda c: c.map(SEVERITY_ORDER)).head(5).iterrows():
            print(f"  [{r.severity}] {r.run_id} step {r.step}: {r.message}")


if __name__ == "__main__":
    main()
