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
| 3 | 04 | Evaluation, Error Analysis & Debugging | `labs/06-Evaluate-Benchmark` |
| 3 | 05 | Multi-Agent Systems & Planning | `labs/07-Onboarding-Assistant` |
| 4 | 06 | LangGraph & Tavily | `labs/08-LangGraph-Essay-Writer` |
| 4 | 07 | Low-Code Agentic Design | `labs/09-Zapier-CustomGPT`, `labs/10-NoCode-CRM-Agent` |
| 4 | 08 | Agentic on AWS Bedrock | `labs/11-Bedrock-CRM-Assistant` |
| 4 | 09 | DSPy & Databricks | `labs/12-DSPy-SelfImproving` |
| 4 | 10 | Agentic with Claude | `labs/13-Claude-Coding-Assistant` |
| 5 | 11 | Voice Agents with Google ADK | `labs/14-Voice-Support-Agent` |
| 5 | 12 | Governance with Databricks | `labs/15-HR-Governance-Agent` |
| 5 | 13 | Capstone: Enterprise AI Agent Challenge | `labs/16-Capstone` |

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
