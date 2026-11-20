# app-eeg-mne

Materiały dydaktyczne dotyczące analizy EEG w MNE-Python. Repozytorium zawiera **dwa różne eksperymenty**:

1. [P3 / ERP CORE: notatnik interaktywny](notebook/eeg_P3_ERP_1.6.4.ipynb) — wizualne zadanie oddball, ERP P3b, ICA, analiza grupowa oraz klasyfikacja z walidacją według uczestników. **Wersja metodologiczna 1.6.5 (2026-11-20)**; dotychczasowa nazwa pliku została zachowana dla zgodności istniejących odnośników.
2. [PhysioNet EEGBCI: prezentacja i pipeline](mne-eeg-presentation/README.md) — wyobrażanie ruchów rąk i stóp, rytmy sensomotoryczne, CSP + LDA. Nie jest to analiza P3.

## Notatnik P3

Komórkę instalacyjną w notatniku należy aktywować w razie braku pakietów. Dane pobierane z OSF wymagają dostępu do internetu (domyślnie 30 osób, w przybliżeniu 1,6 GB samych danych źródłowych). Do demonstracji można ustawić `N_PARTICIPANTS = 5` przed pobieraniem.

Po aktualizacji do 1.6.5 **wyczyszczono wyniki komórek zależnych od poprawionej analizy**. Otwórz notatnik i wykonaj wszystkie komórki po kolei, aby odtworzyć ERP, metryki i zapis wyników. Dane w `notebook/output_P3/` pochodzą z uruchomienia wcześniejszej wersji i są oznaczone jako historyczne; nie stanowią dowodu poprawności wersji 1.6.5.

Zmiany naukowe, ograniczenia i źródła: [notebook/CHANGELOG.md](notebook/CHANGELOG.md).

Testy struktury i kontraktów metodologicznych:

```bash
python -m unittest discover -s notebook/tests -v
```

Testy nie zastępują uruchomienia pełnej analizy na danych ERP CORE ani ręcznej inspekcji artefaktów EEG.
