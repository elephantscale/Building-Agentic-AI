# Low-Code Agentic Design

Elephant Scale

---

## Why This Module

* Not every agent needs a repo

* Business teams want wins this week

* Low-code = ChatGPT + Zapier + Custom GPTs

* Same patterns, less plumbing

> The pattern outlives the tool. Low-code just moves the plumbing behind a UI.

---

## When Low-Code Fits

* **Fits** when:
  - the owner is not a developer
  - the task is business automation (triage, drafting, routing)
  - you want a fast win to prove value
  - the systems already have connectors

* **Reach for code** when:
  - logic is complex or heavily branching
  - you need tests, version control, custom tools
  - latency, cost, or scale are tight

> Pick the lightest tool that does the job — then graduate when it hurts.

---

## The Low-Code Stack

* **ChatGPT** — the reasoning step

* **Custom GPT** — a configured assistant + Actions

* **Zapier** — triggers, connectors, the workflow spine

* **Actions (OpenAPI)** — how a GPT calls real APIs

```text
Trigger  ->  GPT reasons  ->  Action calls an app  ->  Human reviews
(Zapier)     (ChatGPT)        (Zapier / OpenAPI)       (approval step)
```

> Zapier moves data. The GPT makes decisions. You keep the approval.

---

## The Core Flow

```text
   +----------+     +-----------+     +-----------+     +----------+
   | TRIGGER  | --> |    GPT    | --> |  ACTION   | --> |  REVIEW  |
   | new email|     | classify  |     | draft to  |     | human    |
   | / ticket |     | + draft   |     | CRM / doc |     | approves |
   +----------+     +-----------+     +-----------+     +----------+
                          |                                  |
                     structured JSON                    nothing sends
                                                        until approved
```

> Trigger -> reason -> act -> review. Four boxes. Every low-code agent is these.

---

## ChatGPT + Zapier

* Zapier catches an event (email, form, row, ticket)

* A **ChatGPT step** runs your prompt on that data

* Insist on **structured output** so later steps can branch

```text
Return ONLY this JSON:
{ "category": "...", "priority": "...", "summary": "...",
  "risk_flag": "...", "human_review_required": "yes" }
```

> Prose is for people. JSON is for the next Zap step.

---

## Custom GPTs With Actions

* A **Custom GPT** = instructions + knowledge + Actions

* An **Action** lets the GPT call an API you describe

* You describe it with an **OpenAPI** schema

```yaml
paths:
  /tickets/{id}/note:
    post:
      operationId: addTicketNote
      summary: Attach a draft note to a ticket (draft only)
      parameters:
        - name: id
          in: path
          required: true
          schema: { type: string }
```

> The OpenAPI schema is the tool spec — the same contract we wrote in Lab 4.

---

## Memory In A Low-Code Workflow

* Chat memory is short and per-conversation

* Durable memory lives **outside** the GPT:
  - a Zapier Table / Google Sheet
  - the CRM record itself
  - a knowledge file in the Custom GPT

```text
Read prior context (row / record) -> reason -> write context back
```

> If you want the agent to remember, give it a place to write. Chat is not storage.

---

## Chaining Steps

* One Zap = a chain of steps, each feeding the next

* Keep each step **small and single-purpose**

```text
Step 1  Trigger: new support email
Step 2  GPT: classify + extract fields  -> JSON
Step 3  Filter: only if category = billing
Step 4  GPT: draft reply from help center
Step 5  Action: create draft (not send)
Step 6  Human approval before send
```

> Small steps are testable steps. One giant prompt is a black box.

---

## Reflection In Low-Code

* Add a **second GPT step** that critiques the first

* Route the draft back for one revision if weak

```text
GPT draft  ->  GPT critique ("is this grounded? complete? safe?")
   ^                              |
   +---- revise once if score low +
```

* Cap the loop — Zapier has no infinite loops by design

> Reflection is just a second opinion wired in. Same pattern as LangGraph, fewer lines.

---

## A No-Code CRM Agent

* Inbound lead or ticket arrives

* GPT classifies, scores, and drafts a CRM note

* Nothing writes to the record until a human approves

```text
New lead -> GPT: {segment, intent, next_action, draft_note}
         -> write to REVIEW queue (Zapier Table)
         -> human approves -> Action updates CRM
```

> The agent proposes the CRM update. A person commits it. That line never moves.

---

## Governance In Low-Code

* Low-code hides the code, **not** the risk

* Same guardrails as everywhere:
  - **Human approval** on send / write / delete
  - **Least privilege** — scope the connector to one object
  - **Logging** — every run to a table / sheet
  - Treat inbound text as **untrusted data**

> A Zap that auto-sends is not a pilot. It is an incident waiting for a trigger.

---

## Least Privilege With Connectors

* A Zapier connection carries real credentials

* Scope it down:
  - a dedicated service account, not a person's admin login
  - the narrowest permission that works (draft, not send)
  - read-only first; write-back only after review works

> The connector's scope is the agent's blast radius. Keep it small.

---

## Logging Every Run

* Append one row per run — the review queue *is* the log

```text
Run ID | Source | Category | Priority | Risk | Route | Draft | Status
```

* Status stays `NEEDS_REVIEW` until a human acts

* Mirrors `course-materials/audit-log-schema.md`

> If you can't see what the agent did, you can't govern it. Log first.

---

## Low-Code vs. Code: Honest Table

| Concern | Low-Code | Code (LangGraph) |
|---------|----------|------------------|
| Time to first win | Hours | Days |
| Owner | Business user | Developer |
| Branching / cycles | Limited | Full |
| Testing / versioning | Weak | Strong |
| Custom tools | Prebuilt only | Anything |
| Governance | Manual, in-UI | In code |

> Start low-code to prove value. Move to code when the limits start to bite.

---

## Cloud-Free In The Classroom

* No Zapier or ChatGPT account? You are **not** blocked

* Lab 9 ships `zap_sim.py` — the same trigger -> GPT -> action -> review pipeline in Python

* Lab 10 ships `crm_agent.py` — the CRM agent against a local SQLite DB

> We simulate the SaaS locally so everyone builds the pattern, account or not.

---

## Lab 9 — Business Automation With ChatGPT + Zapier

**Stop here and run Lab 9.**

You will:

1. Design a Custom GPT with an Action (OpenAPI) for ticket triage.
2. Build a Zapier flow: trigger -> GPT step -> action -> review.
3. Add memory, a reflection step, and a human-approval gate.
4. Or run the local `zap_sim.py` over `support_tickets.csv` for the same result.

**Deliverable:** a documented Custom GPT + Zap (or a simulator run) with a review queue.

**Time:** 60 minutes

---

## Lab 10 — No-Code AI CRM Agent

**Stop here and run Lab 10.**

You will:

1. Build a no-code CRM assistant that classifies leads/tickets and drafts CRM notes.
2. Put every write behind a human-approval step.
3. Or run `crm_agent.py` against a local SQLite CRM with a review queue.
4. Confirm no dangerous write is ever auto-committed.

**Deliverable:** proposed CRM updates in a review queue, approved by a human before commit.

**Time:** 60 minutes

Notes:
