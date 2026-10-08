# Project Operations

**Last updated:** 2026-10-08
**Owner:** Mark Kerzner
**Status:** Green

## Purpose and business value

Elephant Scale instructor-led course **Building Agentic AI** — a 5-day, developer-level,
hands-on course (~50% labs) on designing, building, evaluating, and governing autonomous AI
agents. Built to a client outline (ProTech, "Building Agentic AI"). Revenue: paid instructor-
led delivery; extends the ES agentic/AI-applications catalog.

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
  frozen lockfile (six-month-lag). Residual: Lab 13 DSPy *lift* still unverified on 3.x without a key.
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
