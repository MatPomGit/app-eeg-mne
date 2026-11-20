csp = CSP(n_components=4, reg="ledoit_wolf",
          log=True)
csp.fit(X, y)
print(csp.patterns_.shape, csp.filters_.shape)
