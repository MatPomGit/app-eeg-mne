# Dane wynikowe analizy P3

- `sub-001_task-P3_ave.fif`: trzy obiekty Evoked pierwszej osoby: target, nontarget, target-minus-nontarget; amplitudy w V.
- `group_task-P3_ave.fif`: średnia po uczestnikach (równa waga osoby) dla obu warunków i różnicy; amplitudy w V.
- `participants_P3.csv`: jeden wiersz na osobę; liczby epok przed/po QC, próg odrzucenia [µV], składowe i zbieżność ICA, liczby odrzuceń w klasach i średnie P3 [µV].
- `results.json`: parametry pipeline, wersje oprogramowania, test grupowy i metryki walidacji, o ile możliwe.

Wykresy pojawiają się w notatniku; nie są automatycznie zapisywane jako obrazy PNG. Surowe dane BIDS nie są kopiowane do katalogu wyników.

## Jak interpretować dane?
W pliku CSV każdy wiersz dotyczy jednej osoby (nie jednej epoki). Kolumny p3_target_uV i p3_nontarget_uV oznaczają średnie amplitudy na Pz w oknie 300–600 ms; p3_difference_uV to różnica cel minus niecel.
Kolumny n_before_qc i n_after_qc opisują liczbę epok, a n_target i n_nontarget liczbę zachowanych bodźców obu rodzajów.
ica_converged i ica_excluded odnoszą się do korekcji artefaktów, zaś threshold_uV to przyjęty próg amplitudowy odrzucania epok.
Plik results.json zawiera wynik testu sparowanego na poziomie osób oraz metryki klasyfikacji, jeśli dało się je obliczyć. Wysokość P3 nie jest bezpośrednim wynikiem testu uwagi, a AUC nie jest odsetkiem poprawnych odpowiedzi uczestników.

Wyniki należy interpretować z uwzględnieniem jakości zapisu i przyjętych założeń analizy.
