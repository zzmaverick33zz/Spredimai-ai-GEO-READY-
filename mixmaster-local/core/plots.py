"""Matplotlib figures for the UI (dark theme)."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

COLORS = {"До": "#8a8f98", "Результат": "#4fd1c5", "Референс": "#f6ad55"}


def spectrum_figure(spectra: dict):
    """Overlay of smoothed spectra (each normalised to equal total power)."""
    fig, ax = plt.subplots(figsize=(9, 3.6), dpi=100)
    fig.patch.set_facecolor("#0f1115")
    ax.set_facecolor("#0f1115")
    for name, (f, db) in spectra.items():
        ax.semilogx(f, db, label=name, color=COLORS.get(name), linewidth=1.6 if name == "Результат" else 1.2)
    ax.set_xlim(20, 20000)
    lo = min(float(db[(f > 30) & (f < 16000)].min()) for f, db in spectra.values()) if spectra else -80
    ax.set_ylim(max(lo - 3, -90), None)
    ax.set_xticks([30, 60, 100, 200, 500, 1000, 2000, 5000, 10000, 20000])
    ax.set_xticklabels(["30", "60", "100", "200", "500", "1k", "2k", "5k", "10k", "20k"])
    ax.set_xlabel("Гц", color="#c9ccd1")
    ax.set_ylabel("дБ (норм.)", color="#c9ccd1")
    ax.tick_params(colors="#c9ccd1")
    for s in ax.spines.values():
        s.set_color("#2a2e36")
    ax.grid(True, which="both", color="#22262d", linewidth=0.6)
    ax.legend(facecolor="#171a20", edgecolor="#2a2e36", labelcolor="#e6e8eb")
    ax.set_title("Спектр (громкость выровнена)", color="#e6e8eb", fontsize=11)
    fig.tight_layout()
    plt.close(fig)
    return fig


def pitch_figure(rep: dict):
    """Detected melody before/after tuning over the key's note grid."""
    import numpy as np

    from .tuning import NOTE_NAMES, allowed_pitch_classes

    t, before, after = rep["times"], rep["midi_before"], rep["midi_after"]
    fig, ax = plt.subplots(figsize=(9, 3.6), dpi=100)
    fig.patch.set_facecolor("#0f1115")
    ax.set_facecolor("#0f1115")
    ok = np.isfinite(before)
    if np.any(ok):
        lo, hi = int(np.floor(np.nanmin(before))) - 1, int(np.ceil(np.nanmax(before))) + 1
        pcs = set(allowed_pitch_classes(rep["tonic"], rep["scale"]).tolist())
        for m in range(lo, hi + 1):
            if m % 12 in pcs:
                ax.axhline(m, color="#2a2e36", linewidth=0.8, zorder=0)
        ax.set_yticks([m for m in range(lo, hi + 1) if m % 12 in pcs])
        ax.set_yticklabels([f"{NOTE_NAMES[m % 12]}{m // 12 - 1}" for m in range(lo, hi + 1) if m % 12 in pcs])
        ax.set_ylim(lo, hi)
    ax.plot(t, before, color="#8a8f98", linewidth=1.0, label="До")
    ax.plot(t, after, color="#4fd1c5", linewidth=1.3, label="После")
    ax.set_xlabel("секунды", color="#c9ccd1")
    ax.tick_params(colors="#c9ccd1")
    for s in ax.spines.values():
        s.set_color("#2a2e36")
    ax.legend(facecolor="#171a20", edgecolor="#2a2e36", labelcolor="#e6e8eb", loc="upper right")
    ax.set_title(f"Ноты вокала, тональность {rep['key']}", color="#e6e8eb", fontsize=11)
    fig.tight_layout()
    plt.close(fig)
    return fig
