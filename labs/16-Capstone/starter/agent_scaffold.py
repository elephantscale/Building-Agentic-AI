"""
Capstone starter scaffold - a minimal, runnable multi-agent skeleton.

It gives you the four pieces the rubric grades, wired together end-to-end so you
spend hour one on YOUR problem, not on plumbing:

    * ToolRegistry  - register tools with a safety_class; a HUMAN GATE fires
                      automatically before any 'dangerous' tool runs.
    * AuditLog      - append-only JSONL, one event per line
                      (course-materials/audit-log-schema.md).
    * Worker        - a role + tools + a (optional) LLM brain; one small ReAct-ish
                      step. Extend into a real loop for your domain.
    * Supervisor    - plans which workers run, coordinates them, and reflects on
                      the result before returning (that's the reflection capability).

It runs OFFLINE with a deterministic fallback, so `python agent_scaffold.py`
works with no key. Set OPENAI_API_KEY to give the workers a real brain.

This is a SKELETON. Search for "TODO" - those are your extension points.

Run:
    pip install -r requirements.txt
    python agent_scaffold.py
    # -> prints a run and writes audit-log.jsonl
"""

import os
import json
import uuid
from pathlib import Path
from datetime import datetime, timezone

from dotenv import load_dotenv

HERE = Path(__file__).resolve().parent
load_dotenv(HERE.parents[1] / ".env")           # labs/.env (optional key)
AUDIT_PATH = HERE / "audit-log.jsonl"


# --- Audit log ---------------------------------------------------------------

class AuditLog:
    """Append-only JSONL logger (see course-materials/audit-log-schema.md)."""

    def __init__(self, path: Path, agent: str, actor: str):
        self.path, self.agent, self.actor = path, agent, actor
        self.run_id = str(uuid.uuid4())[:8]
        self.step = 0
        path.write_text("", encoding="utf-8")    # fresh log per demo run

    def log(self, event: str, detail: dict, result: dict | None = None):
        self.step += 1
        rec = {"run_id": self.run_id,
               "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
               "agent": self.agent, "actor": self.actor, "step": self.step,
               "event": event, "detail": detail}
        if result is not None:
            rec["result"] = result
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec) + "\n")


# --- Tool registry + human gate ----------------------------------------------

class ToolRegistry:
    """Holds tools with a safety class and enforces the human gate on dangerous
    ones. `approver` is a callable(tool, args) -> bool; swap the default for a
    real UI, a Slack approval, or a spoken confirmation (Lab 14)."""

    def __init__(self, audit: AuditLog, approver=None):
        self.tools = {}                          # name -> (fn, safety_class)
        self.audit = audit
        self.approver = approver or self._cli_approver

    def register(self, name, fn, safety_class="safe"):
        assert safety_class in ("safe", "guarded", "dangerous")
        self.tools[name] = (fn, safety_class)

    @staticmethod
    def _cli_approver(tool, args):               # TODO: replace for your channel
        ans = input(f"  [GATE] approve {tool}({args})? [y/N] ").strip().lower()
        return ans in ("y", "yes")

    def call(self, name, **args):
        if name not in self.tools:
            return {"ok": False, "error": f"unknown tool {name!r}"}
        fn, safety = self.tools[name]
        if safety == "dangerous":
            self.audit.log("human_gate",
                           {"tool": name, "args": args, "safety_class": safety,
                            "state": "awaiting_approval"})
            if not self.approver(name, args):
                self.audit.log("human_gate",
                               {"tool": name, "args": args,
                                "safety_class": safety, "state": "denied"})
                return {"ok": False, "denied": True, "summary": "human denied"}
            self.audit.log("human_gate",
                           {"tool": name, "args": args, "safety_class": safety,
                            "state": "approved"})
        self.audit.log("tool_call", {"tool": name, "args": args,
                                     "safety_class": safety})
        result = fn(**args)
        self.audit.log("tool_result", {"tool": name},
                       {"ok": result.get("ok", True),
                        "summary": str(result.get("summary", ""))[:200]})
        return result


# --- Optional LLM brain ------------------------------------------------------

def llm_complete(system: str, user: str) -> str:
    """Return a completion from the LLM, or a deterministic stub offline."""
    if os.getenv("OPENAI_API_KEY"):
        try:
            from openai import OpenAI
            r = OpenAI().chat.completions.create(
                model="gpt-4.1", temperature=0,
                messages=[{"role": "system", "content": system},
                          {"role": "user", "content": user}])
            return r.choices[0].message.content.strip()
        except Exception as exc:
            print(f"  (llm unavailable: {exc}; using stub)")
    return f"[stub reasoning] {user[:120]}"


# --- Worker ------------------------------------------------------------------

class Worker:
    """A role with tools and an optional brain. ONE step here for clarity;
    TODO: expand into a capped ReAct loop (plan -> act -> observe -> reflect)."""

    def __init__(self, name, role, tools, registry: ToolRegistry, audit: AuditLog):
        self.name, self.role = name, role
        self.tools, self.registry, self.audit = tools, registry, audit

    def run(self, task: str, context: dict) -> dict:
        self.audit.log("plan", {"worker": self.name, "task": task})
        thought = llm_complete(f"You are the {self.role}. Be terse.",
                               f"Task: {task}\nContext: {json.dumps(context)}")
        # TODO: parse `thought` into tool calls. The scaffold hard-wires the
        # obvious tool per role so the demo runs; replace with real routing.
        for tool_name in self.tools:
            if tool_name in self.registry.tools:
                out = self.registry.call(tool_name, **context.get(tool_name, {}))
                context[f"{self.name}:{tool_name}"] = out
        return {"worker": self.name, "thought": thought, "context": context}


# --- Supervisor --------------------------------------------------------------

class Supervisor:
    """Plans which workers run, coordinates them, and reflects on the output."""

    def __init__(self, workers, audit: AuditLog):
        self.workers = workers                   # ordered list of Worker
        self.audit = audit

    def handle(self, goal: str, context: dict) -> dict:
        self.audit.log("run_start", {"goal": goal})
        for w in self.workers:                    # TODO: dynamic routing/DAG
            result = w.run(goal, context)
            context = result["context"]
        # Reflection: cheap self-check before returning (a required capability).
        verdict = self.reflect(goal, context)
        self.audit.log("reflection", {"verdict": verdict})
        self.audit.log("run_end", {"success": verdict.get("ok", False)},
                       {"ok": verdict.get("ok", False),
                        "summary": verdict.get("note", "")})
        return {"context": context, "verdict": verdict}

    def reflect(self, goal, context) -> dict:
        # TODO: replace with a real quality check (LLM judge, schema validation,
        # or an eval-set score). Here: did any dangerous action get denied?
        denied = any(isinstance(v, dict) and v.get("denied")
                     for v in context.values())
        return {"ok": not denied,
                "note": "a dangerous action was denied by the gate" if denied
                        else "all steps completed with gates honored"}


# =============================================================================
# DEMO: a 2-agent customer-support system. Delete this and build your domain.
# =============================================================================

_KB = {"refund": "Annual plans: full refund within 14 days.",
       "reset": "Password reset links expire after 60 minutes."}


def kb_search(query: str = "") -> dict:          # SAFE tool
    for k, v in _KB.items():
        if k in query.lower():
            return {"ok": True, "summary": v, "answer": v}
    return {"ok": True, "summary": "no KB match", "answer": None}


def send_email(to: str = "", body: str = "") -> dict:   # DANGEROUS tool
    return {"ok": True, "summary": f"email sent to {to}"}


def build_demo() -> tuple[Supervisor, dict]:
    audit = AuditLog(AUDIT_PATH, agent="capstone-demo", actor="user:team")
    registry = ToolRegistry(audit,
                            approver=lambda t, a: True)   # auto-approve in demo
    registry.register("kb_search", kb_search, "safe")
    registry.register("send_email", send_email, "dangerous")

    analyst = Worker("analyst", "support analyst",
                     ["kb_search"], registry, audit)
    comms = Worker("comms", "customer communicator",
                   ["send_email"], registry, audit)
    supervisor = Supervisor([analyst, comms], audit)

    context = {"kb_search": {"query": "refund window"},
               "send_email": {"to": "customer@example.com",
                              "body": "Here is your refund policy."}}
    return supervisor, context


def main():
    supervisor, context = build_demo()
    print("Running capstone demo (2 agents, 1 safe + 1 dangerous tool)...")
    out = supervisor.handle("Answer the customer's refund question and reply.",
                            context)
    print(f"Verdict: {out['verdict']}")
    print(f"Audit log written to {AUDIT_PATH.name} "
          f"({sum(1 for _ in AUDIT_PATH.open())} events)")
    print("\nNow make it yours: see the TODOs and labs/16-Capstone/README.md")


if __name__ == "__main__":
    main()
