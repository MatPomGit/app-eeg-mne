"""Jednorazowe i idempotentne usunięcie redakcyjnych treści z notatnika P3.

Zachowuje zapisane wyniki, wykresy, wszystkie komórki obliczeniowe i załącznik.
Nie pobiera ani nie przelicza danych EEG.
"""
import json
import re
from pathlib import Path

NOTEBOOK = Path(__file__).with_name("eeg_P3_ERP_1.6.4.ipynb")

# Wyłącznie opis naukowy przeznaczony dla czytelnika. Wyniki i kod pozostają nietknięte.
PUBLICATION_REWRITES = (
    ("**Co robi kod w kolejnej komórce:**", "**Procedura obliczeniowa:**"),
    ("**Co robi kod:**", "**Procedura obliczeniowa:**"),
    ("**Co powstaje:**", "**Wynik:**"),
    ("**Jak czytać:**", "**Interpretacja:**"),
    ("**Co sprawdzić:**", "**Zakres kontroli:**"),
    ("**Pytanie kontrolne:** ilu uczestników wczytano, a ilu z tych uczestników ma wystarczającą liczbę poprawnych epok w obu warunkach?",
     "**Kontrola liczebności próby:** liczba wczytanych uczestników oraz liczba osób z wystarczającą liczbą poprawnych epok w obu warunkach określają zakres możliwych analiz."),
    ("**Pułapka:** przerwane pobieranie. Uruchom komórkę ponownie: gotowe pliki zostaną pominięte, a uszkodzone wykryje suma MD5.",
     "**Odporność na przerwanie transferu:** przy ponownym pobieraniu poprawne pliki są pomijane, a uszkodzone identyfikowane na podstawie sum MD5."),
    ("**Co widać?**", "**Obserwacja:**"),
    ("Zwróć uwagę na ewentualny szczyt **50/60 Hz** (sieć) i na wysoką moc poniżej 1 Hz (dryf).",
     "Ewentualny szczyt **50/60 Hz** wskazuje na zakłócenia sieciowe, a duża moc poniżej 1 Hz może wskazywać na dryf."),
    ("W macierzy pomyłek sprawdź osobno, jak model radzi sobie z celami (rzadka klasa).",
     "Macierz pomyłek umożliwia osobną ocenę klasyfikacji celów, stanowiących rzadszą klasę."),
    ("**Nie traktuj wyniku jako ogólnej skuteczności:** to kilka osób.",
     "**Ograniczenie uogólnienia:** wynik dotyczy niewielkiej liczby uczestników."),
    ("### Instrukcja interpretacji testu grupowego", "### Interpretacja testu grupowego"),
    ("### Jak przedstawić wynik walidacji?", "### Interpretacja wyniku walidacji"),
    ("### Jak poprawnie zapisać nowy eksperyment w BIDS?", "### Zapis nowego eksperymentu zgodnie z BIDS"),
    ("## 2. Jak przebiega analiza w tym notatniku?", "## 2. Przebieg analizy"),
    ("dlatego trzeba sprawdzać liczbę i charakter wykluczonych składowych oraz raportować brak zbieżności algorytmu.",
     "dlatego ocena jakości obejmuje liczbę i charakter wykluczonych składowych oraz informację o zbieżności algorytmu."),
    ("Raportujemy go w µV oraz liczbę epok odrzuconych dla każdej osoby.",
     "Dla każdej osoby przedstawiane są próg odrzucania w µV oraz liczba odrzuconych epok."),
    ("Jako główną metrykę raportujemy średnią AUC foldów,",
     "Główną metryką jest średnia AUC z części walidacyjnych,"),
    ("AUC połączonych predykcji OOF oraz wykres ROC podajemy opisowo.",
     "AUC połączonych predykcji OOF oraz wykres ROC mają charakter opisowy."),
    ("Raportowanie odsetka zachowanych epok i wiarygodności danych",
     "Określenie odsetka zachowanych epok i ocena jakości danych"),
    ("Jeżeli wzorzec i mapa ERP mają podobny układ przestrzenny, można napisać, że **informacja wykorzystywana przez model wykazuje podobieństwo do rozkładu efektu ERP**.",
     "Podobieństwo układu przestrzennego wzorca i mapy ERP oznacza, że **informacja wykorzystywana przez model wykazuje podobieństwo do rozkładu efektu ERP**."),
    ("**Jak przejść od tabeli do wniosku:** najpierw sprawdź retencję i zbieżność ICA, potem policz / odczytaj różnicę P3 każdej osoby, następnie jej rozkład i oszacowanie grupowe z CI. Wynik klasyfikatora podaj **osobno**;",
     "**Synteza wyników:** ocenę rozpoczyna retencja epok i zbieżność ICA, następnie analizowana jest różnica P3 na poziomie poszczególnych osób, rozkład tych różnic i wynik grupowy z przedziałem ufności. Wyniki klasyfikatora są przedstawiane **oddzielnie**;"),
    ("**Co wykonuje notatnik po uruchomieniu:** pobraliśmy dane BIDS, przygotowaliśmy sygnał",
     "**Zakres analizy:** pobrano dane BIDS, przygotowano sygnał"),
    ("wyznaczyliśmy P3 na Pz w oknie ustalonym a priori, przetestowaliśmy go na poziomie uczestników i zdekodowaliśmy warunki z walidacją według uczestników, porównaniem z podziałem losowym i testem permutacyjnym.",
     "wyznaczono P3 na Pz w oknie ustalonym a priori, porównano warunki na poziomie uczestników i oceniono dekodowanie z walidacją międzyosobniczą, podziałem losowym oraz testem permutacyjnym."),
)

FORBIDDEN_PUBLICATION_PHRASES = (
    "sprawozdani", "raport", "prelegent miał", "co robi kod",
    "co powstaje", "pytanie kontrolne", "co sprawdzić",
    "zwróć uwagę", "uruchom komórkę", "można napisać",
    "przykładowy opis do",
)


def polish_markdown(source):
    for before, after in PUBLICATION_REWRITES:
        source = source.replace(before, after)
    return source


def polish_exporter(source):
    source = source.replace(
        "PDF_FILE = Path('output_P3') / 'eeg_P3_ERP_CORE_raport.pdf'",
        "PDF_FILE = Path('output_P3') / 'eeg_P3_ERP_CORE_analiza.pdf'",
    )
    source = source.replace("html_path = work / 'raport.html'",
                            "html_path = work / 'analiza.html'")
    source = source.replace("pdf-report-cover", "pdf-cover")
    source = source.replace(
        "    # Publikacja nie drukuje kodu eksportera; pozostaje on w zalaczniku.",
        "    # Kod eksportera nie wchodzi do wersji publikacyjnej ani załącznika.",
    )
    if "forbidden_publication_phrases =" not in source:
        marker = "    html, _ = exporter.from_notebook_node(public_notebook)"
        if marker not in source:
            raise ValueError("Nie odnaleziono miejsca kontroli treści PDF")
        guard = """    forbidden_publication_phrases = (
        'sprawozdani', 'raport', 'prelegent miał', 'co robi kod',
        'co powstaje', 'pytanie kontrolne', 'co sprawdzić',
        'zwróć uwagę', 'uruchom komórkę', 'można napisać',
        'przykładowy opis do',
    )
    publication_markdown = '\\n'.join(
        item.source for item in public_notebook.cells
        if item.cell_type == 'markdown'
    ).casefold()
    contamination = [phrase for phrase in forbidden_publication_phrases
                     if phrase in publication_markdown]
    if contamination:
        raise ValueError(
            'Eksport PDF wstrzymano: treści redakcyjne: '
            + ', '.join(contamination)
        )
"""
        source = source.replace(marker, guard + marker)
    if "# Weryfikacja warstwy tekstowej PDF" not in source:
        marker = "    # Dołączamy edytowalny notatnik jako osadzony plik PDF (EmbeddedFiles)."
        if marker not in source:
            raise ValueError("Nie odnaleziono miejsca kontroli wygenerowanego PDF")
        guard = """    # Weryfikacja warstwy tekstowej PDF przed osadzeniem załącznika.
    for page_number, page in enumerate(PdfReader(str(PDF_FILE)).pages, 1):
        page_text = (page.extract_text() or '').casefold()
        found = [phrase for phrase in forbidden_publication_phrases
                 if phrase in page_text]
        if found:
            raise ValueError(
                f'Eksport PDF wstrzymano: strona {page_number} zawiera '
                + ', '.join(found)
            )
    # Dołączamy odbiorczą wersję notatnika jako osadzony plik PDF.
"""
        source = source.replace(marker, guard)
    source = source.replace(
        "notebook_bytes = nbformat.writes(notebook).encode('utf-8')",
        "notebook_bytes = nbformat.writes(public_notebook).encode('utf-8')",
    )
    source = source.replace(
        "    # Powstaje samowystarczalny plik PDF: zawiera drukowany raport i źródło.",
        "    # PDF zawiera analizę i jej odtwarzalny kod źródłowy.",
    )
    return source



def clean_notebook(path=NOTEBOOK):
    document = json.loads(Path(path).read_text(encoding="utf-8"))
    new_cells = []
    changes = 0
    for cell in document["cells"]:
        source = "".join(cell.get("source", []))
        before = source
        if cell["cell_type"] == "markdown":
            if "## 30. Zapis raportu PDF wraz z notatnikiem źródłowym" in source:
                changes += 1
                continue
            source = re.sub(
                r"(?s)\n*## 29\. Przykładowy opis wyników do sprawozdania.*?"
                r"(?=\n## \*\*Bibliografia\*\*)", "\n", source,
            )
            source = source.replace(
                " Prelegent miał za mało sił na tak długi wykład.", ""
            )
            source = re.sub(
                r"(?m)^\*\*Przykładowy opis do raportu \(hipotetyczny\):\*\*.*(?:\n|$)",
                "", source,
            )
            source = re.sub(
                r"(?m)^\*\*Przykładowa konkluzja \(bez liczb\):\*\*.*(?:\n|$)",
                "", source,
            )
            source = source.replace(
                "### Co można napisać o mapach?",
                "### Interpretacja map wzorców i ERP",
            )
            source = source.replace(
                "**Raportowanie źródła danych:** opis metody powinien zawierać nazwę i źródło zbioru, liczebność próby oraz kryteria wykluczenia. Brak pobranych danych uniemożliwia przedstawienie wyników empirycznych.",
                "**Pochodzenie i zakres danych:** zbiór ERP CORE ma udokumentowane źródło i strukturę BIDS. Liczebność próby oraz kryteria wykluczenia wynikają z przebiegu analizy. Brak pobranych danych uniemożliwia przedstawienie wyników empirycznych.",
            )
            source = source.replace(
                "**Zawsze raportuj próg i liczbę odrzuconych epok.**",
                "**Ocena jakości danych obejmuje próg i liczbę odrzuconych epok.**",
            )
            source = source.replace(
                "**Przykład opisowy (nie wynik ERP CORE):** jeśli zachowano 700 z 1000 epok, odsetek zachowanych epok wynosi 70%. Raportujemy zarówno 700, jak i 30% odrzuceń, zamiast pisać jedynie „dane oczyszczono”.",
                "**Przykład obliczeniowy (nie wynik ERP CORE):** zachowanie 700 z 1000 epok oznacza 70% retencji i 30% odrzuceń. Sam odsetek nie potwierdza poprawności pomiaru.",
            )
            source = source.replace(
                "| V | eksport, ograniczenia, zadania, bibliografia |",
                "| V | eksport wyników, ograniczenia, bibliografia |",
            )
        elif cell["cell_type"] == "code" and "def export_full_notebook_pdf():" in source:
            source = source.replace(
                "    html, _ = exporter.from_notebook_node(notebook)",
                """    # Publikacja nie drukuje kodu eksportera; pozostaje on w zalaczniku.
    public_notebook = notebook.copy()
    public_notebook.cells = [
        item for item in notebook.cells
        if not (item.cell_type == 'code'
                and 'def export_full_notebook_pdf():' in item.source)
        and not (item.cell_type == 'markdown'
                and 'Zapis raportu PDF wraz z notatnikiem źródłowym' in item.source)
    ]
    html, _ = exporter.from_notebook_node(public_notebook)""",
            )
            start = source.find(
                "    # Krótka strona tytułowa jednoznacznie oznacza źródło i status wyników."
            )
            end = source.find("    html = html.replace(", start)
            if start >= 0 and end > start:
                cover = '''    # Tytul obejmuje tylko zakres i ograniczenia analizy.
    date = datetime.now().strftime('%Y-%m-%d %H:%M')
    header = f"""<section class="pdf-report-cover">
        <p class="pdf-kicker">ANALIZA EEG · ERP CORE</p>
        <h1>Analiza EEG: potencjał P3</h1>
        <p class="pdf-subtitle">Metody, kod, wizualizacje i wyniki analizy</p>
        <p><strong>Data eksportu:</strong> {escape(date)}</p>
        <p><strong>Zakres:</strong> paradygmat oddball, analiza ERP i dekodowanie typu bodźca.</p>
        <p><strong>Stan danych:</strong> {escape(status)}</p>
        <p>Zapisane wyniki i wykresy mogą pochodzić z wcześniejszego wykonania.
           Interpretacja ilościowa wymaga uruchomienia bieżącej wersji kodu
           oraz weryfikacji jakości danych.</p>
    </section>"""
'''
                source = source[:start] + cover + source[end:]
        if cell["cell_type"] == "markdown":
            source = polish_markdown(source)
        elif cell["cell_type"] == "code" and "def export_full_notebook_pdf():" in source:
            source = polish_exporter(source)
        if source != before:
            cell["source"] = source.splitlines(keepends=True)
            changes += 1
        new_cells.append(cell)
    document["cells"] = new_cells
    prose = "\n".join(
        "".join(cell["source"]) for cell in new_cells
        if cell["cell_type"] == "markdown"
    ).casefold()
    for forbidden in FORBIDDEN_PUBLICATION_PHRASES:
        if forbidden in prose:
            raise ValueError("Znaleziono niedozwolona tresc redakcyjna: " + forbidden)
    if len(document["cells"]) != 126:
        raise ValueError("Niespodziewana liczba komorek po modyfikacji")
    if not changes:
        return False
    Path(path).write_text(
        json.dumps(document, ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8",
    )
    return True


if __name__ == "__main__":
    print("Zmodyfikowano notatnik:", clean_notebook())
