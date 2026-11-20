"""Buduje notebooks/mne_eeg_workshop.ipynb z fragmentow presentation/code (te same, co na slajdach)
i opcjonalnie wykonuje go (--execute)."""
import json, re, sys
from pathlib import Path
import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
titles = {}
for line in (ROOT / "notes" / "speaker_notes.md").read_text().splitlines():
    m = re.match(r"## Slajd (\d+)\. (.*)", line)
    if m:
        titles[int(m.group(1))] = m.group(2)
# Canonical descriptions; never overwrite expanded notebook guidance with old inline strings.
DIDACTIC = json.loads((ROOT / "notes" / "notebook_guides.json").read_text(encoding="utf-8"))


nb = nbf.v4.new_notebook()
cells = [nbf.v4.new_markdown_cell(DIDACTIC["__intro__"])]
cells.append(nbf.v4.new_code_cell(
    'import os, sys\nfrom pathlib import Path\nROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()\n'
    'os.chdir(ROOT)\nos.environ.setdefault("MNE_DATA", str(ROOT / "data"))\n'
    'os.environ.setdefault("MNE_DATASETS_EEGBCI_PATH", os.environ["MNE_DATA"])'))
for p in sorted((ROOT / "presentation" / "code").glob("s[0-9][0-9]*.py"), key=lambda p: p.stem):
    n = int(re.match(r"s(\d+)", p.stem).group(1))
    head = f"## Slajd {n:02d}. {titles.get(n, '')}"
    if p.stem == "s29b":
        head = "## Dodatek: test permutacyjny (ok. 1,5 min)"
    head += "\n\n" + DIDACTIC.get(p.stem, "")
    cells.append(nbf.v4.new_markdown_cell(head))
    cells.append(nbf.v4.new_code_cell(p.read_text()))
cells.append(nbf.v4.new_markdown_cell(DIDACTIC["__exercise__"]))
nb.cells = cells
nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
out = ROOT / "notebooks" / "mne_eeg_workshop.ipynb"
if "--execute" in sys.argv:
    from nbclient import NotebookClient
    NotebookClient(nb, timeout=900, kernel_name="python3", resources={"metadata": {"path": str(ROOT)}}).execute()
nbf.write(nb, out)
print("zapisano", out)
