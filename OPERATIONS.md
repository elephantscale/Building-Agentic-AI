# Project Operations

**Last updated:** 2026-10-06
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

## Recent accomplishments

- 2026-09-18: Full initial build of slides + labs across all five days (foundations;
  reflection/tools/eval; advanced patterns; frameworks — LangGraph, low-code, Bedrock, DSPy,
  Claude; voice/governance/capstone). Every cloud lab ships a local fallback.

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

- **Reply to Celia (ProTech)** with the setup spec, and ask: (1) is the network restricted / is public LLM + GitHub access available, (2) who provides API keys/accounts. *Draft ready (2026-10-06), not yet sent.*
- **Ask John (BofA) and the Fluor/Dani side** what AI-usage limitations apply (allowed providers/models, data-handling rules, network/API access) — before finalizing which models the labs default to. **High likelihood of bank restrictions.** *Draft ready (2026-10-06), not yet sent; states Claude as the default lab model.*
- Both email drafts live in a Claude Doc: https://claude.ai/code/artifact/d121dfee-b406-430c-8a81-25a84ede1493
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
