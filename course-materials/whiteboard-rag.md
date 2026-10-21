# Whiteboard: RAG & embeddings (Day 3 opener)

My drawing sequence for the `slides/04-rag-vector-dbs.md` "The Ideas (whiteboard)" slide.
Instructor notes, first person — the deck stays thin on purpose; this is what I draw and say
before sending them into Lab 06. Every number below is the **real** output of
`labs/06-RAG-Vector-DB/rag.py` (offline local embedder), verified 2026-10-20, so what I write
on the board matches what their terminals print.

## 0. The bridge from yesterday afternoon (one minute, no drawing)

Yesterday we ended on three provider APIs, local models, and open-weight models. Pick that up:
**an embedding model is just another model you choose the same way** — hosted
(`text-embedding-3-small`) or local. Lab 06's embedder is local, deterministic, and 15 lines
of NumPy you can read. That's the whole reason the lab needs no key and no network.

> Retrieval is not a product you buy. It's a model, a matrix, and one number.

## 1. Embedding space — "near" means related in meaning

Draw 2-D axes, scatter five dots, label them `returns`, `shipping`, `warranty`, `accounts`,
and a hollow dot for the **question**. Draw the question dot sitting between returns and
shipping.

Say: the real space is 512-D in this lab (`DIM = 512`), thousands-D for a hosted embedder. We
draw 2 because the *only* thing that transfers is "closeness." Ask them: what do we mean by
close? Let them answer — then write the formula.

## 2. Cosine similarity — the one number behind every vector search

```text
                a · b
  cos(a,b) = ───────────        1.0 = same direction    0.0 = nothing shared
              ‖a‖ · ‖b‖
```

Point out what the denominator does: it **divides out length**. Hold that thought — it is the
punchline in step 4.

## 3. Chunk the corpus — what retrieval can even find

Four policy docs become **five chunks** (`max_chars=600`, `overlap=100`). Write the inventory:

| chunk | chars | content words |
|---|---|---|
| `accounts.md#chunk0` | 518 | 59 |
| `returns.md#chunk0` | 443 | 52 |
| `returns.md#chunk1` | 161 | **17** |
| `shipping.md#chunk0` | 541 | 59 |
| `warranty.md#chunk0` | 551 | 62 |

`returns.md` split in two. **That split is about to decide the answer.** Note which chunk holds
what: `#chunk0` has the real policy — *"return most items within **30 days**"*. `#chunk1` is the
short damaged-goods paragraph — *"contact support within **7 days**"*.

## 4. One query, end to end — the money shot

Question: **"how many days do I have to return an item?"**

Strip stopwords (`how`, `many`, `do`, `i`, `have`, `to`, `an` all go) and you are left with
three content words. Write them:

```text
  q = { days , return , item }        ‖q‖ = √3 = 1.732
```

Now count hits per chunk and do the division on the board:

```text
  returns.md#chunk0   days×2  return×2  item×1  → dot 5   ‖c‖ 8.60   5/(8.60·1.732) = 0.336
  returns.md#chunk1   days×1  return×1  item×1  → dot 3   ‖c‖ 4.12   3/(4.12·1.732) = 0.420  ← wins
  shipping.md#chunk0  days×2                    → dot 2   ‖c‖ 11.62  2/(11.62·1.732) = 0.099
  accounts.md#chunk0  (nothing)                 → dot 0              0.000
```

Then let it land:

- Both returns chunks share **all three** query words. Vocabulary overlap is identical.
- `#chunk0` actually mentions them **more** (dot 5 vs 3) — and it holds the correct answer.
- `#chunk1` still wins, **only because it is short**. 17 content words vs 52, so a smaller
  norm, so a bigger cosine. The denominator from step 2 did this.
- So the top-ranked passage says **7 days** and the right answer, **30 days**, ranks second.

> Retrieval didn't fail at reading. It ranked a short, shallow mention above a long, correct
> one — because that's what cosine measures. The chunk boundary chose the winner.

Save the fix for the lab: top-4 (not top-1) still carries `#chunk0` into the prompt, so the
grounded answer is right anyway. That is *why* we retrieve k>1.

**Do not promise that a better embedder fixes the order — it doesn't.** I checked:
`EMBEDDINGS=openai` returns the *same* ranking (`0.570` for `#chunk1` vs `0.485` for `#chunk0`),
just a narrower gap. The short-chunk bias is **cosine's**, not the toy embedder's, and every
embedder normalizes by length. The honest line:

> A better embedder is not the fix. The fix is chunking — and retrieving more than one.

**Show it rather than assert it** — one command, and the agent gives the wrong answer live:

```sh
python rag.py "how many days do I have to return an item?" --k 1
```

Top-1 only, so the prompt sees just `#chunk1`, and the grounded answer comes back as the **7-day**
damaged-goods rule. The question asked about the return window; the answer is about damaged goods.
Then re-run without `--k 1` and the 30-day policy is back. That contrast is the argument for k>1,
and it takes 20 seconds.

## 5. The off-topic guard — abstain instead of guess

Second question: **"what is the capital of France?"** Write the scores:

```text
  shipping.md#chunk0  0.057     ← best of a bad lot
  everything else     0.000
  MIN_SCORE           0.08      → nothing clears the floor → refuse
```

Answer printed: *"I couldn't find that in the knowledge base, so I won't guess. A human should
follow up."* Make the point that the anti-hallucination behavior they'll spend the week wanting
is **one number and one `if`** — and that `MIN_SCORE` is a precision/recall dial with no
universal right value. Too strict → "not found" on real questions; too loose → confident
nonsense.

## 5b. The third case, if the room is with me — "do you ship to Europe?"

Only one chunk scores at all (`shipping.md#chunk0`, **0.170**), and it clears the floor. The
corpus *does* answer this: *"We ship to Canada and Mexico... We do not currently ship to other
countries."* So the honest answer is **no**, and it's grounded.

But watch what prints: offline, the "grounded answer" **pastes the whole chunk** — delivery
times, shipping costs, then the international sentence. The answer is in there, buried in 541
characters. Narrate that, don't apologize for it:

> Retrieval's job is to put the right passage in front of the model. *Writing the answer from
> that passage is the model's job* — and offline we have no model, so we show you the raw
> evidence instead.

And I can prove that in one command, because the VM has keys:

```sh
RAG_GENERATE=1 python rag.py "how are refunds issued?"
```

Verified output — one sentence, cited, instead of a wall of chunk:

```text
Refunds are issued back to the original payment method within 5 business days after Northwind
receives the returned item. If the original card is closed, store credit is issued instead
[returns.md#chunk0].
```

Same retrieval, same passages, same citations. The only thing added is a model that writes.

That's the cleanest in-course argument for why RAG is retrieval **plus** generation, not
retrieval alone.

**The sharper point, and the one to make first.** Run it with `--show-scores` and read the four
passages out loud:

```text
  [0.170] shipping.md#chunk0     <- the only one with any signal
  [0.000] accounts.md#chunk0
  [0.000] returns.md#chunk0
  [0.000] returns.md#chunk1
```

Three of the four scored **exactly zero** — and came back anyway, and got pasted into the grounded
answer. So:

* **`top-k` is a count, not a relevance filter.** We asked the store for the four nearest vectors
  and it returned four, because "nearest" is defined even when nothing is near.
* **`MIN_SCORE` doesn't save us here**, because it only tests the **top** score. One passage
  clearing 0.08 lets three zeros ride along behind it.
* The wall of irrelevant text on screen is therefore not a bug and not a bad corpus — it is
  exactly what a fixed-k nearest-neighbour search does, shown honestly.

> The vector store always has an answer for you. Whether it should is your decision, not its.

Two places to take it from there, depending on the room:

* **A fix they can name themselves:** filter *per passage*, not just on the top one — a one-line
  change in `retrieve` (drop hits below `MIN_SCORE` instead of only checking `hits[0]`). Good
  "your turn" if there's slack.
* **The generation hand-off:** the extractive path has no model to choose among the four, which is
  the lead-in to `RAG_GENERATE=1` below.

Mechanical note: make the terminal pane tall before this one. The useful sentence is at the *top*
of the output and the zero-score chunk fills the view, so in a short pane the punchline scrolls
above the fold.

## 6. Hand off to the lab

Erase nothing. Leave the pipeline arrow and the two score tables on the board — they'll be
looking back at them during Lab 06:

```text
  docs → chunk → embed → store        question → embed → similarity → top-k → augment → cite
```

Lab 06, 60 minutes. First command (`--show-scores` matters, that's how they see the table I
just drew):

```sh
cd labs/06-RAG-Vector-DB
python rag.py "how many days do I have to return an item?" --show-scores
```

## Live terminal, if I want to show instead of draw

**The VM terminal is PowerShell**, so for the keyed demos below set the var on its own line:
`$env:EMBEDDINGS="openai"` / `$env:RAG_GENERATE="1"`, then run `python rag.py ...`, then clear it
with `$env:EMBEDDINGS=""`. A bash `EMBEDDINGS=openai python rag.py` prefix is a parse error there.

```sh
python rag.py "how many days do I have to return an item?" --show-scores   # step 4
python rag.py "what is the capital of France?" --show-scores               # step 5
python rag.py "do you ship to Europe?"                                     # grounded "no"
```

## Footnotes for the sharp question

- **"Your math says 0.336 but it printed 0.331."** Real: words are hashed into 512 dimensions
  (`md5(token) % 512`), so two different words occasionally land in the same slot. Hand-math is
  collision-free; the code isn't. Collisions are a cost of the toy embedder — and a reason real
  embedders learn their dimensions instead of hashing them.
- **"No stemming?"** None. `item` and `items` are different dimensions here. Both appear in
  `returns.md#chunk0`, which is the only reason it shares `item` at all.
- **"Isn't this just keyword search?"** Yes — bag-of-words with cosine *is* lexical search
  wearing a vector coat. That's the honest framing: it teaches the whole pipeline offline, and
  the one thing it cannot do is match meaning across different words. If someone pushes on this,
  run the demo below — it is the cleanest 30 seconds in the lab.

## 5c. The one experiment that proves why learned embeddings exist (needs a key)

Ask something that shares **no content words** with the policy:

```sh
python rag.py "Can I send something back if I change my mind?" --show-scores
EMBEDDINGS=openai python rag.py "Can I send something back if I change my mind?" --show-scores
```

```text
  local   returns.md#chunk1  0.217   shipping 0.072   returns.md#chunk0  0.051   <- real answer 3rd
  hosted  returns.md#chunk0  0.443   returns.md#chunk1 0.427   shipping 0.232     <- real answer 1st
```

"Send something back", "change my mind" — not one of those words is in the return policy. Lexical
retrieval buries the right passage below *shipping*; semantic retrieval puts it first. **That** is
what the embedding model buys, and it is a different problem from the chunk-length bias in step 4.

Mechanical note for the live run: `labs/.env` is now loaded by `rag.py`, so `EMBEDDINGS=openai`
just works on a VM with keys (it used to fall back to local and print
`EMBEDDINGS=openai but OPENAI_API_KEY not set`). Hosted cosine scores sit in a different range
than local ones, so `MIN_SCORE=0.08` is embedder-specific — off-topic hosted scores ~0.038, which
still abstains, but the threshold would need retuning for a different embedder. Worth saying out
loud when someone asks where 0.08 came from.
