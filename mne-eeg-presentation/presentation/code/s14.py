raw_tfr = raw.copy().filter(
    1.0, 40.0, fir_design="firwin")
raw_clf = raw.copy().filter(
    7.0, 30.0, fir_design="firwin")
print(raw_clf.info["lowpass"], "Hz")
