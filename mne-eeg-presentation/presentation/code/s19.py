ica = mne.preprocessing.ICA(n_components=20,
                            random_state=97)
ica.fit(raw_tfr)
idx, sc = ica.find_bads_eog(raw_tfr, ch_name="Fp1")
print("kandydaci:", list(map(int, idx)))
