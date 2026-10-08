# Agentic on AWS Bedrock

Elephant Scale

---

## Part IV G–H — What We'll Cover

* **Bedrock** — one API in front of many foundation models
* The model menu: **Nova**, **Titan**, **Claude on Bedrock**
* Calling models with **boto3** — the **Converse** API + tool use
* **Bedrock Agents** — action groups, knowledge bases, orchestration
* Connecting a **CRM / database** to an agent
* **Latency & scale** — streaming, model choice, prompt caching
* **Guardrails**, transactions, and enterprise compliance
* Lab 12: a CRM assistant on Bedrock (with a local fallback)

> Same agent loop you already know — now behind an enterprise-grade, IAM-governed API.

Notes:

---

## Why Bedrock

* **Managed, serverless** access to foundation models — no GPUs to run
* **One SDK, many models** — swap providers without rewriting your app
* Runs **inside your AWS account** — IAM, VPC, CloudTrail, KMS come for free
* Data is **not used to train** the base models
* Enterprises pick it for **governance**, not because the models are unique

> Bedrock's product is not a model. It's models plus AWS's security and billing perimeter.

Notes:

---

## The Model Menu

| Family | Who | Good for |
|--------|-----|----------|
| **Amazon Nova** | Amazon | Fast, cheap text + multimodal; tool use |
| **Amazon Titan** | Amazon | Text, embeddings, image; low cost |
| **Claude on Bedrock** | Anthropic | Strongest reasoning + tool use |
| Llama, Mistral, Cohere | Others | Open-weight / specialty options |

* Pick per task: **Nova/Haiku** for routing, **Claude Sonnet** for reasoning.
* Model IDs are region-specific — list them with `bedrock list-foundation-models`.

> Choose the cheapest model that passes your eval — not the biggest one you can afford.

Notes:

---

## Two Ways to Build on Bedrock

* **A) Bedrock Runtime + your own loop** *(what Lab 12 does)*
  - You call `converse` / `converse_stream`, you own the tool loop
  - Maximum control; the same ReAct pattern from Day 1
* **B) Bedrock Agents (managed orchestration)**
  - AWS runs the loop; you declare action groups + knowledge bases
  - Less code, less control; good for standard enterprise wiring

```text
A: your code  -> converse() -> tool -> converse() -> answer   (you hold the loop)
B: Bedrock Agent -> orchestrates action groups + KB          (AWS holds the loop)
```

> Learn the loop by hand (A). Reach for managed Agents (B) when the wiring is standard.

Notes:

---

## The Converse API

* **One uniform request/response shape across every model** — no per-model JSON
* Handles multi-turn `messages`, `system`, `inferenceConfig`, and **`toolConfig`**
* `converse` for a single response; `converse_stream` for token streaming
* Tool use is built in — the model returns a `toolUse` block, you reply with `toolResult`

```text
messages[] + toolConfig  ->  converse()  ->  stopReason == "tool_use"
        ^                                              |
        |  append toolResult block                     v
        +------------------------------------  run the tool
```

> Converse is the portable door. Write the loop once; switch Nova <-> Claude by changing one ID.

Notes:

---

## Calling a Model with boto3

```python
import boto3

client = boto3.client("bedrock-runtime", region_name="us-east-1")

resp = client.converse(
    modelId="us.anthropic.claude-sonnet-5-v1:0",   # or amazon.nova-pro-v1:0
    system=[{"text": "You are a concise CRM assistant."}],
    messages=[{"role": "user", "content": [{"text": "Who is account ACME-1042?"}]}],
    inferenceConfig={"maxTokens": 512, "temperature": 0.2},
)

print(resp["output"]["message"]["content"][0]["text"])
print(resp["usage"], resp["stopReason"])
```

* Auth is **IAM** — no API key in the code; creds come from the environment / role.
* `usage` gives token counts for cost logging; `stopReason` drives your loop.

> If you can call one model this way, you can call all of them — that's the whole point.

Notes:

---

## Tool Use with Converse

* Declare tools in `toolConfig` — a JSON Schema per tool (like the Tool Spec Template)
* Model replies with `stopReason="tool_use"` and a `toolUse` block (name + input)
* You run the tool, then append a `toolResult` block and call `converse` again

```python
toolConfig = {"tools": [{
    "toolSpec": {
        "name": "get_customer",
        "description": "Look up a customer by account id.",
        "inputSchema": {"json": {
            "type": "object",
            "properties": {"account_id": {"type": "string"}},
            "required": ["account_id"],
        }},
    }
}]}
```

> Same tool-spec discipline as Day 2 — name, description, typed schema, safety class.

Notes:

---

## The Bedrock Tool Loop

```text
1. converse(messages, toolConfig)
2. stopReason == "tool_use"?
     yes -> for each toolUse block:
              run tool(name, input)
              append {"toolResult": {"toolUseId": id, "content": [...]}}
            goto 1
     no  -> final text answer, stop
```

* Cap the loop (**max steps**) — a runaway loop is an AWS bill.
* `dangerous` tools (update, delete) get a **human gate** before you run them.
* Log every `toolUse` / `toolResult` to your JSONL audit log.

> The provider changed; the safety rules did not. Cap, gate, log — every time.

Notes:

---

## Bedrock Agents — Managed Orchestration

* You **declare**, AWS **orchestrates** the reason-act loop:
  - **Action groups** — your tools, backed by a Lambda or an OpenAPI schema
  - **Knowledge bases** — managed RAG over your docs (S3 -> vector store)
  - **Orchestration** — the agent plans, calls action groups, reads the KB, answers
* **Guardrails** and **memory** attach to the agent as configuration

```text
User -> Bedrock Agent -> [plan] -> Action Group (Lambda) -> observe
                             |-----> Knowledge Base (RAG) -> observe -> Answer
```

> Action group = a tool. Knowledge base = retrieval. The concepts are the same; AWS runs the loop.

Notes:

---

## Knowledge Bases (Managed RAG)

* Point a knowledge base at **S3**; Bedrock chunks, embeds, and indexes
* Backed by a vector store (**OpenSearch Serverless**, Aurora pgvector, Pinecone)
* Query returns **grounded passages with citations** — the agent cites its sources
* Embeddings via **Titan Embeddings** or Cohere on Bedrock

* Use it when the answer must come from **your** documents, not the model's memory.

> Retrieved text is untrusted data, not instructions — even when AWS retrieved it for you.

Notes:

---

## Connecting a CRM / Database

* An agent reaches your data through a **tool** (action group), never raw SQL from the model
* Pattern: model proposes `account_id` -> **your** code runs the parameterized query
* **Reads** are `safe`; **writes** (update balance, delete record) are `dangerous`

```text
model:  toolUse get_customer(account_id="ACME-1042")
you:    SELECT ... WHERE id = ?      (parameterized — never string-concat)
you:    toolResult -> {"name":"ACME","plan":"team","seats":14}
```

* Least privilege: the agent's DB role is **read-only** until a write is truly needed.

> Never let the model write SQL. It names the intent; your code owns the query and the schema.

Notes:

---

## Latency & Scalability Patterns

* **Right-size the model** — Nova/Haiku for routing & extraction, Sonnet for reasoning
* **Stream** with `converse_stream` — first token fast, better perceived latency
* **Prompt caching** — cache the long, stable system prompt / tool specs; pay once
* **Parallelize** independent tool calls; don't serialize what can run at once
* **Provisioned Throughput** for steady high volume; on-demand for spiky loads
* **Cache tool results** that rarely change (pricing tables, product catalog)

> Most latency and cost is model choice and prompt size — fix those before anything clever.

Notes:

---

## Bedrock Guardrails

* A **policy layer** applied to input and output, independent of the model:
  - **Denied topics** — refuse whole subject areas
  - **Content filters** — hate, violence, sexual, prompt-attack strengths
  - **Sensitive info (PII)** — block or **redact** SSNs, cards, emails
  - **Word filters** + **contextual grounding** (catch ungrounded / off-topic answers)
* Attach to a `converse` call via `guardrailConfig`, or to a managed Agent

```text
input -> [guardrail] -> model -> [guardrail] -> output   (blocked or redacted)
```

> Guardrails are defense in depth — a backstop, not a replacement for your own gates and evals.

Notes:

---

## Transactions & Compliance in the Enterprise

* **IAM least privilege** — a per-agent role, scoped to exactly the actions it needs
* **CloudTrail** logs every Bedrock API call; **CloudWatch** for metrics + alarms
* **KMS** encryption at rest; **VPC endpoints** keep traffic off the public internet
* Model **invocation logging** to S3/CloudWatch — full request/response audit
* Certifications: HIPAA-eligible, SOC, ISO — check per model & region
* **Idempotency + human gate** for money-moving or record-changing actions

> In the enterprise, the model is the easy part. The audit trail is the deliverable.

Notes:

---

## Bedrock vs. Direct APIs — Choosing

| | Direct (OpenAI / Anthropic) | Bedrock |
|---|---|---|
| Setup | API key | AWS account + IAM |
| Governance | provider's | your AWS perimeter |
| Model choice | one vendor | many, one SDK |
| Newest models | first | slight lag |
| Best when | fast start, one vendor | AWS shop, compliance, multi-model |

* Lab 12 runs **both** — Bedrock as the primary path, direct API as the local fallback.

> Pick Bedrock for the perimeter and the model menu. Pick direct for speed and the latest model.

Notes:

---

## Putting It Together

* **Converse** is one portable API over every Bedrock model — tool use included
* You can **own the loop** (Runtime) or **let AWS run it** (Bedrock Agents)
* Data reaches the agent through **tools / action groups**, never raw model SQL
* **Guardrails + IAM + CloudTrail** are why enterprises choose Bedrock
* Tune latency & cost with **model choice, streaming, and prompt caching**
* Every Day-1 rule still holds: **cap, gate, log, treat output as untrusted**

> You now have the enterprise door. Next, build a CRM assistant through it.

Notes:

---

## Lab 12 — CRM Assistant on AWS Bedrock

**Stop here and run Lab 12.**

You will:

1. Build a CRM assistant using the **Converse** API with **tool use**.
2. Wire read tools (`get_customer`, `search_customers`) and a write tool (`update_customer`).
3. Gate the **dangerous** write behind an explicit **human approval** step.
4. Run the loop with a **max-steps cap** and a JSONL audit log.
5. Flip one env var to the **local fallback** — same agent against a direct LLM + SQLite CRM.

**Deliverable:** a runnable `bedrock_crm.py` that answers a lookup and performs a gated update, plus the audit log from one run.

**Time:** 60 minutes

Notes:
