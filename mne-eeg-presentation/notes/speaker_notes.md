# Notatki prowadzącego: Analiza EEG z MNE-Python

Notatki w pierwszej osobie, do odczytania. Numeracja zgodna ze slajdami. Limit: 1000 znaków na slajd.

## Slajd 01. Analiza EEG z MNE-Python

Zaczynam od celu: przez 90 minut przejdziemy cały tor od surowego zapisu do klasyfikatora, na jednym zbiorze i jednym uczestniku. Wykres po prawej to prawdziwe EEG z tego zbioru po filtracji 1–40 Hz. Zwracam uwagę, że sygnał wygląda jak szum, a my wydobędziemy z niego informację, czy osoba wyobraża sobie ręce, czy stopy. Zapytam salę: po czym byście to poznali, patrząc tylko na ten wykres? Odpowiedź poznamy na slajdzie 22. Omawiam trzy cele operacyjne ze slajdu.

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

Plan sugerował próg 200 µV. Sprawdziłem go na danych: odrzuciłby 43 z 45 epok, więc jest bezużyteczny dla filtrowanego zakresu 1–40 Hz. Dlatego używamy progu odpornego: mediana plus trzy skalowane odchylenia MAD, bez użycia etykiet klas. Wynosi 722 µV i odrzuca jedną epokę. Wniosek dydaktyczny: kryteria automatyczne trzeba kalibrować na danych i raportować ich skutek. Ograniczenie: próg jest obliczany na całym zapisie, również na biegu testowym. To niesuperwizowane, transdukcyjne przygotowanie danych; nie można twierdzić, że cały pipeline jest wolny od wpływu danych testowych. Dla ścisłej walidacji end-to-end próg ustalmy wcześniej lub w zbiorze treningowym.

## Slajd 19. Independent Component Analysis

ICA rozdziela mieszaniny EEG na składowe o przybliżonej niezależności statystycznej; nie identyfikuje automatycznie anatomicznych źródeł. Dopasowuję 20 składowych na danych 1–40 Hz. Procedura find_bads_eog koreluje składowe z kanałem Fp1 jako zastępczym EOG i wskazuje kandydata: składową 0, o czołowej topografii. To jest identyfikacja, nie decyzja. Nie usuwam jej, bo nie mamy kanału EOG ani potwierdzenia przebiegu; ica.exclude pozostaje puste. Pytanie: czemu nietypowa topografia nie musi oznaczać artefaktu?

## Slajd 20. Uśrednianie EEG

Średnia po próbach daje Evoked. Rytmy ruchowe nie mają stałej fazy względem wskazówki, więc przy uśrednianiu się znoszą. Lewy wykres: szare pojedyncze epoki C3 i średnia dla warunku ręce, bliska zeru. Prawy: średnie dla obu klas praktycznie się nie różnią. Wniosek: analiza potencjałów wywołanych nie jest odpowiednia dla wyobrażania ruchu; potrzebujemy mocy w pasmach, czyli analizy czasowo-częstotliwościowej [9]. Mamy 21 i 23 epoki w klasach.

## Slajd 21. Analiza czasowo-częstotliwościowa

Transformacja Morleta z liczbą cykli równą połowie częstotliwości daje kompromis między rozdzielczością czasu i częstotliwości. Wynik ma kształt 64 kanały, 30 częstotliwości, 481 punktów czasu po decymacji. Spektrogram C3: dla warunku ręce po wskazówce wyraźnie słabnie pas około 12 Hz, dla stóp pozostaje silny. Skala w decybelach pokazuje moc bezwzględną. To jeszcze nie jest ERD, bo brakuje odniesienia do okresu bazowego [10].

## Slajd 22. Normalizacja i ERD/ERS

Normalizuję moc procentowo względem okresu od −0,8 do −0,2 s. Wartość ujemna to desynchronizacja związana ze zdarzeniem (ERD), dodatnia to synchronizacja (ERS) [9]. Dla ręki na C3 średnia zmiana mocy 8–13 Hz w oknie 1–3 s wynosi −55%. Wracam do pytania ze slajdu 1: po czym poznalibyśmy zadanie? Po spadku mocy rytmu μ nad korą ruchową. Okno bazowe omija 0,2 s tuż przed wskazówką, by uniknąć przeciekania falek. Ograniczenie: pojedynczy uczestnik.

## Slajd 23. Porównanie warunków eksperymentalnych

Krzywe to średnia moc 8–13 Hz w czasie, w procentach zmiany. Dla rąk na C3 i C4 spadek wynosi odpowiednio 55% i 45%, a na Cz 18%. Dla stóp moc w tych kanałach rośnie o 12–19%. Różny kierunek zmian to cecha, którą wykorzysta klasyfikator. Nie interpretuję tego jako dowodu ogólnego mechanizmu, bo to jedna osoba; zwrócę uwagę, że oczekiwane ogniskowe ERD na Cz dla stóp się tu nie potwierdza.

## Slajd 24. Analiza pasma μ

Trzy mapy to średnia zmiana mocy 8–13 Hz w oknie 1–3 s: dla rąk, dla stóp i ich różnica. Zakresy to od −55% do 42% dla rąk i od −16% do 74% dla stóp. Silny wzrost nad okolicą potyliczną dla stóp może mieć inne wyjaśnienie niż ruch, na przykład rytm alfa związany z widzeniem; nie rozstrzygam tego. Zmiana mocy na elektrodzie nie wskazuje jednoznacznie źródła neuronalnego, bo przewodnictwo objętościowe rozmywa rozkład. Mapy opisują dane, nie lokalizują generatora.

## Slajd 25. Common Spatial Patterns

CSP szuka filtrów przestrzennych maksymalizujących stosunek wariancji jednej klasy do sumy wariancji obu klas. Rozwiązaniem jest uogólniony problem własny. Cechą próby jest logarytm wariancji sygnału po przefiltrowaniu przestrzennym. Na schemacie dwie elipsy to rozkłady dwóch klas w przestrzeni dwóch kanałów, a w1 wskazuje kierunek największego stosunku wariancji [11, 12]. Wartości własne bliskie 1 i 0 odpowiadają filtrom wyróżniającym klasy. Uwaga: CSP jest uczone z etykietami, więc wymaga ostrożnej walidacji.

## Slajd 26. Przygotowanie danych ML

Budujemy macierz X o wymiarach 44 próby, 64 kanały, 480 próbek, bo klasyfikujemy okno 0,5–3,5 s, wybrane a priori, nie dobrane na danych. Wektor y zawiera etykiety 1 i 2, czyli 21 rąk i 23 stopy. Grupy to numery biegów: 15, 14 i 15 epok. Wykres pokazuje, że klasy są w każdej grupie zrównoważone. Epoki do klasyfikacji pochodzą z danych 7–30 Hz i tych samych zdarzeń, które przeżyły kontrolę jakości.

## Slajd 27. Klasyfikator CSP + LDA

Klasyfikator to model przewidujący kategorię zadania z krótkiego fragmentu EEG. Tu rozpoznaje, czy badany wyobrażał sobie ruch obu rąk, czy obu stóp. Robimy to, by sprawdzić, czy rytmy sensomotoryczne zawierają informację pozwalającą odróżniać te stany. CSP uczy się przestrzennych filtrów maksymalizujących różnicę wariancji klas i tworzy cztery cechy (logarytmy wariancji); LDA wyznacza granicę decyzji. W walidacji oba kroki uczymy wyłącznie na dwóch biegach i sprawdzamy na trzecim. Nie diagnozujemy osoby ani nie odczytujemy intencji poza tym eksperymentem. Regularyzacja Ledoit–Wolf stabilizuje szacowanie kowariancji [13].

## Slajd 28. Walidacja modelu

GroupKFold dzieli epoki według biegów: trening na dwóch biegach, test na trzecim. Wyniki z historycznego wykonania po biegach to 0,93, 1,0 i 1,0; losowy podział dał 0,88, 0,93 i 1,0 (liczby trzeba potwierdzić po ponownym wykonaniu). Wbrew oczekiwaniom losowy podział nie zawyżył tu wyniku; różnice mieszczą się w szumie przy 44 próbach [14]. Nadal zalecam podział według biegów, bo epoki z jednej sesji są skorelowane i w innych zbiorach losowy podział zawyża wyniki. Nie oceniamy generalizacji na nowe osoby.

## Slajd 29. Ocena jakości klasyfikacji

Zbalansowana dokładność wynosi 0,976, a klasyfikator większościowy daje 0,5. Macierz pomyłek: 20 rąk i 23 stóp rozpoznanych poprawnie, jedna ręka uznana za stopę. Test permutacyjny z 200 permutacjami etykiet (w notatniku) daje p = 0,005, a średnia permutacji to 0,49. Wynik jest wysoki, ale dotyczy jednej osoby i 44 prób, więc przedział niepewności jest szeroki [14]. Nie przedstawiam go jako dowodu na ogólną skuteczność.

## Slajd 30. Interpretacja komponentów CSP

Wzorce, górny rząd, pokazują, jak źródło rzutuje na elektrody, i to je interpretujemy [15]. Filtry, dolny rząd, służą do odejmowania szumu i wyglądają bałaganiarsko: dobrze wyróżniają klasy, ale nie mówią wprost, skąd pochodzi sygnał. Wzorzec 1 skupia się nad centralną lewą okolicą, wzorzec 4 nad tyłem głowy. Liczba składowych to 63 przez średnią referencję. Model dopasowany na całym zbiorze służy tylko do interpretacji, nie do oceny. Interpretacja ma charakter korelacyjny, nie przyczynowy.

## Slajd 31. Eksport wyników

Zapisuję epoki do formatu FIF, a wyniki i wersje oprogramowania do JSON. To minimum reprodukowalności [16]: dane przetworzone, parametry, wynik i środowisko. Wynik w konsoli to dwa pliki w katalogu output/results. Surowych danych nie zapisujemy, bo pobiera je load_data. Dodatkowo w repozytorium jest requirements.txt. Uwaga: w pliku wyników zapisuję także liczbę epok, bo różni się od liczby zdarzeń po kontroli jakości.

## Slajd 32. Podsumowanie i zadanie praktyczne

Skrypt run_subject wykonuje cały tor dla wybranej osoby i daje wynik 0,976 dla uczestnika 1, zgodny z tym, co oglądaliśmy. Zadanie dla studentów: po pierwsze uruchomić dla subject=2, po drugie wytrenować na osobie 1 i przetestować na osobie 2, po trzecie porównać wyniki. Parametry, jak okno czy pasma, wybierają bez użycia zbioru testowego. Ograniczenia: jedna osoba, 44 epoki, parametry ustalone a priori. Dziękuję; pytania.

