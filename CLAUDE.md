# Working on this course with Claude

This is the **Building Agentic AI** course (Elephant Scale) — a 5-day, hands-on, developer-
level course on designing, building, evaluating, and governing autonomous AI agents. This file
orients a Claude session started in this directory.

## What's here

- `outline.md` — the course outline (converted from the client Word/PDF doc).
- `slides/NN-name.md` — one Markdown deck per module (00-about + modules 01–13). **The Markdown
  is the source of truth.**
- `labs/NN-Name/README.md` — one lab per topic (16 labs incl. capstone), each with starter
  code where technical and a `## Teacher's Playbook`.
- `labs/assets/` — shared sample data used across labs.
- `course-materials/` — reusable templates (agent design canvas, evaluation rubric, tool spec,
  governance/audit templates, capstone rubric).
- `scripts/validate-course.sh`, `labs/test-all-labs.sh`, `labs/verify-setup.sh` — structure
  checks (keep them green).

## House style (match it)

- **Terse presenter-skeleton slides:** prose collapsed into bullet / nested-bullet skeletons
  the instructor narrates. Keep slide titles, `---` separators, and `>` blockquotes (they
  double as the visual beat / key takeaway per slide). Keep all worked-example / code / JSON /
  ASCII diagram blocks verbatim. Every content deck opens with a title slide (`# Title` +
  `Elephant Scale`) and ends with a "Lab NN" hand-off slide.
- **Provider-honest, not provider-lock:** this course deliberately spans frameworks (OpenAI,
  LangGraph, Zapier, Bedrock, DSPy/Databricks, Claude, Google ADK). Use each framework's real,
  current idioms in its own module. Where a concept is framework-neutral, say so.
- **Current model IDs:** Anthropic — Opus `claude-opus-5`, Sonnet `claude-sonnet-5`, Haiku
  `claude-haiku-4-5-20251001`. OpenAI — use `gpt-4.1` / `gpt-4o` family. Don't invent IDs.
- **Labs:** copy-ready code and prompts AT POINT OF USE. State what to install, how to run,
  what a correct run looks like, and how to record results. Each technical lab ships a
  `requirements.txt` and runnable starter files. Cloud labs (Bedrock, Databricks, Zapier, ADK)
  MUST include a **local-only fallback** so the lab is never blocked. Each lab ends with a rich
  `## Teacher's Playbook` (worked model answer + realistic output, live-demo script, common
  mistakes + fixes, debrief Q&A, "what good looks like").

## Naming conventions (keep filenames stable)

- Decks: `slides/NN-topic.md`, `NN` two digits, listed in `slides/slide-list.txt`.
- Labs: `labs/NN-Topic-Name/README.md`, `NN` two digits matching the course flow in README.

## Build & workflow

- **Never regenerate the PPTX decks — Mark builds them himself.** `slides/gen.sh` refreshes
  `slides/slide-list.txt` and, only when `ES_HOME` is set, assembles PPTX as a side effect —
  don't run it to build decks. To refresh the manifest without assembling:
  `ls slides/[0-9][0-9]-*.md | sed 's#slides/##' | sort > slides/slide-list.txt`.
- Add a slide image: put the file in `images/` and reference it as
  `<img src="../images/foo.png" style="width:60%;"/>`. Keep md image tags to `src` + `width`;
  final layout lives in the PPTX.
- After structural changes, run `./scripts/validate-course.sh`, `./labs/test-all-labs.sh`, and
  `./labs/verify-setup.sh`. Keep them green.

## Provenance

- Built from the client outline `Building Agentic AI` (ProTech). House style borrowed from the
  sibling Elephant Scale courses `ai-automation-essentials` and `Building-AI-Applications` in
  `/media/mark/data1/ES/`.
