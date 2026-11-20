epochs = mne.Epochs(
    raw_tfr, events, dict(hands=1, feet=2),
    tmin=-1.5, tmax=4.5, baseline=None,
    reject=None, preload=True)
print(epochs.get_data().shape)
