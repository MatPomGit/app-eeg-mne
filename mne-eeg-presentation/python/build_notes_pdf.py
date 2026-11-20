"""Generuje output/mne_eeg_32_slajdy_notes.pdf: miniatura slajdu + notatka + bibliografia (IEEE-like)."""
import re, subprocess, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
W = ROOT / "notes" / "build"
shutil.rmtree(W, ignore_errors=True); (W / "thumbs").mkdir(parents=True)
pdf = ROOT / "presentation" / "main.pdf"
subprocess.run(["pdftoppm", "-r", "70", "-png", str(pdf), str(W / "thumbs" / "s")], check=True)
thumbs = sorted((W / "thumbs").glob("s-*.png"))
notes = re.findall(r"## Slajd (\d+)\. (.*?)\n\n(.*?)\n\n", (ROOT / "notes" / "speaker_notes.md").read_text(), re.S)
assert len(notes) == len(thumbs) == 32, (len(notes), len(thumbs))
esc = lambda s: (s.replace("\\", "\\textbackslash{}").replace("&", "\\&").replace("%", "\\%")
                 .replace("_", "\\_").replace("#", "\\#").replace("$", "\\$"))
body = []
for (n, title, text), th in zip(notes, thumbs):
    body.append(f"\\noindent\\begin{{minipage}}[t]{{0.38\\textwidth}}\\includegraphics[width=\\linewidth]{{thumbs/{th.name}}}\\end{{minipage}}\\hfill"
                f"\\begin{{minipage}}[t]{{0.58\\textwidth}}\\textbf{{\\color{{plum}}Slajd {n}. {esc(title)}}}\\par\\smallskip {esc(text)}\\end{{minipage}}\\par\\bigskip\n")
    if int(n) % 5 == 0:
        body.append("\\clearpage\n")
shutil.copy(ROOT / "references" / "references.bib", W / "references.bib")
tex = r"""\documentclass[11pt,a4paper]{article}
\usepackage[margin=1.8cm]{geometry}
\usepackage{fontspec,polyglossia,xcolor,graphicx,url}
\setdefaultlanguage{polish}
\IfFontExistsTF{Inter}{\setmainfont{Inter}}{\setmainfont{TeX Gyre Heros}}
\definecolor{plum}{HTML}{7B2D5F}
\pagestyle{plain}\setlength{\parindent}{0pt}
\begin{document}
{\color{plum}\LARGE\bfseries Notatki prowadzącego: Analiza EEG z MNE-Python\par}\bigskip
""" + "".join(body) + r"""
\clearpage
{\color{plum}\Large\bfseries Bibliografia (numeracja zgodna ze slajdami)\par}\bigskip
\nocite{*}
\bibliographystyle{ieeetr}
\bibliography{references}
\end{document}
"""
(W / "notes.tex").write_text(tex)
for cmd in (["xelatex"], ["bibtex"], ["xelatex"], ["xelatex"]):
    arg = "notes" if cmd[0] == "bibtex" else "notes.tex"
    r = subprocess.run(cmd + (["-interaction=nonstopmode", arg] if cmd[0] == "xelatex" else [arg]),
                       cwd=W, capture_output=True, text=True)
out = ROOT / "output" / "mne_eeg_32_slajdy_notes.pdf"
shutil.copy(W / "notes.pdf", out); print("zapisano", out)
