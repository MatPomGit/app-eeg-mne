mu = {c: 100 * erd[c].get_data(
          **win).mean((1, 2))
      for c in ["hands", "feet"]}
for c, v in mu.items():
    print(c, round(v.min()), round(v.max()))
