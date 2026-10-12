# %% [markdown]
# # Lab 13 — DSPy self-improvement, step by step (VSCode Interactive)
#
# Run each cell with **Shift+Enter** to watch a DSPy program go from baseline to
# optimized one stage at a time: Signature → baseline score → BootstrapFewShot →
# optimized score → inspect the demos the optimizer taught itself.
#
# This lab optimizes a real LLM program, so it needs a key: `OPENAI_API_KEY`, or set
# `DSPY_MODEL=anthropic/claude-haiku-4-5-20251001`. There is no offline mode.
# Same code as `self_improving.py`. CLI version: `python self_improving.py`.
#
# *Needs the VSCode Python + Jupyter extensions. Open this file and click "Run Cell".*

# %%
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__)) if "__file__" in dir() else os.getcwd()
sys.path.insert(0, HERE)

import dspy  # noqa: E402
from self_improving import (  # noqa: E402
    ClassifyTicket, build_program, category_match, load_examples, evaluate,
    _has_llm_key, MODEL, HERE as LAB,
)

# %% [markdown]
# ## 1. The Signature — a contract (what), not a prompt (how)

# %%
print(ClassifyTicket.__doc__)
print("fields:", list(getattr(ClassifyTicket, "model_fields", {}) or getattr(ClassifyTicket, "fields", {})))

# %% [markdown]
# ## 2. Configure the model and load train/dev

# %%
if not _has_llm_key(MODEL):
    print("Lab 13 needs an LLM key (OPENAI_API_KEY, or DSPY_MODEL=anthropic/...). "
          "Set it in labs/.env, then re-run the cells.")
    sys.exit(0)

dspy.configure(lm=dspy.LM(MODEL, temperature=0.0))
trainset = load_examples(LAB / "train.jsonl")
devset = load_examples(LAB / "dev.jsonl")
print(f"model={MODEL}  train={len(trainset)}  dev={len(devset)}")
trainset[0]

# %% [markdown]
# ## 3. Baseline — the program as written, no optimization

# %%
program = build_program()
base = evaluate(program, devset)
print(f"baseline dev accuracy = {base}%")

# %% [markdown]
# ## 4. Optimize with BootstrapFewShot (self-generated few-shot demos)

# %%
from dspy.teleprompt import BootstrapFewShot  # noqa: E402

tele = BootstrapFewShot(metric=category_match, max_bootstrapped_demos=4, max_labeled_demos=4)
optimized = tele.compile(build_program(), trainset=trainset)
opt = evaluate(optimized, devset)
print(f"optimized dev accuracy = {opt}%   (lift {opt - base:+.2f} pts, no hand-written prompt)")

# %% [markdown]
# ## 5. Inspect what the optimizer learned — the selected demos

# %%
preds = optimized.predictors() if hasattr(optimized, "predictors") else []
demos = getattr(preds[0], "demos", []) if preds else []
print(f"{len(demos)} few-shot demos selected by the optimizer.")
demos[0] if demos else "none"
