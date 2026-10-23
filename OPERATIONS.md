# Project Operations

**Last updated:** 2026-10-22
**Owner:** Mark Kerzner
**Status:** Green

## Purpose and business value

Elephant Scale instructor-led course **Building Agentic AI** — a 5-day, developer-level,
hands-on course (~50% labs) on designing, building, evaluating, and governing autonomous AI
agents. Built to a client outline (ProTech, "Building Agentic AI"). Revenue: paid instructor-
led delivery; extends the ES agentic/AI-applications catalog.

## Delivery in progress (first delivery, 2026-10-19 → 10-23)

- **Day 1 (10-19) and Day 2 (10-20) delivered; both ran fine** (Mark's assessment). Teaching
  from Ubuntu with a bigger screen + keyboard, switching to the Mac in Zoom for live segments.
- Day 2 included an **unplanned live segment not in any deck**: AI APIs across the three
  providers, local models, and open-weight models. Taught from the Mac, no slides.
- **Consequence: RAG (module 04 + Lab 06) slipped to Day 3 morning (10-21)** and now opens the
  day, whiteboard-led. Decision (Mark, 2026-10-20): **do not deepen deck 04** to compensate —
  the thin deck is correct; instructor-side whiteboard notes carry the depth.
- Mid-delivery fixes committed from real classroom experience: Lab 01 (VM-student skip banner,
  stranded `cd`), Lab 03 (Playbook rewritten to match actual critic behavior, explore §6b, demo
  meters), Lab 06 (citation line in the expected run).
- Day 3 material verified offline on the Ubuntu box 2026-10-20: **Lab 07** reproduces its
  README table exactly (base 7/8 → reflect 8/8 on `ambiguous-01`); **Lab 08** clean on all four
  paths (gate denied, `--approve`, role switch, `a2a_peer.py`); **Lab 06** matches its expected
  scores. New: `course-materials/whiteboard-rag.md`.
- ~~Lab 08 has no explore notebook~~ **DONE 2026-10-20.** Labs **08 and 09** now ship
  `explore.py` + executed `explore.ipynb` (students reportedly took well to the notebooks), so all
  four Day-3 labs have one. Companion labs are now 03, 06, 07, 08, 09, 13.
- **Day 4 verified keyed 2026-10-20** on the course lockfile: Lab 10 (Zapier sim), 11 (NoCode CRM),
  12 (Bedrock `CRM_BACKEND=LOCAL`), 14 (Claude `claude-sonnet-5` — the dangerous-write gate fires
  and degrades gracefully) all run. **Lab 13 DSPy lift confirmed on dspy 3.1.3: 80% -> 100%
  (+20 pts)** — this closes the risk item open since 2026-10-08.
- Mid-delivery defects found by actually running the labs (all fixed + pushed 2026-10-20):
  **Lab 07** reflection pass received no tool observations, so the critic stripped correct answers
  and reflection scored *below* base on the keyed path; refusal rule also lost to the NO_RECORD
  rule (`gpt-4o-mini` can't follow it, `gpt-4.1` can — `LAB7_MODEL` now overrides).
  **Lab 09** rich parsed model text as markup and silently deleted `[source.txt]` citations.
  **Lab 06** `rag.py` never called `load_dotenv`, so `EMBEDDINGS=openai` / `RAG_GENERATE=1`
  were unreachable from `labs/.env` for every student.
  **Labs 06 + 12** shipped bash-only `NAME=value python ...` commands, which are a parse error in
  the VM's PowerShell.
- **Day 4 re-verified 2026-10-21** against the lockfile venv, every lab run from a scratch copy so
  the repo stayed clean: Lab 10 `zap_sim.py` offline, Lab 11 both offline and keyed, Lab 12
  `CRM_BACKEND=LOCAL` (gate fires, DENIED, graceful answer) including a cold start with no `crm.db`,
  Lab 13 keyed **80% -> 100% (+20 pts)** reproduced, and Lab 13's no-key path fails with a clear
  message rather than a traceback. Deck→lab mapping for Day 4 confirmed against each deck's own
  hand-off slide (07→09, 08→10, 08→11, 09→12, 10→13).
- Day 4 defects found and fixed 2026-10-21:
  **Lab 11** `rich` parsed the `[safe]` / `[dangerous]` tag as a style tag and deleted it, so the
  column the README promises printed blank — same bug class as Lab 09's citations (`markup=False`).
  **Lab 11, more serious:** the lab's central beat (a dangerous proposal REFUSED without `--force`)
  **does not fire on the keyed path at all** — `gpt-4.1` proposes `escalate` instead of
  `issue_refund` for T-1003/T-1004, so every row is `safe` and the gate is never exercised. The
  README claimed "a real key gives richer intents, same gating," which was wrong. Now documented:
  demo on the rule-based stub, and the keyed result is a Playbook lesson ("a gate you never saw
  refuse is a gate you have not tested").
  **Repo hygiene:** Lab 12 shipped `crm.db` and `run-log.jsonl` as *tracked* files that every run
  mutates (5 → 13 log lines on one run), so a student's first Lab 12 run would have blocked
  `git pull` on the class VM mid-class. Both untracked (they regenerate from `crm_seed.sql`), and
  `.gitignore` now covers the run artifacts of labs 02, 05, 07, 08, 11, 12, 13, 14, 15, 16 — which
  also means `git status` on the VM is now a real signal instead of lab noise.
- **Open Day 4 question (Mark's call, not a defect):** Labs **10, 11, 12 have no `explore.ipynb`**;
  only Lab 13 does. Students took well to the notebooks on Day 3. Not built unprompted — the
  Day-4 labs are CLI-driven by design (`crm_agent.py` subcommands, an approval gate), so a
  notebook is a bigger rewrite there than it was for 08/09.
- **Day 5 verified 2026-10-22** against the lockfile venv, every lab run from a scratch copy:
  **Lab 14** (Claude, keyed `claude-sonnet-5`) — session 1 fixes the bug through both gates to
  `ALL TESTS PASSED`, session 2 recalls it from `memory.json`, and the **denied** path leaves
  `mathutils.py` byte-identical while the agent prints the fix for manual application.
  **Lab 15** both paths, properly isolated: no-key deterministic responder *and* keyed `gpt-4.1`
  (they differ in wording only, as the README claims), gate denied on the refund and approved on
  the cancel, `VOICE_BACKEND=adk` falling back cleanly with `google-adk` absent.
  **Lab 16** 30 events / 4 runs -> **8 findings (2 critical)**, `--narrate` adds the reviewer
  summary. **Lab 17** scaffold runs offline, 11 events, gates honoured.
  Deck→lab mapping for Day 5 confirmed against each deck's hand-off slide (11→14, 12→15, 13→16,
  14→Capstone).
- **New Day 5 closing beat, verified end to end:** Lab 16's auditor reads any log in
  `audit-log-schema.md` form, so it audits the students' *own* output. Lab 15's `turn_log.jsonl`
  -> **0 findings** (clean); the capstone scaffold's `audit-log.jsonl` -> **0 critical but 4
  `pii_in_log`** (it writes email addresses into the log payload). A clean gate record is not a
  clean log. Added as Lab 16 step 8 and as the way to *prove* the capstone's governance box.
- Day 5 defects found and fixed 2026-10-22:
  **Capstone scaffold's closing line pointed at `labs/16-Capstone/README.md`** — a directory that
  does not exist (RAG-renumber leftover). Every student hits that dead path on the last day.
  **`requirements.txt` headers off by one** in labs 12-16 (`Lab 11` on lab 12, ... `Lab 15` on
  lab 16) — comment-only, but it is the first line a student reads in the file.
  **Lab 15 README shipped a bash-only `VOICE_BACKEND=adk python ...`** — a parse error in the
  VM's PowerShell, the same class as the Labs 06/12 fix on Day 4. Both shell forms now given.
  **Expected-output drift:** Lab 15's "correct run" block predated the current gate string and
  was silently the *no-key* wording (students with a key in `labs/.env` see `gpt-4.1` phrasing);
  Lab 16's "Top findings" omitted one of the five printed rows and showed column padding the
  script does not emit. Both synced verbatim to real runs and the key/no-key difference called out.
  **Repo hygiene:** `.gitignore` was missing `compliance_report.md` (Lab 16) and the capstone's
  `audit-log.jsonl`, both rewritten on every run.
- **Capstone recast as a DESIGN REVIEW (Mark's decision, 2026-10-22).** Teams no longer build;
  they fill the Agent Design Canvas, draw **one picture** carrying all six capabilities, swap
  designs with another team at 14:15 to find three holes each, and defend the design for ten
  minutes. Rationale: in their jobs the design review *is* the first deliverable, and a half-built
  demo teaches less than a design they can defend. `labs/17-Capstone/README.md` rewritten,
  `starter/` demoted to reference reading ("read it, don't write it"), and `slides/14-capstone.md`
  rewritten to match: 14 slides -> 16, adding **Deliverable 2 — The Picture** and **The Pressure
  Test (14:15)**; Demo Format -> The Presentation, Deliverables off "runnable code", 5 grading
  rows reworded. `check-slides.sh 14` OK. **The PPTX still needs Mark's rebuild.**
  Picture medium: text, so it lives inside the canvas — ASCII, or Mermaid at mermaid.live.
  **Unverified: whether mermaid.live is reachable from the class VM** — ASCII is the fallback.
- **Day 5 defect found live on the VM, fixed 2026-10-22:** Lab 14's Session-1 command used a bash
  line continuation (`\`), which PowerShell treats as the *argument* — the agent received the task
  `"\"`, answered politely, and the quoted task line was then echoed as its own command. Third
  bash-only line to reach the VM this week (after Labs 06/12 and Lab 15). Now one line, labelled
  `powershell`. A repo-wide sweep found no others. **Post-delivery TODO: a PowerShell-syntax pass
  over every lab README** — running the labs from bash on Ubuntu does not exercise what students type.
- **Lab 14 reset is now at point of use** (step 2, not buried in step 7):
  `git checkout workspace/; del memory.json -ErrorAction Ignore`. The `git checkout` is the required
  half; deleting `memory.json` only decides whether the agent rediscovers the bug or recalls it.
- **Lab 16 step 8 rewritten around a real finding (verified 2026-10-22).** The auditor reads any
  JSONL log, so it now audits the students' own week. **Lab 08** (Day 3, offline) -> 10 events,
  **2 findings**, both `pii_in_log`. **Lab 12** (Day 4) -> 11 events, **0 findings — and that zero
  is false.** Lab 12 writes the right event names and even a `safety_class`, but **flat**: no
  `step`, no `actor`, and `tool`/`safety_class` at top level instead of nested in `detail`. Every
  policy check reads `detail`, finds nothing, reports nothing. *"Lab 12 passed the audit because it
  does not record enough to fail it."* Contrast with Lab 15's log — also 0 findings, genuinely clean.
  **Real defect, deliberately NOT fixed mid-delivery:** Lab 12's README lists `audit-log-schema.md`
  under Tools while its log does not follow it. **Post-delivery TODO:** nest Lab 12's fields *and*
  keep a deliberately non-conformant sample log, because this is the strongest governance beat on Day 5.
- **Anonymous end-of-course feedback form added** (`course-materials/create-feedback-form.gs`, same
  Apps Script pattern as the intro form, `setCollectEmail(false)` for the locked-down VMs).
  **Share it right after Lab 14 on Day 5 morning, not at 16:30** (Mark's call): Day 5 runs past
  16:00 and Zoom attendance collapses after the last capstone presentation, whereas after Lab 14 the
  room is full and has just watched an agent be refused at a gate. Cost: it cannot ask about the
  capstone — ask that out loud at the end instead. **ProTech's own evaluation does not reach Mark**,
  so this is the only cohort feedback he will see. Nine questions; three are decision-grade:
  why the least-useful lab was least useful, notebooks vs scripts (6 of 16 labs ship a notebook),
  and whiteboard/live segments vs slides (tests a bet he has run on all week).
- **Lab 14 behaviour worth knowing live:** in 3 keyed runs of the Step-2 task, 2 reproduced the
  failing test before editing and **1 went straight from reading to `write_file`**. The README's
  §8 question and the Playbook's "editing before reproducing" mistake are about exactly this, so
  the skip is a teaching moment, not a defect — now noted in the Playbook.
- Still carried: labs 07/08 use `LAB6_OFFLINE` / `LAB7_OFFLINE` env-var names left over from the
  RAG renumber (internally consistent, just off-by-one against the lab number).

## Current status

- Course repo built out from the client outline: README, outline, CLAUDE.md, 14 slide decks
  (00-about + 13 modules), 16 labs (15 + capstone), course-materials templates, setup and
  validation scripts.
- House style borrowed from sibling ES courses `ai-automation-essentials` and
  `Building-AI-Applications`.

## Course positioning (decision, 2026-10-07)

- **Teach durable agentic fundamentals, not specific targeted tools.** This is the client's
  first agentic AI course; the goal is a solid conceptual foundation they can expand later.
  Frameworks/tools appear as illustrations of transferable concepts, not as the subject.
- Implication: do **not** chase tool-specific coverage seen in competitor curricula (e.g.
  Edureka's CrewAI, LangSmith, N8N, GraphRAG, guardrails-library modules). Keep the course
  concept-first and provider-honest.

## Recent accomplishments

- 2026-09-18: Full initial build of slides + labs across all five days (foundations;
  reflection/tools/eval; advanced patterns; frameworks — LangGraph, low-code, Bedrock, DSPy,
  Claude; voice/governance/capstone). Every cloud lab ships a local fallback.
- 2026-10-07: Keyless smoke test of all 16 labs in an isolated venv. `requirements-all.txt`
  installs clean, zero resolver conflicts. **8 labs run fully offline** (06, 07, 08, 09, 10,
  14, 15, 16). Found two real fallback bugs (Lab 11 Bedrock, Lab 12 DSPy — see Risks).
- 2026-10-07: Added a **Day-2 RAG & Vector DBs module** (thin deck 04 + new Lab 06, offline
  NumPy vector store with grounding/citations). Renumbered later decks/labs; validators green.
- 2026-10-07: Reviewed against Ng's DeepLearning.AI "Agentic AI" course + Edureka's cert.
  Conclusion: our spine maps 1:1 to Ng and is appropriately concept-first; **no slide/lab
  changes needed** — Mark delivers the extra framings (e.g. degrees-of-autonomy spectrum) live.
- 2026-10-08: Fixed the two keyless-crash labs from the smoke test (Bedrock → offline stub;
  DSPy → graceful needs-key exit). After the RAG renumber, **7 of 17 labs still require live
  LLM egress** (01-05, 13-DSPy, 14-Claude); the rest run fully offline. This is the key fact for
  the BofA network question.

## Current priorities

- Mark to review technical accuracy of framework labs (LangGraph, Bedrock, DSPy, ADK) against
  current library versions before first delivery.
- Mark builds the PPTX decks himself on the Mac (per house rules — Claude never builds PPTX).
- **Work through DeepLearning.AI's “Agentic AI” Coursera course (Ng)** to align/refresh before delivery.
- **Lab environment: requirements sent to ProTech (2026-10-07); proceeding on the assumption
  they'll provision** public-LLM + GitHub access + keys (see Working assumption). Not treated as
  a blocker.

## Customers and revenue connections

- **ProTech** (reseller). Contacts: **Philip A. Anderson Jr. — CEO** (panderson@protechtraining.com); **Mathew Caccavale**; **Celia Woronowicz** (logistics/setup).
- **End client (confirmed): Bank of America — 12 students** (ProTech contact **John**, cc'd) **+ Fluor — 2 students** (prior ES client, trained for **Dani**). **14 total.**
- Philip confirmed (2026-10-05) the engagement is on and **Mark is teaching**.
- **AI-usage / environment: requirements sent to John (BofA) and Celia (ProTech) 2026-10-07.**
  Per Mark, assume they'll provision per spec (public LLM + GitHub + keys), with Claude as the
  default model. Fallbacks remain as insurance. Will adjust only if they come back with a
  specific restriction. (Prior NNL ProTech engagement is the cautionary precedent.)

## Upcoming deadlines

- **First delivery: 2026-10-19 → 10-23** (5-day), via ProTech (Mathew Caccavale). ~2.5-week prep runway from 2026-10-02.

## Important TODOs

- **Celia (ProTech) + John (BofA): setup/AI-usage requests sent 2026-10-07.** Proceeding on the
  assumption they'll provision per spec (public LLM + GitHub + keys, Claude as default). Chase
  only if we hit the week without confirmation; adjust if they flag a restriction.
- Email drafts archived in a Claude Doc: https://claude.ai/code/artifact/d121dfee-b406-430c-8a81-25a84ede1493
- ~~Fix Lab 11/12 (Bedrock/DSPy) fallbacks~~ **DONE 2026-10-08** (now Lab 12/13 after renumber):
  Bedrock CRM gained a true offline deterministic stub (runs with no key/network); DSPy now exits
  cleanly with a "needs an LLM key" message (it has no LLM-free mode — prompt optimization needs a
  model). Both verified keyless.
- ~~Freeze a dependency lockfile before delivery~~ **DONE 2026-10-08.** `labs/requirements-lock.txt`
  (114 exact pins) + `requirements-lock.in` (editable target). Policy: **six-month-lag** — a
  coherent ~2026-04 snapshot (openai 2.31.0, anthropic 0.92.0, langchain/langgraph 1.x, dspy 3.1.3,
  numpy 2.4.4, pandas 3.0.2), seasoned and mutually compatible, deliberately avoiding the brand-new
  openai 3.x / anthropic 1.x majors. Smoke-tested on this exact set: all 16 labs import clean, Lab 06
  RAG + guard correct, Lab 12 keyless stub OK, Lab 13 keyless guard OK (dspy 3.x API surface intact),
  Lab 09 LangGraph imports resolve. SETUP.md points the class VM at the lock.
  **Still needs a keyed end-to-end dry-run** (esp. Lab 13 DSPy *lift* on 3.x) on the class VM — the
  offline smoke test here had no API keys.
- Optional dry-run of each lab's starter code in the class VM with real API keys.
- Add slide images to `images/` where decks would benefit (currently text-first).

## Blockers and dependencies

- Cloud labs depend on class-provided accounts (OpenAI, Anthropic, Tavily, AWS, Databricks,
  Zapier, Google ADK); mitigated by local fallbacks in every cloud lab.
- **Repo is private.** Will be opened (made accessible to students) for the delivery window
  **2026-10-19 → 10-23**. Re-privatize or decide access policy after delivery.

## Risks

- ~~Framework APIs move fast; lab code may need version pinning~~ **Mitigated 2026-10-08** by the
  frozen lockfile (six-month-lag). ~~Residual: Lab 13 DSPy lift unverified on 3.x~~ **Closed
  2026-10-20: verified keyed, 80% -> 100% (+20 pts) on dspy 3.1.3.**
- **Bank-of-America environment (now a managed assumption, not a blocker).** Per Mark, we assume
  ProTech/BofA will provision public LLM + GitHub access + keys as requested. Residual risk if
  they don't: 7 labs need live LLM egress (01-05, 13-DSPy, 14-Claude). Mitigation already in
  place — 10/17 labs run fully offline, and the fallbacks were smoke-tested keyless.

## Related initiatives

- **Recorded practice on sealearning.ca** (adjacent to this delivery). Mark + partner **Moshe
  Shamy** plan to record pieces of the course as self-paced practice content. Early-stage
  experiment; the offline, self-contained labs are the best candidates for short segments.

## Working assumption (set by Mark, 2026-10-08)

- **Assume John (BofA) and Celia (ProTech) will provision what we ask for** — public LLM API
  access (OpenAI/Anthropic), GitHub access, and class API keys. Plan the delivery on that
  assumption; do **not** design around a worst-case locked-down network. The local fallbacks
  stay as insurance, not the base plan. Requirements were sent to both on 2026-10-07.

## Decisions needed from Mark

- ~~Whether to freeze a dependency lockfile~~ **Decided 2026-10-08: yes, frozen (six-month-lag).**
- (Customer/date confirmed: BofA + Fluor, 2026-10-19 → 10-23.)

## Next three highest-value actions

1. **Keyed end-to-end dry-run on the class VM** from `requirements-lock.txt` — esp. Lab 13 DSPy
   lift on dspy 3.x (the one thing the keyless smoke test couldn't verify).
2. Keep Claude as the default lab model (assume it's approved); build PPTX decks (Mark, on Mac).
3. Add slide imagery where decks would benefit.
