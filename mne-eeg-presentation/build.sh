#!/usr/bin/env bash
# Pelna przebudowa: dane -> kod ze slajdow -> rysunki -> PDF -> notatki -> notebook
# Uzycie: ./build.sh            (z testem permutacyjnym: ./build.sh --perm)
set -euo pipefail
cd "$(dirname "$0")"
python python/run_workshop.py "$@"          # wykonuje presentation/code/*.py, zapisuje console/ i figures/
(cd presentation && xelatex -interaction=nonstopmode main.tex >/dev/null && xelatex -interaction=nonstopmode main.tex >/dev/null)
mkdir -p output && cp presentation/main.pdf output/mne_eeg_32_slajdy.pdf
python python/build_notes_pdf.py
python python/build_notebook.py --execute
python -m unittest discover -s tests -v
