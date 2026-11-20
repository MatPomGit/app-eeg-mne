# app-eeg-mne

Repozytorium zawiera **dwa niezależne materiały dydaktyczne EEG/MNE**:

- [Analiza ERP CORE P3](notebook/eeg_P3_ERP_1.6.4.ipynb): EEG w paradygmacie oddball, ERP, średnia amplituda P3 oraz klasyfikator `cel / niecel` (regresja logistyczna), walidacja według uczestników.
- [Warsztat MNE: wyobrażanie ruchu](mne-eeg-presentation/README.md): PhysioNet EEGBCI, zmiany mocy mu, CSP + LDA, klasyfikacja `ręce / stopy`, walidacja według biegów tej samej osoby.

**Klasyfikator** uczy się związku między cechami EEG a znanymi etykietami warunków eksperymentu. Wynik testuje możliwość dekodowania bodźca lub zadania, a nie diagnozuje procesów poznawczych. Poszczególne części korzystają z różnych danych, sygnałów i protokołów walidacji.

## Odtwarzanie wyników

Pliki `output_P3/` i `mne-eeg-presentation/output/` zawierają zapisy historycznych wyników; należy ponownie uruchomić właściwy notatnik lub pipeline przed cytowaniem wartości po aktualizacji metody. Duże, uprzednio osadzone wyniki graficzne usunięto z notatnika P3, aby nie prezentować nieaktualnych obliczeń. Gotowe animacje GIF nadal znajdują się w `notebook/output_P3/` i można je ponownie wygenerować w notatniku.

Przegląd metodologiczny i ograniczenia: [audyt naukowy](docs/SCIENTIFIC_AUDIT.md).

## Wersja metodologiczna P3 / ERP CORE

Aktualizacja P3 **v1.6.5 (2026-11-20)** poprawia analizę oddball i klasyfikację `cel / niecel`; nazwę `notebook/eeg_P3_ERP_1.6.4.ipynb` zachowano, aby nie zrywać istniejących odnośników. Szczegóły i ograniczenia opisano w [dzienniku zmian P3](notebook/CHANGELOG.md).

W notatniku P3 wyczyszczono wyniki komórek zależnych od zmienionej metodologii. Pliki w `notebook/output_P3/` są **historyczne** i nie stanowią potwierdzenia aktualnego wariantu. Aby uzyskać nowe wyniki, uruchom wszystkie komórki na danych ERP CORE. Pobranie pełnego zbioru z OSF wymaga internetu i znacznej ilości miejsca (około 1,6 GB danych wejściowych dla 30 osób); do demonstracji można zmniejszyć `N_PARTICIPANTS` do 5.

Testy kontraktów metodologicznych P3:

```bash
python -m unittest discover -s notebook/tests -v
```

Testy strukturalne nie zastępują analizy na danych i wizualnej kontroli artefaktów.
