"""Buduje notebooks/mne_eeg_workshop.ipynb z fragmentow presentation/code (te same, co na slajdach)
i opcjonalnie wykonuje go (--execute)."""
import re, sys
from pathlib import Path
import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
titles = {}
for line in (ROOT / "notes" / "speaker_notes.md").read_text().splitlines():
    m = re.match(r"## Slajd (\d+)\. (.*)", line)
    if m:
        titles[int(m.group(1))] = m.group(2)
DIDACTIC = {
    26: "**Instrukcja:** sprawdź `X.shape`, `y` oraz `groups`. Każda epoka ma 64 kanały i próbki z okna 0,5–3,5 s; `y` oznacza wyobrażanie obu rąk lub obu stóp, a `groups` identyfikuje bieg. To numer biegu rozdziela trening i test.",
    27: "**Co to jest klasyfikator?** To model przewidujący klasę nieznanej epoki EEG. Pytamy, czy badany wyobrażał sobie ruch obu rąk czy obu stóp. CSP wyznacza filtry przestrzenne i cztery logarytmy wariancji, a LDA na ich podstawie uczy się rozdzielać klasy. Oba kroki są dopasowywane tylko na treningu danego foldu. Nie jest to diagnoza funkcji ruchowych ani odczytywanie dowolnych intencji.",
    28: "**Jak czytać:** dwa biegi służą do nauki, trzeci do testu. Balanced accuracy to średnia czułość obu klas. Porównanie z podziałem losowym jest demonstracją, a nie alternatywnym wynikiem głównym. Ten test ocenia nowe biegi tej samej osoby, nie nowych uczestników.",
    29: "**Po co punkt odniesienia?** Model większościowy zawsze zwraca jedną klasę. Balanced accuracy około 0,5 stanowi właściwy punkt odniesienia. Macierz pomyłek pokazuje, którą klasę model myli i jak często. Wynik CSP+LDA nie uprawnia do wnioskowania o innych uczestnikach.",
}
PERM_DESCRIPTION = "**Ograniczenie:** permutujemy etykiety wewnątrz biegów, zakładając wymienność prób; nie gwarantuje jej z definicji struktura zapisu. Próg QC oszacowano z całości sygnału przed CV (offline/transdukcyjnie)."

nb = nbf.v4.new_notebook()
cells = [nbf.v4.new_markdown_cell(
    "# Analiza EEG z MNE-Python: notatnik do prezentacji\n"
    "Komórki kodu są identyczne z fragmentami na slajdach (`presentation/code/sNN.py`) i wykonują się po kolei "
    "we wspólnej przestrzeni nazw. Dane (PhysioNet EEGBCI, uczestnik 1, biegi 6, 10, 14) pobiera "
    "`eegbci.load_data()`. Katalog danych: zmienna `MNE_DATA` (domyślnie `data/`).")]
cells.append(nbf.v4.new_code_cell(
    'import os, sys\nfrom pathlib import Path\nROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()\n'
    'os.chdir(ROOT)\nos.environ.setdefault("MNE_DATA", str(ROOT / "data"))\n'
    'os.environ.setdefault("MNE_DATASETS_EEGBCI_PATH", os.environ["MNE_DATA"])'))
for p in sorted((ROOT / "presentation" / "code").glob("s[0-9][0-9]*.py"), key=lambda p: p.stem):
    n = int(re.match(r"s(\d+)", p.stem).group(1))
    head = f"## Slajd {n:02d}. {titles.get(n, '')}"
    if p.stem == "s29b":
        head = "## Dodatek: test permutacyjny (ok. 1,5 min)"
    head += "\n\n" + (PERM_DESCRIPTION if p.stem == "s29b" else DIDACTIC.get(n, ""))
    cells.append(nbf.v4.new_markdown_cell(head))
    cells.append(nbf.v4.new_code_cell(p.read_text()))
cells.append(nbf.v4.new_markdown_cell(
    "## Ćwiczenie\n1. `run_subject(subject=2)` (walidacja w obrębie osoby).\n"
    "2. Trening na S1, test na S2.\n3. Porównaj wyniki; parametry wybieraj bez użycia zbioru testowego."))
nb.cells = cells
nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
out = ROOT / "notebooks" / "mne_eeg_workshop.ipynb"
if "--execute" in sys.argv:
    from nbclient import NotebookClient
    NotebookClient(nb, timeout=900, kernel_name="python3", resources={"metadata": {"path": str(ROOT)}}).execute()
nbf.write(nb, out)
print("zapisano", out)
