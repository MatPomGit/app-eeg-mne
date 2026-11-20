y_hat = ms.cross_val_predict(
    clf, X, y, groups=groups, cv=cv)
s, perm, p = ms.permutation_test_score(
    clf, X, y, groups=groups, cv=cv, random_state=0,
    scoring="balanced_accuracy", n_permutations=200)
print("p =", round(p, 3), "| srednia perm.:", perm.mean().round(2))
