from mne.decoding import CSP
from sklearn.discriminant_analysis import (
    LinearDiscriminantAnalysis as LDA)
from sklearn.pipeline import make_pipeline

clf = make_pipeline(
    CSP(n_components=4, reg="ledoit_wolf",
        log=True),
    LDA())
print([name for name, _ in clf.steps])
