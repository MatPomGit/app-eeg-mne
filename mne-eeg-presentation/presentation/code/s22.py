erd = {c: t.copy().apply_baseline(
           (-0.8, -0.2), mode="percent")
       for c, t in tfr.items()}
win = dict(fmin=8, fmax=13, tmin=1, tmax=3)
v = erd["hands"].get_data(picks=["C3"], **win)
print("C3, hands: %.0f %%" % (100 * v.mean()))
