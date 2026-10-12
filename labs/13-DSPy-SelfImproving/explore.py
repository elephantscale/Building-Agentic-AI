# %% [markdown]
# # Lab 13 — DSPy self-improvement, step by step (interactive)
#
# Open this as a **notebook** (`explore.ipynb`) or run the `.py` cell-by-cell in VSCode with
# **Shift+Enter**. Watch a DSPy program go from baseline to optimized one stage at a time:
# Signature → baseline score → BootstrapFewShot → optimized score → the demos it taught itself.
#
# This lab optimizes a real LLM program, so it needs a key: `OPENAI_API_KEY`, or set
# `DSPY_MODEL=anthropic/claude-haiku-4-5-20251001`. There is no offline mode.
# Same code as `self_improving.py`. The CLI is `python self_improving.py`.
#
# **How to work through it** — three beats:
# - 🔮 **Predict** — before you run a cell, say what you expect. Then run and compare.
# - 🛠️ **Your turn** — vary the optimizer budget; the reference answer is in the README Playbook.
# - 🗣️ **Explain** — end by answering the question in your own words.

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
#
# 🔮 **Predict first:** this is a plain ChainOfThought classifier with **no examples** — just the
# Signature. Across 6 ticket categories, what dev accuracy do you expect — **~40%, ~70%, or ~90%?**

# %%
program = build_program()
base = evaluate(program, devset)
print(f"baseline dev accuracy = {base}%")

# %% [markdown]
# ## 4. Optimize with BootstrapFewShot (self-generated few-shot demos)
#
# 🔮 **Predict first:** BootstrapFewShot will pick a handful of worked examples automatically. How
# many **points** of lift do you expect over the baseline — a little (1–3) or a lot (10+)? You wrote
# no new prompt; the gain comes entirely from examples + the metric.

# %%
from dspy.teleprompt import BootstrapFewShot  # noqa: E402

tele = BootstrapFewShot(metric=category_match, max_bootstrapped_demos=4, max_labeled_demos=4)
optimized = tele.compile(build_program(), trainset=trainset)
opt = evaluate(optimized, devset)
print(f"optimized dev accuracy = {opt}%   (lift {opt - base:+.2f} pts, no hand-written prompt)")

# %% [markdown]
# ## 5. 🛠️ Your turn — does more few-shot budget keep helping?
#
# Re-compile with different demo budgets and watch the accuracy curve. Is more always better, or do
# the gains flatten (or even wobble) on such a small train set? Edit `BUDGETS` and re-run.
#
# *Reference answer in the README Teacher's Playbook.*

# %%
BUDGETS = [0, 2, 8]        # 🛠️ try your own, e.g. [0, 1, 2, 4, 8]
for n in BUDGETS:
    t = BootstrapFewShot(metric=category_match, max_bootstrapped_demos=n, max_labeled_demos=n)
    prog = t.compile(build_program(), trainset=trainset)
    print(f"demos={n:>2}: dev accuracy = {evaluate(prog, devset)}%")

# %% [markdown]
# ## 6. Inspect what the optimizer learned — the selected demos

# %%
preds = optimized.predictors() if hasattr(optimized, "predictors") else []
demos = getattr(preds[0], "demos", []) if preds else []
print(f"{len(demos)} few-shot demos selected by the optimizer.")
demos[0] if demos else "none"

# %% [markdown]
# ## 7. 🗣️ Explain
#
# You never wrote a prompt. In two or three sentences, **what did BootstrapFewShot actually change**
# to improve accuracy? Look at the demos from the cell above. Why is "declare the contract + a metric,
# let the optimizer find the examples" more maintainable than hand-tuning a prompt string?
