"""Regression tests for methodology and alignment of teaching materials."""
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
import analysis  # noqa: E402


class MethodologyTests(unittest.TestCase):
    def test_classifier_epochs_do_not_inherit_exploratory_qc_selection(self):
        events = np.array([
            [100, 0, 1], [300, 0, 2], [500, 0, 1], [700, 0, 2],
        ], dtype=int)

        class DummyEpochs:
            def __init__(self):
                self.events = events.copy()

            def get_data(self):
                return np.array([
                    [[0.0, 0.001]], [[0.0, 0.001]],
                    [[0.0, 0.001]], [[0.0, 1.0]],
                ])

            def drop_bad(self, reject):
                self.events = self.events[:-1]

        descriptive = DummyEpochs()
        predictive = DummyEpochs()
        with patch.object(analysis.mne, "events_from_annotations", return_value=(events, {})), \
             patch.object(analysis.mne, "Epochs", side_effect=[descriptive, predictive]) as factory:
            tfr, clf = analysis.make_epochs(object(), object())

        self.assertEqual(len(tfr.events), 3)
        self.assertEqual(len(clf.events), 4)
        np.testing.assert_array_equal(factory.call_args_list[1].args[1], events)

    def test_notebook_code_is_same_as_slide_snippets(self):
        nb = json.loads((ROOT / "notebooks/mne_eeg_workshop.ipynb").read_text())
        scripts = sorted((ROOT / "presentation/code").glob("s[0-9][0-9]*.py"))
        code = [c for c in nb["cells"] if c["cell_type"] == "code"][1:]
        self.assertEqual(len(code), len(scripts))
        for cell, script in zip(code, scripts):
            self.assertEqual("".join(cell["source"]), script.read_text(), script.name)

    def test_notebook_has_canonical_guides(self):
        nb = json.loads((ROOT / "notebooks/mne_eeg_workshop.ipynb").read_text())
        guides = json.loads((ROOT / "notes/notebook_guides.json").read_text())
        self.assertIn("**Co to jest klasyfikator?**", guides["s27"])
        self.assertIn("oryginalnej listy zdarzeń", guides["s26"])
        for i, cell in enumerate(nb["cells"]):
            if cell["cell_type"] == "markdown" and i not in (0, len(nb["cells"]) - 1):
                title = "".join(cell["source"]).split("\n", 1)[0]
                key = "s29b" if title.startswith("## Dodatek") else "s" + title.split()[2].rstrip(".")
                self.assertIn(guides[key], "".join(cell["source"]), key)

    def test_synthetic_cross_run_model(self):
        from contextlib import redirect_stdout
        import io
        rng = np.random.default_rng(7)
        X = rng.normal(scale=0.1, size=(30, 8, 128))
        y = np.tile([1, 2], 15)
        groups = np.repeat([0, 1, 2], 10)
        for i in range(len(y)):
            X[i, 0 if y[i] == 1 else 1] *= 4.0
        with redirect_stdout(io.StringIO()):
            result = analysis.evaluate(X, y, groups)
        self.assertEqual(result["protocol"], "all_task_epochs_groupkfold_v2")
        self.assertEqual(sum(sum(row) for row in result["confusion"]), 30)
        self.assertTrue(0 <= result["bal_acc"] <= 1)
        self.assertEqual(len(result["folds"]), 3)


if __name__ == "__main__":
    unittest.main()
