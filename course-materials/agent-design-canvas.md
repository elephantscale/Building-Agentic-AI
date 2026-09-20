# Agent Design Canvas

Fill this out *before* you write agent code. One page forces the decisions that make an agent
safe and testable. Used in Labs 2, 7, and the Capstone.

## 1. Goal

- **One-sentence goal:** _What does this agent accomplish for whom?_
- **Success looks like:** _A concrete, checkable outcome._
- **Out of scope:** _What this agent must NOT try to do._

## 2. Inputs

- **Trigger:** _What starts a run (user message / new row / schedule / event)?_
- **Inputs available:** _Data, files, context the agent can read._
- **Untrusted inputs:** _Which inputs are attacker-controllable and must be treated as data._

## 3. Tools

| Tool | What it does | Read / Write | Safety class |
|------|--------------|--------------|--------------|
| | | read / write | safe / guarded / dangerous |

- **Least privilege:** _Fewest tools and narrowest scopes that still work._

## 4. Reasoning & Memory

- **Pattern:** _ReAct / plan-then-execute / reflection / multi-agent._
- **Max steps / budget:** _Loop cap, token/cost cap, wall-clock cap._
- **Memory:** _None / scratchpad (this run) / persistent (across runs) — what is stored and where._

## 5. Reflection & Evaluation

- **Self-check:** _What does the agent verify before finishing?_
- **Eval metrics:** _Task success, tool-call accuracy, factuality, cost, latency._
- **Test cases:** _Happy path, missing data, ambiguous input, unsafe request._

## 6. Guardrails & Human-in-the-Loop

- **Human approval required for:** _send / publish / delete / buy / change records / spend._
- **Hard stops:** _Conditions that abort the run._
- **Fallback:** _What happens when a tool fails or the agent is unsure._

## 7. Observability

- **Logged:** _Every plan, tool call + args, tool result, final output (see `audit-log-schema.md`)._
- **Owner / escalation:** _Who reviews failures and audits logs._
