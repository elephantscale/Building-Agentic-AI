# Instructor day-one runbook — getting students onto the VM

My opening choreography — the sequence I narrate live while students follow on their
ProTech VMs. This is **instructor notes, not student instructions**: steps marked ⚠ depend
on the VM image (Celia / ProTech IT owns it and it can change), so I verify them against the
actual VM each cohort rather than committing them into the student-facing `labs/SETUP.md`.

## The sequence (narrate, students follow)

1. **Copy the repo URL** from the Desktop file `Git Repo URL.txt`.
   - ⚠ The file holds the **bare** link — tell students to **prepend `https://`** (a bare
     `github.com/...` fails in `git clone`).
2. **Clone** in Git Bash (Desktop icon):
   ```
   git clone https://github.com/elephantscale/Building-Agentic-AI
   cd Building-Agentic-AI
   ```
   (Clones over HTTPS, no credentials — repo is readable.)
3. **`code .`** — opens VS Code already rooted in the repo.
4. ⚠ **Workspace Trust** dialog ("Do you trust the authors of the files in this folder?") →
   **Yes, I trust the authors.** Without it the terminal + Python/Jupyter run restricted.
5. ⚠ **Open a PowerShell terminal.** The default integrated terminal opens as **cmd** — switch
   via the `⌄` next to the `+` → **PowerShell**. (`` Ctrl+` `` is eaten by the browser client.)
6. ⚠ **Dismiss the Copilot sign-in** prompt — not needed, and I don't want it ghosting answers
   into the labs. (If not signed in, it does nothing anyway.)
7. **Bootstrap** — one command:
   ```powershell
   ./labs/start-here.ps1
   ```
   Wait for **"Environment looks ready."** (builds venv, installs the locked packages, copies
   `env.txt` → `labs/.env`, imports libs, verifies both API keys).
8. **Activate the venv** for this terminal:
   ```powershell
   .venv\Scripts\Activate.ps1
   ```
   `(.venv)` appears on the prompt.
9. **Open Lab 01** (`labs/01-Agent-Loop-Setup/agent_loop.py`) and begin.

## Notes

- Close the **Welcome** tab before projecting, for a clean editor.
- Validated end-to-end on the live VM (COMPUTER650) 2026-10-18: clone → `start-here.ps1`
  (all PASS, both keys) → Lab 01 ReAct trace ran with live OpenAI calls.
- Why this isn't in `labs/SETUP.md`: the ⚠ steps are image-specific and the repo opens to
  students — a committed student doc that drifts from the image is worse than none. Keep
  `SETUP.md` generic; this runbook is mine.
