"""Jednorazowe i idempotentne usunięcie redakcyjnych treści z notatnika P3.

Zachowuje zapisane wyniki, wykresy, wszystkie komórki obliczeniowe i załącznik.
Nie pobiera ani nie przelicza danych EEG.
"""
import json
import re
from pathlib import Path

NOTEBOOK = Path(__file__).with_name("eeg_P3_ERP_1.6.4.ipynb")


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
        if source != before:
            cell["source"] = source.splitlines(keepends=True)
            changes += 1
        new_cells.append(cell)
    document["cells"] = new_cells
    prose = "\n".join(
        "".join(cell["source"]) for cell in new_cells
        if cell["cell_type"] == "markdown"
    ).casefold()
    for forbidden in ("sprawozdani", "prelegent miał",
                      "przykładowy opis do raportu", "zapis raportu pdf wraz"):
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
