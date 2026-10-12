#!/usr/bin/env python3
"""Convert a `# %%` cell-script into a Jupyter notebook (nbformat).

The `.py` companions (labs/*/explore.py) are the source of truth — diffable, git-friendly,
runnable as `python explore.py`, and usable cell-by-cell in VSCode. This regenerates the
student-facing `.ipynb` from one of them so there are never two hand-maintained copies.

    python scripts/py-to-ipynb.py labs/06-RAG-Vector-DB/explore.py            # -> explore.ipynb
    python scripts/py-to-ipynb.py labs/06-RAG-Vector-DB/explore.py out.ipynb

Cell rules (match the companions):
  * `# %% [markdown]`  starts a markdown cell; following `# ...` lines are the rendered text.
  * `# %%`             starts a code cell; following lines are code verbatim.

To embed outputs (offline labs), execute afterwards from the lab folder:
    cd labs/06-RAG-Vector-DB && jupyter nbconvert --to notebook --execute --inplace explore.ipynb
"""
import sys
from pathlib import Path

import nbformat
from nbformat.v4 import new_notebook, new_code_cell, new_markdown_cell


def to_notebook(src: str):
    cells, cur, kind = [], [], None

    def flush():
        if kind is None:
            return
        if kind == "markdown":
            md = "\n".join(l[2:] if l.startswith("# ") else l.lstrip("#").lstrip()
                           if l.startswith("#") else l for l in cur).strip()
            if md:
                cells.append(new_markdown_cell(md))
        else:
            code = "\n".join(cur).strip("\n")
            if code.strip():
                cells.append(new_code_cell(code))

    for line in src.split("\n"):
        s = line.strip()
        if s.startswith("# %% [markdown]"):
            flush(); cur, kind = [], "markdown"; continue
        if s.startswith("# %%"):
            flush(); cur, kind = [], "code"; continue
        cur.append(line)
    flush()

    nb = new_notebook(cells=cells)
    nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3"}
    nb.metadata["language_info"] = {"name": "python"}
    return nb


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: py-to-ipynb.py <explore.py> [out.ipynb]")
    src_path = Path(sys.argv[1])
    out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else src_path.with_suffix(".ipynb")
    nb = to_notebook(src_path.read_text(encoding="utf-8"))
    nbformat.write(nb, str(out_path))
    print(f"wrote {out_path}  ({len(nb.cells)} cells)")


if __name__ == "__main__":
    main()
