# Notatki prowadzącego: Analiza EEG z MNE-Python

Notatki w pierwszej osobie, do odczytania. Numeracja zgodna ze slajdami. Limit: 1000 znaków na slajd.

## Slajd 01. Analiza EEG z MNE-Python

Zaczynam od pytania badawczego: czy z krótkiego fragmentu EEG da się przewidzieć, czy osoba otrzymała polecenie wyobrażenia ruchu obu rąk, czy obu stóp? Klasyfikator uczy się przypisywać takim fragmentom znane etykiety. Pokażę cały tor analizy na jednej osobie. Wykres po prawej to prawdziwe EEG z tego zbioru po filtracji 1–40 Hz. Zwracam uwagę, że sygnał wygląda jak szum, a my wydobędziemy z niego informację, czy osoba wyobraża sobie ręce, czy stopy. Zapytam salę: po czym byście to poznali, patrząc tylko na ten wykres? Odpowiedź poznamy na slajdzie 22. Omawiam trzy cele operacyjne ze slajdu.

## Slajd 02. Pipeline analizy EEG

Pokazuję mapę całych zajęć. Kolejność operacji ma znaczenie: filtracja przed epokowaniem, odrzucanie epok przed uczeniem, dopasowanie CSP wyłącznie na zbiorze treningowym. Numery pod nazwami etapów to slajdy, na których dany krok wykonujemy. Fioletowe pola to część analityczna i uczenie maszynowe. Uwaga dydaktyczna: proszę studentów, by zapamiętali, że walidacja jest ostatnim etapem, ale wymaga decyzji podjętych na samym początku, na przykład podziału według biegów.

## Slajd 03. Zbiór EEGBCI

Dane pochodzą z systemu BCI2000 i są udostępnione na PhysioNet [1–3]. Kluczowe: te same kody T1 i T2 znaczą co innego w różnych biegach, więc zawsze mapujemy je według numeru biegu. W biegach 6, 10, 14 T1 to obie ręce, T2 to obie stopy, w trybie wyobrażania. Biegi 5, 9, 13 to ten sam ruch faktycznie wykonywany. Oś czasu: odpoczynek 4,2 s, potem zadanie 4,1 s, na przemian. Ograniczenie: używamy jednej osoby, więc wnioski nie uogólniają się na populację.

## Slajd 04. Instalacja środowiska

Pokazuję cztery polecenia: wirtualne środowisko, aktywacja, instalacja z requirements.txt i weryfikacja. Wynik po prawej to rzeczywiste wersje z mojego uruchomienia: MNE 1.13.2, NumPy 2.5.4, SciPy 1.18.1, Matplotlib 3.11.2, scikit-learn 1.9.1. Przy pierwszym uruchomieniu eegbci.load_data pobierze około 8 MB, więc potrzebny jest internet. Uwaga: wersje bibliotek mają znaczenie, część funkcji i nazw montaży zmienia się między wydaniami MNE. Poproszę studentów o uruchomienie weryfikacji teraz.

## Slajd 05. Struktury danych MNE-Python

To najważniejszy schemat całego wykładu. Raw to kanały razy czas, ciągły zapis. Po wycięciu fragmentów wokół zdarzeń powstaje Epochs: próby, kanały, czas. Uśrednienie prób daje Evoked. Spectrum i TFR to reprezentacje częstotliwościowe: bez osi czasu albo z nią. Każdy obiekt ma inne osie, dlatego tak ważne jest, by przy każdej operacji pytać: którą oś zmieniam albo usuwam? Pytanie do sali: która oś znika przy average()? Odpowiedź: oś prób.

## Slajd 06. Import bibliotek

Kod jest rzeczywisty i uruchamialny, zgodny ze skryptem python/analysis.py. set_log_level na WARNING ucisza komunikaty, żeby slajdy były czytelne. Wynik to wersje bibliotek, które warto zapisywać przy każdej analizie, bo ułatwia to odtworzenie wyników. Po prawej krótko, za co odpowiada każdy pakiet. Uwaga dydaktyczna: pokażę, że import eegbci pochodzi z mne.datasets, czyli dane są częścią ekosystemu MNE.

## Slajd 07. Pobieranie danych

Funkcja load_data przyjmuje numer uczestnika i listę biegów, pobiera pliki EDF i zwraca listę ścieżek. Parametr update_path=False sprawia, że MNE nie pyta interaktywnie o zmianę konfiguracji, co jest ważne w skryptach. Wynik: trzy pliki po 2596 kB. Pliki są identyczne co do bajtu z oficjalnymi, bo sprawdziłem ich sumy kontrolne z rejestrem MNE. Dane nie są dołączone do repozytorium, pobierają się automatycznie.

## Slajd 08. Wczytywanie plików EDF

Wczytuję każdy bieg osobno, potem łączę je funkcją concatenate_raws. Pułapka: concatenate_raws modyfikuje pierwszy obiekt, więc długości biegów trzeba zapisać wcześniej, w zmiennej lens. Zapisane długości posłużą nam do grup w walidacji. Wynik: trzy biegi po 20 000 próbek, razem 60 000. standardize usuwa kropki z nazw kanałów, na przykład Fc5. staje się FC5, co jest potrzebne do dopasowania montażu. Na granicach biegów MNE dodaje adnotacje EDGE i BAD boundary.

## Slajd 09. Metadane EEG

Czytamy z raw.info podstawowe parametry: 160 Hz, 64 kanały, 375 s. Z częstotliwości próbkowania wynika częstotliwość Nyquista 80 Hz. Zwracam uwagę na jednostki: MNE przechowuje EEG w woltach, więc wartość 8,2e-05 V to 82 µV. Typowy błąd studentów to wykresy w woltach z osią bez opisu. Pytanie: ile próbek ma 125-sekundowy bieg? Odpowiedź: 20 000.

## Slajd 10. Rozmieszczenie elektrod

set_montage nadaje kanałom pozycje 3D, bez których nie narysujemy map topograficznych. Użyty montaż colin27_1005 to nowa nazwa dawnego standard_1005, który w MNE 1.13 jest przestarzały; współrzędne są identyczne. Wynik to współrzędne Cz i C3 w metrach. Na mapie zaznaczone są C3, Cz i C4, czyli okolice kory ruchowej, które będą nas interesować. Ograniczenie: montaż standardowy, nie zmierzone pozycje tej osoby.

## Slajd 11. Surowy sygnał EEG

Pokazuję dziesięć sekund z pięciu kanałów. Kanał Fp1 jest czołowy i widać w nim wolne wychylenia, zazwyczaj mrugnięcia. Na C3, Cz i C4 wychylenia są mniejsze. Rozstęp C3 w tym oknie to 419 µV, czyli sygnał jest zdominowany przez wolne zmiany i artefakty, a nie przez rytmy ruchowe. Wniosek: surowego sygnału nie analizujemy bez inspekcji. Pytanie: które wychylenia to prawdopodobnie mrugnięcia i dlaczego?

## Slajd 12. Znaczniki eksperymentalne

Adnotacje to etykiety wstawione przez system stymulacji. W trzech biegach mamy 45 odpoczynków T0, 21 zadań T1 i 24 zadania T2. Rysunek pokazuje wzorzec: odpoczynek, zadanie, odpoczynek. Znacznik to moment, w którym pojawiła się wskazówka, a nie dowód, że ruch był wyobrażany: nie mamy kontroli, czy osoba wykonywała polecenie. Dlatego mówimy o zadaniu, nie o stanie mózgu.

## Slajd 13. Widmo mocy EEG

Widmo Welcha z oknem 4 s daje rozdzielczość 0,25 Hz. Skala logarytmiczna pokazuje spadek mocy ze wzrostem częstotliwości. Wyraźny szczyt w okolicy 10–13 Hz to rytm alfa/μ; średnia moc C3 w paśmie 8–13 Hz to 43,5 µV²/Hz. Pasma zaznaczone kolorami to konwencja, nie granice biologiczne. Uwaga: zapis pochodzi z USA, więc ewentualna zakłócająca sieć to 60 Hz, powyżej naszego zakresu wykresu.

## Slajd 14. Filtracja EEG

Tworzymy dwie kopie: 1–40 Hz do ICA, kontroli jakości i analizy czasowo-częstotliwościowej oraz 7–30 Hz do klasyfikacji. Filtr FIR firwin działa osobno na segmentach rozdzielonych adnotacjami EDGE, więc nie powstają artefakty na łączeniach biegów. Rysunek: przed filtracją widać dryf i duży artefakt w 39. sekundzie, po filtracji dryf znika, artefakt zostaje. Filtracja nie usuwa artefaktów, tylko pasma [7]. Wynik: górna częstotliwość 30 Hz.

## Slajd 15. Referencjonowanie EEG

Potencjał jest zawsze różnicą względem referencji. Mapa po lewej to rozkład potencjału w jednej chwili przy referencji z zapisu, po prawej przy średniej referencji. Średnia referencja zeruje sumę po kanałach, co sprawdzamy w kodzie. Zmienia to topografię i amplitudy, więc nie wolno porównywać map z różnymi referencjami. Konsekwencja techniczna: macierz kowariancji ma rząd 63, więc w CSP stosujemy regularyzację. Pytanie: dlaczego rząd spada o jeden?

## Slajd 16. Wykrywanie zdarzeń

events_from_annotations zamienia adnotacje na macierz zdarzeń: numer próbki, wartość poprzedzająca, kod. Jawnie mapujemy T1 na 1 i T2 na 2, pomijając T0. Mamy 45 zdarzeń: 21 razy ręce i 24 razy stopy. Pierwsze zdarzenie przypada na próbkę 672, czyli 4,2 s po starcie. Rysunek pokazuje ich rozmieszczenie w trzech biegach, przerywane linie to granice biegów. Uwaga: kolejność T1 i T2 jest losowa, ale zrównoważona.

## Slajd 17. Segmentacja EEG

Epoki obejmują okno od −1,5 do 4,5 s względem wskazówki. Rozszerzyłem je względem planu (−1 do 4 s), by falki Morleta nie miały efektów brzegowych w oknie odniesienia. Bez korekcji baseline, bo do TFR korygujemy później. Wynik: tablica 45 prób, 64 kanałów i 961 próbek. Obraz po lewej to C3 we wszystkich epokach, po prawej przykładowe przebiegi dla obu klas. Pojedyncze epoki wyglądają jak szum, rytm ujawni dopiero analiza mocy.

## Slajd 18. Kontrola jakości

Analizujemy rozstęp peak-to-peak każdej epoki w kopii 1–40 Hz. Demonstracyjny próg mediany + 3 MAD jest oszacowany na wszystkich epokach i usuwa jedną z historycznych 45 prób. To selekcja wyłącznie do opisowej analizy ERD/ERS, a nie filtr, który decyduje o tym, jakie próby trafią do treningu i testu klasyfikatora. Model CSP + LDA otrzyma wszystkie poprawnie wycięte epoki zadania z kopii 7–30 Hz, co eliminuje przeciek informacji przez wspólny próg QC. Wyjaśniam studentom, dlaczego selekcja wykonana na testowych danych przed walidacją mogłaby zniekształcić jej wynik.

## Slajd 19. Independent Component Analysis

ICA rozdziela mieszaniny EEG na składowe o przybliżonej niezależności statystycznej; nie identyfikuje automatycznie anatomicznych źródeł. Dopasowuję 20 składowych na danych 1–40 Hz. Procedura find_bads_eog koreluje składowe z kanałem Fp1 jako zastępczym EOG i wskazuje kandydata: składową 0, o czołowej topografii. To jest identyfikacja, nie decyzja. Nie usuwam jej, bo nie mamy kanału EOG ani potwierdzenia przebiegu; ica.exclude pozostaje puste. Pytanie: czemu nietypowa topografia nie musi oznaczać artefaktu?

## Slajd 20. Uśrednianie EEG

Średnia po próbach daje Evoked. Rytmy ruchowe nie mają stałej fazy względem wskazówki, więc przy uśrednianiu się znoszą. Lewy wykres: szare pojedyncze epoki C3 i średnia dla warunku ręce, bliska zeru. Prawy: średnie dla obu klas praktycznie się nie różnią. Wniosek: samo uśrednienie potencjałów nie wystarcza tutaj do uchwycenia zmian rytmów niewyrównanych fazowo; dlatego dodatkowo badamy moc w pasmach, czyli analizę czasowo-częstotliwościową [9]. Mamy 21 i 23 epoki w klasach.

## Slajd 21. Analiza czasowo-częstotliwościowa

Transformacja Morleta z liczbą cykli równą połowie częstotliwości daje kompromis między rozdzielczością czasu i częstotliwości. Wynik ma kształt 64 kanały, 30 częstotliwości, 481 punktów czasu po decymacji. Spektrogram C3: dla warunku ręce po wskazówce wyraźnie słabnie pas około 12 Hz, dla stóp pozostaje silny. Jeśli pokazujemy skalę dB mocy, musimy podać jej poziom odniesienia; decybel sam w sobie jest miarą względną. W tym kroku nie stosujemy jeszcze normalizacji do okresu bazowego. To jeszcze nie jest ERD, bo brakuje odniesienia do okresu bazowego [10].

## Slajd 22. Normalizacja i ERD/ERS

Normalizuję moc procentowo względem okresu od −0,8 do −0,2 s. Wartość ujemna to desynchronizacja związana ze zdarzeniem (ERD), dodatnia to synchronizacja (ERS) [9]. Dla ręki na C3 średnia zmiana mocy 8–13 Hz w oknie 1–3 s wynosi −55%. Wracam do pytania ze slajdu 1: po czym poznalibyśmy zadanie? Po spadku mocy rytmu μ nad korą ruchową. Okno bazowe omija 0,2 s tuż przed wskazówką, by uniknąć przeciekania falek. Ograniczenie: pojedynczy uczestnik.

## Slajd 23. Porównanie warunków eksperymentalnych

Krzywe to średnia moc 8–13 Hz w czasie, w procentach zmiany. Dla rąk na C3 i C4 spadek wynosi odpowiednio 55% i 45%, a na Cz 18%. Dla stóp moc w tych kanałach rośnie o 12–19%. Różny kierunek zmian to cecha, którą wykorzysta klasyfikator. Nie interpretuję tego jako dowodu ogólnego mechanizmu, bo to jedna osoba; zwrócę uwagę, że oczekiwane ogniskowe ERD na Cz dla stóp się tu nie potwierdza.

## Slajd 24. Analiza pasma μ

Trzy mapy to średnia zmiana mocy 8–13 Hz w oknie 1–3 s: dla rąk, dla stóp i ich różnica. Zakresy to od −55% do 42% dla rąk i od −16% do 74% dla stóp. Silny wzrost nad okolicą potyliczną dla stóp może mieć inne wyjaśnienie niż ruch, na przykład rytm alfa związany z widzeniem; nie rozstrzygam tego. Zmiana mocy na elektrodzie nie wskazuje jednoznacznie źródła neuronalnego, bo przewodnictwo objętościowe rozmywa rozkład. Mapy opisują dane, nie lokalizują generatora.

## Slajd 25. Common Spatial Patterns

CSP szuka filtrów przestrzennych maksymalizujących stosunek wariancji jednej klasy do sumy wariancji obu klas. Rozwiązaniem jest uogólniony problem własny. Cechą próby jest logarytm wariancji sygnału po przefiltrowaniu przestrzennym. Na schemacie dwie elipsy to rozkłady dwóch klas w przestrzeni dwóch kanałów, a w1 wskazuje kierunek największego stosunku wariancji [11, 12]. Wartości własne bliskie 1 i 0 odpowiadają filtrom wyróżniającym klasy. Uwaga: CSP jest uczone z etykietami, więc wymaga ostrożnej walidacji.

## Slajd 26. Przygotowanie danych ML

Zaczynam od pytania: jaki jest pojedynczy przykład dla modelu? To trzysekundowa epoka EEG po wskazówce. Macierz X ma osie: próby, kanały, próbki czasu; wektor y zawiera etykiety z protokołu, a groups identyfikatory biegów. Klasyfikator otrzymuje **wszystkie** epoki zadania z pasma 7–30 Hz, niezależnie od eksploracyjnej selekcji QC w analizie ERD/ERS. W oryginalnym zbiorze mamy 45 zdarzeń, ale faktyczna liczba epok zależy od możliwości ich wycięcia. Wyjaśniam rolę grup: jeden bieg nigdy nie znajduje się jednocześnie w treningu i w teście.

## Slajd 27. Klasyfikator CSP + LDA

Wyjaśniam, czym jest klasyfikator: to model nadzorowany, który uczy się na oznaczonych przykładach i przypisuje nowej epoce EEG jedną z dwóch etykiet. Tutaj przewiduje warunek zadania: wskazówkę wyobrażenia ruchu obu rąk albo obu stóp. Po co go tworzymy? Aby sprawdzić, czy EEG zawiera informację predykcyjną, a nie tylko różnice średnich przebiegów. CSP uczy się przestrzennych filtrów maksymalizujących różnicę wariancji klas i tworzy cztery cechy (logarytmy wariancji); LDA wyznacza granicę decyzji. W każdym podziale uczymy obydwa kroki od nowa na dwóch biegach i oceniamy na trzecim; wspólny próg QC jest jednak wyznaczony wcześniej na całym zbiorze. Nie diagnozujemy osoby ani nie odczytujemy intencji poza tym eksperymentem. Regularyzacja Ledoit–Wolf stabilizuje szacowanie kowariancji [13].

## Slajd 28. Walidacja modelu

GroupKFold uczy oba składniki pipeline'u CSP + LDA na dwóch biegach, a ocenia na trzecim. Pokazuję wyniki obliczone przy aktualnym uruchomieniu, a nie wartości zapamiętane z poprzedniej wersji analizy. Losowy StratifiedKFold służy tylko jako porównanie dydaktyczne. Wynik po zmianie kwalifikacji epok może różnić się od archiwalnego. Walidacja dotyczy kolejnego biegu tej samej osoby. Nie obejmuje nowych uczestników, innych urządzeń ani innych sesji. Klasyfikator nie korzysta z eksploracyjnego progu QC.

## Slajd 29. Ocena jakości klasyfikacji

Objaśniam macierz pomyłek: wiersze to rzeczywiste etykiety polecenia, kolumny to predykcje modelu. Balanced accuracy jest średnią czułości dla obu klas; porównujemy ją z klasyfikatorem większościowym, którego zbalansowana dokładność wynosi około 0,5. Prezentuję tylko wynik wygenerowany z aktualnego kodu. Historyczne 0,976 uzyskano po wyselekcjonowaniu 44 epok na podstawie progu QC całego zbioru i **nie jest ono wynikiem bieżącego protokołu**. Test permutacyjny i jego wartość p również wymagają przeliczenia.

## Slajd 30. Interpretacja komponentów CSP

Wzorce, górny rząd, pokazują, jak źródło rzutuje na elektrody, i to je interpretujemy [15]. Filtry, dolny rząd, służą do odejmowania szumu i wyglądają bałaganiarsko: dobrze wyróżniają klasy, ale nie mówią wprost, skąd pochodzi sygnał. Wzorzec 1 skupia się nad centralną lewą okolicą, wzorzec 4 nad tyłem głowy. Liczba składowych to 63 przez średnią referencję. Model dopasowany na całym zbiorze służy tylko do interpretacji, nie do oceny. Interpretacja ma charakter korelacyjny, nie przyczynowy.

## Slajd 31. Eksport wyników

Zapisuję epoki używane do klasyfikacji i wynik bieżącej walidacji do plików FIF oraz JSON. Wyraźnie odróżniam dane do klasyfikacji od epok odrzuconych wyłącznie w eksploracyjnej analizie TFR. Metadane obejmują liczbę ocenionych epok, protokół walidacji i wersję środowiska; taki zapis umożliwia wykrycie, czy ktoś nie prezentuje rezultatu innej wersji analizy. Starsze liczby z poprzedniego przebiegu nie powinny pojawiać się na slajdach jako aktualne.

## Slajd 32. Podsumowanie i zadanie praktyczne

Podsumowuję logikę analizy: od surowego EEG przez czasowo-częstotliwościowy opis rytmów do modelu CSP + LDA, który odróżnia dwie etykiety zadania. Klasyfikator trenujemy osobno na każdym podziale walidacji między biegami. Proszę uruchomić ten sam protokół dla uczestnika 2, a następnie rozważyć odrębne badanie transferu S1 → S2: wszystkie uczone kroki trzeba wówczas dopasować bez dostępu do danych S2. Nie porównujemy wyników bez sprawdzenia, czy dotyczą identycznego doboru epok i metryk.