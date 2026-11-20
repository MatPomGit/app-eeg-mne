# Raport końcowy

## Środowisko (rzeczywiste wersje)
Python 3.12.3, MNE 1.13.2, NumPy 2.5.4, SciPy 1.18.1, Matplotlib 3.11.2, scikit-learn 1.9.1, pandas 3.0.6,
nbformat 5.11.1, nbclient 0.11.0, XeTeX 3.141592653-2.6-0.999995 (TeX Live 2023/Debian), Linux x86_64.

## Wynik eksperymentu (uczestnik 1, biegi 6/10/14, rzeczywiste dane)
- 45 zdarzeń (21 hands, 24 feet); po kontroli jakości 44 epoki (21 hands, 23 feet), grupy po biegach: 15/14/15.
- GroupKFold (3 biegi): balanced accuracy po foldach 0,93 / 1,0 / 1,0; łącznie (out-of-fold) 0,976.
- Macierz pomyłek [[20, 1], [0, 23]]; klasyfikator większościowy 0,50.
- Losowy StratifiedKFold: 0,88 / 0,93 / 1,0 (w tym zbiorze nie zawyżył wyniku; różnice w granicach szumu przy n = 44).
- Test permutacyjny (200 permutacji, GroupKFold): p = 0,005, średnia permutacji 0,49 (dodatek w notatniku).
- ERD pasma 8-13 Hz (okno 1-3 s, baseline -0,8...-0,2 s), ręce: C3 -55%, Cz -18%, C4 -45%; stopy: C3 +12%, Cz +19%, C4 +18%.
Wyniki dotyczą jednej osoby i 44 prób (eksploracyjne, nie dowód ogólnego mechanizmu).

## Wykryte i poprawione problemy w materiałach wejściowych
Dostarczono wyłącznie plan (.md) i specyfikację; notebook i skrypt `pipeline.py` z opisu nie zostały załączone,
więc pipeline napisano od nowa, a plan zaudytowano:
1. Montaż `standard_1005` jest w MNE 1.13 przestarzały (usunięcie w 1.14): użyto `colin27_1005` (współrzędne identyczne, sprawdzone).
2. Próg peak-to-peak 200 µV (przykład z planu) odrzuca 43 z 45 epok przy filtracji 1-40 Hz: zastąpiono progiem odpornym
   (mediana + 3 skalowane MAD = 722 µV, bez użycia etykiet); decyzja pokazana na slajdzie 18.
3. Plan łączył dB (slajd 24) z normalizacją procentową (slajd 22): ujednolicono do % zmiany mocy.
4. Okno epok -1...4 s zastąpiono -1,5...4,5 s (margines na efekty brzegowe falek Morleta w oknie odniesienia).
5. `concatenate_raws` modyfikuje `raws[0]`: długości biegów (do grup w GroupKFold) zapisywane są przed połączeniem
   (błąd wykryty w trakcie testów: wszystkie epoki trafiały do jednej grupy).
6. Średnia referencja obniża rząd danych do 63: CSP z regularyzacją Ledoit-Wolf (wynik `patterns_.shape = (63, 64)`).
7. Filtracja po konkatenacji: adnotacje EDGE rozdzielają segmenty (domyślne `skip_by_annotation`), brak artefaktów na łączeniach.
8. `np.ndarray.ptp` nie istnieje w NumPy 2: użyto `np.ptp`.
9. Klasyfikator trenowany na epokach z tych samych zdarzeń co analiza jakości (jedna lista epok dla TFR i ML).
10. ICA: komponent kandydat (IC0) jest wskazany, ale nie usuwany (brak kanału EOG; identyfikacja ≠ decyzja).

## Testy wykonane
- 8 testów jednostkowych (`tests/test_project.py`): OK.
- Wykonanie wszystkich fragmentów kodu ze slajdów po kolei oraz notatnika Jupyter (0 błędów w komórkach).
- Pipeline `analysis.py` na rzeczywistych danych; wynik zgodny ze slajdami (0,976; 44 epoki).
- Kompilacja XeLaTeX: 32 strony, 0 błędów; polskie znaki poprawne.
- Audyt wizualny: obejrzano render wszystkich 32 stron; poprawiono nakładające się etykiety, legendy, przepełnienia kodu i podziałek.
  Pozostałe ostrzeżenia `Overfull hbox` (do ok. 30 pt) dotyczą ramek kodu w kilku slajdach; po ostatnich poprawkach nie zauważono obciętej treści.

## Testy niewykonane i ograniczenia
- Pobieranie z physionet.org nie było możliwe w środowisku budowania (brak dostępu do sieci). Trzy pliki EDF (S001R06/R10/R14)
  pozyskano z publicznego mirrora GitHub i zweryfikowano sumami SHA-256 z rejestrem MNE (`eegbci_checksums.txt`): zgodne.
  `eegbci.load_data()` wykonano na tych plikach (bez pobierania). Pierwsze pobranie z PhysioNet nie było testowane.
- Nie testowano innych wersji MNE ani systemów operacyjnych, ani kompilacji bez czcionki Inter (jest ścieżka zapasowa).
- Uczestnik 2 (ćwiczenie) nie był analizowany.
- Bibliografię zweryfikowano wyrywkowo przez wyszukiwanie (DOI zbioru PhysioNet i Tallon-Baudry 1996); pozostałe pozycje z wiedzy autora, warto sprawdzić przed publikacją.
- Styl bibliografii: `ieeetr` (zbliżony do IEEE; `IEEEtran.bst` niedostępny w środowisku).
