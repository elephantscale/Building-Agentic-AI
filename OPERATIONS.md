# Project Operations

**Last updated:** 2026-10-02
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

- Client outline sourced from **ProTech** (reseller). **Booked via ProTech; contact: Mathew Caccavale.** End client *behind* ProTech — **Needs CEO input** (confirm audience/level and lab-environment constraints — cf. the NNL ProTech engagement, where a restricted/secure network can break cloud-dependent labs).

## Upcoming deadlines

- **First delivery: 2026-10-19 → 10-23** (5-day), via ProTech (Mathew Caccavale). ~2.5-week prep runway from 2026-10-02.

## Important TODOs

- Optional dry-run of each lab's starter code in the class VM with real API keys.
- Add slide images to `images/` where decks would benefit (currently text-first).

## Blockers and dependencies

- Cloud labs depend on class-provided accounts (OpenAI, Anthropic, Tavily, AWS, Databricks,
  Zapier, Google ADK); mitigated by local fallbacks in every cloud lab.

## Risks

- Framework APIs (LangGraph, DSPy, ADK, Bedrock) move fast; lab code may need version pinning
  and a pre-delivery smoke test.

## Decisions needed from Mark

- Confirm delivery customer and date.
- Confirm which cloud accounts will be available in the class VM (drives cloud-vs-fallback
  emphasis).

## Next three highest-value actions

1. Review + smoke-test the six framework labs against pinned library versions.
2. Confirm delivery logistics (customer, date, available cloud accounts).
3. Add slide imagery and build PPTX (Mark, on Mac).
