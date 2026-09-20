# Agent Safety Checklist

Run through this before an agent touches any real system. Used in Labs 5, 11, 15, and required
for the Capstone demo.

## Permissions

- [ ] **Least privilege** — the agent has only the tools it needs, with the narrowest scopes.
- [ ] Credentials are per-agent and revocable, never a human's personal admin token.
- [ ] Read-only first: the first connected version can observe and draft, not change the world.

## Dangerous actions

- [ ] Every `send / publish / delete / buy / pay / change-record` action is classed `dangerous`.
- [ ] Dangerous actions require **explicit human approval** (a gate, not a log-after-the-fact).
- [ ] Irreversible actions have a confirmation step and are reversible where possible.

## Inputs & injection

- [ ] Tool output and retrieved/pasted text are treated as **data, not instructions**.
- [ ] System prompt separates trusted instructions from untrusted content.
- [ ] Prompt-injection test cases are in the eval set (Lab 6).

## Limits

- [ ] Loop cap (max steps), token/cost cap, and wall-clock timeout are enforced in code.
- [ ] The agent has a defined **fallback** when a tool fails or it is unsure (ask a human).

## Observability

- [ ] Every plan, tool call (name + args), tool result, and final output is logged.
- [ ] Logs are tamper-evident and retained per policy (see `audit-log-schema.md`).
- [ ] An owner is named to review failures and audit logs.

## Sign-off

- Reviewer: __________  Date: ________  Verdict: `ready` / `read-only only` / `not ready`
