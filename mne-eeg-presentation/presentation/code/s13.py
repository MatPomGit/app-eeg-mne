spec = raw.compute_psd(
    method="welch", fmax=45, n_fft=640)
psd = spec.get_data(picks="C3")[0]
mu = (spec.freqs >= 8) & (spec.freqs <= 13)
print("C3 mu:", (psd[mu] * 1e12).mean().round(1))
