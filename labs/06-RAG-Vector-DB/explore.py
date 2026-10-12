# %% [markdown]
# # Lab 6 — RAG, step by step (interactive)
#
# Open this as a **notebook** (`explore.ipynb`) or run the `.py` cell-by-cell in VSCode with
# **Shift+Enter** — same content either way. It walks retrieval one stage at a time:
# corpus → chunks → embeddings → vector store → retrieve → grounded answer.
# **Fully offline** (local hashing embeddings) — no API key or network needed.
#
# This drives the same code as `rag.py`; the command line is `python rag.py "your question"`.
#
# **How to work through it** — three beats:
# - 🔮 **Predict** — before you run a cell, say what you expect. Then run and compare.
# - 🛠️ **Your turn** — one cell is yours to change; the reference answer is in the README Playbook.
# - 🗣️ **Explain** — end by answering the question in your own words.

# %%
import os
import sys

# Make the lab's modules importable whether cells run from the repo root or here.
HERE = os.path.dirname(os.path.abspath(__file__)) if "__file__" in dir() else os.getcwd()
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402
from rag import (  # noqa: E402
    load_corpus, chunk_text, get_embedder, build_index, retrieve,
    ground_answer, CORPUS_DIR, MIN_SCORE,
)

# %% [markdown]
# ## 1. The corpus and how it chunks

# %%
docs = load_corpus(CORPUS_DIR)
print(f"{len(docs)} documents:", [name for name, _ in docs])
chunks = chunk_text(docs[0][1])
print(f"\n{docs[0][0]} -> {len(chunks)} chunks. First chunk:\n")
print(chunks[0])

# %% [markdown]
# ## 2. Build the vector index (embed every chunk)

# %%
embedder, used = get_embedder("local")
store = build_index(embedder)
print(f"embeddings: {used} | chunks indexed: {len(store.meta)} | "
      f"vector dim: {store.matrix.shape[1]}")

# %% [markdown]
# ## 3. Retrieve for an on-topic question
#
# 🔮 **Predict first:** the question below is *"how long do I have to return something?"*
# Which document do you think the top passage will come from — `returns.md`, `shipping.md`,
# or `accounts.md`? And will the top score be large (~0.5) or modest (~0.1)? Run and check — the
# number is smaller than people expect, because this toy embedder only counts shared words.

# %%
hits = retrieve(store, embedder, "how long do I have to return something?", k=4)
for s, m in hits:
    print(f"[{s:.3f}] {m['source']}#chunk{m['chunk_id']}: "
          f"{' '.join(m['text'].split())[:80]}...")

# %% [markdown]
# ## 4. The off-topic guard — scores collapse toward 0
#
# 🔮 **Predict first:** *"what is the capital of France?"* shares almost no content words with a
# returns-and-shipping corpus. Will its top score clear `MIN_SCORE`, or fall below it? What should
# the agent answer when nothing clears the bar?

# %%
off = retrieve(store, embedder, "what is the capital of France?", k=4)
print("top score:", round(off[0][0], 3), " | MIN_SCORE:", MIN_SCORE)
answer, _ = ground_answer("what is the capital of France?", off)
print(answer)

# %% [markdown]
# ## 5. Grounded answer + citations for the on-topic question

# %%
answer, cites = ground_answer("how long do I have to return something?", hits)
print(answer)
print("\nCitations:", cites)

# %% [markdown]
# ## 6. 🛠️ Your turn — find the abstain threshold
#
# The anti-hallucination gate lives in **one number**: a question whose top score is below
# `THRESHOLD` gets *"not in the knowledge base"* instead of a guess. Below are two on-topic and two
# off-topic questions. Change `THRESHOLD` and find the value that **answers both on-topic questions
# and abstains on both off-topic ones**. Then push it too high and too low to see what breaks.
#
# *Reference answer + discussion in the README Teacher's Playbook.*

# %%
THRESHOLD = MIN_SCORE   # 🛠️ try values between 0.04 and 0.25 and watch the line move

probe = [
    ("how long do I have to return something?", "on-topic"),
    ("do you refund shipping?",                 "on-topic"),
    ("what is the capital of France?",          "off-topic"),
    ("do you price match a competitor?",        "off-topic"),
]
for q, label in probe:
    top = retrieve(store, embedder, q, k=4)[0][0]
    decision = "ANSWER " if top >= THRESHOLD else "ABSTAIN"
    print(f"{top:.3f}  {decision}  ({label:<9}) {q}")
print(f"\nthreshold = {THRESHOLD}")

# %% [markdown]
# ## 7. 🗣️ Explain
#
# In one or two sentences: **why** does *"capital of France"* score near zero while
# *"return policy"* scores high, even though this toy embedder never learned any language?
# (Hint: look at `_tokens` and `_STOPWORDS` in `rag.py` — what actually drives the similarity?)
#
# ---
# ### (optional) Swap in hosted embeddings and compare
# Set `OPENAI_API_KEY`, then uncomment to see how learned embeddings change retrieval:

# %%
# os.environ["EMBEDDINGS"] = "openai"
# emb2, used2 = get_embedder("openai")
# store2 = build_index(emb2)
# for s, m in retrieve(store2, emb2, "warranty on electronics?", k=4):
#     print(f"[{s:.3f}] {m['source']}#chunk{m['chunk_id']}")
