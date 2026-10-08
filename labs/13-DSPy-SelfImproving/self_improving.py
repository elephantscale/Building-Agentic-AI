#!/usr/bin/env python3
"""
Lab 13 — Self-Improving Agent with DSPy + Delta-style analytics.

We build a support-ticket classifier as a DSPy program (Signature + ChainOfThought),
define a metric, measure a BASELINE on a held-out dev set, then run the BootstrapFewShot
optimizer over a small train set and re-measure. The OPTIMIZED program should score higher
with no hand-written prompt — the agent teaches itself from examples + the metric.

We then write the run metrics to a Parquet file and read them back with pandas — a local
stand-in for a Databricks **Delta table**. The Delta equivalent is one line, noted below.

Run:
  cp ../.env.example ../.env         # needs OPENAI_API_KEY (or set DSPY_MODEL to anthropic/...)
  pip install -r requirements.txt
  python self_improving.py
"""

import os
import sys
import json
import datetime
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")  # labs/.env

import dspy
import pandas as pd

HERE = Path(__file__).parent
PARQUET_PATH = HERE / "runs.parquet"

# Cheap, fast default; swap to "anthropic/claude-haiku-4-5-20251001" or "openai/gpt-4.1".
MODEL = os.getenv("DSPY_MODEL", "openai/gpt-4o-mini")

CATEGORIES = ["billing", "technical", "account", "sales", "policy_compliance", "other"]


# ---------------------------------------------------------------------------
# 1. Signature — declare the contract (what), not the prompt (how)
# ---------------------------------------------------------------------------
class ClassifyTicket(dspy.Signature):
    """Classify a customer support ticket into exactly one category."""

    ticket: str = dspy.InputField(desc="the raw customer message")
    category: str = dspy.OutputField(
        desc="one of: billing, technical, account, sales, policy_compliance, other"
    )


# ---------------------------------------------------------------------------
# 2. Module — choose the strategy. ChainOfThought reasons before answering.
# ---------------------------------------------------------------------------
def build_program():
    return dspy.ChainOfThought(ClassifyTicket)


# ---------------------------------------------------------------------------
# 3. Metric — define "better". The optimizer maximizes this.
# ---------------------------------------------------------------------------
def category_match(example, pred, trace=None) -> bool:
    got = (getattr(pred, "category", "") or "").strip().lower()
    want = example.category.strip().lower()
    # tolerate the model wrapping the label in a sentence
    return want == got or want in got


# ---------------------------------------------------------------------------
# Data helpers
# ---------------------------------------------------------------------------
def load_examples(path: Path):
    out = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            out.append(
                dspy.Example(ticket=row["ticket"], category=row["category"]).with_inputs(
                    "ticket"
                )
            )
    return out


def evaluate(program, devset) -> float:
    """Return accuracy as a percentage using dspy.Evaluate (return shape guarded)."""
    from dspy.evaluate import Evaluate

    ev = Evaluate(
        devset=devset, metric=category_match, num_threads=1, display_progress=False
    )
    result = ev(program)
    # DSPy versions return either a float or an object carrying `.score`.
    score = getattr(result, "score", result)
    return round(float(score), 2)


# ---------------------------------------------------------------------------
# Delta-style analytics — write metrics, read them back
# ---------------------------------------------------------------------------
def write_runs(rows):
    df = pd.DataFrame(rows)
    # Local stand-in for a Delta table (append + read back).
    if PARQUET_PATH.exists():
        prev = pd.read_parquet(PARQUET_PATH)
        df = pd.concat([prev, df], ignore_index=True)
    df.to_parquet(PARQUET_PATH, index=False)  # engine: pyarrow
    #
    # === Databricks Delta equivalent (production) ===
    # spark.createDataFrame(rows) \
    #      .write.format("delta").mode("append") \
    #      .saveAsTable("agentics.lab12.dspy_runs")
    # ...then query trends with SQL / Spark, with ACID + time travel + lineage.
    return df


def _has_llm_key(model: str) -> bool:
    provider = model.split("/", 1)[0].lower()
    if provider == "anthropic":
        return bool(os.getenv("ANTHROPIC_API_KEY"))
    if provider == "openai":
        return bool(os.getenv("OPENAI_API_KEY"))
    # Unknown provider prefix: accept if either common key is present.
    return bool(os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY"))


def main():
    # This lab OPTIMIZES an LLM program, so it genuinely needs model access - the
    # "local fallback" here is the Parquet/Delta analytics swap, not an LLM-free mode.
    # Fail clearly instead of deep in a litellm traceback when no key is configured.
    if not _has_llm_key(MODEL):
        provider = MODEL.split("/", 1)[0].lower()
        key = "ANTHROPIC_API_KEY" if provider == "anthropic" else "OPENAI_API_KEY"
        print(
            f"This lab needs an LLM key to run (DSPy bootstraps and scores real model calls).\n"
            f"  - Set {key} in labs/.env, or\n"
            f"  - choose another provider with DSPY_MODEL, e.g. "
            f"DSPY_MODEL=anthropic/claude-haiku-4-5-20251001\n"
            f"Unlike the other cloud labs, there is no offline mode: optimizing prompts "
            f"requires a model. The Databricks part already runs locally (Parquet stands in "
            f"for Delta).",
            file=sys.stderr,
        )
        sys.exit(2)

    dspy.configure(lm=dspy.LM(MODEL, temperature=0.0))
    print(f"Model: {MODEL}")

    trainset = load_examples(HERE / "train.jsonl")
    devset = load_examples(HERE / "dev.jsonl")
    print(f"train={len(trainset)}  dev={len(devset)}\n")

    # ---- Baseline: the program as written, no optimization ----
    program = build_program()
    base = evaluate(program, devset)
    print(f"[baseline]  dev accuracy = {base}%")

    # ---- Optimize: BootstrapFewShot self-generates + selects few-shot demos ----
    from dspy.teleprompt import BootstrapFewShot

    tele = BootstrapFewShot(
        metric=category_match, max_bootstrapped_demos=4, max_labeled_demos=4
    )
    optimized = tele.compile(build_program(), trainset=trainset)
    opt = evaluate(optimized, devset)
    print(f"[optimized] dev accuracy = {opt}%")

    lift = round(opt - base, 2)
    print(f"\n>>> lift: {base}% -> {opt}%  ({'+' if lift >= 0 else ''}{lift} pts)")

    # ---- Write metrics to the (Parquet) analytics table ----
    ts = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    rows = [
        {
            "ts": ts, "model": MODEL, "task": "ticket_classification",
            "stage": "baseline", "optimizer": "none",
            "n_train": len(trainset), "n_dev": len(devset), "accuracy_pct": base,
        },
        {
            "ts": ts, "model": MODEL, "task": "ticket_classification",
            "stage": "optimized", "optimizer": "BootstrapFewShot",
            "n_train": len(trainset), "n_dev": len(devset), "accuracy_pct": opt,
        },
    ]
    df = write_runs(rows)

    print(f"\nMetrics written to {PARQUET_PATH.name} (Delta stand-in). Read back:")
    print(
        df.tail(6)[["ts", "stage", "optimizer", "accuracy_pct"]].to_string(index=False)
    )

    # Optionally persist the compiled program for serving (MLflow in production).
    optimized.save(str(HERE / "optimized_program.json"))
    print("\nCompiled program saved -> optimized_program.json")


if __name__ == "__main__":
    main()
