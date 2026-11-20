import scipy.stats as st
pp = np.ptp(epochs.get_data(), axis=2).max(1)
mad = st.median_abs_deviation(pp, scale="normal")
thr = np.median(pp) + 3 * mad
print("200 uV:", (pp > 200e-6).sum(), "z", len(pp))
epochs.drop_bad(reject=dict(eeg=thr))
print(round(thr * 1e6), "uV;", len(epochs), "epok")
