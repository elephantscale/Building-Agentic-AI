# DSPy & Databricks

Elephant Scale

---

## Part IV I–J — What We'll Cover

* The **DSPy idea** — program your LLM, don't hand-tune prompt strings
* **Signatures** — declare *what* (inputs -> outputs), not *how*
* **Modules** — `Predict`, `ChainOfThought`, `ReAct`
* **Metrics + optimizers** — `BootstrapFewShot` makes agents *self-improve*
* When DSPy **beats** hand-prompting (and when it doesn't)
* **Databricks** enterprise integration — Delta, MLflow, model serving
* Lab 13: a self-improving DSPy agent + "Delta" analytics (local fallback)

> Stop editing prompt strings by hand. Declare the behavior and let a compiler optimize it.

Notes:

---

## The Problem DSPy Solves

* Hand-prompting is **brittle string surgery** — tweak wording, re-test, repeat
* Prompts don't **transfer** — new model, redo the fiddling
* No **metric in the loop** — "seems better" is not measurable
* Few-shot examples are **hand-picked** and go stale

* DSPy: treat the prompt as **compiled output**, not source code you hand-write.

> You wouldn't hand-tune assembly. DSPy is the compiler; your program is the source.

Notes:

---

## The DSPy Idea — Programs Over Prompts

* Write a **program** in Python; DSPy generates + optimizes the actual prompts
* Three layers:
  - **Signature** — the typed contract (`question -> answer`)
  - **Module** — the strategy (`Predict`, `ChainOfThought`, `ReAct`)
  - **Optimizer** — compiles the program against a **metric** + examples

```text
Signature (what)  +  Module (how)  ->  Program
Program  +  metric  +  trainset  --compile-->  optimized Program
```

> Separate *intent* (signature) from *strategy* (module) from *tuning* (optimizer).

Notes:

---

## Signatures — Declare the Contract

* A **Signature** names inputs and outputs with descriptions — not a prompt
* Short form for quick work; class form when fields need docs

```python
import dspy

# short form
classify = dspy.Predict("ticket -> category, priority")

# class form — self-documenting fields
class Triage(dspy.Signature):
    """Classify a support ticket."""
    ticket: str = dspy.InputField()
    category: str = dspy.OutputField(desc="billing | technical | account | other")
    priority: str = dspy.OutputField(desc="urgent | normal | low")
```

> A signature is *what you want*. DSPy writes the prompt words for you.

Notes:

---

## Modules — Choose the Strategy

| Module | What it does | Use when |
|--------|--------------|----------|
| `Predict` | Direct input -> output | Simple classify / extract |
| `ChainOfThought` | Adds a reasoning step first | Reasoning, math, judgment |
| `ReAct` | Reason + call tools in a loop | Agents that use tools |
| `ProgramOfThought` | Generates + runs code | Precise calculation |

```python
qa = dspy.ChainOfThought("question -> answer")
agent = dspy.ReAct("question -> answer", tools=[search, calculator])
```

* Swap the module without touching the signature — same contract, new strategy.

> `Predict` for facts, `ChainOfThought` for judgment, `ReAct` for tools. Start simple.

Notes:

---

## Configuring the LM

* One global config points DSPy at any provider (OpenAI, Anthropic, Bedrock, local)
* `dspy.LM` uses LiteLLM under the hood — same string names you already know

```python
import dspy

lm = dspy.LM("openai/gpt-4.1", temperature=0.2)   # or "anthropic/claude-sonnet-5"
dspy.configure(lm=lm)

triage = dspy.ChainOfThought(Triage)
out = triage(ticket="My invoice doubled and the app won't load.")
print(out.category, out.priority)
```

> One line swaps the model. The program — signatures and modules — stays put.

Notes:

---

## Metrics — Define "Better"

* An optimizer needs a **metric**: a function scoring an example vs. the prediction
* Return a bool or a float; this is the objective the compiler maximizes
* This is the same discipline as your eval set (Day 3) — now *in the training loop*

```python
def category_match(example, pred, trace=None):
    return example.category.lower() == pred.category.lower()
```

* Good metrics are **cheap, deterministic, and aligned** with what you actually want.

> No metric, no optimization. "Looks good" cannot be compiled.

Notes:

---

## Optimizers — Self-Improvement from Examples

* An **optimizer** (a "teleprompter") compiles your program to raise the metric
* `BootstrapFewShot` — the model **generates its own** few-shot demos, keeps the ones that pass the metric, and bakes them into the prompt

```python
from dspy.teleprompt import BootstrapFewShot

tele = BootstrapFewShot(metric=category_match, max_bootstrapped_demos=4)
optimized = tele.compile(triage, trainset=train_examples)
```

* Others: `BootstrapFewShotWithRandomSearch`, `MIPROv2` (optimizes instructions too).

> The agent teaches itself: try examples, keep what scores, embed the winners. That's the loop.

Notes:

---

## The Compile Loop, Visualized

```text
   trainset ---> run program on each example
                        |
                 score with metric
                        |
        keep traces that PASS as few-shot demos
                        |
        assemble optimized prompt (demos + instructions)
                        |
   evaluate on held-out devset  ->  before vs. after lift
```

* You measure the **lift**: metric on devset before compile vs. after.
* Lab 13 makes this number real — and writes it to an analytics table.

> Self-improving is not magic. It's search over prompts, scored by your metric.

Notes:

---

## Evaluating a Program

* `dspy.Evaluate` runs a program over a devset and reports the aggregate metric
* Always evaluate on **held-out** data — never the trainset you compiled on

```python
from dspy.evaluate import Evaluate

ev = Evaluate(devset=dev_examples, metric=category_match, num_threads=4)
base_score = ev(triage)        # before optimization
opt_score  = ev(optimized)     # after
print(f"lift: {base_score} -> {opt_score}")
```

> Report before *and* after on held-out data, or the "improvement" is just memorization.

Notes:

---

## When DSPy Beats Hand-Prompting

* **Beats** hand-prompting when:
  - You have (or can label) **examples + a metric**
  - The task is **repeated at scale** — worth optimizing once
  - You need to **swap models** without redoing prompt work
  - You're chaining **multiple LLM steps** (compounding prompt debt)
* **Skip** it when:
  - A **one-off** prompt already works
  - You have **no examples and no metric**
  - The team can't maintain the extra abstraction

> DSPy pays off where prompts are assets you maintain — not for a throwaway one-liner.

Notes:

---

## Databricks — Where This Goes to Production

* Databricks is the **enterprise platform** DSPy programs often ship on:
  - **Delta tables** — reliable, versioned tables (ACID) for training data & run metrics
  - **MLflow** — track runs, params, metrics; register + version the compiled program
  - **Model Serving** — deploy the program behind a REST endpoint, autoscaled
  - **Unity Catalog** — governance, lineage, and access control (Day 5)
* **Foundation Model APIs** serve LLMs inside the Databricks perimeter

> DSPy compiles the agent; Databricks stores its data, tracks its runs, and serves it.

Notes:

---

## Delta Tables (Conceptual)

* A **Delta table** = Parquet files + a transaction log -> ACID, time travel, schema evolution
* Perfect home for **agent run metrics**: append each run, query trends, audit history
* Reads back into Spark **or** pandas — the analytics are just SQL/DataFrames

```text
run metrics --append--> Delta table --query--> dashboards / lineage / eval trends
```

* Lab 13 stand-in: write metrics to **Parquet**, read back with **pandas/pyarrow**.
* The Databricks equivalent: `df.write.format("delta").mode("append").saveAsTable(...)`.

> Same shape, smaller footprint: a Parquet file locally *is* a Delta table without the log.

Notes:

---

## MLflow & Model Serving (Conceptual)

* **MLflow tracking** — log the metric, the model id, the optimizer, the before/after lift
  - every compile becomes a **comparable, reproducible experiment**
* **MLflow Models** — package the compiled DSPy program as an artifact you can version
* **Model Serving** — one click to a scalable REST endpoint; A/B new compiles safely

```text
compile -> log to MLflow (params + metric) -> register model -> serve endpoint
```

> Track every compile like an experiment. "Which prompt is in prod?" should have an exact answer.

Notes:

---

## Putting It Together

* DSPy = **Signatures** (what) + **Modules** (how) + **Optimizers** (tune to a metric)
* `BootstrapFewShot` makes an agent **self-improve** from examples + a metric
* Always measure **before vs. after** on a **held-out** devset
* Use DSPy where prompts are **maintained assets**; skip it for one-offs
* **Databricks** productionizes it: Delta (data), MLflow (tracking), Serving (deploy)
* Locally, **Parquet + pandas** stands in for Delta — same shape, no cluster

> Declare the behavior, define the metric, let the compiler do the prompt engineering.

Notes:

---

## Lab 13 — Self-Improving Agent with DSPy + Delta Analytics

**Stop here and run Lab 13.**

You will:

1. Write a DSPy **Signature** + **Module** (`ChainOfThought`) for a classifier.
2. Define a **metric** and score a **baseline** on a held-out devset with `dspy.Evaluate`.
3. Run **`BootstrapFewShot`** over a small trainset and re-score — measure the **lift**.
4. Write run metrics to a **Parquet** file and read them back with **pandas** (Delta stand-in).
5. Note the **Databricks Delta** equivalent for production.

**Deliverable:** a runnable `self_improving.py` that prints a before/after lift and writes `runs.parquet`.

**Time:** 60 minutes

Notes:
