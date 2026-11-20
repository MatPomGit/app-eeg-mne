epochs_clf = mne.Epochs(
    raw_clf, epochs.events,
    dict(hands=1, feet=2),
    tmin=-1.5, tmax=4.5, baseline=None,
    reject_by_annotation=False, preload=True)
X = epochs_clf.get_data(tmin=0.5, tmax=3.5)
y = epochs_clf.events[:, 2]
t0 = epochs_clf.events[:, 0] - raw.first_samp
edges = np.cumsum(lens)
groups = np.searchsorted(edges, t0, side="right")
print(X.shape, np.bincount(y)[1:],
      np.bincount(groups))
