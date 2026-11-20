# Korekty metodologiczne P3/ERP CORE

**Wersja:** 1.6.5  
**Data:** 2026-11-20  
**Zakres:** `notebook/eeg_P3_ERP_1.6.4.ipynb` (ścieżka pozostawiona ze względu na istniejące odnośniki).

## Naprawione problemy

1. **Montaż EEG i zgodność z MNE.** Notatnik nieprawidłowo zaprzeczał istnieniu `colin27_1005`. Od MNE 1.13 nazwa `standard_1005` została zastąpiona przez `colin27_1005`. Wybór nazwy odbywa się na podstawie `get_builtin_montages()`, co zachowuje zgodność ze starszymi wersjami.
2. **Kolejność ICA i korekcji linii bazowej.** Epoki przekazywane do ICA są teraz początkowo tworzone z `baseline=None`. Korekcja `(-0.2, 0)` jest stosowana dopiero po `ICA.apply()`. Zmiana chroni przed niejednoznaczną kolejnością operacji i ostrzeżeniami MNE dotyczącymi korekcji baseline przed ICA.
3. **Niezbieżna ICA.** Ostrzeżenie o braku zbieżności nie może być równoznaczne z przyzwoleniem na automatyczne usuwanie komponentów. Model niespełniający kryterium zbieżności nie jest stosowany do epok, co jest jawnie raportowane (`ica_converged`, `ica_applied`, `ica_n_excluded`). Nie oznacza to jednak, że zapis pozbawiony korekcji ICA jest wolny od artefaktów.
4. **Kontrola selekcji epok.** Raport obejmuje odrzucone epoki oddzielnie dla celów i niecelów oraz odsetek odrzuceń. Progi MAD są estymowane osobno dla każdej osoby i pozostają heurystyką, a nie regułą kliniczną.
5. **AUC i test permutacyjny.** Główną metryką jest teraz **średnia AUC po foldach** `GroupKFold`, zgodna z wynikiem używanym przez `permutation_test_score`. AUC obliczana z połączonych prognoz OOF jest oznaczona jako *eksploracyjna*, ponieważ skale ocen różnych modeli nie muszą być porównywalne. Analogiczne rozróżnienie wprowadzono dla losowego `StratifiedKFold`.
6. **Zakres generalizacji.** Podział krzyżowy oddziela osoby przy dopasowywaniu modelu i skalera, ale ICA oraz kontrola jakości korzystają wcześniej z całego, **nieoznakowanego** zapisu każdej osoby. To konfiguracja transdukcyjna, nie pełny pomiar indukcyjnej generalizacji pipeline na nową osobę.
7. **Opis i reprodukowalność.** Skorygowano nieaktualne twierdzenia o instalacji pakietów, czasochłonności analizy i rozmiarze danych dla 30 uczestników. W eksporcie wyniku dodano numer wersji, raport braków zbieżności i porównywalne metryki walidacji.

## Integralność wyników

Dane w `notebook/output_P3/` i zapisane rezultaty w starszym notebooku pochodzą z wykonania **1.6.4**. Zmiana sposobu postępowania przy niezbieżnej ICA może zmienić liczbę odrzuconych epok, średnią P3, wartość testu i parametry modelu. **Nie przenosimy liczb z 1.6.4 do 1.6.5.** Wyczyszczono wyjścia komórek 62 i późniejszych oraz komórki z montażem; pozostałe wcześniejsze wizualizacje poglądowe pozostawiono. Konieczny jest nowy przebieg wszystkich komórek na danych źródłowych.

Testy statyczne sprawdzają strukturę i kontrakty kodu, nie weryfikują wyników empirycznych. Szczególnie potrzebna jest inspekcja wybranych komponentów EOG i udziału epok odrzuconych w obu warunkach.

## Źródła

- [MNE 1.13: zmiany nazw montaży](https://mne.tools/stable/changes/v1.13.html).
- [MNE: ICA i ponowna korekcja baseline po czyszczeniu](https://mne.tools/stable/generated/mne.preprocessing.ICA.html).
- [MNE: korekcja artefaktów przez ICA](https://mne.tools/stable/auto_tutorials/preprocessing/40_artifact_correction_ica.html).
- [MNE-BIDS-Pipeline: ERP CORE i kody zdarzeń P3](https://mne.tools/mne-bids-pipeline/stable/examples/ERP_CORE.html).
- [ERP CORE: artykuł opisujący zbiór](https://pmc.ncbi.nlm.nih.gov/articles/PMC7909723/).
