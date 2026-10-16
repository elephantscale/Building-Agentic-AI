# %% [markdown]
# # Reflection: making an AI agent check its own work
#
# **The idea in one line:** an agent's first attempt is rarely its best. *Reflection* wires in a
# second step — the agent **critiques its own output, then revises it** — before anything reaches a
# human.
#
# ```
#   draft  ->  critique ("what's wrong with this?")  ->  revise  ->  (repeat, capped)
# ```
#
# We'll summarize a messy internal field report. First a **quick, cheap first pass** (what a hurried
# agent produces), then we let the agent **critique and fix its own work** — and watch what the
# second pair of eyes catches.

# %%
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)) if "__file__" in dir() else os.getcwd()
sys.path.insert(0, HERE)

import reflective_summarizer as rs
from reflective_summarizer import load_source, critique, revise, Meter, TARGET
from openai import OpenAI

client = OpenAI()
source = load_source("demo-article.txt")
print("The spec we're holding the summary to:\n ", TARGET)
print(f"\nSource: {len(source)} characters of messy, fact-dense prose — numbers buried in asides.")

# %% [markdown]
# ## 1. The quick first pass
#
# A fast, cheap draft — the kind of first attempt a busy agent (or person) dashes off. It reads
# fine at a glance. That glance is the trap.


# %%
def quick_draft(source):
    """A deliberately fast, high-level first pass — cheap tokens, not comprehensive."""
    resp = client.chat.completions.create(
        model=rs.MODEL, temperature=0,
        messages=[
            {"role": "system", "content": "Summarize in EXACTLY 2 short bullets, under 30 words "
             "total. Keep it extremely high-level; don't try to be comprehensive."},
            {"role": "user", "content": f"Summarize this:\n\n{source}"},
        ],
    )
    return resp.choices[0].message.content.strip()


draft = quick_draft(source)
print(draft)

# %% [markdown]
# ## 2. The agent critiques its own draft
#
# Same model, new job: *be a strict editor.* Is every claim grounded in the source? Did it miss
# anything important? Does it match the spec (3–5 bullets, grounded, executive tone)? The critic
# returns a structured list of concrete issues.

# %%
verdict = critique(client, source, draft, Meter())
print("verdict:", verdict["verdict"])
print(f"\nthe critic found {len(verdict['issues'])} issue(s) in its own first pass:\n")
for i, issue in enumerate(verdict["issues"], 1):
    print(f"  {i}. {issue}")

# %% [markdown]
# ## 3. The agent revises to fix exactly those issues
#
# It gets its own draft back plus the critic's list, and rewrites — still grounded only in the
# source, now hitting the spec.

# %%
revised = revise(client, source, draft, verdict["issues"], Meter())
print(revised)

# %% [markdown]
# ## 4. Before and after
#
# The first pass vs. the reflected version. The revision recovers the facts the quick draft dropped
# — the numbers and risks a busy reviewer would also have skimmed past.

# %%
print("=" * 72)
print("QUICK FIRST PASS")
print("=" * 72)
print(draft)
print("\n" + "=" * 72)
print("AFTER REFLECTION  (critiqued + revised by the same model)")
print("=" * 72)
print(revised)

# %% [markdown]
# ## The takeaway
#
# - **Reflection is just a second opinion, wired into the loop** — the agent is both author and editor.
# - It costs more (an extra critique + revise call), so it earns its keep when **correctness matters**:
#   contracts, money, compliance — anything a human will act on.
# - On an easy task a first pass is often already fine, and a good critic will simply *accept* it.
#   The skill is **matching the effort to the stakes.**
#
# *This is Module 2 of Elephant Scale's **Building Agentic AI**. The same pattern reappears in
# LangGraph (a critique node), in low-code tools (a second GPT step), and everywhere agents act.*
