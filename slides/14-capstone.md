# Capstone: Enterprise AI Agent Challenge

Elephant Scale

---

## The Challenge

* In teams, **design and build a multi-agent system** in one domain:
  - **Finance** · **HR** · **Real Estate** · **Customer Support**
* You have one day: **design → build → evaluate → demo**
* It must be a *system*, not a single prompt — agents that **cooperate**
* Everything you learned this week shows up here **at least once**

> This is the whole course in one project. Small scope, done well, beats big scope, half-built.

Notes:

---

## Required Capabilities (all six)

* A passing project shows **every** capability at least once (ref `capstone-rubric.md`):

| Capability | Minimum bar |
|------------|-------------|
| **Reasoning** | An explicit plan / ReAct loop, not one prompt |
| **Tool use** | ≥ 2 real tools with validated schemas |
| **Reflection** | The system self-checks or revises ≥ 1 output |
| **Multi-agent** | ≥ 2 cooperating roles/agents |
| **Evaluation** | A small frozen eval set + before/after scores |
| **Governance** | Audit log + human gate on dangerous actions |

> Six checkboxes. Wire all six early with one thin thread, then make each one good.

Notes:

---

## Scope It With the Agent Design Canvas

* Fill `agent-design-canvas.md` **before** you write code — one page, seven boxes:

```text
1. Goal        one sentence + what "done" looks like + out of scope
2. Inputs      trigger, data available, which inputs are UNTRUSTED
3. Tools       name, read/write, safety class (safe/guarded/dangerous)
4. Reasoning   pattern, max steps, budget, memory
5. Reflection  self-check + eval metrics + test cases
6. Guardrails  human gate for send/pay/delete, hard stops, fallback
7. Observ.     what's logged, who owns review/escalation
```

* The **"out of scope"** line is the most valuable thing you'll write today.

> A finished canvas is a scoped project. A blank canvas is a demo that dies at 4 p.m.

Notes:

---

## Timeline for the Day

```text
09:30  Form teams, pick a domain + one concrete use case
10:00  DESIGN   fill the Agent Design Canvas; agree the eval set (5-8 cases)
10:45  BUILD    thin end-to-end thread: supervisor + 1 worker + 1 tool + log
12:30  lunch (agent keeps running in your head)
13:15  BUILD    add 2nd agent, reflection, the human gate on dangerous actions
15:00  EVALUATE run the frozen eval set; record before/after; fix the top failure
16:00  POLISH   rehearse the 10-min demo; pick your edge case + gate moment
16:30  DEMOS    ~10 min per team
```

* Use the `starter/` scaffold in `labs/17-Capstone` so hour one isn't plumbing.

> Hit "end-to-end but ugly" by lunch. Everything after lunch is making it good, not making it work.

Notes:

---

## The Demo Format (10 min / team)

* From `capstone-rubric.md`:

```text
2 min  problem, domain, and the design canvas
5 min  LIVE demo — include ONE edge case and ONE human-gate moment
2 min  evaluation results + what you'd fix next
1 min  Q&A
```

* Show the **audit log** live — reviewers grade the *process*, not just the answer.
* A handled edge case earns more than a flawless happy path.

> Don't narrate what it *would* do. Run it, break it on purpose, and show the gate catching it.

Notes:

---

## How You're Graded (100 pts)

| Dimension | Wt | Full marks |
|-----------|---:|-----------|
| Problem & design | 15 | Clear goal, sane scope, completed canvas |
| Reasoning & planning | 15 | Robust loop; recovers from surprises |
| Tools & integration | 15 | Well-specified tools; clean error handling |
| Reflection & quality | 10 | Measurable lift from self-evaluation |
| Multi-agent coordination | 15 | Distinct roles that actually cooperate |
| Evaluation | 15 | Frozen set, honest metrics, before/after |
| Governance & safety | 10 | Least privilege, human gate, full audit log |
| Demo & communication | 5 | Clear demo; team explains tradeoffs |

> Notice the weights: reasoning, tools, multi-agent, and eval are 60 of 100. Depth beats features.

Notes:

---

## Deliverables

* Repo with runnable code (or a documented low-code flow) + `requirements.txt`
* Completed `agent-design-canvas.md` **and** `agent-safety-checklist.md`
* Eval set + a results table (before/after one change)
* A sample **audit log (JSONL)** from a real run

```text
capstone-<team>/
  README.md            what it does + how to run
  agents/  tools/      the system
  eval/    eval_set.jsonl  results.md
  audit/   run-log.jsonl
  agent-design-canvas.md   agent-safety-checklist.md
```

> If the audit log and the eval results are missing, two of the six capabilities are unproven.

Notes:

---

## Tips

* **Thin thread first** — one supervisor, one worker, one tool, one logged run
* **Freeze the eval set early** and never edit it — that's how "before/after" means anything
* **Fake slow/expensive tools** with local stubs; spend your time on the *loop*, not integrations
* **Cap the loop** (max steps + cost) on line one
* **One dangerous action, well-gated** beats five ungated ones
* Reuse the course assets: `help_center.md`, `support_tickets.csv`, the audit schema

> Every hour ask: "what's the one thing that, if it breaks in the demo, sinks us?" Fix that.

Notes:

---

## Common Pitfalls

* **Scope creep** — five domains, zero finished. Pick one use case.
* **Prompt-in-a-trenchcoat** — one giant prompt pretending to be multi-agent
* **No eval set** — "it worked when I tried it" is not evaluation
* **Governance bolted on at 4 p.m.** — the log and the gate are design, not garnish
* **Demo-by-slides** — reviewers want it *live*, including the failure case
* **Real integrations eating the day** — a flaky API will cost you the eval

> The failure mode is always the same: too much scope, safety last, and nothing that runs end to end.

Notes:

---

## Gallery — Finance

* **Invoice triage & approval** — extract → validate against PO → flag anomalies → **human gate** to approve payment
* **Expense-policy auditor** — read expense rows, cite the policy clause, escalate the gray areas
* **Earnings-call briefer** — retrieve transcript → summarize → reflect for factuality → cite sources

> Finance = high stakes, clear rules to cite, obvious dangerous action (pay). A natural governance story.

Notes:

---

## Gallery — HR & Real Estate

* **HR**
  - **Onboarding coordinator** — schedule, draft welcome emails, checklist (draft-only, human sends)
  - **Pay-equity analyst** — query aggregates (no raw PII), reflect on the finding, gated report
  - **Policy Q&A** — answer only from the handbook; escalate anything legal
* **Real Estate**
  - **Listing assistant** — draft listings from specs + comps; reflect for compliance wording
  - **Lead qualifier** — score inbound leads, route hot ones, book viewings (gated)
  - **Comps analyst** — pull comparables, compute a range, cite each comp

> HR and Real Estate both live near regulated data — perfect for showing least privilege and gates.

Notes:

---

## Gallery — Customer Support

* **Tier-1 resolver** — answer from `help_center.md`, escalate what it can't ground
* **Refund handler** — verify eligibility from the KB, then a **human gate** before issuing
* **Voice support line** — reuse your Lab 15 agent; add a second agent for account changes
* **Ticket triage swarm** — classifier agent + drafting agent + a QA/reflection agent

> Support has ready-made assets (`help_center.md`, `support_tickets.csv`) — you can be building by 10:15.

Notes:

---

## Build It — Good Luck

* Go to **`labs/17-Capstone`** — run-of-show, the `starter/` scaffold, and the rubric
* Design on paper first. Get one thread running. Then make it good.
* Log everything. Gate the dangerous thing. Prove it with the eval set.
* Demo it **live** — edge case and all.

> You started the week hand-building a ReAct loop. Today you ship a governed multi-agent system. Go build.

Notes:
