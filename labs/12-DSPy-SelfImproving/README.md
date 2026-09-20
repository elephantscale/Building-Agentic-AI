# Lab 12 — Self-Improving Agent with DSPy + Delta Analytics

## Goal

Build a **self-improving** agent with **DSPy**: a support-ticket classifier written as a
**Signature + Module**, scored by a **metric**, then optimized with **`BootstrapFewShot`** over
a small training set. You measure the **before/after lift** on a held-out dev set — the program
improves with **no hand-written prompt**, because the optimizer generates and selects its own
few-shot examples against your metric.

You then write the run metrics to a **Parquet** file and read them back with **pandas** — a
local stand-in for a Databricks **Delta table** (the one-line Delta equivalent is in the code).

## Time

60 minutes

## Tools

- Python 3.11+, `pip`
- `labs/.env` with `OPENAI_API_KEY` (default), or set `DSPY_MODEL=anthropic/claude-haiku-4-5-20251001`
- `dspy-ai`, `pandas`, `pyarrow`
- Concept deck: `slides/09-dspy-databricks.md`

## Files in this lab

```text
12-DSPy-SelfImproving/
├── README.md            # this file
├── requirements.txt     # dspy-ai, openai, anthropic, pandas, pyarrow, python-dotenv
├── self_improving.py    # Signature + Module + metric + optimizer + eval + parquet
├── train.jsonl          # 16 labeled tickets (optimizer learns from these)
└── dev.jsonl            # 10 held-out tickets (scored before & after — never trained on)
```

## Steps

1. Install and configure:

   ```sh
   cd labs/12-DSPy-SelfImproving
   pip install -r requirements.txt
   cp ../.env.example ../.env         # fill in OPENAI_API_KEY
   ```

2. Run it:

   ```sh
   python self_improving.py
   ```

3. Read the output: **baseline** accuracy, **optimized** accuracy, and the **lift** in points.

4. Open `runs.parquet` (read back and printed at the end) — this is your Delta-style metrics
   table. Re-run the script and watch rows **append**.

5. Read the **Databricks Delta equivalent** comment in `write_runs()` — the same append, one
   line of Spark, with ACID + time travel.

## Starter Code

The whole program is three declarations. **Signature** (what), **Module** (how), **metric**
(better):

```python
class ClassifyTicket(dspy.Signature):
    """Classify a customer support ticket into exactly one category."""
    ticket: str = dspy.InputField(desc="the raw customer message")
    category: str = dspy.OutputField(desc="billing | technical | account | sales | policy_compliance | other")

program = dspy.ChainOfThought(ClassifyTicket)          # strategy: reason, then answer

def category_match(example, pred, trace=None) -> bool: # the objective to maximize
    return example.category.strip().lower() in (pred.category or "").strip().lower()
```

**Self-improvement** is the optimizer compiling the program against the metric — it bootstraps
its own few-shot demos and keeps the ones that pass:

```python
from dspy.teleprompt import BootstrapFewShot

base = evaluate(program, devset)                       # measure before
tele = BootstrapFewShot(metric=category_match, max_bootstrapped_demos=4, max_labeled_demos=4)
optimized = tele.compile(program, trainset=trainset)   # self-improve from examples + metric
opt = evaluate(optimized, devset)                      # measure after
```

**Delta-style analytics** — write metrics, read them back (Parquet locally; Delta in prod):

```python
df.to_parquet("runs.parquet", index=False)             # local stand-in
# Databricks:  spark.createDataFrame(rows).write.format("delta").mode("append").saveAsTable(...)
```

## What a correct run looks like

Exact numbers vary by model and run, but you should see a clear lift:

```text
$ python self_improving.py
Model: openai/gpt-4o-mini
train=16  dev=10

[baseline]  dev accuracy = 70.0%
[optimized] dev accuracy = 90.0%

>>> lift: 70.0% -> 90.0%  (+20.0 pts)

Metrics written to runs.parquet (Delta stand-in). Read back:
                      ts     stage      optimizer  accuracy_pct
 2026-09-19T15:04:11+00:00  baseline           none          70.0
 2026-09-19T15:04:11+00:00 optimized BootstrapFewShot          90.0

Compiled program saved -> optimized_program.json
```

The exact percentages matter less than the **direction and the method**: the optimized program
scores higher without you editing a single prompt string.

## Deliverable

- Terminal output showing **baseline**, **optimized**, and the **lift** in points.
- The `runs.parquet` file, with at least one baseline + optimized row pair.
- One paragraph: *why* did accuracy go up, given you never changed the prompt text? (Because
  `BootstrapFewShot` compiled effective few-shot demos into the prompt, selected by your metric.)

## Troubleshooting

- **`AuthenticationError` / no key.** Put `OPENAI_API_KEY` in `labs/.env`, or switch model:
  `DSPY_MODEL=anthropic/claude-haiku-4-5-20251001 python self_improving.py`.
- **Lift is zero or negative.** With tiny data this happens occasionally (baseline was already
  strong, or an unlucky bootstrap). Re-run, raise `max_bootstrapped_demos`, or add train rows.
  Discuss variance — this is why we measure on a held-out set, not vibes.
- **`ModuleNotFoundError: pyarrow`.** `pip install pyarrow` (Parquet engine for pandas).
- **Rate limits / slow.** `num_threads=1` is set for classroom stability; the dev set is small.
- **DSPy version differences.** Written against DSPy 2.5+ (`dspy.LM`, `dspy.ChainOfThought`,
  `dspy.Evaluate`, `BootstrapFewShot`). The `evaluate()` helper guards the return shape.

## Teacher's Playbook

**The one big idea.** Prompt engineering becomes *compilation*. You declare intent (Signature),
pick a strategy (Module), and define success (metric); the optimizer writes the effective prompt
for you and proves it with a number on held-out data. This is the bridge from "prompt tinkering"
to "ML engineering discipline."

**Live-demo script (8 min).**
1. Run once; read out baseline -> optimized -> lift.
2. Open `optimized_program.json` — show the **bootstrapped demos** the optimizer chose. "You
   didn't write these; the optimizer did."
3. Re-run; show `runs.parquet` **appending** — "this is your metrics history, i.e. a Delta table."
4. Point at the Delta one-liner in `write_runs()` — "same shape on Databricks, plus ACID and
   lineage."

**Worked model answer.** Baseline `ChainOfThought` usually lands ~60–80% on the 10-row dev set;
after `BootstrapFewShot` it typically reaches 80–100%. The compiled program contains 3–4
self-generated demos embedded in the prompt.

**Common mistakes + fixes.**
- *Evaluating on the trainset.* Then "improvement" is memorization. Always score on held-out dev.
- *No metric, or a fuzzy one.* The optimizer maximizes exactly what you give it — a vague metric
  yields a vague agent. Ours is a strict category match.
- *Expecting monotonic gains from tiny data.* Show variance across two runs; connect to Day 3
  evaluation. Bigger train/dev sets stabilize the number.
- *Confusing train vs dev roles.* Train = what the optimizer may learn from; dev = the honest
  scoreboard.

**Debrief Q&A.**
- *When does DSPy beat hand-prompting?* When you have examples + a metric, the task repeats at
  scale, or you need to swap models without redoing prompt work.
- *What is a Delta table really giving us over a CSV?* ACID appends, versioning/time-travel,
  schema evolution, and governed lineage — critical when metrics drive deployment decisions.
- *Where does MLflow fit?* Log each compile (params, metric, lift) as an experiment; register and
  serve the winning compiled program.

**What good looks like.** A student who can point to (a) the Signature/Module/metric split, (b) a
measured lift on held-out data, (c) the bootstrapped demos in the saved program, and (d) the
Parquet-as-Delta metrics table with the production one-liner.

---
