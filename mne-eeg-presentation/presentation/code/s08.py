raws = [read_raw_edf(f, preload=True)
        for f in files]
lens = [int(r.n_times) for r in raws]
raw = concatenate_raws(raws)
eegbci.standardize(raw)
print(lens, raw.n_times)
print(raw.ch_names[:5])
