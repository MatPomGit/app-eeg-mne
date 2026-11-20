# Audyt merytoryczny EEG/MNE — 1.0.0 (2026-11-20)

## Zakres
Audyt obejmuje dwa **niezależne** przykłady: (A) ERP CORE, oddball/P3 i dekodowanie celu oraz (B) PhysioNet EEGBCI, wyobrażanie ruchu i CSP+LDA. Ich klasyfikatory, bodźce oraz jednostki walidacji **nie są zamienne**.

## Potwierdzone korekty

1. **Montaż MNE:** od wersji 1.13 nazwę `standard_1005` zastąpiono `colin27_1005`; poprzednia adnotacja w notatniku P3 błędnie przeczyła temu. Kod i opisy ujednolicono z ograniczeniem wersji MNE.
2. **Baseline po ICA:** zastosowanie ICA do epok skorygowanych względem okresu bazowego może zmienić ich średnią sprzed bodźca. Przywrócono korektę `epochs.apply_baseline((-0.2, 0))` po `ica.apply`.
3. **Interpretacja miar:** AUC obliczone na połączonych wynikach decyzyjnych modeli z różnych foldów nie jest tożsame ze średnią AUC foldów. Główne AUC i porównanie podziałów są teraz średnią niezależnych AUC testowych; połączona ROC OOF jest opisana jako poglądowa. Dodatkowo raportowana jest średnia `balanced_accuracy` foldów.
4. **Granice wnioskowania:** przygotowanie EEG (ICA i próg QC) jest wyznaczane oddzielnie z całego zapisu uczestnika, również tego, na którym później testujemy klasyfikator. Brak użycia etykiet nie oznacza, że walidacja całego preprocessing jest nietransdukcyjna. Wskazano zakres oceny offline i wymagania przyszłej walidacji end-to-end.
5. **Dydaktyka:** opisano klasę, obserwację, wektor cech, trening, predykcję, bazę odniesienia, metryki, sens klasyfikatora i jego ograniczenia w obu przykładach.

## Ważne ograniczenia, których nie należy ukrywać

- P3 to uśredniona amplituda ERP w oknie 300–600 ms na Pz; nie jest bezpośrednim testem uwagi. Dekodowanie mówi, czy EEG odróżnia kategorię bodźca, a nie czy uczestnik poprawnie odpowiada.
- EEGBCI używa biegów 6/10/14. Walidacja `GroupKFold` w tym przykładzie uogólnia **między biegami jednej osoby**, nie między osobami. Przedstawienie CSP+LDA jako ogólnego odczytywania intencji byłoby błędne.
- `Fp1` to kanał czołowego EEG wykorzystywany jako **zastępnik sygnału EOG** w przykładzie EEGBCI, nie rzeczywisty kanał EOG. Zidentyfikowanych składowych ICA nie wykluczamy automatycznie z klasyfikatora.
- Krzywe średnich wyobrażania ruchu nie mają takiej samej interpretacji jak bodźcowo zsynchronizowany potencjał P3; w EEGBCI zasadnicze znaczenie mają zmiany mocy mu/ERD-ERS.
- Permutowanie etykiet wewnątrz osób lub biegów zakłada wymienność obserwacji w tych blokach, co może nie zachodzić przy trendach w czasie.
- Odrzucanie epok na podstawie progu wyliczonego z całego zapisu jest metodą eksploracyjną. Dla oceny nowego sygnału parametry wymagają zamrożenia a priori lub estymacji wyłącznie na treningu.

## Weryfikacja
Zmiany notatnika obejmują kod, opisy i metryki eksportu; historycznych wyników nie wolno traktować jako przeliczonych. Wyniki wymagające EEG i dostępu do OSF/PhysioNet należy odtworzyć przez wykonanie pipeline. Automatyczny test statyczny sprawdza integralność JSON notatników, obecność wyjaśnienia klasyfikatorów, nazwę montażu i korektę baseline.

## Źródła
- MNE 1.13.2, changelog: https://mne.tools/stable/changes/v1.13.html
- MNE, ICA: https://mne.tools/stable/auto_tutorials/preprocessing/40_artifact_correction_ica.html
- MNE, ERP: https://mne.tools/stable/auto_tutorials/evoked/30_eeg_erp.html
- MNE, CSP motor imagery: https://mne.tools/stable/auto_examples/decoding/decoding_csp_eeg.html
- scikit-learn, cross-validation: https://scikit-learn.org/stable/modules/cross_validation.html
- scikit-learn, permutation tests: https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.permutation_test_score.html
