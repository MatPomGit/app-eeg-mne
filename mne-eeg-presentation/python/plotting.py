"""Rysunki do prezentacji. Kazda funkcja HOOKS[sNN](ns, figdir) generuje wykresy
z RZECZYWISTYCH obiektow MNE (ns = przestrzen nazw po wykonaniu fragmentu sNN)."""
from __future__ import annotations

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.colors import LinearSegmentedColormap
import mne

PLUM, ROSE, VIOLET, LAV, BLUSH, INK, GREY = (
    "#7B2D5F", "#D94F8A", "#6C5CB8", "#B7A9E0", "#FBE4EE", "#3B2A3F", "#8A7F8D")
CMAP = LinearSegmentedColormap.from_list("rose_violet", [VIOLET, "#FFFFFF", ROSE])
CMAP_SEQ = LinearSegmentedColormap.from_list(
    "plum_seq", ["#FFFFFF", "#F3D4E4", ROSE, PLUM, "#2A0F25"])
W = 5.9  # szerokosc tekstu na slajdzie [cale] (15 cm)


def _style():
    names = {f.name for f in font_manager.fontManager.ttflist}
    fam = "Inter" if "Inter" in names else "DejaVu Sans"
    mpl.rcParams.update({
        "font.family": fam, "font.size": 10.5, "axes.labelsize": 10.5,
        "axes.titlesize": 11, "xtick.labelsize": 10, "ytick.labelsize": 10,
        "legend.fontsize": 10, "axes.edgecolor": INK, "axes.labelcolor": INK,
        "xtick.color": INK, "ytick.color": INK, "text.color": INK,
        "axes.spines.top": False, "axes.spines.right": False,
        "figure.facecolor": "white", "axes.facecolor": "white",
        "pdf.fonttype": 3, "axes.unicode_minus": True,
        "figure.dpi": 100, "savefig.dpi": 220,
    })


_style()


def _save(fig, figdir, name):
    fig.savefig(figdir / f"{name}.pdf")
    plt.close(fig)


def _ch(info_or_names, name):
    names = info_or_names.ch_names if hasattr(info_or_names, "ch_names") else info_or_names
    return list(names).index(name)


# ----------------------------------------------------------------------------- s09-s12
def hook_s09(ns, figdir):
    """Slajd 1: wielokanalowy zapis EEG (1-40 Hz, average ref. liczone lokalnie)."""
    raw = ns["raw"].copy().crop(60, 66).filter(1, 40, verbose=False)
    raw.set_eeg_reference("average", projection=False, verbose=False)
    chs = ["Fp1", "F3", "Fz", "F4", "C3", "Cz", "C4", "P3", "Pz", "P4", "O1", "Oz"]
    d = raw.get_data(picks=chs, units="uV")
    t = raw.times
    fig, ax = plt.subplots(figsize=(3.2, 2.95), layout="constrained")
    step = 100
    for i, (c, x) in enumerate(zip(chs, d)):
        col = ROSE if c in ("C3", "C4", "Cz") else PLUM
        ax.plot(t, x - x.mean() - i * step, color=col, lw=0.8)
        ax.text(-0.08, -i * step, c, ha="right", va="center", fontsize=10, color=col)
    y0 = -step * 11 - 150
    ax.plot([6.1, 6.1], [y0, y0 + 100], color=INK, lw=2, clip_on=False)
    ax.text(6.18, y0 + 50, "100 uV", ha="left", va="center", fontsize=10)
    ax.set_xlim(0, 6); ax.set_ylim(y0 - 20, 80); ax.set_yticks([]); ax.set_xlabel("czas [s]")
    ax.spines["left"].set_visible(False)
    _save(fig, figdir, "s01_hero")


def hook_s10(ns, figdir):
    raw = ns["raw"]
    fig, ax = plt.subplots(figsize=(1.75, 1.85), layout="constrained")
    mne.viz.plot_sensors(raw.info, kind="topomap", show_names=False,
                         axes=ax, show=False, title="")
    for t in ax.texts:
        t.set_fontsize(10.5); t.set_color(PLUM); t.set_fontweight("bold")
    for coll in ax.collections:
        try:
            coll.set_facecolor(LAV); coll.set_edgecolor("none"); coll.set_sizes([20])
        except Exception:
            pass
    pos = raw.get_montage().get_positions()["ch_pos"]
    sel = np.array([pos[c][:2] for c in ("C3", "Cz", "C4")])
    ax.scatter(sel[:, 0], sel[:, 1], s=40, color=ROSE, zorder=5)
    for (x, y), nm, off in zip(sel, ("C3", "Cz", "C4"), ((-9, 7), (0, 9), (9, 7))):
        ax.annotate(nm, (x, y), xytext=off, textcoords="offset points", ha="center",
                    fontsize=10, color=PLUM, fontweight="bold")
    ax.set_title("64 elektrody", fontsize=11)
    _save(fig, figdir, "s10_sensors")


def hook_s11(ns, figdir):
    data, chs = ns["data"], ns["chs"]
    fs = ns["raw"].info["sfreq"]
    t = np.arange(data.shape[1]) / fs + 20
    fig, ax = plt.subplots(figsize=(W, 1.7), layout="constrained")
    step = 250
    for i, (c, x) in enumerate(zip(chs, data)):
        col = ROSE if c in ("C3", "Cz", "C4") else PLUM
        ax.plot(t, x - x.mean() - i * step, color=col, lw=0.9)
        ax.text(t[0] - 0.1, -i * step, c, ha="right", va="center", fontsize=10.5, color=col)
    ax.plot([30.12, 30.12], [-1100, -900], color=INK, lw=2, clip_on=False)
    ax.text(30.2, -1000, "200 uV", ha="left", va="center", fontsize=10, clip_on=False)
    ax.set_xlim(20, 30); ax.set_yticks([]); ax.set_xlabel("czas od poczatku zapisu [s]")
    ax.spines["left"].set_visible(False)
    _save(fig, figdir, "s11_raw")


def hook_s12(ns, figdir):
    raw = ns["raw"]; lens = ns["lens"]; fs = raw.info["sfreq"]
    ann = raw.annotations
    col = {"T0": "#E9E3EC", "T1": ROSE, "T2": VIOLET}
    lab = {"T0": "T0 odpoczynek", "T1": "T1 rece", "T2": "T2 stopy"}
    edges = np.concatenate([[0], np.cumsum(lens)]) / fs
    fig, axes = plt.subplots(3, 1, figsize=(W, 1.55), sharex=False, layout="constrained")
    for k, ax in enumerate(axes):
        lo, hi = edges[k], edges[k + 1]
        for o, d, desc in zip(ann.onset, ann.duration, ann.description):
            if desc in col and lo <= o < hi:
                ax.barh(0, d, left=o - lo, color=col[desc], edgecolor="white", lw=0.6, height=0.8)
        ax.set_xlim(0, hi - lo); ax.set_yticks([])
        ax.set_ylabel(f"bieg {(6, 10, 14)[k]}", rotation=0, ha="right", va="center")
        for s in ("left",):
            ax.spines[s].set_visible(False)
        if k < 2:
            ax.set_xticklabels([])
    axes[-1].set_xlabel("czas w obrebie biegu [s]")
    h = [plt.Rectangle((0, 0), 1, 1, color=col[k]) for k in col]
    axes[0].legend(h, [lab[k] for k in col], ncol=3, loc="lower center",
                   bbox_to_anchor=(0.5, 1.0), frameon=False)
    _save(fig, figdir, "s12_annot")


# ----------------------------------------------------------------------------- s13-s16
def hook_s13(ns, figdir):
    spec = ns["spec"]; f = spec.freqs
    fig, ax = plt.subplots(figsize=(W, 1.5), layout="constrained")
    bands = [("delta", 1, 4, "#F3D4E4"), ("theta", 4, 8, "#E6DDF5"),
             ("mu / alfa", 8, 13, "#FBC9DD"), ("beta", 13, 30, "#D9D0F0")]
    for n, a, b, c in bands:
        ax.axvspan(a, b, color=c, alpha=0.8, lw=0)
        ax.text((a + b) / 2, 1.02, n, transform=ax.get_xaxis_transform(),
                ha="center", va="bottom", fontsize=10, color=PLUM)
    for ch, col in (("C3", ROSE), ("Cz", PLUM), ("C4", VIOLET)):
        x = spec.get_data(picks=[ch])[0] * 1e12
        ax.semilogy(f, x, color=col, lw=1.6, label=ch)
    ax.set_xlim(1, 45); ax.set_xlabel("czestotliwosc [Hz]")
    ax.set_ylabel("PSD [uV$^2$/Hz]"); ax.legend(frameon=False, loc="upper right", ncol=3, bbox_to_anchor=(1.0, 1.02), columnspacing=0.8, handlelength=1.2)
    _save(fig, figdir, "s13_psd")


def hook_s14(ns, figdir):
    raw, rc = ns["raw"], ns["raw_clf"]
    fs = raw.info["sfreq"]; i = _ch(raw, "C3")
    a, b = int(30 * fs), int(40 * fs)
    t = np.arange(a, b) / fs
    x0 = raw.get_data(picks=[i])[0, a:b] * 1e6
    x1 = rc.get_data(picks=[i])[0, a:b] * 1e6
    fig, ax = plt.subplots(2, 1, figsize=(W, 1.5), sharex=True, layout="constrained")
    ax[0].plot(t, x0 - x0.mean(), color=PLUM, lw=0.9)
    ax[0].set_title("C3 [uV], przed filtracja", loc="left", fontsize=10.5, pad=2)
    ax[1].plot(t, x1, color=ROSE, lw=0.9)
    ax[1].set_title("C3 [uV], po filtracji 7-30 Hz", loc="left", fontsize=10.5, pad=2)
    for a_ in ax:
        a_.yaxis.set_major_locator(mpl.ticker.MaxNLocator(2))
    ax[1].set_xlabel("czas [s]")
    _save(fig, figdir, "s14_filter")
    # widmo przed/po
    f = ns["spec"].freqs
    p0 = ns["spec"].get_data(picks=["C3"])[0]
    sp = rc.compute_psd(method="welch", fmax=45, n_fft=640, verbose=False)
    fig, ax = plt.subplots(figsize=(2.9, 2.2), layout="constrained")
    ax.semilogy(f, p0 * 1e12, color=PLUM, lw=1.6, label="surowy")
    ax.semilogy(sp.freqs, sp.get_data(picks=["C3"])[0] * 1e12, color=ROSE, lw=1.6, label="7-30 Hz")
    ax.axvspan(7, 30, color=BLUSH, zorder=0)
    ax.set_xlabel("czestotliwosc [Hz]"); ax.set_ylabel("PSD [uV$^2$/Hz]")
    ax.legend(frameon=False, loc="upper right"); ax.set_xlim(1, 45)
    _save(fig, figdir, "s14_psd")


def hook_s15(ns, figdir):
    raw, rc = ns["raw"], ns["raw_clf"]
    info = rc.info; fs = info["sfreq"]
    ref0 = raw.copy().filter(7, 30, verbose=False)
    k = int(35.0 * fs)
    v0 = ref0.get_data()[:, k] * 1e6
    v1 = rc.get_data()[:, k] * 1e6
    lim = max(np.abs(v0).max(), np.abs(v1).max())
    fig, axes = plt.subplots(1, 2, figsize=(W, 1.7), layout="constrained")
    for ax, v, ttl in zip(axes, (v0, v1), ("zapis, t = 35 s", "average reference")):
        im, _ = mne.viz.plot_topomap(v, info, axes=ax, show=False, cmap=CMAP,
                                     vlim=(-lim, lim), sensors=False, contours=4)
        ax.set_title(ttl, fontsize=11)
    cb = fig.colorbar(im, ax=axes, shrink=0.8, pad=0.02)
    cb.set_label("uV")
    _save(fig, figdir, "s15_ref")


def hook_s16(ns, figdir):
    ev = ns["events"]; raw = ns["raw"]; fs = raw.info["sfreq"]; lens = ns["lens"]
    t = (ev[:, 0] - raw.first_samp) / fs
    col = {1: ROSE, 2: VIOLET}
    fig, ax = plt.subplots(figsize=(W, 1.35), layout="constrained")
    for e, tt in zip(ev, t):
        ax.vlines(tt, 0, 1, color=col[e[2]], lw=2.4)
    for b in np.cumsum(lens)[:-1] / fs:
        ax.axvline(b, color=GREY, ls="--", lw=1)
    for k, x in enumerate(np.concatenate([[0], np.cumsum(lens)[:-1]]) / fs):
        ax.text(x + 2, 1.12, f"bieg {(6, 10, 14)[k]}", fontsize=10, color=GREY, va="bottom")
    ax.set_ylim(0, 1.45); ax.set_yticks([]); ax.set_xlim(0, sum(lens) / fs)
    ax.set_xlabel("czas [s]"); ax.spines["left"].set_visible(False)
    h = [plt.Line2D([0], [0], color=ROSE, lw=3), plt.Line2D([0], [0], color=VIOLET, lw=3)]
    fig.legend(h, ["1 = hands (T1)", "2 = feet (T2)"], ncol=2, frameon=False,
               loc="outside upper center")
    _save(fig, figdir, "s16_events")


# ----------------------------------------------------------------------------- s17-s20
def hook_s17(ns, figdir):
    ep = ns["epochs"]; c3 = _ch(ep, "C3")
    d = ep.get_data()[:, c3, :] * 1e6
    t = ep.times; y = ep.events[:, 2]
    fig, axes = plt.subplots(1, 2, figsize=(W, 1.5), gridspec_kw=dict(width_ratios=[1, 1.15]),
                             layout="constrained")
    ax = axes[0]
    im = ax.imshow(d, aspect="auto", cmap=CMAP, vmin=-100, vmax=100, extent=[t[0], t[-1], len(d), 0])
    ax.axvline(0, color=INK, lw=1)
    ax.set_xlabel("czas wzgl. wskazowki [s]"); ax.set_ylabel("numer epoki")
    cb = fig.colorbar(im, ax=ax, pad=0.02); cb.set_label("C3 [uV]")
    ax = axes[1]
    for lab, c, col, off in ((1, "hands", ROSE, 0), (2, "feet", VIOLET, -260)):
        idx = np.where(y == lab)[0][:2]
        for j, ii in enumerate(idx):
            ax.plot(t, d[ii] + off - j * 130 * 0, color=col, lw=0.8, alpha=0.9 if j == 0 else 0.45)
        ax.text(t[0] + 0.05, off + 120, c, color=col, fontsize=10.5, fontweight="bold")
    ax.axvline(0, color=INK, lw=1); ax.set_yticks([]); ax.spines["left"].set_visible(False)
    ax.set_xlabel("czas wzgl. wskazowki [s]")
    ax.set_ylim(-560, 200)
    ax.plot([4.45, 4.45], [-540, -340], color=INK, lw=2); ax.text(4.35, -440, "200 uV", ha="right", va="center", fontsize=10)
    _save(fig, figdir, "s17_epochs")


def hook_s18(ns, figdir):
    p2p = ns["pp"] * 1e6; thr = ns["thr"] * 1e6
    fig, axes = plt.subplots(1, 2, figsize=(W, 1.3), layout="constrained")
    ax = axes[0]
    ax.hist(p2p, bins=np.arange(100, 820, 40), color=LAV, edgecolor="white")
    ax.axvline(200, color=VIOLET, ls="--", lw=2)
    ax.axvline(thr, color=ROSE, lw=2)
    ax.set_xlabel("max. p-p w epoce [uV]"); ax.set_ylabel("liczba epok")
    ax.set_title(f"prog: 200 (- -) i {thr:.0f} uV (\u2014)", fontsize=10, loc="left", pad=3)
    ax = axes[1]
    o = np.sort(p2p)
    ax.scatter(np.arange(len(o)), o, s=18, color=[ROSE if v > thr else PLUM for v in o], zorder=3)
    ax.axhline(200, color=VIOLET, ls="--", lw=2); ax.axhline(thr, color=ROSE, lw=2)
    ax.set_xlabel("epoki posortowane"); ax.set_ylabel("max. p-p [uV]")
    ax.text(0.03, 0.82, "43 z 45 epok\npowyzej 200 uV", fontsize=10, color=VIOLET, va="top",
            transform=ax.transAxes)
    _save(fig, figdir, "s18_qc")


def hook_s19(ns, figdir):
    ica = ns["ica"]; comps = ica.get_components(); cand = [int(i) for i in ns["idx"]]
    fig, axes = plt.subplots(1, 6, figsize=(W, 1.5), layout="constrained")
    for k, ax in enumerate(axes.ravel()):
        v = comps[:, k]; lim = np.abs(v).max()
        mne.viz.plot_topomap(v, ica.info, axes=ax, show=False, cmap=CMAP, vlim=(-lim, lim),
                             sensors=False, contours=0)
        ax.set_title(f"IC{k}" + (" *" if k in cand else ""), fontsize=11,
                     color=ROSE if k in cand else INK, fontweight="bold" if k in cand else "normal")
    _save(fig, figdir, "s19_ica")


def hook_s20(ns, figdir):
    ep = ns["epochs"]; c3 = _ch(ep, "C3"); t = ep.times
    fig, axes = plt.subplots(1, 2, figsize=(W, 1.5), sharey=True, layout="constrained")
    ax = axes[0]
    hands = ep["hands"].get_data()[:, c3, :] * 1e6
    for x in hands[:12]:
        ax.plot(t, x, color=GREY, lw=0.5, alpha=0.6)
    ax.plot(t, hands.mean(0), color=ROSE, lw=2.2)
    ax.set_title("C3, hands: epoki i srednia", loc="left", fontsize=10.5)
    ax.set_xlabel("czas [s]"); ax.set_ylabel("C3 [uV]"); ax.axvline(0, color=INK, lw=0.8)
    ax = axes[1]
    for c, col in (("hands", ROSE), ("feet", VIOLET)):
        ax.plot(t, ns["evokeds"][c].data[c3] * 1e6, color=col, lw=2, label=c)
    ax.axvline(0, color=INK, lw=0.8); ax.set_xlabel("czas [s]"); ax.legend(frameon=False)
    ax.set_title("srednie (Evoked)", loc="left", fontsize=10.5)
    _save(fig, figdir, "s20_evoked")


# ----------------------------------------------------------------------------- s21-s24
def _tf(ax, tfr, ch, power_db=True, vlim=None, cmap=CMAP_SEQ, pct=False):
    i = _ch(tfr.info if hasattr(tfr, "info") else tfr.ch_names, ch)
    z = tfr.data[i]
    if pct:
        z = 100 * z
    elif power_db:
        z = 10 * np.log10(z * 1e12)
    im = ax.pcolormesh(tfr.times, tfr.freqs, z, shading="auto", cmap=cmap,
                       vmin=None if vlim is None else vlim[0], vmax=None if vlim is None else vlim[1],
                       rasterized=True)
    ax.axvline(0, color=INK, lw=1); ax.set_xlabel("czas wzgl. wskazowki [s]")
    return im


def hook_s21(ns, figdir):
    tfr = ns["tfr"]
    allv = np.concatenate([10 * np.log10(tfr[c].data[_ch(tfr[c].info, "C3")] * 1e12).ravel() for c in tfr])
    vl = (np.percentile(allv, 2), np.percentile(allv, 98))
    fig, axes = plt.subplots(1, 2, figsize=(W, 1.4), sharey=True, layout="constrained")
    for ax, c in zip(axes, ("hands", "feet")):
        im = _tf(ax, tfr[c], "C3", vlim=vl); ax.set_title(f"C3, {c}", loc="left", fontsize=11)
    axes[0].set_ylabel("Hz")
    cb = fig.colorbar(im, ax=axes, pad=0.02); cb.set_label("dB")
    _save(fig, figdir, "s21_tfr")


def hook_s22(ns, figdir):
    erd = ns["erd"]
    fig, axes = plt.subplots(1, 3, figsize=(W, 1.4), sharey=True, layout="constrained")
    for ax, ch in zip(axes, ("C3", "Cz", "C4")):
        im = _tf(ax, erd["hands"], ch, vlim=(-100, 100), cmap=CMAP, pct=True)
        ax.set_title(f"{ch}, hands", loc="left", fontsize=11); ax.set_xlabel("czas [s]")
        ax.axvspan(-0.8, -0.2, facecolor="none", edgecolor=INK, lw=1, hatch="///", alpha=0.35)
    axes[0].set_ylabel("Hz")
    cb = fig.colorbar(im, ax=axes, pad=0.02, ticks=[-100, 0, 100]); cb.set_label("%")
    _save(fig, figdir, "s22_erd")


def hook_s23(ns, figdir):
    erd = ns["erd"]
    fig, axes = plt.subplots(1, 3, figsize=(W, 1.55), sharey=True, layout="constrained")
    for ax, ch in zip(axes, ("C3", "Cz", "C4")):
        for c, col in (("hands", ROSE), ("feet", VIOLET)):
            t = erd[c]; i = _ch(t.info, ch)
            fsel = (t.freqs >= 8) & (t.freqs <= 13)
            y = 100 * t.data[i][fsel].mean(0)
            ax.plot(t.times, y, color=col, lw=1.8, label=c)
        ax.axhline(0, color=GREY, lw=0.8); ax.axvline(0, color=INK, lw=0.8)
        ax.axvspan(1, 3, color=BLUSH, zorder=0)
        ax.set_title(ch, loc="left", fontsize=11); ax.set_xlabel("czas [s]")
    axes[0].set_ylabel("% zmiany")
    h = [plt.Line2D([0], [0], color=ROSE, lw=3), plt.Line2D([0], [0], color=VIOLET, lw=3)]
    fig.legend(h, ["hands", "feet"], ncol=2, frameon=False, loc="outside upper center")
    _save(fig, figdir, "s23_cond")


def hook_s24(ns, figdir):
    info = ns["epochs"].info; mu = ns["mu"]; diff = mu["hands"] - mu["feet"]
    names = [n if n in ("C3", "Cz", "C4") else "" for n in info.ch_names]
    fig, axes = plt.subplots(1, 3, figsize=(W, 1.5), layout="constrained")
    for ax, v, ttl, lim in ((axes[0], mu["hands"], "hands", 80), (axes[1], mu["feet"], "feet", 80),
                            (axes[2], diff, "hands - feet", 80)):
        im, _ = mne.viz.plot_topomap(v, info, axes=ax, show=False, cmap=CMAP, vlim=(-lim, lim),
                                     names=names, sensors=True, contours=4)
        for t in ax.texts:
            t.set_fontsize(10); t.set_color(INK)
        ax.set_title(ttl, fontsize=11)
    cb = fig.colorbar(im, ax=axes, shrink=0.8, pad=0.02); cb.set_label("% zmiany")
    _save(fig, figdir, "s24_topo")


# ----------------------------------------------------------------------------- s26-s30
def hook_s26(ns, figdir):
    y, g = ns["y"], ns["groups"]
    runs = (6, 10, 14)
    fig, ax = plt.subplots(figsize=(1.75, 2.0), layout="constrained")
    h = [np.sum((g == k) & (y == 1)) for k in range(3)]
    f = [np.sum((g == k) & (y == 2)) for k in range(3)]
    x = np.arange(3)
    ax.bar(x, h, color=ROSE, label="hands"); ax.bar(x, f, bottom=h, color=VIOLET, label="feet")
    for k in range(3):
        ax.text(k, h[k] / 2, str(h[k]), ha="center", va="center", color="white", fontsize=10.5)
        ax.text(k, h[k] + f[k] / 2, str(f[k]), ha="center", va="center", color="white", fontsize=10.5)
    ax.set_xticks(x, [f"{r}\n(g{k})" for k, r in enumerate(runs)]); ax.set_xlabel("bieg (grupa)")
    ax.set_ylabel("liczba epok")
    fig.legend(*ax.get_legend_handles_labels(), loc="outside upper center", ncol=2, frameon=False,
               handlelength=1, columnspacing=0.8)
    _save(fig, figdir, "s26_groups")


def hook_s28(ns, figdir):
    g = ns["groups"]; sc, rnd = ns["scores"], ns["rnd"]
    fig, axes = plt.subplots(2, 1, figsize=(1.75, 2.5), gridspec_kw=dict(height_ratios=[1, 1.4]),
                             layout="constrained")
    ax = axes[0]
    order = np.argsort(g, kind="stable")
    for fold in range(3):
        for j, i in enumerate(order):
            ax.add_patch(plt.Rectangle((j, 2 - fold), 1, 0.8, color=ROSE if g[i] == fold else "#E6DDF5", lw=0))
    ax.set_xlim(0, len(g)); ax.set_ylim(-0.1, 3)
    ax.set_yticks([0.4, 1.4, 2.4], ["f3", "f2", "f1"]); ax.set_xticks([])
    for b in np.cumsum(np.bincount(g))[:-1]:
        ax.axvline(b, color="white", lw=2)
    ax.spines["left"].set_visible(False); ax.spines["bottom"].set_visible(False); ax.tick_params(length=0)
    
    ax = axes[1]
    xs = np.arange(3); wd = 0.38
    ax.bar(xs - wd / 2, sc, wd, color=ROSE, label="biegi")
    ax.bar(xs + wd / 2, rnd, wd, color=LAV, label="losowo")
    ax.set_ylim(0.5, 1.0); ax.set_xticks(xs, ["1", "2", "3"]); ax.set_xlabel("fold")
    ax.set_ylabel("bal. accuracy")
    fig.legend(*ax.get_legend_handles_labels(), loc="outside upper center", ncol=2, frameon=False,
               handlelength=1, columnspacing=0.8)
    _save(fig, figdir, "s28_cv")


def hook_s29(ns, figdir):
    cm = np.array(ns["cm"]); ba = ns["ba"]; base = ns["bas"](ns["y"], ns["y_base"])
    fig, axes = plt.subplots(2, 1, figsize=(1.75, 2.5), gridspec_kw=dict(height_ratios=[1.2, 1]),
                             layout="constrained")
    ax = axes[0]
    ax.imshow(cm, cmap=CMAP_SEQ, vmin=0, vmax=cm.max() * 1.1)
    for i in range(2):
        for j in range(2):
            ax.text(j, i, cm[i, j], ha="center", va="center", fontsize=13,
                    color="white" if cm[i, j] > cm.max() / 2 else INK, fontweight="bold")
    ax.set_xticks([0, 1], ["h", "f"]); ax.set_yticks([0, 1], ["h", "f"])
    ax.set_xlabel("przewidziane"); ax.set_ylabel("prawdziwe")
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax = axes[1]
    ax.bar([0, 1], [base, ba], color=[LAV, ROSE], width=0.65)
    for k, v in enumerate([base, ba]):
        ax.text(k, v + 0.03, f"{v:.2f}", ha="center", fontsize=10)
    ax.set_xticks([0, 1], ["baza", "CSP+LDA"]); ax.set_ylim(0, 1.25); ax.set_yticks([0, 0.5, 1])
    ax.set_ylabel("bal. accuracy")
    _save(fig, figdir, "s29_eval")


def hook_s30(ns, figdir):
    csp = ns["csp"]; info = ns["epochs_clf"].info
    fig, axes = plt.subplots(2, 4, figsize=(W, 1.7), layout="constrained")
    for k in range(4):
        for r, (arr, nm) in enumerate(((csp.patterns_, "wzorzec"), (csp.filters_, "filtr"))):
            v = arr[k]; lim = np.abs(v).max()
            mne.viz.plot_topomap(v, info, axes=axes[r, k], show=False, cmap=CMAP, vlim=(-lim, lim),
                                 sensors=False, contours=0)
            axes[r, k].set_title(f"{nm} {k + 1}", fontsize=11)
    _save(fig, figdir, "s30_csp")


HOOKS = {
    "s09": hook_s09, "s10": hook_s10, "s11": hook_s11, "s12": hook_s12, "s13": hook_s13,
    "s14": hook_s14, "s15": hook_s15, "s16": hook_s16, "s17": hook_s17, "s18": hook_s18,
    "s19": hook_s19, "s20": hook_s20, "s21": hook_s21, "s22": hook_s22, "s23": hook_s23,
    "s24": hook_s24, "s26": hook_s26, "s28": hook_s28, "s29": hook_s29, "s30": hook_s30,
}
