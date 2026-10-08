# Building Agentic AI

*Design, build, evaluate, and govern autonomous AI agents.*

© Elephant Scale

## Course Description

A five-day, hands-on course for developers, data scientists, team leads, and project managers.
You learn how AI agents plan, reason, reflect, and act — starting from a hand-built agent loop
and the ReAct pattern, then adding tools, reflection, evaluation, and multi-agent coordination.
Across the week you build agents on the major frameworks in production use today — LangGraph,
low-code (Zapier + Custom GPTs), AWS Bedrock, DSPy + Databricks, Anthropic's Claude, and
Google's ADK for voice — and you close with governance and a team capstone. Roughly half the
time is lecture, half is labs, in a cloud-based, zero-install environment.

## Audience

Developers, data scientists, team leads, and project managers who want to build and ship
autonomous agents. Basic Python and comfort with API calls and JSON are assumed.

## Duration

5 Days / ~40 hours. Intermediate. Hands-on, lab-driven (~50% labs).

## Prerequisites

- Basic understanding of machine-learning concepts.
- Familiarity with Python (preferred).
- Knowledge of API calls and JSON.

## Repo Structure

| Path | Purpose |
|------|---------|
| `outline.md` | Full course description and module outline |
| `slides/` | Markdown slide decks, one per module |
| `labs/` | Lab guides, starter code, and setup docs |
| `course-materials/` | Reusable templates, rubrics, checklists |
| `scripts/` | Course validation helpers |
| `docs/` | Supporting source documents |
| `images/` | Slide images |

## Course Flow

| Day | Module | Topic | Lab Folder(s) |
|-----|--------|-------|---------------|
| 1 | 01 | Foundations of Agentic AI | `labs/01-Agent-Loop-Setup`, `labs/02-Research-Assistant` |
| 2 | 02 | Reflection & Self-Evaluation | `labs/03-Reflective-Summarization` |
| 2 | 03 | Tools, Structured Output & MCP | `labs/04-Python-Functions-to-Tools`, `labs/05-Email-Assistant` |
| 2 | 04 | RAG & Vector Databases | `labs/06-RAG-Vector-DB` |
| 3 | 05 | Evaluation, Error Analysis & Debugging | `labs/07-Evaluate-Benchmark` |
| 3 | 06 | Multi-Agent Systems & Planning | `labs/08-Onboarding-Assistant` |
| 4 | 07 | LangGraph & Tavily | `labs/09-LangGraph-Essay-Writer` |
| 4 | 08 | Low-Code Agentic Design | `labs/10-Zapier-CustomGPT`, `labs/11-NoCode-CRM-Agent` |
| 4 | 09 | Agentic on AWS Bedrock | `labs/12-Bedrock-CRM-Assistant` |
| 4 | 10 | DSPy & Databricks | `labs/13-DSPy-SelfImproving` |
| 4 | 11 | Agentic with Claude | `labs/14-Claude-Coding-Assistant` |
| 5 | 12 | Voice Agents with Google ADK | `labs/15-Voice-Support-Agent` |
| 5 | 13 | Governance with Databricks | `labs/16-HR-Governance-Agent` |
| 5 | 14 | Capstone: Enterprise AI Agent Challenge | `labs/17-Capstone` |

## Lab Environment

- Cloud-based, zero-install: a browser and the class VM.
- Python 3.11+ with the per-lab `requirements.txt`.
- API keys provided in class (OpenAI, Anthropic, Tavily) — see `labs/SETUP.md`.
- Cloud-console labs (AWS Bedrock, Databricks, Zapier, Google ADK) use instructor-provided
  accounts; each has a **local-only fallback** so no lab is blocked if a cloud account is
  unavailable.

## Validate the Repo

```sh
./scripts/validate-course.sh
./labs/test-all-labs.sh
./labs/verify-setup.sh
```
