# %% [markdown]
# # Lab 7 — Evaluation harness, step by step (VSCode Interactive)
#
# Run each cell with **Shift+Enter** to watch one case flow through the agent and the
# scorer, then run the full base-vs-reflection benchmark. Runs **offline**
# (deterministic) with no key; set `OPENAI_API_KEY` for real model + LLM-judge scoring.
#
# Same code as `run_eval.py`, driven cell-by-cell. CLI version: `python run_eval.py`.
#
# *Needs the VSCode Python + Jupyter extensions. Open this file and click "Run Cell".*

# %%
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__)) if "__file__" in dir() else os.getcwd()
sys.path.insert(0, HERE)

from agent_under_test import ToolAgent, OFFLINE  # noqa: E402
from run_eval import (  # noqa: E402
    load_cases, deterministic, score_case, run_variant, summarize,
)
print("mode:", "OFFLINE (deterministic)" if OFFLINE else "LLM (gpt-4o-mini)")

# %% [markdown]
# ## 1. The frozen eval set — inspect one case

# %%
cases = load_cases()
print(f"{len(cases)} frozen cases. Families:", sorted({c['family'] for c in cases}))
cases[0]

# %% [markdown]
# ## 2. Run ONE case through the base agent — see the full trace

# %%
agent = ToolAgent(use_reflection=False)
result = agent.run(cases[0]["input"])
print("answer    :", result["answer"])
print("tool_calls:", [c["tool"] for c in result["tool_calls"]], "| steps:", result["steps"])

# %% [markdown]
# ## 3. Score that case — deterministic checks first, then combined dimensions
#
# Deterministic ground truth (substring / tool / refusal assertions) always caps the
# LLM judge, so a confident-but-wrong answer can't score well.

# %%
dims, assertions, passed = deterministic(cases[0], result)
print("assertions:", assertions, "| passed:", passed)
score_case(cases[0], result)

# %% [markdown]
# ## 4. Benchmark both variants over the whole set

# %%
base_rows = run_variant(ToolAgent(use_reflection=False), cases)
refl_rows = run_variant(ToolAgent(use_reflection=True), cases)
print("BASE   ", summarize(base_rows))
print("REFLECT", summarize(refl_rows))

# %% [markdown]
# ## 5. Find where reflection actually changed the outcome

# %%
by_id = {r["id"]: r for r in base_rows}
for r in refl_rows:
    b = by_id[r["id"]]
    if r["total"] != b["total"]:
        print(f"{r['id']:<12} base={b['total']:>2} -> reflect={r['total']:>2}  ({r['family']})")
