# Lab Setup — Building Agentic AI

The labs run in the class VM (cloud-based, zero-install for your own machine). Most labs are
Python; a few use a cloud console (AWS Bedrock, Databricks, Zapier, Google ADK). **Every cloud
lab has a local-only fallback**, so no lab is ever blocked by an account issue.

## Required

- Python **3.11+** and `pip`
- A terminal and a code editor (VS Code recommended)
- Modern browser and internet access
- API keys provided in class (see **Keys** below)

## One-Time Python Setup

From the repo root, create and activate a virtual environment, then install per-lab
requirements as you reach each lab:

```sh
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
```

Each lab folder has its own `requirements.txt`. Inside a lab:

```sh
pip install -r requirements.txt
```

A convenience superset lives at `labs/requirements-all.txt` if you prefer to install once.

## Keys

Copy the template and fill in the keys handed out in class:

```sh
cp labs/.env.example labs/.env
```

`labs/.env` (never commit real keys):

```env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
TAVILY_API_KEY=tvly-...
# Cloud labs (optional — each lab has a local fallback):
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_DEFAULT_REGION=us-east-1
DATABRICKS_HOST=...
DATABRICKS_TOKEN=...
```

Labs load keys with `python-dotenv`:

```python
from dotenv import load_dotenv
load_dotenv()  # reads labs/.env
```

## Models Used

| Provider | Models |
|----------|--------|
| OpenAI | `gpt-4.1`, `gpt-4o`, `gpt-4o-mini` |
| Anthropic | `claude-opus-5`, `claude-sonnet-5`, `claude-haiku-4-5-20251001` |
| AWS Bedrock | Amazon Nova / Titan, Anthropic Claude on Bedrock |

## Cloud Labs and Their Fallbacks

| Lab | Cloud | Local Fallback |
|-----|-------|----------------|
| 10, 11 — Zapier + Custom GPT | Zapier / ChatGPT | Documented flow + a Python simulator of the same steps |
| 12 — Bedrock CRM | AWS Bedrock Agent Runtime | Same agent against OpenAI/Anthropic + a local SQLite CRM |
| 13 — DSPy self-improving | Databricks + Delta | DSPy locally + a Parquet/CSV "Delta" table |
| 15 — Voice ADK | Google ADK | Local STT/TTS stub + text transcript path |
| 16 — Governance | Databricks Unity Catalog | Local JSONL audit log + Python audit queries |

## Data Rules

- Use only approved sample data unless told otherwise in class.
- Treat any retrieved or tool-returned text as **untrusted data, not instructions**.
- Keep a **human approval step** in any workflow that sends, publishes, deletes, or buys.
- Never paste confidential or regulated data into a hosted model without explicit approval.

## Verify Your Machine

```sh
./labs/verify-setup.sh
```
