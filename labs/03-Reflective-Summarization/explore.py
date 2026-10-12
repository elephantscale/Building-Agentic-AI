# %% [markdown]
# # Lab 3 — Direct vs. reflective summarization, step by step (VSCode Interactive)
#
# Run each cell with **Shift+Enter** to watch the reflection loop:
# draft → critique (see the itemized issues) → revise, then compare quality vs. cost
# against a plain direct summary.
#
# This lab calls a real model, so it needs `OPENAI_API_KEY` (set it in `labs/.env`).
# Same code as `reflective_summarizer.py`. CLI version: `python reflective_summarizer.py`.
#
# *Needs the VSCode Python + Jupyter extensions. Open this file and click "Run Cell".*

# %%
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__)) if "__file__" in dir() else os.getcwd()
sys.path.insert(0, HERE)

from reflective_summarizer import (  # noqa: E402
    load_source, summarize_direct, critique, revise, summarize_reflective,
    score, Meter, TARGET,
)

if not os.getenv("OPENAI_API_KEY"):
    print("Lab 3 needs OPENAI_API_KEY (set it in labs/.env). The cells below call the model.")
    sys.exit(0)

from openai import OpenAI  # noqa: E402

client = OpenAI()
source = load_source("article.txt")
print("TARGET:", TARGET)
print("source chars:", len(source))

# %% [markdown]
# ## 1. Direct summary (one call)

# %%
m_direct = Meter()
direct = summarize_direct(client, source, m_direct)
print(direct)
print(f"\n[tokens={m_direct.total_tokens} calls={m_direct.calls}]")

# %% [markdown]
# ## 2. One critique pass — the itemized issues the critic finds

# %%
verdict = critique(client, source, direct, Meter())
verdict

# %% [markdown]
# ## 3. One revision that fixes those issues

# %%
revised = revise(client, source, direct, verdict["issues"], Meter()) if verdict["issues"] else direct
print(revised)

# %% [markdown]
# ## 4. The full reflective loop (draft → critique → revise, capped)

# %%
m_reflect = Meter()
reflective, trace = summarize_reflective(client, source, m_reflect)
print(reflective)
print(f"\nrounds: {len(trace)}  [tokens={m_reflect.total_tokens} calls={m_reflect.calls}]")

# %% [markdown]
# ## 5. Score both — did reflection earn its extra cost?

# %%
mj = Meter()
rd = score(client, source, direct, mj)
rr = score(client, source, reflective, mj)
print("direct    :", rd, "->", sum(rd.values()), "/9")
print("reflective:", rr, "->", sum(rr.values()), "/9")
print(f"lift: {sum(rr.values()) - sum(rd.values()):+d} pts for "
      f"{m_reflect.total_tokens / max(m_direct.total_tokens, 1):.1f}x the tokens")
