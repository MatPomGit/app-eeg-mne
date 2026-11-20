freqs = np.arange(6, 36, 1.0)
tfr = {c: epochs[c].compute_tfr(
           "morlet", freqs, n_cycles=freqs / 2,
           decim=2, average=True)
       for c in ["hands", "feet"]}
print(tfr["hands"].data.shape)
