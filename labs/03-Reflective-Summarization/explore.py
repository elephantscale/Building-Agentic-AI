# %% [markdown]
# # Lab 3 — Direct vs. reflective summarization, step by step (interactive)
#
# Open this as a **notebook** (`explore.ipynb`) or run the `.py` cell-by-cell in VSCode with
# **Shift+Enter** — same content either way. Watch the reflection loop:
# draft → critique (see the itemized issues) → revise, then compare quality vs. cost against a
# plain direct summary.
#
# This lab calls a real model, so it needs `OPENAI_API_KEY` (set it in `labs/.env`).
# It drives the same code as `reflective_summarizer.py`; the CLI is `python reflective_summarizer.py`.
#
# **How to work through it** — three beats:
# - 🔮 **Predict** — before you run a cell, say what you expect. Then run and compare.
# - 🛠️ **Your turn** — one cell is yours to change; the reference answer is in the README Playbook.
# - 🗣️ **Explain** — end by answering the question in your own words.

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
#
# 🔮 **Predict first:** the direct summary above probably reads fine to a human. How many issues do
# you think a strict critic will raise — **0, 1–2, or 3+**? And will they be about **factuality**
# (a claim not in the source), **coverage** (a missed point), or **style** (format/length/tone)?

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
#
# 🔮 **Predict first:** you're about to see quality (out of 9) and token cost for each. Predict the
# **quality lift** (will reflective beat direct by 0, 1, or 2+ points?) and roughly **how many times
# more tokens** reflection spent. Was it worth it on *this* document?

# %%
mj = Meter()
rd = score(client, source, direct, mj)
rr = score(client, source, reflective, mj)
print("direct    :", rd, "->", sum(rd.values()), "/9")
print("reflective:", rr, "->", sum(rr.values()), "/9")
print(f"lift: {sum(rr.values()) - sum(rd.values()):+d} pts for "
      f"{m_reflect.total_tokens / max(m_direct.total_tokens, 1):.1f}x the tokens")

# %% [markdown]
# ## 6. 🛠️ Your turn — tighten the spec and watch reflection enforce it
#
# Reflection is only as good as the TARGET it's held to. Make the spec **stricter** (fewer words,
# a fixed number of bullets) and re-run the loop. Does the critic now find more to fix? Does the
# final summary obey the new limit? Edit `NEW_TARGET` and re-run.
#
# *Reference answer in the README Teacher's Playbook.*

# %%
import reflective_summarizer as rs  # noqa: E402

NEW_TARGET = "EXACTLY 3 bullets, <= 60 words total, executive tone, grounded ONLY in the source"
rs.TARGET = NEW_TARGET            # 🛠️ try your own: stricter length, a required angle, etc.

m = rs.Meter()
strict, strict_trace = rs.summarize_reflective(client, source, m, rounds=2)
print(strict)
print(f"\nrounds used: {len(strict_trace)}  tokens: {m.total_tokens}  "
      f"words: {len(strict.split())}")

rs.TARGET = TARGET               # restore so re-running earlier cells behaves

# %% [markdown]
# ## 6b. 🔮 The flip side — a *weak first pass* is what makes reflection bite
#
# §6 showed that a **stricter spec** does **not** make the critic complain — `summarize_direct`
# just obeys it, so the critic still accepts. So what *does* trigger a revision? A **bad first
# draft.** Below we force a rushed, shallow draft (2 bullets, no detail), then critique it against
# the proper spec. Watch the critic find real omissions and the revision put them back — the exact
# opposite of §6.
#
# 🔮 **Predict:** how many issues will the critic raise on a deliberately lazy 2-bullet draft — and
# what kind (factuality, coverage, style)?

# %%
import reflective_summarizer as rs  # noqa: E402
rs.TARGET = TARGET                   # critique against the PROPER spec, not §6's tightened one


def weak_draft(src):
    """A deliberately rushed first pass — high-level, drops facts (cheap, not comprehensive)."""
    resp = client.chat.completions.create(
        model=rs.MODEL, temperature=0,
        messages=[
            {"role": "system", "content": "Summarize in EXACTLY 2 short bullets, under 30 words "
             "total. Keep it extremely high-level; don't try to be comprehensive."},
            {"role": "user", "content": f"Summarize this:\n\n{src}"},
        ],
    )
    return resp.choices[0].message.content.strip()


bad = weak_draft(source)
print("WEAK FIRST PASS:\n", bad, "\n")

m_bad = Meter()
v = critique(client, source, bad, m_bad)
print("verdict:", v["verdict"], "| issues:", len(v["issues"]))
for i, issue in enumerate(v["issues"], 1):
    print(f"  {i}. {issue}")

if v["issues"]:
    fixed = revise(client, source, bad, v["issues"], m_bad)
    print("\nAFTER REVISION (facts restored):\n", fixed)

# %% [markdown]
# ## 7. 🗣️ Explain
#
# In two or three sentences: **when is the extra cost of reflection worth it, and when is a direct
# summary the right call?** Use the numbers you saw (quality lift vs. token ratio). What kind of task
# would make reflection clearly pay off — and what kind would make it pure waste?
