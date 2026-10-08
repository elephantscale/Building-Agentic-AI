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
- **Confirm the end client's lab environment with ProTech** (public-LLM + GitHub access, shared repo vs. ship-ahead) *before* finalizing labs — cloud-dependent agentic labs won't run in a restricted environment.

## Customers and revenue connections

- **ProTech** (reseller). Contacts: **Philip A. Anderson Jr. — CEO** (panderson@protechtraining.com); **Mathew Caccavale**; **Celia Woronowicz** (logistics/setup).
- **End client (confirmed): Bank of America — 12 students** (ProTech contact **John**, cc'd) **+ Fluor — 2 students** (prior ES client, trained for **Dani**). **14 total.**
- Philip confirmed (2026-10-05) the engagement is on and **Mark is teaching**.
- **AI-usage limitations are the open question — and BofA is a highly regulated bank**, so expect strict rules on which providers/models and what data may touch a hosted model. Ask **John (BofA)** and the **Fluor/Dani** side what AI is permitted — this drives default model choices and whether cloud labs run live or fall back to local. cf. the NNL ProTech engagement, where a restricted/secure network broke cloud-dependent labs.

## Upcoming deadlines

- **First delivery: 2026-10-19 → 10-23** (5-day), via ProTech (Mathew Caccavale). ~2.5-week prep runway from 2026-10-02.

## Important TODOs

- **Awaiting Celia (ProTech)** reply re: setup — is the network restricted / public LLM + GitHub access available, and who provides API keys/accounts. *Sent 2026-10-07.*
- **Awaiting John (BofA) / Fluor-Dani side** reply re: AI-usage limitations (allowed providers/models, data-handling rules, network/API access) — gates which models the labs default to. **High likelihood of bank restrictions.** *Sent 2026-10-07; stated Claude as the default lab model.*
- Email drafts archived in a Claude Doc: https://claude.ai/code/artifact/d121dfee-b406-430c-8a81-25a84ede1493
- ~~Fix Lab 11/12 (Bedrock/DSPy) fallbacks~~ **DONE 2026-10-08** (now Lab 12/13 after renumber):
  Bedrock CRM gained a true offline deterministic stub (runs with no key/network); DSPy now exits
  cleanly with a "needs an LLM key" message (it has no LLM-free mode — prompt optimization needs a
  model). Both verified keyless.
- **Freeze a dependency lockfile** (`pip freeze` of the known-good set) before delivery — all
  pins are unbounded `>=` and the class VM floated to newest majors (openai 2.x, langchain 1.x,
  dspy 3.4, pandas 3.0). Validate DSPy Lab end-to-end on 3.x or pin to 2.6.x.
- Optional dry-run of each lab's starter code in the class VM with real API keys.
- Add slide images to `images/` where decks would benefit (currently text-first).

## Blockers and dependencies

- Cloud labs depend on class-provided accounts (OpenAI, Anthropic, Tavily, AWS, Databricks,
  Zapier, Google ADK); mitigated by local fallbacks in every cloud lab.
- **Repo is private.** Will be opened (made accessible to students) for the delivery window
  **2026-10-19 → 10-23**. Re-privatize or decide access policy after delivery.

## Risks

- Framework APIs (LangGraph, DSPy, ADK, Bedrock) move fast; lab code may need version pinning
  and a pre-delivery smoke test.
- **Bank-of-America restrictions (elevated).** As a major bank, BofA likely restricts public
  LLM API access, external GitHub, and what data may touch hosted models. If so, cloud labs
  must run in local-fallback mode and model defaults may need to change. Confirm before
  delivery; our local fallbacks are the mitigation but need a smoke test in that mode.

## Decisions needed from Mark

- Confirm delivery customer and date.
- Confirm which cloud accounts will be available in the class VM (drives cloud-vs-fallback
  emphasis).

## Next three highest-value actions

1. Review + smoke-test the six framework labs against pinned library versions.
2. Confirm delivery logistics (customer, date, available cloud accounts).
3. Add slide imagery and build PPTX (Mark, on Mac).
