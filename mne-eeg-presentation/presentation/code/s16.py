events, _ = mne.events_from_annotations(
    raw_tfr, event_id={"T1": 1, "T2": 2})
print(events.shape)
print(events[:4])
print(np.bincount(events[:, 2])[1:])
