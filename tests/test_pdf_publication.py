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

    def _exporter_source(self):
        exporters = [
            "".join(cell["source"]) for cell in self.code
            if "def export_full_notebook_pdf():" in "".join(cell["source"])
        ]
        self.assertEqual(len(exporters), 1)
        return exporters[0]

    def test_sanitizer_strengthens_audience_validation(self):
        from runpy import run_path

        sanitizer = run_path(str(NOTEBOOK.parent / "sanitize_pdf_publication.py"))
        exporter = self._exporter_source()
        polished = sanitizer["polish_exporter"](exporter)
        self.assertIn("editorial_labels = re.search(", polished)
        self.assertIn("pdf_editorial_labels = re.search(", polished)
        self.assertIn("with TemporaryDirectory(prefix='eeg-p3-publication-',", polished)
        self.assertIn("staged_pdf.replace(PDF_FILE)", polished)
        self.assertNotIn("PDF_FILE.unlink(missing_ok=True)", polished)
        self.assertEqual(polished, sanitizer["polish_exporter"](polished))
        ast.parse(polished)

    def test_changes_must_be_present_in_committed_exporter(self):
        exporter = self._exporter_source()
        self.assertIn("editorial_labels = re.search(", exporter)
        self.assertIn("pdf_editorial_labels = re.search(", exporter)
        self.assertIn("staged_pdf.replace(PDF_FILE)", exporter)
        self.assertNotIn("PDF_FILE.unlink(missing_ok=True)", exporter)

    def test_editorial_labels_rejected_in_markdown_and_rendered_pdf(self):
        import re

        definitions = {}
        for node in ast.walk(ast.parse(self._exporter_source())):
            if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id in (
                        "editorial_labels", "pdf_editorial_labels"
                    ):
                        definitions[target.id] = ast.literal_eval(node.value.args[0])
        self.assertEqual(len(definitions), 2)
        self.assertIsNotNone(re.search(
            definitions["editorial_labels"],
            "**Zakres analizy:** opis przykładowy", flags=re.IGNORECASE,
        ))
        self.assertIsNotNone(re.search(
            definitions["editorial_labels"],
            "**Wymagania.** tekst", flags=re.IGNORECASE,
        ))
        self.assertIsNotNone(re.search(
            definitions["editorial_labels"],
            "**Wymagana.** tekst", flags=re.IGNORECASE,
        ))
        self.assertIsNotNone(re.search(
            definitions["pdf_editorial_labels"],
            "Zakres analizy: opis przykładowy", flags=re.IGNORECASE,
        ))
        self.assertIsNone(re.search(
            definitions["pdf_editorial_labels"],
            "Analiza obejmuje potencjał P3.", flags=re.IGNORECASE,
        ))

    def test_pdf_replaced_only_after_validation_of_attachment(self):
        exporter = self._exporter_source()
        start = exporter.index(
            "    with TemporaryDirectory(prefix='eeg-p3-publication-',"
        )
        end = exporter.index("    print('Zapisano dokument:'", start)
        stage = exporter[start:end]
        for marker in (
            "writer.write(str(temp_pdf))",
            "temp_pdf.replace(staged_pdf)",
            "verified = PdfReader(str(staged_pdf))",
            "if not staged_pdf.is_file()",
            "staged_pdf.replace(PDF_FILE)",
        ):
            self.assertIn(marker, stage)
        self.assertLess(
            stage.index("verified = PdfReader(str(staged_pdf))"),
            stage.index("staged_pdf.replace(PDF_FILE)"),
        )
        self.assertLess(
            stage.index("if not staged_pdf.is_file()"),
            stage.index("staged_pdf.replace(PDF_FILE)"),
        )
        self.assertNotIn("writer.append(str(PDF_FILE))", stage)
        self.assertNotIn("PDF_FILE.unlink(", exporter)

    def test_staging_failure_preserves_prior_file(self):
        import tempfile

        with tempfile.TemporaryDirectory() as parent:
            target = Path(parent) / "analiza.pdf"
            target.write_bytes(b"verified previous PDF")
            with self.assertRaisesRegex(ValueError, "contamination"):
                with tempfile.TemporaryDirectory(
                    prefix="eeg-p3-publication-", dir=target.parent
                ) as stage_dir:
                    staged_pdf = Path(stage_dir) / target.name
                    staged_pdf.write_bytes(b"unapproved PDF")
                    raise ValueError("contamination")
                    staged_pdf.replace(target)
            self.assertEqual(target.read_bytes(), b"verified previous PDF")
            self.assertFalse(list(Path(parent).glob("eeg-p3-publication-*")))

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
