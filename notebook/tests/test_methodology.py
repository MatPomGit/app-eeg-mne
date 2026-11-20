"""Statyczne testy niezbędnych kontraktów metodologicznych notatnika P3.

Uruchamiane bez pobierania danych: python -m unittest discover -s notebook/tests -v
"""
import json
import unittest
from pathlib import Path

NOTEBOOK = Path(__file__).resolve().parents[1] / "eeg_P3_ERP_1.6.4.ipynb"


def read_notebook():
    with NOTEBOOK.open(encoding="utf-8") as file:
        return json.load(file)


def source(nb, index):
    lines = nb["cells"][index]["source"]
    return "".join(lines) if isinstance(lines, list) else lines


class P3Methodology(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.nb = read_notebook()

    def test_notebook_format_and_revision(self):
        self.assertEqual(self.nb["nbformat"], 4)
        self.assertEqual(self.nb["metadata"]["methodology_revision"]["version"], "1.6.5")

    def test_all_code_compiles(self):
        for i, cell in enumerate(self.nb["cells"]):
            if cell["cell_type"] == "code":
                with self.subTest(cell=i):
                    compile(source(self.nb, i), f"cell-{i}", "exec")

    def test_event_code_mapping(self):
        events = source(self.nb, 40)
        self.assertIn(r'^stimulus/[1-5]{2}$', events)
        self.assertIn(r'^stimulus/([1-5])\1, events)
        self.assertIn("TARGET_RE.fullmatch(description)", events)

    def test_montage_is_version_aware(self):
        self.assertIn("get_builtin_montages()", source(self.nb, 31))
        self.assertIn('"colin27_1005"', source(self.nb, 31))
        self.assertIn('"standard_1005"', source(self.nb, 31))
        self.assertIn("montage_name", source(self.nb, 93))

    def test_baseline_follows_ica(self):
        self.assertIn("baseline=None", source(self.nb, 62))
        self.assertIn("baseline=None", source(self.nb, 93))
        ica = source(self.nb, 66)
        self.assertIn("model.apply(ep)\n    ep.apply_baseline((EPOCH_TMIN, 0))", ica)
        self.assertIn('if not model.converged_', ica)
        self.assertIn('return model, [],', ica)

    def test_quality_reports_condition_specific_rejections(self):
        qc = source(self.nb, 71)
        self.assertIn('"n_rejected_target"', qc)
        self.assertIn('"n_rejected_nontarget"', qc)
        self.assertIn('"rejected_fraction"', qc)
        self.assertIn('"ica_applied"', source(self.nb, 93))

    def test_auc_is_fold_mean(self):
        eval_code = source(self.nb, 109)
        self.assertIn('scoring="roc_auc"', eval_code)
        self.assertIn('auc = float(auc_fold.mean())', eval_code)
        self.assertIn('auc_oof = float(sm.roc_auc_score(y, s))', eval_code)
        random_code = source(self.nb, 117)
        self.assertIn('auc_random = float(auc_random_fold.mean())', random_code)
        self.assertIn('permutation_test_score', random_code)
        export = source(self.nb, 123)
        self.assertIn('"roc_auc_fold_mean"', export)
        self.assertIn('"roc_auc_pooled_oof_exploratory"', export)
        self.assertIn('"pipeline_version": "1.6.5"', export)

    def test_no_old_results_after_method_changes(self):
        self.assertFalse(self.nb["cells"][31].get("outputs"))
        for i, cell in enumerate(self.nb["cells"][62:], 62):
            if cell["cell_type"] == "code":
                with self.subTest(cell=i):
                    self.assertFalse(cell.get("outputs"))
                    self.assertIsNone(cell.get("execution_count"))


if __name__ == "__main__":
    unittest.main()
, events)
        self.assertIn("TARGET_RE.fullmatch(description)", events)

    def test_montage_is_version_aware(self):
        self.assertIn("get_builtin_montages()", source(self.nb, 31))
        self.assertIn('"colin27_1005"', source(self.nb, 31))
        self.assertIn('"standard_1005"', source(self.nb, 31))
        self.assertIn("montage_name", source(self.nb, 93))

    def test_baseline_follows_ica(self):
        self.assertIn("baseline=None", source(self.nb, 62))
        self.assertIn("baseline=None", source(self.nb, 93))
        ica = source(self.nb, 66)
        self.assertIn("model.apply(ep)\n    ep.apply_baseline((EPOCH_TMIN, 0))", ica)
        self.assertIn('if not model.converged_', ica)
        self.assertIn('return model, [],', ica)

    def test_quality_reports_condition_specific_rejections(self):
        qc = source(self.nb, 71)
        self.assertIn('"n_rejected_target"', qc)
        self.assertIn('"n_rejected_nontarget"', qc)
        self.assertIn('"rejected_fraction"', qc)
        self.assertIn('"ica_applied"', source(self.nb, 93))

    def test_auc_is_fold_mean(self):
        eval_code = source(self.nb, 109)
        self.assertIn('scoring="roc_auc"', eval_code)
        self.assertIn('auc = float(auc_fold.mean())', eval_code)
        self.assertIn('auc_oof = float(sm.roc_auc_score(y, s))', eval_code)
        random_code = source(self.nb, 117)
        self.assertIn('auc_random = float(auc_random_fold.mean())', random_code)
        self.assertIn('permutation_test_score', random_code)
        export = source(self.nb, 123)
        self.assertIn('"roc_auc_fold_mean"', export)
        self.assertIn('"roc_auc_pooled_oof_exploratory"', export)
        self.assertIn('"pipeline_version": "1.6.5"', export)

    def test_no_old_results_after_method_changes(self):
        self.assertFalse(self.nb["cells"][31].get("outputs"))
        for i, cell in enumerate(self.nb["cells"][62:], 62):
            if cell["cell_type"] == "code":
                with self.subTest(cell=i):
                    self.assertFalse(cell.get("outputs"))
                    self.assertIsNone(cell.get("execution_count"))


if __name__ == "__main__":
    unittest.main()
