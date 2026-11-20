"""Sprawdzenie spójności metodologicznej materiałów bez pobierania EEG."""
import ast
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P3 = ROOT / "notebook" / "eeg_P3_ERP_1.6.4.ipynb"
MI = ROOT / "mne-eeg-presentation" / "notebooks" / "mne_eeg_workshop.ipynb"


def read_nb(path):
    nb = json.loads(path.read_text(encoding="utf-8"))
    assert nb["nbformat"] == 4 and nb["cells"]
    return nb


def sources(nb, kind):
    return "\n".join("".join(cell["source"]) for cell in nb["cells"] if cell["cell_type"] == kind)


class ScientificNotebookTests(unittest.TestCase):
    def test_p3_methodology(self):
        nb = read_nb(P3)
        code = sources(nb, "code")
        prose = sources(nb, "markdown")
        self.assertIn('set_montage("colin27_1005"', code)
        self.assertNotIn('set_montage("standard_1005"', code)
        self.assertIn("ep.apply_baseline((EPOCH_TMIN, 0.0))", code)
        self.assertIn('scoring="roc_auc"', code)
        self.assertIn("fold_auc.mean()", code)
        self.assertIn("roc_auc_mean_folds", code)
        self.assertIn("offline", prose)
        self.assertIn("Czym jest klasyfikator", prose)
        for cell in nb["cells"]:
            if cell["cell_type"] == "code":
                ast.parse("".join(cell["source"]))

    def test_motor_imagery_methodology(self):
        nb = read_nb(MI)
        code = sources(nb, "code")
        prose = sources(nb, "markdown")
        self.assertIn("CSP(", code)
        self.assertIn("GroupKFold", code)
        self.assertIn("hands", code)
        self.assertIn("feet", code)
        self.assertIn("Co to jest klasyfikator", prose)
        self.assertIn("tej samej osoby", prose)


if __name__ == "__main__":
    unittest.main()
