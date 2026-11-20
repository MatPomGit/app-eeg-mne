"""Wykonuje fragmenty kodu ze slajdow (presentation/code/sNN*.py) po kolei we wspolnej
przestrzeni nazw, zapisuje rzeczywiste wyjscia konsoli (presentation/console/*.txt)
i generuje rysunki (plotting.HOOKS). Uzycie: python python/run_workshop.py"""
import contextlib
import io
import os
import re
import subprocess
import sys
import time
import warnings
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
os.chdir(ROOT)
os.environ.setdefault("MNE_DATA", str(ROOT / "data"))
os.environ.setdefault("MNE_DATASETS_EEGBCI_PATH", os.environ["MNE_DATA"])
import matplotlib  # noqa: E402
matplotlib.use("Agg")

CODE = ROOT / "presentation" / "code"
CONSOLE = ROOT / "presentation" / "console"
FIGS = ROOT / "presentation" / "figures"


def main(only=None, no_figs=False):
    warnings.filterwarnings("ignore")
    CONSOLE.mkdir(exist_ok=True)
    FIGS.mkdir(exist_ok=True)
    plotting = None
    if not no_figs:
        import plotting  # noqa: E402
    ns = {"__name__": "__workshop__"}
    files = sorted(CODE.glob("s[0-9][0-9]*.py"), key=lambda p: p.stem)
    for p in files:
        key = p.stem
        num = int(re.match(r"s(\d+)", key).group(1))
        if only and num not in only and not (ns.get("raw") is not None and False):
            pass
        if key == "s29b" and "--perm" not in sys.argv:
            continue
        t0 = time.time()
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            exec(compile(p.read_text(), str(p), "exec"), ns)
        (CONSOLE / f"{key}.txt").write_text(buf.getvalue())
        if plotting is not None and key in plotting.HOOKS:
            plotting.HOOKS[key](ns, FIGS)
        print(f"{key}: ok ({time.time() - t0:.1f}s)", flush=True)
    # s04: weryfikacja srodowiska (bez instalacji)
    out = subprocess.run([sys.executable, "-c", "import mne; mne.sys_info()"],
                         capture_output=True, text=True).stdout
    (CONSOLE / "s04_full.txt").write_text(out)
    import sklearn
    keep = [re.sub(r"\s*\(.*", "", l.split("\u2611")[-1]).split() for l in out.splitlines() if "\u2611" in l]
    keep_lines = [" ".join(k[:2]) for k in keep[:4]] + [f"scikit-learn {sklearn.__version__}"]
    (CONSOLE / "s04.txt").write_text("\n".join(keep_lines) + "\n")
    return ns


if __name__ == "__main__":
    main(no_figs="--no-figs" in sys.argv)
