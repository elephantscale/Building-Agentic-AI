# RAG & Vector Databases

Elephant Scale

---

## Part II — What We'll Cover

* **Why RAG** — give the agent facts it wasn't trained on, and *ground* what it says
* **Embeddings** — turning text into vectors that carry meaning
* **Vector databases** — storing those vectors and searching them by similarity
* **Chunking** — how you split documents decides what retrieval can find
* **Grounding & citation** — answer *from the sources*, cite them, or say "not found"
* **Retrieval as a tool** — the agent decides when to go look things up

> RAG is how an agent stops guessing from memory and starts answering from evidence.

Notes: Most of this module is at the whiteboard. These slides are beats, not the explanation.

---

## The Ideas (whiteboard)

* Embedding space — "near" means "related in meaning," not "same words"
* Cosine similarity — the one number behind every vector search
* Chunk size vs. recall — too big dilutes, too small loses context
* Top-k retrieval — how many passages to pull, and why more isn't better
* The failure mode: retrieve the wrong chunk → confidently wrong answer

> We'll draw the vector space and walk one query end to end before the lab.

Notes:

---

## The RAG Pipeline (reference)

```text
                    INDEX (build once)                 QUERY (every question)
  docs ──► chunk ──► embed ──► vector store      question ──► embed ──► similarity search
                                   │                                        │
                                   └──────────────► top-k chunks ◄──────────┘
                                                        │
                                             augment the prompt
                                                        │
                                   grounded answer  +  citations   (or "not in the sources")
```

> Same embedder on both sides. The store is just "find the nearest vectors, fast."

Notes:

---

## Vector DBs in the Wild (reference)

* **Local / embedded:** FAISS, Chroma, a plain NumPy matrix (what the lab uses offline)
* **Server / managed:** pgvector, Pinecone, Weaviate, Milvus
* They differ in scale, ops, and filters — **the idea is identical**: nearest-neighbor search
* For a locked-down network, embedded + local embeddings runs with **no cloud at all**

> Pick the DB for your ops reality; the retrieval concept doesn't change.

Notes:

---

## Grounding: the Agentic Payoff

* Retrieval returns **passages with sources** — not an answer
* The agent answers **only** from those passages, and **cites** them
* No supporting passage? **Say so** — don't fill the gap from memory
* Wrap it as a tool — `search_knowledge_base(query)` — and the agent calls it when it needs facts

> Grounding + citation + "I don't know" is what makes retrieval trustworthy in production.

Notes:

---

## Lab 6 — RAG over a Local Vector Store

**Stop here and run Lab 6.**

You will:

1. **Chunk** a small document corpus and **embed** every chunk.
2. Build a **vector store** and run **similarity search** for a question.
3. Return the **top-k passages with their sources**.
4. Produce a **grounded answer that cites** the passages — or says the answer isn't in the corpus.
5. Expose retrieval as a `search_knowledge_base` **tool** the agent can call.

**Runs fully offline** (local embeddings + NumPy store); hosted embeddings are an optional switch.

**Time:** 60 minutes

Notes:
