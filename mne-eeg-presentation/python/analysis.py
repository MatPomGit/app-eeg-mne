"""Pelny pipeline EEG: PhysioNet EEGBCI -> MNE-Python -> CSP + LDA.

Funkcje odpowiadaja kolejnym etapom z prezentacji (slajdy 07-31).
Uzycie:  python python/analysis.py --subject 1
Dane sa pobierane automatycznie przez mne.datasets.eegbci.load_data()
do katalogu wskazanego zmienna MNE_DATA (domyslnie: <projekt>/data).
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MNE_DATA", str(ROOT / "data"))
os.environ.setdefault("MNE_DATASETS_EEGBCI_PATH", os.environ["MNE_DATA"])

import numpy as np  # noqa: E402
import mne  # noqa: E402
import sklearn  # noqa: E402
from scipy.stats import median_abs_deviation  # noqa: E402
from mne.datasets import eegbci  # noqa: E402
from mne.decoding import CSP  # noqa: E402
from mne.io import concatenate_raws, read_raw_edf  # noqa: E402
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA  # noqa: E402
from sklearn.dummy import DummyClassifier  # noqa: E402
from sklearn.metrics import balanced_accuracy_score, confusion_matrix  # noqa: E402
from sklearn.model_selection import GroupKFold, cross_val_predict, cross_val_score  # noqa: E402
from sklearn.pipeline import make_pipeline  # noqa: E402

RUNS = (6, 10, 14)            # wyobrazanie ruchu: obie rece (T1) lub obie stopy (T2)
EVENT_ID = {"hands": 1, "feet": 2}
TMIN, TMAX = -1.5, 4.5        # margines na efekty brzegowe falek Morleta
CLF_WINDOW = (0.5, 3.5)       # okno klasyfikacji ustalone a priori (nie strojone na danych)


def load_raw(subject: int = 1, runs=RUNS):
    files = eegbci.load_data(subject, list(runs), update_path=False)
    raws = [read_raw_edf(f, preload=True) for f in files]
    lens = [r.n_times for r in raws]      # PRZED concatenate_raws (ono modyfikuje raws[0])
    raw = concatenate_raws(raws)
    eegbci.standardize(raw)               # "Fc5." -> "FC5"
    raw.set_montage("colin27_1005")       # = dawny standard_1005 (MNE >= 1.13)
    return raw, lens


def preprocess(raw):
    """Oddzielne kopie: 1-40 Hz do eksploracyjnej TFR/QC i 7-30 Hz do ML."""
    raw_tfr = raw.copy().filter(1.0, 40.0, fir_design="firwin")
    raw_clf = raw.copy().filter(7.0, 30.0, fir_design="firwin")
    for r in (raw_tfr, raw_clf):
        r.set_eeg_reference("average", projection=False)
    return raw_tfr, raw_clf


def make_epochs(raw_tfr, raw_clf):
    events, _ = mne.events_from_annotations(raw_tfr, event_id={"T1": 1, "T2": 2})
    epochs = mne.Epochs(raw_tfr, events, EVENT_ID, tmin=TMIN, tmax=TMAX,
                        baseline=None, reject=None, preload=True)
    p2p = np.ptp(epochs.get_data(), axis=2).max(axis=1)       # V, najgorszy kanal w epoce
    thr = np.median(p2p) + 3 * median_abs_deviation(p2p, scale="normal")
    epochs.drop_bad(reject=dict(eeg=thr))                     # prog odporny, bez uzycia etykiet
    # Klasyfikator używa WSZYSTKICH zdarzeń, niezależnie od progowej selekcji QC.
    # Próg wyznaczony z pełnego zapisu jest używany wyłącznie do eksploracyjnej TFR;
    # zastosowanie go przed CV do danych ML ujawniałoby informację z biegów testowych.
    epochs_clf = mne.Epochs(raw_clf, events, EVENT_ID, tmin=TMIN, tmax=TMAX,
                            baseline=None, reject_by_annotation=False, preload=True)
    return epochs, epochs_clf


def make_xy(raw, epochs_clf, run_lengths):
    X = epochs_clf.get_data(tmin=CLF_WINDOW[0], tmax=CLF_WINDOW[1])
    y = epochs_clf.events[:, 2]
    edges = np.cumsum(run_lengths)
    groups = np.searchsorted(edges, epochs_clf.events[:, 0] - raw.first_samp, side="right")
    return X, y, groups


def make_classifier():
    """Klasyfikator wyobrażania ruchu: EEG -> filtry CSP -> 4 log-wariancje -> LDA.

    Model przewiduje hands/feet; obie transformacje są uczone wewnątrz foldu
    treningowego. Nie jest to detektor dowolnych intencji ani diagnoza.
    """
    return make_pipeline(CSP(n_components=4, reg="ledoit_wolf", log=True), LDA())


def evaluate(X, y, groups, n_splits=3):
    clf, cv = make_classifier(), GroupKFold(n_splits=n_splits)
    y_hat = cross_val_predict(clf, X, y, groups=groups, cv=cv)
    folds = cross_val_score(clf, X, y, groups=groups, cv=cv, scoring="balanced_accuracy")
    base = cross_val_predict(DummyClassifier(strategy="most_frequent"), X, y, groups=groups, cv=cv)
    return dict(
        bal_acc=float(balanced_accuracy_score(y, y_hat)),
        protocol="all_task_epochs_groupkfold_v2",
        folds=[float(f) for f in folds],
        balanced_accuracy_mean_folds=float(np.mean(folds)),
        evaluation_scope="all task epochs; GroupKFold by run, one subject; exploratory TFR QC does not select ML epochs",
        confusion=confusion_matrix(y, y_hat).tolist(),
        baseline_bal_acc=float(balanced_accuracy_score(y, base)),
    )


def run_subject(subject: int = 1, runs=RUNS):
    raw, lens = load_raw(subject, runs)
    raw_tfr, raw_clf = preprocess(raw)
    epochs, epochs_clf = make_epochs(raw_tfr, raw_clf)
    X, y, groups = make_xy(raw, epochs_clf, lens)
    res = evaluate(X, y, groups)
    res.update(subject=subject, n_epochs=int(len(y)), n_tfr_epochs=int(len(epochs)), X=X, y=y, groups=groups)
    return res


def environment_info():
    return dict(python=platform.python_version(), platform=platform.platform(),
                mne=mne.__version__, numpy=np.__version__, sklearn=sklearn.__version__)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--subject", type=int, default=1)
    ap.add_argument("--out", default=str(ROOT / "output" / "results"))
    a = ap.parse_args()
    mne.set_log_level("WARNING")
    res = run_subject(a.subject)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    payload = {k: v for k, v in res.items() if k not in ("X", "y", "groups")}
    payload["environment"] = environment_info()
    (out / f"results_S{a.subject:03d}.json").write_text(json.dumps(payload, indent=2))
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    sys.exit(main())
