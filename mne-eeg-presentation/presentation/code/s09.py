info = raw.info
fs = info["sfreq"]
print("sfreq:", fs, "| nchan:", info["nchan"])
print("czas:", raw.times[-1] + 1 / fs, "s")
cz = raw.get_data(picks="Cz")[0]
print("Cz [V]:", cz[:3])
print("Cz [uV]:", cz[:3] * 1e6)
