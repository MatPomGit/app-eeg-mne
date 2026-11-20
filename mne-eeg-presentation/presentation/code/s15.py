for r in (raw_tfr, raw_clf):
    r.set_eeg_reference("average",
                        projection=False)
x = raw_clf.get_data()
print("suma = 0:", abs(x.sum(0)).max() < 1e-12)
