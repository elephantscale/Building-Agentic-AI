# Lab 5 — Email Assistant Workflow (draft, summarize, send)

## Goal

Build an agent that takes an inbound support ticket and walks it through a real, governed
workflow:

1. **Summarize** the message into structured triage fields.
2. **Draft** a reply grounded **only** in `assets/help_center.md` — no invented policy.
3. Pass the draft through a **human-approval gate** — because sending email is safety class
   **`dangerous`**, it never happens without a person saying yes.
4. **"Send"** via a `send_email` **stub** that appends to `outbox.jsonl` — it never really
   emails anyone.
5. Write an append-only **audit log** of every step.

This is the human-in-the-loop and audit-logging discipline from Day 1, made concrete on a task
that actually touches the outside world.

## Time

60 minutes

## Tools

- Python 3.11+
- OpenAI API (`gpt-4.1` by default; `gpt-4o-mini` also works)
- `labs/.env` with `OPENAI_API_KEY` (see `labs/SETUP.md`)
- Shared assets: `../assets/support_tickets.csv`, `../assets/help_center.md`

## Files in this lab

- `email_assistant.py` — the full workflow: summarize -> draft -> human gate -> send-stub,
  plus the audit logger and the `send_email` stub.
- `requirements.txt` — `openai`, `python-dotenv`, `rich`.
- Generated at runtime: `outbox.jsonl` (queued "sent" messages) and `audit_log.jsonl` (every
  step). Neither is committed.

## Steps

1. Install and confirm your key:
   ```sh
   cd labs/05-Email-Assistant
   pip install -r requirements.txt
   ```
2. Run the workflow on the first ticket and use the interactive gate:
   ```sh
   python email_assistant.py
   ```
   At the prompt, try `a` (approve), `e` (edit), and `r` (reject) on separate runs.
3. **🔮 Predict, then run the sensitive ticket.** Before running `T-1002` (patient records),
   predict its triage JSON: will `sensitive` be true? what `category` and `priority`? Then run it
   and confirm the draft **escalates** instead of answering, and that the gate flags it:
   ```sh
   python email_assistant.py --ticket T-1002
   ```
4. Run the **messy / urgent** ticket and check the draft doesn't invent card numbers or dates:
   ```sh
   python email_assistant.py --ticket T-1004
   ```
5. Reject one at the gate and confirm **nothing** is written to `outbox.jsonl`:
   ```sh
   python email_assistant.py --ticket T-1003 --auto-reject
   ```
6. Inspect the artifacts:
   ```sh
   cat outbox.jsonl        # only approved messages appear here
   cat audit_log.jsonl     # every step, approved or not
   ```

7. **🛠️ Your turn — author your own ticket and predict its triage.** Use `--text` to write a brand-new
   ticket (no CSV editing). **First predict the triage JSON** (`sensitive`, `category`, `priority`,
   `multiple_asks`) and whether the draft will answer or escalate — *then* run and compare:
   ```sh
   # one that SHOULD force escalation (asks something the help center can't ground):
   python email_assistant.py --text "Can you delete all of a customer's data under GDPR by Friday?" --from "Acme Legal"
   # one that SHOULD be answerable from the help center (e.g. a refund-window question):
   python email_assistant.py --text "How many days do I have to return an item?" --from "Dana R."
   ```
   Try to write one that *looks* safe but should escalate (hidden PII, a legal ask, two questions at
   once). *Reference answer in the Teacher's Playbook.*

8. **🗣️ Explain.** In one or two sentences: why does the workflow **triage (summarize) before it
   drafts and gates**? What does the structured triage give the human at the gate that the raw ticket
   wouldn't?

## Starter Code

The **human gate** is the heart of the lab — `send_email` (dangerous) is unreachable until this
returns `approved=True`:

```python
def human_gate(ticket, triage, draft, mode):
    console.print(draft)
    if triage.get("sensitive") or triage.get("multiple_asks"):
        console.print("NOTE: flagged - review extra carefully.")
    if mode == "auto-approve":  return True, draft, "auto-approve"
    if mode == "auto-reject":   return False, draft, "auto-reject"
    choice = console.input("Approve send? [a]pprove / [e]dit / [r]eject: ").strip().lower()
    if choice.startswith("a"): return True, draft, "human:approve"
    if choice.startswith("e"): return True, (console.input("Edited:\n") or draft), "human:edit"
    return False, draft, "human:reject"
```

The **dangerous tool** is a stub that queues instead of sending, and is only ever called after
approval:

```python
def send_email(to, subject, body):
    record = {"ts": ..., "to": to, "subject": subject, "body": body, "status": "queued_stub"}
    with open(OUTBOX, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
    return {"ok": True, "delivered": False, "queued_to": str(OUTBOX)}
```

Grounding is enforced in the draft prompt — **use only the help center, escalate otherwise**:

```python
"Use ONLY the HELP CENTER below as your source of facts. If it does not answer the question,
 say the answer isn't in the help center and that a human will follow up - do NOT invent policy."
```

Every step is audited:

```python
audit("summarize", ticket_id=..., triage=triage)
audit("draft", ticket_id=..., draft=draft)
audit("human_gate", ticket_id=..., approved=approved, decided_by=decided_by)
audit("send_email", ticket_id=..., to=..., result=result)   # only if approved
```

## What a correct run looks like

Interactive run on the messy/urgent billing ticket (`T-1004`), approved:

```text
──────────────── Ticket T-1004 - BlueTree Realty ────────────────
pymnt failed?? card ****4417 charged 3x?? pls fix asap this is urgent

Triage: {"summary": "Customer reports a failed payment and a card charged three times, urgent.",
"category": "billing", "priority": "urgent", "sensitive": false, "multiple_asks": false}

──────────── HUMAN APPROVAL REQUIRED (safety class: dangerous) ────────────
To: BlueTree Realty (email)
Triage: {...}
Proposed reply:

Hi BlueTree Realty, thanks for flagging this. Duplicate charges are refunded within 5 business
days once we confirm them, so we'll verify the three charges on your card ending 4417 and
process the refund for the extra amounts. A member of our billing team will follow up shortly
to confirm the details. We're sorry for the trouble.

Approve send? [a]pprove / [e]dit / [r]eject: a
──────────────── Queued to outbox (stub - not really sent) ────────────────
outbox: .../05-Email-Assistant/outbox.jsonl
```

The sensitive ticket (`T-1002`, patient records) **escalates** rather than answering:

```text
Triage: {"summary": "Customer asks whether patient records can be uploaded to the AI summary
tool.", "category": "policy_compliance", "priority": "normal", "sensitive": true,
"multiple_asks": false}
...
NOTE: flagged sensitive and/or multiple asks - review extra carefully.
Proposed reply:
Hi Rivera Health - uploading patient/health records to AI features requires a signed BAA/DPA
and a human-approved, compliant workflow, so I can't confirm this is allowed for your
workspace. I'm escalating to a specialist who will follow up before your Friday demo.
```

A rejected run writes an audit entry but leaves `outbox.jsonl` untouched:

```text
$ python email_assistant.py --ticket T-1003 --auto-reject
──────────── Not sent - rejected at the human gate ────────────
$ wc -l outbox.jsonl        # unchanged - nothing was queued
```

`audit_log.jsonl` (one JSON object per line):

```json
{"ts": "2026-09-19T15:04:01Z", "event": "run_start", "ticket_id": "T-1004", ...}
{"ts": "2026-09-19T15:04:03Z", "event": "summarize", "ticket_id": "T-1004", "triage": {...}}
{"ts": "2026-09-19T15:04:05Z", "event": "draft", "ticket_id": "T-1004", "draft": "..."}
{"ts": "2026-09-19T15:04:12Z", "event": "human_gate", "approved": true, "decided_by": "human:approve"}
{"ts": "2026-09-19T15:04:12Z", "event": "send_email", "to": "BlueTree Realty", "result": {"ok": true, "delivered": false}}
```

## Deliverable

A runnable `email_assistant.py` that, for a chosen ticket:

1. produces a structured triage summary,
2. drafts a reply grounded only in the help center (and escalates when it can't ground),
3. requires human approval before the `dangerous` send step,
4. "sends" only on approval, appending to `outbox.jsonl` (never really emailing), and
5. writes a complete `audit_log.jsonl` for the run — including rejected runs.

Bonus: show one approved run and one rejected run, and prove from `outbox.jsonl` that the
rejected one never queued.

## Troubleshooting

- **`OPENAI_API_KEY not set`.** Copy `labs/.env.example` to `labs/.env` and add your key.
- **`FileNotFoundError` on tickets/help center.** Run from inside the lab folder; the paths
  resolve to `../assets/` from the script location.
- **The prompt hangs in CI or a non-TTY.** Use `--auto-approve` / `--auto-reject` for
  non-interactive runs; keep the interactive gate for real use.
- **The draft invents a refund amount or a date.** Tighten the grounding instruction and remind
  it to escalate when the help center doesn't cover the ask. Grounding beats cleverness.
- **The sensitive ticket gets answered.** Confirm `sensitive` is detected in triage and that
  the draft prompt says to escalate; re-run `T-1002`.
- **Something appears in `outbox.jsonl` after a reject.** That's a bug — `send_email` must be
  called only inside the `if approved:` branch. Check the orchestration order.

## Teacher's Playbook

**Three-beat reference answers (Steps 3, 7, 8).**
- **🔮 Predict (§3):** `T-1002` triages to roughly `{"category":"policy_compliance","priority":
  "normal","sensitive":true,"multiple_asks":false}` and the draft **escalates** (patient records need
  a BAA/DPA) rather than answering.
- **🛠️ Your turn (§7):** the GDPR-deletion `--text` ticket should come back **sensitive:true**
  (legal/PII), `category:policy_compliance`, and **escalate** — the help center can't ground a legal
  deletion deadline. The refund-window ticket should be **sensitive:false**, `category:billing`,
  **answerable** from `help_center.md` (the 30-day window). A good "looks safe but should escalate"
  case hides PII (a name + account/SSN), makes a legal/compliance ask, or stacks two asks
  (`multiple_asks:true`). What good looks like: the student **wrote the triage down first**, then
  explains any gap between their prediction and the model's triage — that gap *is* the lesson about
  where triage is reliable.
- **🗣️ Explain (§8):** triage-first gives the gate **structured, reviewable context** — the approver
  sees `sensitive`/`priority`/`category` at a glance and can judge in seconds, and the
  escalate-vs-answer decision is driven by triage *fields*, not buried in prose. Separation of
  concerns: summarize **classifies**, draft **grounds**, the gate **decides** — each step auditable on
  its own.

**Worked answer / what good looks like.** A complete submission shows the send step is
*structurally* unreachable without approval (not just discouraged by a prompt), grounds drafts
in the help center, escalates the patient-records ticket, and produces an audit log that would
let someone reconstruct exactly who approved what and when. The strongest students note that
the audit log records *rejections* too — governance is about the decisions not taken as much as
those taken.

**Live-demo script (7–9 min).**
1. Run `python email_assistant.py --ticket T-1004`. Approve it. "The model drafted; *I*
   authorized. That keystroke is the human-in-the-loop."
2. Re-run the same ticket and **reject** it. `cat outbox.jsonl` — the rejected one isn't there.
   "The gate isn't advisory. Reject means nothing leaves."
3. Run `--ticket T-1002` (patient records). Show it escalates. "Grounding + a compliance rule.
   It won't answer what the help center says needs a human and a BAA."
4. `cat audit_log.jsonl`. "Every step, every decision, timestamped. This is what an auditor or
   an incident review reads — not the chat."
5. Point at `send_email`: "It writes to a file. In production it's a mail API. The *shape* — a
   dangerous tool behind a gate with an audit trail — is identical."

**Common mistakes + fixes.**
- *Calling `send_email` before the gate returns* -> messages leak on reject. Fix: send only
  inside `if approved:`.
- *Grounding by hope, not instruction* -> invented policy. Fix: "use ONLY the help center;
  escalate otherwise," and test `T-1002`.
- *No audit entry for rejects* -> you can't prove the near-miss was caught. Fix: log
  `send_skipped`.
- *Auto-approve left on in "production"* -> the gate is bypassed. Fix: `--auto-approve` is a
  demo/CI flag only; the default is interactive.
- *Dumping the whole help center as the "reply"* -> treat it as a source to draft from, not
  content to paste.

**Debrief Q&A.**
- *Q: Why a stub instead of a real send?* A: You get the whole governed workflow with zero risk
  of emailing a real customer from a classroom. Swap the stub for a mail API in production; the
  gate and audit log don't change.
- *Q: Is the prompt "draft only" enough to make it safe?* A: No — prompts are guidance, not
  guarantees. Safety comes from the *code*: `send_email` is only reachable past the gate. Class
  it `dangerous` and enforce it structurally.
- *Q: What belongs in the audit log?* A: Enough to reconstruct the run: inputs, the triage, the
  draft, who decided, and the result — including skips and rejects.
- *Q: How does this connect to Lab 4?* A: Same tool discipline (schema, safety class), now with
  the `dangerous` branch turned on and wired to a real human gate.
- *Q: Where could this still go wrong?* A: Automation bias — a human clicking "approve" without
  reading. Design the gate so skipping the review is a deliberate act, and spot-check the log.

---
