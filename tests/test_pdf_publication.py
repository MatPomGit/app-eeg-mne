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
            "zapis raportu pdf wraz",
        ):
            with self.subTest(phrase=forbidden):
                self.assertNotIn(forbidden, self.markdown)

    def test_pdf_export_excludes_technical_cell_and_absolute_path(self):
        exporters = [
            "".join(c["source"]) for c in self.code
            if "def export_full_notebook_pdf():" in "".join(c["source"])
        ]
        self.assertEqual(len(exporters), 1)
        exporter = exporters[0]
        self.assertIn("public_notebook.cells", exporter)
        self.assertIn("from_notebook_node(public_notebook)", exporter)
        self.assertIn("notebook_bytes = nbformat.writes(notebook)", exporter)
        self.assertIn("ANALIZA EEG · ERP CORE", exporter)
        self.assertNotIn("<strong>Źródło:</strong> {escape(source)}", exporter)

    def test_analysis_code_and_saved_outputs_remain(self):
        self.assertGreaterEqual(len(self.code), 45)
        self.assertGreaterEqual(
            sum(len(c.get("outputs", [])) for c in self.code), 70
        )
        for cell in self.code:
            ast.parse("".join(cell["source"]))


if __name__ == "__main__":
    unittest.main()
