"""Poprawia redakcję akapitów notatnika P3 bez modyfikowania obliczeń i wyników."""
import copy
import json
import re
from pathlib import Path

PATH = Path(__file__).with_name("eeg_P3_ERP_1.6.4.ipynb")
BT = chr(96)

RESULTS = {
    1: ["Dostępne są parametry analizy, wersje pakietów i ustawienia kolorystyki wykresów. Na tym etapie nie powstają pliki wynikowe."],
    3: ["Powstaje schemat osi czasu z okresem przedbodźcowym i oknem P3. Sygnał EEG pozostaje niezmieniony."],
    8: ["Powstaje schemat drogi od surowego EEG do wniosków na poziomie osoby i grupy."],
    11: ["Powstaje schemat kolejnych etapów analizy."],
    14: ["Powstaje tekst manifestu zakodowany w Base64, rozpakowywany w następnej komórce.",
         "W katalogu §data/ERP_CORE/P3§ znajdują się pliki BIDS, a lista §SUBJECTS§ zawiera identyfikatory uczestników. Integralność istniejących plików jest również sprawdzana."],
    18: ["Powstaje ramka §events_tsv§ z metadanymi zdarzeń. Wyświetlane są przykładowe wiersze i liczebności poszczególnych etykiet."],
    24: ["W pamięci dostępne są obiekt §raw§ (kanały × próbki) i słownik §CH§. Oryginalne pliki §.set§ i §.fdt§ pozostają niezmienione."],
    27: ["W obiekcie §raw§ dostępne są dwa kanały EOG obok kanałów EEG. §FP2§ pozostaje kanałem EEG."],
    30: ["Do obiektu §raw§ przypisano montaż standardowy i utworzono schemat topograficzny. Nie są to współrzędne zmierzone na głowie uczestnika."],
    33: ["Powstaje wykres pięciu kanałów i liczbowe oszacowanie rozstępu VEOG. Przesunięcia na wykresie nie zmieniają próbek."],
    36: ["Powstaje orientacyjny schemat głowy z zaznaczonymi elektrodami Fz, Cz, Pz, Oz, P9, P10 i kanałami EOG."],
    39: ["Dostępne są słowniki §stim§ i §ignored§, liczniki §n_t§ i §n_n§ oraz wykres liczebności zdarzeń."],
    42: ["Powstają wektor częstotliwości, oszacowanie PSD w µV²/Hz i informacja o lokalnym maksimum w paśmie 8–13 Hz."],
    45: ["W pamięci dostępny jest sygnał EEG po zmianie odniesienia oraz porównanie kanałów. Surowe pliki nie są nadpisywane."],
    48: ["W pamięci dostępne są obiekty §raw_erp§ i §raw_ica§ oraz wykres porównawczy. Filtracja może zmienić fazę i amplitudę sygnału."],
    58: ["Powstaje macierz §events§, której pierwsza kolumna zawiera numer próbki, a trzecia kod klasy 1 lub 2. Tworzony jest także wykres osi czasu."],
    61: ["Powstają obiekt §epochs§ (epoki × kanały × próbki), mapa barwna Pz i przykładowe przebiegi pojedynczych prób."],
    64: ["Dostępne są model §ica§, lista §idx§, wyniki korelacji §scores§, epoki po korekcji i topografie składowych."],
    70: ["Wyniki obejmują statystyki §qc_one§, listę zachowanych epok i histogram artefaktów. Odrzucone epoki nie trafiają do ERP."],
    73: ["Powstają dwa obiekty §Evoked§ (§t§ i §n§) oraz wykres przebiegów Pz z pasmami błędu standardowego."],
    76: ["Powstaje wykres pokazujący, jak uśrednianie uwydatnia wspólny składnik odpowiedzi."],
    81: ["Powstają obiekt §Evoked§ o nazwie §diff§, średnia amplituda w µV, maksimum w µV i czas jego wystąpienia w ms."],
    84: ["Powstaje wykres objaśniający amplitudę i latencję składowej P3."],
    87: ["Powstają trzy mapy topograficzne i wartości skrajne różnicy przestrzennej. Mapy nie lokalizują źródeł korowych."],
    92: ["Dostępne są lista §eps§ z epokami uczestników, tabela kontroli jakości §qc_df§ i wykres liczby zachowanych epok."],
    95: ["Powstają macierz §a§, różnice §d§ w µV, statystyki grupowe i dwa wykresy. Każdy uczestnik ma równą wagę."],
    100: ["Powstają macierz §X§ (epoki × kanały EEG × czas), etykiety §y§ (0/1) i identyfikatory uczestników §groups§."],
    103: ["Dostępne są wartości AUC dla poszczególnych części walidacyjnych i punktów czasu, średnia AUC oraz zmienność między częściami walidacyjnymi. Dane grupy testowej nie służą do dopasowania modelu."],
    108: ["Powstają macierz §Xw§ (epoki × kanały), predykcje z walidacji krzyżowej, krzywa ROC, macierz pomyłek i wartość trafności zrównoważonej."],
    111: ["Powstają dwa rysunki objaśniające krzywą ROC i macierz pomyłek."],
    116: ["Wyniki obejmują AUC obu podziałów, rozkład zerowy AUC i wartość p z permutacji w obrębie uczestników."],
    119: ["Powstają wzorzec klas i mapa średniej różnicy P3. Model opisowy nie dowodzi możliwości uogólnienia wyników."],
    122: ["W katalogu §output_P3/§ powstają dwa pliki §*.fif§, pliki §participants_P3.csv§, §results.json§ i §README.md§. Nie zapisuje się tam surowych sygnałów EEG."],
}

SPECIAL = {
    0: [
        ("**Zakres analizy.** (1) Pobrać i wczytać dane EEG zgodnie ze standardem BIDS. (2) Przygotować sygnał: kanały EOG, odniesienie, filtry, epoki, ICA, kontrola jakości. (3) Wyznaczyć potencjał **P3** i przetestować go na grupie osób. (4) Rozróżniać warunki eksperymentalne (bodziec docelowy / niedocelowy) za pomocą klasyfikatora i ocenić go **bez wykorzystania etykiet osób testowych do dopasowania klasyfikatora** (indywidualne ICA i kontrola jakości wykorzystują nieoznaczone sygnały także tych osób; jest to element przetwarzania transdukcyjnego).",
         "Analiza obejmuje wczytanie danych EEG zgodnie ze standardem BIDS, przygotowanie sygnału, wyznaczenie potencjału **P3** i porównanie warunków na poziomie uczestników. Przygotowanie sygnału obejmuje kanały EOG, zmianę odniesienia, filtrację, epokowanie, ICA i kontrolę jakości. Klasyfikator odróżnia bodźce docelowe od niedocelowych bez wykorzystywania etykiet osób testowych do dopasowania modelu. Indywidualne ICA i kontrola jakości uwzględniają jednak nieoznakowane sygnały tych osób, dlatego przetwarzanie ma charakter transdukcyjny."),
        ("**Układ analizy:** metoda → przetwarzanie danych → wynik → interpretacja.",
         "Analiza przebiega od opisu metody przez przetwarzanie danych i prezentację wyników do ich interpretacji."),
        ("**Zbiór.** ERP CORE [1]: 40 zdrowych dorosłych, sześć zadań, siedem klasycznych składowych ERP; używamy zadania **P3** (wzrokowego zadania z rzadkim bodźcem docelowym, tzw. *oddball*). Dane pochodzą z OSF [2].",
         "Zbiór ERP CORE [1] obejmuje dane 40 zdrowych dorosłych, którzy wykonywali sześć zadań pozwalających analizować siedem klasycznych składowych ERP. W tej analizie wykorzystano zadanie **P3**, oparte na wzrokowym paradygmacie rzadkiego bodźca docelowego (*oddball*). Dane pochodzą z OSF [2]."),
        ("**Wymagania.** Python ≥ 3.10, internet przy pierwszym uruchomieniu (5 uczestników ≈ 300 MB), czas obliczeń zależy od liczby uczestników i kosztownego dekodowania w czasie; dla 30 osób potrzeba około 1,6 GB danych źródłowych. Polecenie instalacyjne w pierwszej komórce jest komentarzem i trzeba je uruchomić osobno.",
         "Do wykonania analizy potrzebny jest Python w wersji co najmniej 3.10 oraz dostęp do internetu przy pierwszym pobieraniu danych. Dane pięciu uczestników zajmują około 300 MB, a 30 uczestników około 1,6 GB. Czas obliczeń zależy od liczby osób i kosztu dekodowania w czasie. Polecenie instalacyjne zapisano w komentarzu pierwszej komórki, dlatego w razie potrzeby należy je wykonać osobno."),
        ("**Skróty metod i miar.** ", ""),
    ],
    14: [("**Licencja zbioru:** CC BY 4.0, zgodnie z dokumentacją §mne-bids-pipeline§.",
          "Zgodnie z dokumentacją §mne-bids-pipeline§ dane udostępniono na licencji CC BY 4.0.")],
    17: [("**Wynik etapu:** pasek postępu pobierania, a potem listę uczestników (§['001', '002', ...]§). Każdy uczestnik to ok. 55 MB.",
          "Podczas pobierania wyświetlany jest pasek postępu, a następnie lista identyfikatorów uczestników (§['001', '002', ...]§). Dane jednej osoby zajmują około 55 MB.")],
    26: [("**Wynik etapu:** częstotliwość próbkowania oryginału (wyższa niż użyjemy do analizy; zmniejszymy ją po filtracji), czas zapisu i listę kanałów: elektrody EEG oraz kanały okoruchowe (§HEOG_left§, §HEOG_right§, §VEOG_lower§).",
          "Wyświetlane są pierwotna częstotliwość próbkowania, czas trwania rejestracji oraz lista kanałów EEG i kanałów okoruchowych (§HEOG_left§, §HEOG_right§, §VEOG_lower§). Częstotliwość próbkowania zostanie zmniejszona po filtracji.")],
    29: [("**Wynik etapu:** liczbę kanałów EEG (w ERP CORE 30) i dwa kanały EOG.",
          "Po przetworzeniu sygnału dostępnych jest 30 kanałów EEG i dwa kanały EOG.")],
    48: [("**Wynik etapu:** oczyszczone pasmowo serie EEG, nie „czystsza uwaga” ani oszacowanie procesów psychicznych.",
          "Wynikiem filtracji są sygnały EEG o ograniczonym paśmie częstotliwości. Nie jest to pomiar „czystszej uwagi” ani oszacowanie procesów psychicznych.")],
    64: [("**Wynik po ICA:** zmodyfikowane epoki EEG.",
          "Po zastosowaniu ICA uzyskuje się zmodyfikowane epoki EEG.")],
    72: [("**Przykład obliczeniowy (nie wynik ERP CORE):** zachowanie 700 z 1000 epok oznacza 70% retencji i 30% odrzuceń.",
          "W hipotetycznym przykładzie zachowanie 700 z 1000 epok oznacza 70% zachowanych i 30% odrzuconych epok. Nie są to wartości uzyskane z danych ERP CORE.")],
    83: [("**Przykład hipotetyczny:** „Średnia różnica wyniosła +2,6 µV, a maksimum przypadło na 440 ms”. Taki zapis opisuje pomiar, lecz nie dowodzi istotności efektu ani sprawniejszego funkcjonowania poznawczego tej osoby.",
          "Hipotetyczna średnia różnica +2,6 µV z maksimum po 440 ms ilustruje wartości opisujące ERP, ale nie dowodzi istotności statystycznej ani sprawniejszego funkcjonowania poznawczego badanej osoby.")],
    89: [("**Bezpieczne sformułowanie:** „Największą dodatnią różnicę między warunkami odnotowano nad rejonem ... elektrody ...”. **Nieuprawnione:** „To dowodzi, że obszar X odpowiada za uwagę u tej osoby”.",
          "Na mapie można wskazać elektrody, nad którymi odnotowano największą dodatnią różnicę potencjału między warunkami. Sama topografia EEG nie pozwala jednak przypisać określonemu obszarowi mózgu odpowiedzialności za uwagę badanej osoby.")],
    95: [("**Hipotezy do testu dwustronnego:** H₀ — średnia różnica §cel − niecel§ w populacji wynosi 0 µV; H₁ — różni się od 0 µV.",
          "W teście dwustronnym hipoteza zerowa (H₀) zakłada, że średnia różnica §cel − niecel§ w populacji wynosi 0 µV, natomiast hipoteza alternatywna (H₁), że różni się ona od 0 µV."),
         ("Jeśli konkretna hipoteza przewiduje efekt dodatni, odnotuj kierunek oddzielnie. Sprawdź również rozkład i obserwacje odstające różnic na poziomie osób; test t dla małej próby może być wrażliwy na odstępstwa od założeń.",
          "Jeżeli hipoteza przewiduje efekt dodatni, jej kierunek należy określić osobno. W interpretacji wyników należy uwzględnić rozkład różnic i obserwacje odstające na poziomie uczestników, ponieważ test t przy małej próbie może być wrażliwy na naruszenie założeń."),
         ("Uwaga: z 1–2 osobami wyniki pokazujemy tylko opisowo. Wnioskowanie grupowa wymaga liczby osób wystarczającej do wiarygodnego oszacowania zmienności.",
          "W przypadku jednej lub dwóch osób wyniki należy przedstawiać opisowo. Wnioskowanie grupowe wymaga liczby uczestników wystarczającej do wiarygodnego oszacowania zmienności.")],
    97: [("**Pułapki:** (1) przy kilku osobach test ma małą moc i wynik jest wstępny; (2) dz bywa duże dla silnych efektów ERP, ale z małej próby jest niepewne (patrz przedział ufności); (3) nie testuj epok jako niezależnych obserwacji.",
          "Przy niewielkiej liczbie osób test ma małą moc, a oszacowanie wielkości efektu §dz§ jest niepewne nawet przy dużej wartości punktowej. Niepewność należy ocenić na podstawie przedziału ufności. Epok pojedynczych uczestników nie wolno traktować jako niezależnych obserwacji w analizie grupowej.")],
    102: [("**Przykład:** jeśli cele stanowią 20% prób, bezmyślny model zawsze odpowiadający „bodziec niedocelowy” osiągnie 80% zwykłej trafności mimo że nie wykrywa żadnego celu.",
           "Jeżeli cele stanowią 20% prób, klasyfikator stale przypisujący etykietę „bodziec niedocelowy” uzyska 80% zwykłej trafności, mimo że nie wykryje żadnego celu.")],
    105: [("**Przykład hipotetyczny:** AUC 0,72 w okolicach 420 ms sugeruje, że w tym momencie EEG zawiera informację o statusie bodźca, która częściowo przenosi się na niewidzianych uczestników.",
           "Hipotetyczna wartość AUC równa 0,72 w okolicach 420 ms sugerowałaby, że EEG zawiera wtedy informację o kategorii bodźca, częściowo uogólniającą się na niewidzianych uczestników.")],
    110: [("**Trafność zrównoważona (balanced accuracy):** średnia z czułości dla celów i swoistości dla niecelów.",
           "Trafność zrównoważona (ang. *balanced accuracy*) jest średnią czułości dla celów i swoistości dla niecelów."),
          ("**Przykład hipotetyczny:** AUC = 0,76 i balanced accuracy = 0,68 wskazują na częściową rozróżnialność warunków w zapisie EEG, ale nie na „68% sprawności poznawczej”.",
           "Hipotetyczne wartości AUC = 0,76 i trafności zrównoważonej równej 0,68 wskazywałyby na częściową rozróżnialność warunków w EEG, ale nie na „68% sprawności poznawczej”.")],
    124: [("**Ograniczenia.** Domyślna analiza niewielkiej liczby osób ma charakter dydaktyczny, nie stanowi pełnego badania populacyjnego; okno P3 i filtry zdefiniowane w kodzie bez prerejestracji, a próg jakości obliczany na danych każdej osoby; klasyfikator liniowy na uśrednionych amplitudach; interpretacja wzorców jest korelacyjna; wyniki są eksploracyjne.",
           "Domyślna analiza obejmuje niewielką liczbę osób i ma charakter dydaktyczny, dlatego nie stanowi pełnego badania populacyjnego. Okno P3 i parametry filtracji określono w kodzie bez prerejestracji, a próg jakości obliczono osobno na danych każdej osoby. Zastosowano liniowy klasyfikator wykorzystujący uśrednione amplitudy. Interpretacja wzorców ma charakter korelacyjny, a wyniki należy traktować jako eksploracyjne.")],
}

PREFIXES = {
    "Główne pytanie badawcze": "W badaniu sprawdzamy, ",
    "Pytanie badawcze": "Sprawdzamy, ",
    "Kluczowe pytanie metodologiczne": "Należy ustalić, ",
    "Wykres po lewej": "Na wykresie po lewej ",
    "Wykres po prawej": "Na wykresie po prawej ",
    "Krzywa ROC": "Krzywa ROC ",
    "Macierz pomyłek": "W macierzy pomyłek ",
}
SIMPLE = set((
    "Interpretacja;Zakres kontroli;Zakres danych;Zakres pomiaru;Wniosek praktyczny;"
    "Alternatywna lokalizacja danych;Pochodzenie i zakres danych;Odporność na przerwanie transferu;"
    "Kontrola liczebności próby;Granica;Ważna różnica;Czego nie należy mieszać;Jednostki;"
    "Pułapka;Ograniczenie;Ograniczenia;Ograniczenie uogólnienia;Częsty błąd interpretacyjny;"
    "50 Hz, a filtr 30 Hz;Interpretacja wykresu;Obserwacja;Granica interpretacji;"
    "Ważne;Istotna zależność;Ważna korekta statystyczna;Uwaga metodologiczna;"
    "Ważne metodologicznie;Synteza wyników;Zakres analizy;Ograniczenia interpretacji;Przykład"
).split(";")) | set(PREFIXES)
LABEL_RE = re.compile(r"\*\*([^*\n]{3,85}):\*\*\s*([^\n]*)")


def first_letter(text, uppercase):
    pattern = r"^([\s*"+BT+r"„'(\[]*)([a-ząćęłńóśźżA-ZĄĆĘŁŃÓŚŹŻ])"
    return re.sub(
        pattern,
        lambda m: m.group(1) + (m.group(2).upper() if uppercase else m.group(2).lower()),
        text,
        count=1,
    )


def polish(path=PATH):
    document = json.loads(path.read_text(encoding="utf-8"))
    if len(document["cells"]) != 126:
        raise ValueError("Nieoczekiwana liczba komórek")
    old = copy.deepcopy(document)
    changed = 0
    for index, cell in enumerate(document["cells"]):
        if cell["cell_type"] != "markdown":
            continue
        source = "".join(cell.get("source", []))
        original = source
        for a, b in SPECIAL.get(index, []):
            a, b = a.replace("§", BT), b.replace("§", BT)
            if a not in source:
                raise ValueError(f"Nie znaleziono fragmentu w komórce {index}: {a[:60]}")
            source = source.replace(a, b, 1)
        for a, b in (
            ("**FIR i IIR.** ", ""),
            ("**Faza i filtracja dwukierunkowa.** ", ""),
            ("**Nie ma ostrej granicy „przepuszcza / zatrzymuje”.** ",
             "Nie ma ostrej granicy między pasmem przepustowym a zaporowym. "),
            ("**Ocena jakości danych obejmuje próg i liczbę odrzuconych epok.** ",
             "Ocena jakości danych obejmuje próg i liczbę odrzuconych epok. "),
        ):
            source = source.replace(a, b)
        if index == 21:
            source = source.replace(
                "Źródła techniczne: [specyfikacja EEG-BIDS](https://bids-specification.readthedocs.io/en/stable/modality-specific-files/electroencephalography.html) i [MNE-BIDS](https://mne.tools/mne-bids/stable/).",
                "Szczegółowe informacje znajdują się w [specyfikacji EEG-BIDS](https://bids-specification.readthedocs.io/en/stable/modality-specific-files/electroencephalography.html) i w [dokumentacji MNE-BIDS](https://mne.tools/mne-bids/stable/)."
            )
        if index == 53:
            source = source.replace(
                "### Filtracja, a próbkowanie - z czego wynika ograniczenie Nyquista?",
                "### Filtracja a próbkowanie: ograniczenie wynikające z twierdzenia Nyquista"
            )
        source = re.sub(
            r"\*\*Procedura obliczeniowa:\*\*\s*([A-ZĄĆĘŁŃÓŚŹŻa-ząćęłńóśźż])",
            lambda m: "Kod " + m.group(1).lower(),
            source,
        )
        result_number = [0]

        def result_rewrite(_match):
            choices = RESULTS.get(index, [])
            if result_number[0] >= len(choices):
                raise ValueError(f"Brakuje poprawnego opisu wyniku w komórce {index}")
            answer = choices[result_number[0]].replace("§", BT)
            result_number[0] += 1
            return answer

        source = re.sub(r"\*\*Wynik:\*\*[^\n]*", result_rewrite, source)
        if result_number[0] != len(RESULTS.get(index, [])):
            raise ValueError(f"Niepełne opisy wyników w komórce {index}")

        for _ in range(8):
            found = [0]

            def rewrite(match):
                label, following = match.group(1), match.group(2)
                if label not in SIMPLE:
                    raise ValueError(f"Nieznana etykieta w komórce {index}: {label}")
                found[0] += 1
                intro = PREFIXES.get(label, "")
                return intro + first_letter(following, not intro)

            source = LABEL_RE.sub(rewrite, source)
            if not found[0]:
                break
        if LABEL_RE.search(source):
            raise ValueError(f"Pozostały etykiety w komórce {index}")
        if source != original:
            changed += 1
            cell["source"] = source.splitlines(keepends=True)

    code = next(c for c in document["cells"] if c["cell_type"] == "code"
                and "def export_full_notebook_pdf():" in "".join(c.get("source", [])))
    exporter = "".join(code["source"])
    for a, b in (
        ("<p><strong>Data eksportu:</strong> {escape(date)}</p>",
         "<p>Dokument wygenerowano {escape(date)}.</p>"),
        ("<p><strong>Zakres:</strong> paradygmat oddball, analiza ERP i dekodowanie typu bodźca.</p>",
         "<p>Analiza obejmuje paradygmat oddball, potencjały ERP i dekodowanie typu bodźca.</p>"),
        ("<p><strong>Stan danych:</strong> {escape(status)}</p>",
         "<p>{escape(status)}</p>"),
    ):
        if a not in exporter:
            raise ValueError("Nie znaleziono fragmentu okładki PDF")
        exporter = exporter.replace(a, b, 1)
    code["source"] = exporter.splitlines(keepends=True)

    old_code = [c for c in old["cells"] if c["cell_type"] == "code"]
    new_code = [c for c in document["cells"] if c["cell_type"] == "code"]
    assert len(old_code) == len(new_code) == 45
    for original, updated in zip(old_code, new_code):
        assert original.get("outputs") == updated.get("outputs"), "Zmiana zapisanych wyników"
        if "def export_full_notebook_pdf():" not in "".join(original["source"]):
            assert original == updated, "Niedozwolona zmiana kodu obliczeniowego"
    prose = "\n".join("".join(c["source"]) for c in document["cells"]
                      if c["cell_type"] == "markdown")
    if LABEL_RE.search(prose) or "Wnioskowanie grupowa" in prose:
        raise ValueError("Pozostały niepoprawne opisy w notatniku")
    if changed < 50:
        raise ValueError(f"Niespodziewanie mała liczba poprawionych komórek: {changed}")
    path.write_text(json.dumps(document, ensure_ascii=False, indent=1) + "\n",
                    encoding="utf-8")
    print(f"Zaktualizowano {changed} komórek opisowych; kod i zapisane wyniki pozostają niezmienione.")


if __name__ == "__main__":
    polish()
