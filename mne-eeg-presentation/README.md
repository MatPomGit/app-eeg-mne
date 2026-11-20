# Analiza EEG z MNE-Python: prezentacja (32 slajdy), kod i materiały

Prezentacja akademicka (ok. 90 min) z jednym spójnym eksperymentem na rzeczywistych danych
PhysioNet EEG Motor Movement/Imagery (uczestnik 1, biegi 6, 10, 14: wyobrażanie obu rąk vs obu stóp):
od surowego EEG do klasyfikatora CSP + LDA z walidacją między przebiegami.

## Gotowe pliki
- `output/mne_eeg_32_slajdy.pdf`: prezentacja (32 slajdy, 16:9, białe tło)
- `output/mne_eeg_32_slajdy_notes.pdf`: notatki prowadzącego z miniaturami slajdów i bibliografią
- `output/RAPORT.md`: raport końcowy (wersje, testy, wykryte i poprawione problemy, ograniczenia)
- `notes/speaker_notes.md`: notatki (po polsku, pierwsza osoba, max 1000 znaków na slajd)
- `notebooks/mne_eeg_workshop.ipynb`: notatnik z wykonanymi komórkami (te same fragmenty kodu co na slajdach)

## Struktura
```
presentation/  main.tex, preamble.tex, slides/sNN.tex, code/ (kod ze slajdów), console/ (rzeczywiste wyjścia), figures/ (PDF z danych)
python/        analysis.py (pełny pipeline), plotting.py (rysunki), run_workshop.py, build_notebook.py, build_notes_pdf.py
notebooks/     mne_eeg_workshop.ipynb
notes/         speaker_notes.md
references/    references.bib (numeracja [1]-[17] = kolejność pierwszego cytowania na slajdach)
tests/         test_project.py
output/        PDF-y, results/ (epoki FIF, results.json)
```
Kod na slajdach (`presentation/code/sNN.py`) jest jedynym źródłem: `run_workshop.py` wykonuje go po kolei,
zapisuje wyjścia konsoli pokazane na slajdach (`console/`) i generuje rysunki (`figures/`) z tych samych obiektów MNE.

## Instalacja
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```
Wymagane MNE 1.13.x (nazwa montażu `colin27_1005`; w nowszych wersjach `standard_1005` nie istnieje).
Dane (ok. 8 MB) pobiera automatycznie `mne.datasets.eegbci.load_data()` do katalogu `MNE_DATA` (domyślnie `data/`);
nie są dołączone do repozytorium.

## Uruchomienie
```bash
python python/analysis.py --subject 1      # sam pipeline, wynik w output/results/
./build.sh                                 # wszystko: kod -> rysunki -> PDF -> notatki -> notebook -> testy
./build.sh --perm                          # j.w. + test permutacyjny (ok. 1,5 min, dodatek w notatniku)
```

## Kompilacja PDF
Wymagane: XeLaTeX (TeX Live z `beamertheme-metropolis`, `polyglossia`, `listings`, `tikz`), `poppler-utils` (pdftoppm, pdfinfo).
```bash
cd presentation && xelatex main.tex && xelatex main.tex
```
Czcionki: Inter (tekst) i Latin Modern Mono (kod); gdy brak, preambuła przechodzi na Fira Sans / TeX Gyre Heros
i DejaVu Sans Mono. Rysunki Matplotlib używają Inter albo DejaVu Sans.

## Testy
```bash
python -m unittest discover -s tests -v
```
Sprawdzają m.in.: 32 strony PDF, notatki (32, max 1000 znaków, tytuły zgodne ze slajdami), kolejność numeracji
bibliografii, brak czcionek poniżej 10 pt, zgodność `analysis.py` z wynikami na slajdach.

## Ćwiczenie dla studentów
`from analysis import run_subject` -> `run_subject(subject=2)`; następnie trening na S1 i test na S2; porównanie wyników.

## Co klasyfikuje model i dlaczego?
Model **CSP + LDA** rozróżnia epoki EEG zarejestrowane podczas wyobrażania ruchu **obu rąk** oraz **obu stóp**. CSP uczy się filtrów przestrzennych i zamienia sygnał w logarytmy wariancji; LDA przypisuje jedną z dwóch etykiet. To demonstracja dekodowania warunku eksperymentalnego, a nie diagnostyka zdolności ruchowych. Ocena `GroupKFold` obejmuje trzy biegi jednej osoby; nie dowodzi generalizacji na nowych uczestników. ICA na kanale Fp1 wskazuje kandydatów artefaktów, lecz nie jest automatycznie stosowana do danych klasyfikatora. Kryterium QC oszacowano offline z całości zapisu, co ogranicza interpretację wyników jako walidacji end-to-end.

Materiał P3/ERP to **odrębny eksperyment**: jego regresja logistyczna rozróżnia bodźce docelowe i niedocelowe, a nie wyobrażenie rąk i stóp.
