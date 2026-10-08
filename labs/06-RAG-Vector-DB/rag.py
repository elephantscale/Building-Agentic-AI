#!/usr/bin/env python3
"""Lab 6 - RAG over a local vector store.

Runs FULLY OFFLINE by default: local hashing embeddings + an in-memory NumPy
vector store. No API key and no network required. Set EMBEDDINGS=openai (with a
key) to swap in hosted embeddings, and RAG_GENERATE=1 to have an LLM write the
grounded answer instead of the deterministic extractive one.

    python rag.py "how long do I have to return something?"
    python rag.py "do you ship to Europe?" --show-scores
    EMBEDDINGS=openai python rag.py "warranty on electronics?"   # needs OPENAI_API_KEY
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import os
import re
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
CORPUS_DIR = HERE / "corpus"
DIM = 512               # local embedding dimensionality
MIN_SCORE = 0.08        # below this top score, we say "not in the corpus" instead of guessing


# ----------------------------- corpus + chunking -----------------------------
def load_corpus(corpus_dir: Path):
    docs = []
    for path in sorted(glob.glob(str(corpus_dir / "*.md"))):
        docs.append((Path(path).name, Path(path).read_text(encoding="utf-8")))
    return docs


def chunk_text(text: str, max_chars: int = 600, overlap: int = 100):
    """Pack paragraphs into ~max_chars windows; hard-split any giant paragraph."""
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks, buf = [], ""
    for p in paras:
        if len(buf) + len(p) + 1 <= max_chars:
            buf = (buf + "\n" + p).strip()
            continue
        if buf:
            chunks.append(buf)
            buf = ""
        if len(p) > max_chars:
            start = 0
            while start < len(p):
                chunks.append(p[start:start + max_chars])
                start += max_chars - overlap
        else:
            buf = p
    if buf:
        chunks.append(buf)
    return chunks


# ------------------------------- embeddings ---------------------------------
_TOKEN_RE = re.compile(r"[a-z0-9]+")

# Dropping common words keeps similarity driven by *content* words, so an off-topic
# question ("capital of France") shares almost nothing with the corpus and scores ~0.
_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "but", "by", "can", "do", "does", "for", "from",
    "how", "i", "if", "in", "is", "it", "many", "me", "my", "of", "on", "or", "the", "to", "we",
    "what", "when", "where", "which", "will", "with", "you", "your", "have", "has", "that", "this",
}


def _tokens(text: str):
    return [t for t in _TOKEN_RE.findall(text.lower()) if t not in _STOPWORDS and len(t) > 1]


def local_embed(texts):
    """Deterministic hashing bag-of-words embedding. No network, numpy only.

    Each content word is hashed to a dimension and counted. Cosine similarity of the
    normalized vectors then measures shared vocabulary - a simple but real stand-in for
    a learned embedding model, good enough to teach retrieval end to end offline."""
    vecs = np.zeros((len(texts), DIM), dtype=np.float32)
    for i, t in enumerate(texts):
        for tok in _tokens(t):
            vecs[i, int(hashlib.md5(tok.encode()).hexdigest(), 16) % DIM] += 1.0
    norms = np.linalg.norm(vecs, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return vecs / norms


def openai_embed(texts):
    from openai import OpenAI

    client = OpenAI()
    model = os.getenv("EMBED_MODEL", "text-embedding-3-small")
    resp = client.embeddings.create(model=model, input=list(texts))
    arr = np.array([d.embedding for d in resp.data], dtype=np.float32)
    norms = np.linalg.norm(arr, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return arr / norms


def get_embedder(name: str):
    if name == "openai":
        if not os.getenv("OPENAI_API_KEY"):
            print("EMBEDDINGS=openai but OPENAI_API_KEY not set - using local.", file=sys.stderr)
            return local_embed, "local"
        return openai_embed, "openai"
    return local_embed, "local"


# ------------------------------ vector store --------------------------------
class VectorStore:
    """Toy nearest-neighbor index. A real deployment swaps this for FAISS/Chroma/pgvector;
    the interface - add(vectors, metadata) and search(query_vector, k) - is the same idea."""

    def __init__(self):
        self.matrix = None   # (N, DIM), L2-normalized
        self.meta = []       # [{source, chunk_id, text}, ...]

    def add(self, vecs, metas):
        self.matrix = vecs if self.matrix is None else np.vstack([self.matrix, vecs])
        self.meta.extend(metas)

    def search(self, qvec, k=4):
        sims = self.matrix @ qvec[0]          # cosine == dot product for normalized vectors
        order = np.argsort(-sims)[:k]
        return [(float(sims[i]), self.meta[i]) for i in order]


# -------------------------------- pipeline ----------------------------------
def build_index(embedder):
    docs = load_corpus(CORPUS_DIR)
    if not docs:
        sys.exit(f"No corpus found in {CORPUS_DIR}")
    texts, metas = [], []
    for source, text in docs:
        for j, ch in enumerate(chunk_text(text)):
            texts.append(ch)
            metas.append({"source": source, "chunk_id": j, "text": ch})
    store = VectorStore()
    store.add(embedder(texts), metas)
    return store


def retrieve(store, embedder, question, k=4):
    return store.search(embedder([question]), k=k)


# -------------------------------- answering ---------------------------------
def ground_answer(question, hits):
    top = hits[0][0] if hits else 0.0
    if not hits or top < MIN_SCORE:
        return ("I couldn't find that in the knowledge base, so I won't guess. "
                "A human should follow up.", [])
    cites = [f"{m['source']}#chunk{m['chunk_id']}" for _, m in hits]
    if os.getenv("OPENAI_API_KEY") and os.getenv("RAG_GENERATE") == "1":
        return llm_answer(question, hits), cites
    body = "\n\n".join(f"- {m['text']}" for _, m in hits[:2])
    answer = ("Based on the knowledge base:\n\n" + body +
              "\n\n(Grounded in the retrieved passages above - verify against the sources.)")
    return answer, cites


def llm_answer(question, hits):
    """Optional: have an LLM write the answer, grounded ONLY in retrieved passages."""
    from openai import OpenAI

    client = OpenAI()
    model = os.getenv("CHAT_MODEL", "gpt-4.1")
    context = "\n\n".join(
        f"[{m['source']}#chunk{m['chunk_id']}]\n{m['text']}" for _, m in hits
    )
    system = ("Answer the user's question using ONLY the sources below. Cite the source tags you "
              "use, e.g. [returns.md#chunk0]. If the sources do not answer it, say so - do not "
              "invent policy.")
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": system},
                  {"role": "user", "content": f"SOURCES:\n{context}\n\nQUESTION: {question}"}],
        temperature=0,
    )
    return resp.choices[0].message.content.strip()


# -------------------------- retrieval as a tool -----------------------------
def search_knowledge_base(query, k=4):
    """Tool the agent calls when it needs facts. Returns passages with sources + scores."""
    embedder, _ = get_embedder(os.getenv("EMBEDDINGS", "local"))
    store = build_index(embedder)
    return [
        {"source": m["source"], "chunk_id": m["chunk_id"],
         "score": round(s, 3), "text": m["text"]}
        for s, m in retrieve(store, embedder, query, k=k)
    ]


# ----------------------------------- cli ------------------------------------
def main():
    ap = argparse.ArgumentParser(description="RAG over a local vector store (offline).")
    ap.add_argument("question", nargs="?",
                    default="How many days do I have to return an item?")
    ap.add_argument("--k", type=int, default=4)
    ap.add_argument("--embeddings", default=os.getenv("EMBEDDINGS", "local"),
                    choices=["local", "openai"])
    ap.add_argument("--show-scores", action="store_true")
    args = ap.parse_args()

    embedder, used = get_embedder(args.embeddings)
    store = build_index(embedder)
    hits = retrieve(store, embedder, args.question, k=args.k)

    print(f"Q: {args.question}")
    print(f"Embeddings: {used} | chunks indexed: {len(store.meta)} | top-{args.k}\n")
    print("Retrieved passages:")
    for s, m in hits:
        tag = f"[{s:.3f}] " if args.show_scores else ""
        snippet = " ".join(m["text"].split())[:90]
        print(f"  {tag}{m['source']}#chunk{m['chunk_id']}: {snippet}...")

    answer, cites = ground_answer(args.question, hits)
    print("\nGrounded answer:\n" + answer)
    if cites:
        print("\nCitations: " + ", ".join(cites))


if __name__ == "__main__":
    main()
