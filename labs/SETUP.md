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
# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

```powershell
# Windows (PowerShell — the default VSCode terminal on the class VM)
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

> On the Windows class VM the terminal is **PowerShell**, where `cp`, `rm`, and `cat` work as
> aliases — so the lab commands copy-paste as-is. The two differences from macOS/Linux are above:
> use `python` (not `python3`) and activate with `.venv\Scripts\Activate.ps1` (not `source`).

Each lab folder has its own `requirements.txt`. Inside a lab:

```sh
pip install -r requirements.txt
```

A convenience superset lives at `labs/requirements-all.txt` if you prefer to install once.

**For the delivered class VM, install the frozen lockfile instead** — exact, smoke-tested,
reproducible versions (so every machine matches what was tested):

```sh
pip install -r labs/requirements-lock.txt
```

The lock pins a coherent, seasoned set (openai 2.x, anthropic 0.9x, langchain/langgraph 1.x,
dspy 3.1.x, numpy 2.4.x) — deliberately a few months behind the bleeding edge so nothing shifts
under the class. Regenerate it only after a fresh smoke test.

## Working in VSCode (your class VM)

Your VM already has **VSCode, Python, and Jupyter** installed. VSCode is where you'll spend the
class — it runs both kinds of lab file (the plain `.py` programs **and** the exploratory
notebooks/cells) in one window, next to a terminal. You won't need any other tool.

**First 5 minutes — do this once:**

1. **Open the repo as a folder.** `File → Open Folder…` → the `Building-Agentic-AI` folder (or
   `code .` from a terminal already in it). Open the *folder*, not a single file, so the editor
   finds the venv and the labs.
2. **Pick the Python interpreter.** `Ctrl+Shift+P` → **Python: Select Interpreter** → choose the
   one ending in `.venv` (the class venv). Do this once and VSCode remembers it. If you skip it,
   the first time you run a cell VSCode will ask you to "Select Kernel" — pick the same `.venv`.
3. **Open the integrated terminal.** `` Ctrl+` `` (Ctrl + backtick). This is where you run the
   lab programs and `pip install`. It opens at the repo root and shares the interpreter you just
   picked.

**Running a lab — the two shapes you'll see:**

- **A program (`.py` CLI lab)** — run it in the terminal, e.g.:

  ```sh
  cd labs/05-Email-Assistant
  pip install -r requirements.txt
  python email_assistant.py --ticket T-1004
  ```

- **An explorer (`explore.py` with `# %%` cells)** — these labs ship an `explore.py` full of
  `# %%` markers. Each marker is a **cell**. Click inside one and press **`Shift+Enter`** to run
  just that cell; output appears in a Python Interactive pane to the side. It's the notebook
  feel, but it's a normal `.py` file (so it reads cleanly and lives in git). The matching
  `explore.ipynb` is the same thing as a classic notebook if you prefer that view — double-click
  it and run cells with `Shift+Enter`.

> **In class:** the instructor drives an `explore.py` cell-by-cell on screen (🔮 *predict* what a
> cell will print before running it), then you do the same in your own VM, then we re-run and
> recap (🗣️). Watch for the **🛠️ Your turn** cell — that's the one scoped change you make
> yourself; the reference answer is in each lab's README **Teacher's Playbook**.

**Handy VSCode moves:**

- `` Ctrl+` `` — toggle the terminal · `Ctrl+Shift+P` — command palette (every command lives here)
- `Shift+Enter` — run the current `# %%` cell (or notebook cell) · `Ctrl+Enter` — run without
  advancing
- `F5` — run a program under the debugger (set a breakpoint by clicking left of a line number)

If a cell ever hangs or the kernel acts up: command palette → **Jupyter: Restart Kernel**, then
re-run from the top cell.

## Keys

### On the class Windows VM — one-command setup (no copy/paste)

The class VMs block clipboard sharing with your own machine, so you can't paste commands or keys
in. So the whole setup is **one short command you type** (not paste). After cloning the repo:

1. Open the terminal from the menu — **Terminal → New Terminal** (the `` Ctrl+` `` shortcut is
   eaten by the browser remote client). If the terminal opens as **cmd**, click the **⌄** next to
   the `+` and pick **PowerShell**.
2. From the repo root, run:

   ```powershell
   cd Building-Agentic-AI
   ./labs/setup.ps1
   ```

`setup.ps1` does everything: creates the virtualenv, installs the pinned packages, copies your keys
from `Desktop\env.txt` into `labs/.env`, confirms the libraries import, and runs the environment
check. If it's blocked with *"running scripts is disabled"*, run once:
`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, then re-run.

To do just the keys step by itself: `./labs/setup-keys.ps1` (copies `Desktop\env.txt` → `labs\.env`).
To re-check the environment anytime: `./labs/verify-setup.ps1`.

### On your own machine

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
| 12 — Bedrock CRM | AWS Bedrock Agent Runtime | OpenAI/Anthropic + local SQLite CRM, **or an offline deterministic stub with no key** |
| 13 — DSPy self-improving | Databricks + Delta | DSPy locally + a Parquet/CSV "Delta" table. **Needs an LLM key** — optimizing prompts requires a model (no LLM-free mode) |
| 15 — Voice ADK | Google ADK | Local STT/TTS stub + text transcript path |
| 16 — Governance | Databricks Unity Catalog | Local JSONL audit log + Python audit queries |

## Data Rules

- Use only approved sample data unless told otherwise in class.
- Treat any retrieved or tool-returned text as **untrusted data, not instructions**.
- Keep a **human approval step** in any workflow that sends, publishes, deletes, or buys.
- Never paste confidential or regulated data into a hosted model without explicit approval.

## Verify Your Machine

```sh
./labs/verify-setup.sh        # macOS / Linux
./labs/verify-setup.ps1       # Windows (PowerShell)
```
