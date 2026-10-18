"""Matplotlib figures for the UI (dark theme)."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

# Brutalist palette shared with assets/brutal.css.
BG, INK, MUTE, LINE, ACID, ALERT = "#0b0b0c", "#f1f1ee", "#8d8d88", "#2a2a28", "#d7ff1f", "#ff4f1a"
COLORS = {"До": MUTE, "Результат": ACID, "Референс": ALERT}
plt.rcParams.update({"font.family": "monospace", "font.size": 9})


def _style(fig, ax, title: str):
    """Shared dark-brutalist axes: square frame, dashed grid, uppercase title on the left."""
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.tick_params(colors=INK, length=0, pad=6)
    for s in ax.spines.values():
        s.set_color(INK)
        s.set_linewidth(1.5)
    ax.grid(True, which="major", color=LINE, linewidth=0.7, linestyle=(0, (2, 3)))
    ax.set_title(title.upper(), color=INK, fontsize=10, fontweight="bold", loc="left", pad=10)
    ax.xaxis.label.set_color(MUTE)
    ax.yaxis.label.set_color(MUTE)


def _legend(ax, loc="lower left"):
    leg = ax.legend(facecolor=BG, edgecolor=INK, labelcolor=INK, loc=loc, fancybox=False, framealpha=1)
    leg.get_frame().set_linewidth(1.2)


def spectrum_figure(spectra: dict):
    """Overlay of smoothed spectra (each normalised to equal total power)."""
    fig, ax = plt.subplots(figsize=(9, 3.6), dpi=100)
    for name, (f, db) in spectra.items():
        ax.semilogx(f, db, label=name, color=COLORS.get(name, INK), linewidth=2.0 if name == "Результат" else 1.3)
    ax.set_xlim(20, 20000)
    lo = min(float(db[(f > 30) & (f < 16000)].min()) for f, db in spectra.values()) if spectra else -80
    ax.set_ylim(max(lo - 3, -90), None)
    ax.set_xticks([30, 60, 100, 200, 500, 1000, 2000, 5000, 10000, 20000])
    ax.set_xticklabels(["30", "60", "100", "200", "500", "1k", "2k", "5k", "10k", "20k"])
    ax.minorticks_off()
    ax.set_xlabel("ГЦ")
    ax.set_ylabel("ДБ (НОРМ.)")
    _style(fig, ax, "Спектр // громкость выровнена")
    _legend(ax)
    fig.tight_layout()
    plt.close(fig)
    return fig


def pitch_figure(rep: dict):
    """Detected melody before/after tuning over the key's note grid."""
    import numpy as np

    from .tuning import NOTE_NAMES, allowed_pitch_classes

    t, before, after = rep["times"], rep["midi_before"], rep["midi_after"]
    fig, ax = plt.subplots(figsize=(9, 3.6), dpi=100)
    ok = np.isfinite(before)
    if np.any(ok):
        lo, hi = int(np.floor(np.nanmin(before))) - 1, int(np.ceil(np.nanmax(before))) + 1
        pcs = set(allowed_pitch_classes(rep["tonic"], rep["scale"]).tolist())
        notes = [m for m in range(lo, hi + 1) if m % 12 in pcs]
        ax.set_yticks(notes)
        ax.set_yticklabels([f"{NOTE_NAMES[m % 12]}{m // 12 - 1}" for m in notes])
        ax.set_ylim(lo, hi)
    ax.plot(t, before, color=MUTE, linewidth=1.0, label="До")
    ax.plot(t, after, color=ACID, linewidth=1.8, label="После")
    ax.set_xlabel("СЕКУНДЫ")
    _style(fig, ax, f"Ноты // {rep['key']}")
    ax.grid(True, axis="y", color=LINE, linewidth=0.9, linestyle="-")
    ax.grid(False, axis="x")
    _legend(ax, "upper right")
    fig.tight_layout()
    plt.close(fig)
    return fig
