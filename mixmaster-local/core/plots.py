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
