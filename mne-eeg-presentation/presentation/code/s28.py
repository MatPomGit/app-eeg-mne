import sklearn.model_selection as ms
cv = ms.GroupKFold(n_splits=3)
bal = dict(scoring="balanced_accuracy")
scores = ms.cross_val_score(
    clf, X, y, groups=groups, cv=cv, **bal)
skf = ms.StratifiedKFold(
    3, shuffle=True, random_state=0)
rnd = ms.cross_val_score(
    clf, X, y, cv=skf, **bal)
print("biegi :", scores.round(2))
print("losowo:", rnd.round(2))
