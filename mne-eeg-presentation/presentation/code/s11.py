seg = raw.copy().crop(20, 30)
chs = ["Fp1", "C3", "Cz", "C4", "Oz"]
data = seg.get_data(picks=chs, units="uV")
print(data.shape, np.ptp(data[1]).round(1))
