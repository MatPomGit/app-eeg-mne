"""Testy projektu: python -m unittest discover -s tests -v   (po zbudowaniu PDF-ow)"""
import ast, json, re, subprocess, sys, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))


class Project(unittest.TestCase):
    def test_snippets_syntax(self):
        files = list((ROOT / "presentation" / "code").glob("s*.py"))
        self.assertGreaterEqual(len(files), 27)
        for f in files:
            ast.parse(f.read_text(), str(f))

    def test_snippet_length(self):
        for f in (ROOT / "presentation" / "code").glob("s*.py"):
            if f.stem == "s29b":
                continue
            n = len(f.read_text().rstrip().splitlines())
            self.assertLessEqual(n, 13, f.name)

    def test_pdf_has_32_pages(self):
        out = subprocess.run(["pdfinfo", str(ROOT / "output" / "mne_eeg_32_slajdy.pdf")], capture_output=True, text=True).stdout
        self.assertEqual(int(re.search(r"Pages:\s+(\d+)", out).group(1)), 32)

    def test_notes(self):
        md = (ROOT / "notes" / "speaker_notes.md").read_text()
        notes = re.findall(r"## Slajd (\d+)\. (.*?)\n\n(.*?)\n\n", md, re.S)
        self.assertEqual([int(n[0]) for n in notes], list(range(1, 33)))
        for n, t, text in notes:
            self.assertLessEqual(len(text), 1000, n)
        titles = {}
        for i in range(2, 33):
            m = re.search(r"\\begin\{frame\}\{(.*?)\}\n", (ROOT / "presentation" / "slides" / f"s{i:02d}.tex").read_text())
            titles[i] = re.sub(r"\$|\\mu", "", m.group(1)).replace("  ", " ")
        for n, t, _ in notes[1:]:
            self.assertEqual(re.sub(r"\s+", " ", re.sub(r"μ", "", t)).strip(), re.sub(r"\s+", " ", titles[int(n)]).strip(), n)

    def test_references_order(self):
        bib = re.findall(r"@\w+\{(\w+),", (ROOT / "references" / "references.bib").read_text())
        first = []
        for i in range(1, 33):
            s = (ROOT / "presentation" / "slides" / f"s{i:02d}.tex").read_text()
            m = re.search(r"\\setsrc\{(.*?)\}", s)
            for k in re.findall(r"\[(\d+)\]", m.group(1)) if m else []:
                if int(k) not in first:
                    first.append(int(k))
        self.assertEqual(first, sorted(first))
        self.assertEqual(len(bib), 17)
        self.assertLessEqual(max(first), len(bib))

    def test_no_tiny_fonts(self):
        for f in (ROOT / "presentation").rglob("*.tex"):
            t = f.read_text()
            self.assertNotRegex(t, r"\\(tiny|scriptsize)\b", f.name)
            for sz in re.findall(r"\\fontsize\{(\d+(?:\.\d+)?)\}", t):
                self.assertGreaterEqual(float(sz), 10, f.name)

    def test_results_consistent(self):
        res = json.loads((ROOT / "output" / "results" / "results.json").read_text())
        console = (ROOT / "presentation" / "console" / "s32.txt").read_text().split()
        self.assertEqual(int(console[0]), res["n_epochs"])
        self.assertAlmostEqual(float(console[1]), res["bal_acc"], places=3)

    def test_analysis_matches_slides(self):
        try:
            import analysis
            res = analysis.run_subject(1)
        except Exception as e:  # brak danych
            self.skipTest(str(e))
        c = (ROOT / "presentation" / "console" / "s29.txt").read_text().split()
        self.assertAlmostEqual(res["bal_acc"], float(c[0]), places=3)
        self.assertEqual(res["n_epochs"], 44)


if __name__ == "__main__":
    unittest.main()
