# %% [markdown]
# # Lab 6 — RAG, step by step (VSCode Interactive)
#
# Run each cell with **Shift+Enter** to watch retrieval happen one stage at a time:
# corpus → chunks → embeddings → vector store → retrieve → grounded answer.
# Fully **offline** (local hashing embeddings) — no API key or network needed.
#
# This is the same code as `rag.py`, just driven cell-by-cell so you can inspect the
# intermediate values. The command-line version is `python rag.py "your question"`.
#
# *Needs the VSCode Python + Jupyter extensions. Open this file and click "Run Cell".*

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
# ## 3. Retrieve for an on-topic question — inspect the similarity scores

# %%
hits = retrieve(store, embedder, "how long do I have to return something?", k=4)
for s, m in hits:
    print(f"[{s:.3f}] {m['source']}#chunk{m['chunk_id']}: "
          f"{' '.join(m['text'].split())[:80]}...")

# %% [markdown]
# ## 4. The off-topic guard — scores collapse toward 0
#
# A question the corpus can't answer scores below `MIN_SCORE`, so the agent says
# "not in the knowledge base" instead of guessing. This is the anti-hallucination gate.

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
# ## 6. (optional) Swap in hosted embeddings and compare
#
# Set `OPENAI_API_KEY`, then uncomment to see how learned embeddings change retrieval:

# %%
# os.environ["EMBEDDINGS"] = "openai"
# emb2, used2 = get_embedder("openai")
# store2 = build_index(emb2)
# for s, m in retrieve(store2, emb2, "warranty on electronics?", k=4):
#     print(f"[{s:.3f}] {m['source']}#chunk{m['chunk_id']}")
