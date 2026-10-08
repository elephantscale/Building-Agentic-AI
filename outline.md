# Building Agentic AI

*Elephant Scale — instructor-led, 5 days, ~50% lecture / 50% hands-on labs.*

## Course Summary

### Description

This instructor-led program guides developers, data scientists, team leads, and project
managers through designing, deploying, and governing AI agents that autonomously plan, reason,
reflect, and execute tasks. The course combines roughly 50% lecture and 50% hands-on labs in a
cloud-based, zero-install environment.

### Objectives

After taking this course, students will be able to:

- Understand the design principles of Agentic AI systems.
- Build, evaluate, and govern autonomous AI agents.
- Integrate agentic frameworks (LangGraph, LlamaIndex, Bedrock, DSPy, Claude).
- Implement multi-agent collaboration and reflection mechanisms.
- Optimize deployments for latency, cost, and evaluation metrics.

### Topics

- Foundations of Agentic AI
- Reflection, Tools, and Evaluation
- Advanced Agentic Patterns
- Frameworks, Deployment & Governance
- Final Capstone Project

### Audience

Developers, data scientists, team leads, and project managers.

### Prerequisites

- Basic understanding of machine learning concepts.
- Familiarity with Python (preferred).
- Knowledge of API calls and JSON.

### Duration

Five days.

## Course Outline

### I. Foundations of Agentic AI

- What is Agentic AI?
- From prompt-based AI to autonomous agents.
- OpenAI's agentic guidelines and best practices.
- When and why to use Agentic AI.
- Design principles: autonomy, reasoning, reflection, planning, safety.
- Customer-support / research-assistant agentic system.
- **Lab 1:** Lab environment setup and first "agent loop" using OpenAI & the ReAct pattern.
- Agentic AI workflow: Input -> Plan -> Act -> Reflect -> Output.
- Single- vs. multi-step reasoning and tool/memory usage.
- **Lab 2:** Build a Research Assistant agent with multi-step reasoning and logging.

### II. Reflection, Tools, and Evaluation

- Reflection and self-evaluation patterns.
- Improving factuality/style; generating charts/reports reflectively.
- **Lab 3:** Build and compare direct vs. reflective summarization agent workflows.
- Tools in Agentic AI: function calling, schema validation, structured responses.
- Example tools: email, CRM query, code execution.
- **Lab 4:** Convert Python functions to agentic tools.
- **Lab 5:** Create and test an "Email Assistant Workflow" (draft, summarize, send emails).
- Explore the MCP protocol / code execution inside agents.
- **Retrieval-Augmented Generation (RAG) and vector databases** — embeddings, chunking,
  similarity search, grounding and citation; retrieval as an agent tool. (Major ideas taught at
  the whiteboard; the lab makes them concrete.)
- **Lab 6:** Build a RAG pipeline over a local vector store — chunk, embed, retrieve, and ground
  answers with citations (runs fully offline; optional hosted embeddings).

### III. Advanced Agentic Patterns

- Evaluation metrics, error analysis, debugging (tool errors, plan drift, hallucination).
- Workflow optimization and next-step prioritization.
- **Lab 7:** Evaluate and benchmark agentic workflows.
- Multi-agent conversation flows and sequential chatbots.
- Planning-driven agents for onboarding / blog-post generation.
- **Lab 8:** Build an onboarding assistant agent (meeting scheduler, email generator, welcome
  messaging).

### IV. Frameworks, Deployment & Governance

- **LangGraph & Tavily integration** — LangGraph architecture (nodes/edges/state); agentic
  search via Tavily; persistence, streaming, human-in-the-loop feedback.
- **Lab 9:** Build an Essay Writer agent with retrieval + reflection on LangGraph.
- **Low-code agentic design.**
- **Lab 10:** Create business automation agents: ChatGPT + Zapier, Custom GPTs (memory,
  chaining, and reflection in Zapier).
- **Lab 11:** Build a no-code AI CRM agent with Zapier + Custom GPT.
- **Agentic on AWS Bedrock** — Bedrock APIs, CRM/database connection, latency/scalability
  patterns; guardrails, transactions, compliance.
- **Lab 12:** Build a CRM assistant via Bedrock Agent Runtime & a Titan/Nova model.
- **Agentic with DSPy and Databricks** — declarative agent design, self-improving loops,
  Databricks enterprise integration.
- **Lab 13:** Create a self-improving agent with DSPy; integrate Delta Table analytics.
- **Agentic with Claude** — multi-tool coding assistants using Anthropic's Claude; memory /
  context management.
- **Lab 14:** Build a Claude-based coding assistant with persistent memory.
- **Voice Agents with Google's ADK** — Agent Development Kit for speech input/output, context
  continuity.
- **Lab 15:** Build a live Voice Support Agent (ADK + OpenAI).
- **Governance with Databricks** — tracking agent actions, data lineage, audit logs, HR
  analytics.
- **Lab 16:** Build an HR Governance Agent that audits agent activity logs.

### V. Final Capstone Project

- **Enterprise AI Agent Challenge** — teams design and demo a multi-agent system (domain:
  Finance, HR, Real Estate, or Customer Support), showcasing agent reasoning, tool use,
  reflection, evaluation, and governance.

## Five-Day Map

| Day | Focus | Modules | Labs |
|-----|-------|---------|------|
| 1 | Foundations of Agentic AI | 01 | 1, 2 |
| 2 | Reflection, Tools, RAG & Vector DBs | 02, 03, 04 | 3, 4, 5, 6 |
| 3 | Advanced Agentic Patterns | 05, 06 | 7, 8 |
| 4 | Frameworks & Deployment | 07, 08, 09, 10, 11 | 9, 10, 11, 12, 13, 14 |
| 5 | Voice, Governance & Capstone | 12, 13, 14 | 15, 16, Capstone |
