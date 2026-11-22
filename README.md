# app-eeg-mne

Repozytorium zawiera **dwa niezależne materiały dydaktyczne EEG/MNE**:

- [Analiza ERP CORE P3](notebook/eeg_P3_ERP_1.6.4.ipynb): EEG w paradygmacie oddball, ERP, średnia amplituda P3 oraz klasyfikator `cel / niecel` (regresja logistyczna), walidacja według uczestników.
- [Warsztat MNE: wyobrażanie ruchu](mne-eeg-presentation/README.md): PhysioNet EEGBCI, zmiany mocy mu, CSP + LDA, klasyfikacja `ręce / stopy`, walidacja według biegów tej samej osoby.

**Klasyfikator** uczy się związku między cechami EEG a znanymi etykietami warunków eksperymentu. Wynik testuje możliwość dekodowania bodźca lub zadania, a nie diagnozuje procesów poznawczych. Poszczególne części korzystają z różnych danych, sygnałów i protokołów walidacji.

## Odtwarzanie wyników

Pliki `output_P3/` i `mne-eeg-presentation/output/` zawierają zapisy historycznych wyników. **Osadzone w notatniku P3 wykresy, obrazy i wyniki wykonania 1.6.4 zachowano do celów archiwalnych; nie są to wyniki metody 1.6.5.** Przed cytowaniem wartości dla 1.6.5 należy ponownie uruchomić pełną analizę na danych źródłowych. Gotowe animacje GIF nadal znajdują się w `notebook/output_P3/` i można je ponownie wygenerować w notatniku.

Przegląd metodologiczny i ograniczenia: [audyt naukowy](docs/SCIENTIFIC_AUDIT.md).

## Wersja metodologiczna P3 / ERP CORE

Aktualizacja P3 **v1.6.5 (2026-11-20)** poprawia analizę oddball i klasyfikację `cel / niecel`; nazwę `notebook/eeg_P3_ERP_1.6.4.ipynb` zachowano, aby nie zrywać istniejących odnośników. Szczegóły i ograniczenia opisano w [dzienniku zmian P3](notebook/CHANGELOG.md).

W notatniku P3 zachowano **historyczne wyjścia komórek** (wykresy, wartości i liczniki uruchomień). Nie potwierdzają one aktualnego wariantu metodologii 1.6.5. Pliki w `notebook/output_P3/` są również **historyczne** i nie stanowią potwierdzenia aktualnego wariantu. Aby uzyskać nowe wyniki, uruchom wszystkie komórki na danych ERP CORE. Pobranie pełnego zbioru z OSF wymaga internetu i znacznej ilości miejsca (około 1,6 GB danych wejściowych dla 30 osób); do demonstracji można zmniejszyć `N_PARTICIPANTS` do 5.

Testy kontraktów metodologicznych P3:

```bash
python -m unittest discover -s notebook/tests -v
```

Testy strukturalne nie zastępują analizy na danych i wizualnej kontroli artefaktów.

## Eksport publikacyjny PDF

Końcowa komórka notatnika P3 tworzy dokument `notebook/output_P3/eeg_P3_ERP_CORE_analiza.pdf`.
Wersja przeznaczona dla odbiorcy zawiera opis metod, kod obliczeniowy, zachowane wyniki,
wykresy i ograniczenia interpretacji, ale **nie zawiera instrukcji redakcyjnych,
szablonów sprawozdań ani kodu samego eksportera**. Osadzony w PDF notatnik jest
tą samą wersją publikacyjną. Eksport jest wstrzymywany, gdy kontrola tekstu
wykryje niedozwolone treści.

Historyczny plik `eeg_P3_ERP_CORE_raport.pdf` został wycofany z bieżącego
drzewa repozytorium ze względu na przestarzałą treść redakcyjną. Aby otrzymać nowy PDF, należy uruchomić aktualną komórkę
eksportu w notatniku po wykonaniu analizy. Poprawki redakcyjne nie oznaczają
ponownego obliczenia wyników EEG.

## Strona internetowa

Prosta, statyczna strona projektu znajduje się w katalogu [site/](site/) (nie w `docs/`). Można ją uruchomić lokalnie:

```bash
python -m http.server 8000 --directory site
```

Po zmianach w `main` workflow [EEG website](.github/workflows/pages.yml) publikuje zawartość `site/` przez GitHub Pages. W ustawieniach repozytorium **Settings → Pages → Build and deployment** wybierz źródło **GitHub Actions**, jeżeli nie jest jeszcze aktywne. Adres: https://matpomgit.github.io/app-eeg-mne/.

Sprawdzenie strony: `python -m unittest discover -s tests -p 'test_site.py' -v`. Strona jest niezależna od generatorów dokumentacji i nie wymaga Node.js ani pakietów Pythona.
