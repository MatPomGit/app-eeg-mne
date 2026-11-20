import sklearn.metrics as sm
from sklearn.dummy import DummyClassifier
bas = sm.balanced_accuracy_score
y_hat = ms.cross_val_predict(
    clf, X, y, groups=groups, cv=cv)
ba = bas(y, y_hat)
cm = sm.confusion_matrix(y, y_hat)
dummy = DummyClassifier(
    strategy="most_frequent")
y_base = ms.cross_val_predict(
    dummy, X, y, groups=groups, cv=cv)
print(round(ba, 3), round(bas(y, y_base), 3))
