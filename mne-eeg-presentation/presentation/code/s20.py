evokeds = {c: epochs[c].average()
           for c in ["hands", "feet"]}
print([e.nave for e in evokeds.values()])
