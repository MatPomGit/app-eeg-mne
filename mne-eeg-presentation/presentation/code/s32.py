import sys
sys.path.insert(0, "python")
from analysis import run_subject

res = run_subject(subject=1)
print(res["n_epochs"], round(res["bal_acc"], 3))
# zadanie: subject=2
