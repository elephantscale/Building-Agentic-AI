# Lab 6 — RAG over a Local Vector Store

## Goal

Build a complete **Retrieval-Augmented Generation** pipeline over a small document corpus and
make the agent answer **from evidence, with citations** — or admit it doesn't know:

1. **Chunk** the corpus and **embed** every chunk into a vector.
2. Build a **vector store** and run **similarity search** for a question.
3. Return the **top-k passages with their sources**.
4. Produce a **grounded answer that cites** those passages — or says the answer isn't in the
   corpus instead of guessing.
5. Expose retrieval as a `search_knowledge_base` **tool** the agent can call.

This is the retrieval half of "tools" from the last module: the agent reaches out for *facts*,
not actions, and we hold it to grounding + citation — the same discipline you'll carry into the
framework labs (LangGraph retrieval, agentic RAG).

## Time

60 minutes

## Tools

- Python 3.11+
- **NumPy only** for the offline path — no API key, no network needed
- `openai` is **optional**: set `EMBEDDINGS=openai` (with `OPENAI_API_KEY`) for hosted
  embeddings, or `RAG_GENERATE=1` to have an LLM write the grounded answer
- Corpus: `corpus/*.md` (a small fictional "Northwind" help center, shipped with the lab)

> **Local-only by design.** The default run uses local hashing embeddings and an in-memory
> NumPy store, so it works on a locked-down network with nothing installed but NumPy.

## Files in this lab

- `rag.py` — the full pipeline: load → chunk → embed → index → retrieve → ground + cite, plus
  the `search_knowledge_base` tool.
- `corpus/` — four short policy docs (returns, shipping, warranty, accounts).
- `requirements.txt` — `numpy` (required), `openai` (optional).

## Steps

1. Install and run the default question — **no key required**:
   ```sh
   cd labs/06-RAG-Vector-DB
   pip install -r requirements.txt
   python rag.py "how many days do I have to return an item?" --show-scores
   ```
2. Ask something the corpus **doesn't** cover and confirm it refuses to guess:
   ```sh
   python rag.py "what is the capital of France?" --show-scores
   ```
3. Ask an out-of-scope-but-related question and read the grounded "no":
   ```sh
   python rag.py "do you ship to Europe?"
   ```
4. Tune retrieval: change `--k`, then open `rag.py` and change `max_chars`/`overlap` in
   `chunk_text` and the `MIN_SCORE` threshold. Re-run and watch what changes.
5. (Optional, needs a key) Swap in hosted embeddings and/or an LLM answer:
   ```sh
   EMBEDDINGS=openai python rag.py "warranty on electronics?"
   RAG_GENERATE=1 python rag.py "how are refunds issued?"
   ```

## Starter Code

The **embedder** turns text into a vector; the same function runs on documents and on the query:

```python
def local_embed(texts):
    vecs = np.zeros((len(texts), DIM), dtype=np.float32)
    for i, t in enumerate(texts):
        for tok in _tokens(t):                      # content words only (stopwords dropped)
            vecs[i, int(hashlib.md5(tok.encode()).hexdigest(), 16) % DIM] += 1.0
    norms = np.linalg.norm(vecs, axis=1, keepdims=True); norms[norms == 0] = 1.0
    return vecs / norms                             # L2-normalized -> cosine == dot product
```

The **vector store** is deliberately a few lines — a real one (FAISS/Chroma/pgvector) has the
same shape, `add()` + `search()`:

```python
def search(self, qvec, k=4):
    sims = self.matrix @ qvec[0]                    # cosine for normalized vectors
    order = np.argsort(-sims)[:k]
    return [(float(sims[i]), self.meta[i]) for i in order]
```

**Grounding** is enforced in code: below a similarity floor we return "not found" instead of an
answer, and every answer carries citations:

```python
if not hits or hits[0][0] < MIN_SCORE:
    return ("I couldn't find that in the knowledge base, so I won't guess. "
            "A human should follow up.", [])
cites = [f"{m['source']}#chunk{m['chunk_id']}" for _, m in hits]
```

Retrieval exposed as a **tool** — the agentic entry point from the last module:

```python
def search_knowledge_base(query, k=4):
    """Tool the agent calls when it needs facts. Returns passages with sources + scores."""
    ...
    return [{"source": ..., "chunk_id": ..., "score": ..., "text": ...}, ...]
```

## What a correct run looks like

The returns question retrieves from `returns.md` and answers with citations (offline, local
embeddings):

```text
Q: how many days do I have to return an item?
Embeddings: local | chunks indexed: 5 | top-4

Retrieved passages:
  [0.420] returns.md#chunk1: If an item arrives damaged or you received the wrong product...
  [0.331] returns.md#chunk0: # Northwind Returns & Refunds Policy ## Return window You may return...
  [0.107] warranty.md#chunk0: # Northwind Warranty ## Coverage All electronics include...
  [0.093] shipping.md#chunk0: # Northwind Shipping Policy ## Delivery times...

Grounded answer:
Based on the knowledge base:
... You may return most items within **30 days** of delivery for a full refund ...

Citations: returns.md#chunk1, returns.md#chunk0, warranty.md#chunk0, accounts.md#chunk0
```

An out-of-corpus question is **refused**, not guessed:

```text
Q: what is the capital of France?
Retrieved passages:
  [0.057] shipping.md#chunk0: ...
  [0.000] accounts.md#chunk0: ...

Grounded answer:
I couldn't find that in the knowledge base, so I won't guess. A human should follow up.
```

## Deliverable

A runnable `rag.py` that, for a question:

1. chunks + embeds the corpus and builds a searchable vector store,
2. retrieves the top-k passages with sources and similarity scores,
3. produces a grounded answer **with citations**, and refuses (no guess) when nothing clears the
   similarity floor, and
4. offers `search_knowledge_base(query)` as a callable tool.

Bonus: show how changing chunk size or `k` changes which passage ranks first, and find one
question where a bad chunk boundary hurts the answer.

## Troubleshooting

- **`ModuleNotFoundError: numpy`.** `pip install -r requirements.txt`.
- **Everything scores 0.000.** Your query has only stopwords, or words that never appear in the
  corpus — that's the "not found" path working. Try words that are actually in the docs.
- **The wrong chunk ranks first.** Expected sometimes with a bag-of-words embedder — it's the
  teaching point. Shrink `max_chars` so chunks are more focused, or switch to `EMBEDDINGS=openai`
  for semantic embeddings and compare.
- **An off-topic question still gets answered.** Raise `MIN_SCORE`. Too many "not found"s? Lower
  it. There's no universal value — it's a precision/recall dial.
- **`EMBEDDINGS=openai` says "using local".** No `OPENAI_API_KEY` in the environment; the lab
  falls back to local on purpose so it never blocks.

## Teacher's Playbook

**Worked answer / what good looks like.** A complete submission retrieves the right source for
in-corpus questions, cites it, and **refuses** out-of-corpus ones. The strongest students can
explain *why* a chunk ranked where it did (shared content words), and show that grounding is
enforced in **code** (the `MIN_SCORE` gate and citation list), not merely requested in a prompt.

**Live-demo script (7–9 min).**
1. Run the returns question with `--show-scores`. "Same embedder on the docs and the query. The
   score is just cosine similarity — one dot product."
2. Run "capital of France." "Nothing clears the floor, so it says *I don't know*. A RAG system
   that won't say that is a liability."
3. Open `corpus/returns.md` and point at the chunk that was cited. "The answer is traceable to a
   source. That's the difference between RAG and a confident guess."
4. Change `max_chars` from 600 to 200, re-run. "Smaller chunks, different ranking. Chunking is a
   design decision, not a detail."
5. Point at `search_knowledge_base`. "This is retrieval as a *tool*. In the LangGraph lab the
   agent decides when to call it; here you're seeing what it returns."

**Common mistakes + fixes.**
- *Embedding the query with a different method than the documents* → garbage similarity. Fix: one
  embedder, both sides.
- *No "not found" path* → the system invents policy. Fix: a similarity floor that returns a
  refusal, and test it with an off-topic question.
- *Giant chunks (whole document = one chunk)* → retrieval can't localize the answer. Fix: chunk.
- *Grounding by prompt only* → still hallucinates. Fix: enforce in code (floor + citations), and
  keep the prompt instruction as a second layer when using `RAG_GENERATE=1`.
- *Citing sources the answer didn't actually use* → fake grounding. Fix: cite only retrieved
  passages, and keep the passage text next to the claim.

**Debrief Q&A.**
- *Q: Why does the damaged-items chunk sometimes outrank the 30-day chunk?* A: Bag-of-words
  shares the words "item/return/days." A learned embedding (`EMBEDDINGS=openai`) captures meaning
  better — run both and compare. This is exactly why embedding quality matters.
- *Q: Is this a "real" vector database?* A: It's a real nearest-neighbor search, just in NumPy.
  FAISS/Chroma/pgvector add scale, persistence, and filters — same `add`/`search` idea.
- *Q: How do I choose `k` and the threshold?* A: Empirically, against real questions. More `k`
  gives recall but adds noise to the prompt; the floor trades a few "not founds" for fewer wrong
  answers. Measure it (that's the next module — evaluation).
- *Q: Where does this meet governance?* A: Citations are an audit trail; "I don't know" is a
  safety behavior. Both reappear in the governance lab.
- *Q: How does this connect to the agent?* A: `search_knowledge_base` is a tool with the same
  schema discipline as Lab 4 — retrieval is just a read-only tool the planner can call.

---
