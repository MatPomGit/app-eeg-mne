import json, sklearn
from pathlib import Path
out = Path("output/results")
out.mkdir(parents=True, exist_ok=True)
epochs_clf.save(out / "S001-clf-epo.fif",
                overwrite=True)
res = dict(subject=1, n_epochs=len(y),
           protocol="all_task_epochs_groupkfold_v2",
           bal_acc=round(ba, 3),
           mne=mne.__version__,
           sklearn=sklearn.__version__)
f = out / "results.json"
f.write_text(json.dumps(res))
print(sorted(p.name for p in out.iterdir()))
