"""Regression tests for scientific PDF publication without editorial text."""
import ast
import json
import unittest
from pathlib import Path

NOTEBOOK = Path(__file__).resolve().parents[1] / "notebook" / "eeg_P3_ERP_1.6.4.ipynb"


class P3PdfPublicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
        cls.markdown = "\n".join(
            "".join(c["source"]) for c in cls.document["cells"]
            if c["cell_type"] == "markdown"
        ).casefold()
        cls.code = [
            c for c in cls.document["cells"] if c["cell_type"] == "code"
        ]

    def test_no_editorial_report_templates(self):
        for forbidden in (
            "sprawozdani", "przykładowy opis do raportu",
            "przykładowa konkluzja", "prelegent miał",
            "zapis raportu pdf wraz", "raport", "co robi kod",
            "co powstaje", "pytanie kontrolne", "co sprawdzić",
            "zwróć uwagę", "uruchom komórkę", "można napisać",
        ):
            with self.subTest(phrase=forbidden):
                self.assertNotIn(forbidden, self.markdown)

    def test_no_short_labels_in_notebook_prose(self):
        import re

        self.assertIsNone(re.search(r"\*\*[^*\n]{2,85}:\*\*", self.markdown))
        self.assertIsNone(re.search(
            r"\*\*(?:zakres analizy|zbiór|wymagania|ograniczenia)\.\*\*",
            self.markdown,
        ))
        self.assertNotIn("wnioskowanie grupowa", self.markdown)

    def test_pdf_export_excludes_technical_cell_and_absolute_path(self):
        exporters = [
            "".join(c["source"]) for c in self.code
            if "def export_full_notebook_pdf():" in "".join(c["source"])
        ]
        self.assertEqual(len(exporters), 1)
        exporter = exporters[0]
        self.assertIn("public_notebook.cells", exporter)
        self.assertIn("from_notebook_node(public_notebook)", exporter)
        self.assertIn("notebook_bytes = nbformat.writes(public_notebook)", exporter)
        self.assertIn("forbidden_publication_phrases", exporter)
        self.assertIn("publication_markdown", exporter)
        self.assertIn("page.extract_text()", exporter)
        self.assertIn("eeg_P3_ERP_CORE_analiza.pdf", exporter)
        self.assertNotIn("eeg_P3_ERP_CORE_raport.pdf", exporter)
        self.assertIn("ANALIZA EEG · ERP CORE", exporter)
        self.assertNotIn("<strong>Źródło:</strong> {escape(source)}", exporter)
        self.assertNotIn("pdf-report-cover", exporter)
        self.assertNotIn("<strong>Zakres:</strong>", exporter)
        self.assertNotIn("<strong>Stan danych:</strong>", exporter)
        self.assertNotIn("<strong>Data eksportu:</strong>", exporter)

    def test_sanitizer_strengthens_audience_validation(self):
        from runpy import run_path

        sanitizer = run_path(str(NOTEBOOK.parent / "sanitize_pdf_publication.py"))
        exporters = [
            "".join(c["source"]) for c in self.code
            if "def export_full_notebook_pdf():" in "".join(c["source"])
        ]
        self.assertEqual(len(exporters), 1)
        polished = sanitizer["polish_exporter"](exporters[0])
        self.assertIn("editorial_labels = re.search(", polished)
        self.assertIn("skrótowe etykiety redakcyjne", polished)
        self.assertIn("PDF_FILE.unlink(missing_ok=True)", polished)
        self.assertEqual(polished, sanitizer["polish_exporter"](polished))
        ast.parse(polished)

    def test_obsolete_report_pdf_is_not_published(self):
        self.assertFalse(
            (NOTEBOOK.parent / "output_P3" / "eeg_P3_ERP_CORE_raport.pdf").exists()
        )

    def test_analysis_code_and_saved_outputs_remain(self):
        self.assertGreaterEqual(len(self.code), 45)
        self.assertGreaterEqual(
            sum(len(c.get("outputs", [])) for c in self.code), 70
        )
        for cell in self.code:
            ast.parse("".join(cell["source"]))


if __name__ == "__main__":
    unittest.main()
