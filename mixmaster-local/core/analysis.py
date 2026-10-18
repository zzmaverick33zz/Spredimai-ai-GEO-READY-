"""Loudness and spectrum analysis (LUFS via pyloudnorm, true peak, LRA, band balance)."""

from __future__ import annotations

import numpy as np
import pyloudnorm as pyln
from pyloudnorm.iirfilter import IIRfilter
from scipy import signal

from .dsp import chunk_len

BANDS_HZ = {
    "sub": (20, 60),
    "bass": (60, 200),
    "lowmid": (200, 500),
    "mid": (500, 2000),
    "presence": (2000, 6000),
    "high": (6000, 12000),
    "air": (12000, 20000),
}

BAND_LABELS = {
    "sub": "Sub 20–60",
    "bass": "Bass 60–200",
    "lowmid": "Low-mid 200–500",
    "mid": "Mid 0.5–2k",
    "presence": "Presence 2–6k",
    "high": "High 6–12k",
    "air": "Air 12–20k",
}

SILENCE_LUFS = -70.0


def integrated_lufs(audio: np.ndarray, sr: int) -> float:
    """Integrated loudness (ITU-R BS.1770-4) via pyloudnorm. Silence returns -70."""
    meter = pyln.Meter(sr)
    data = audio.T.astype(np.float64) if audio.shape[0] > 1 else audio[0].astype(np.float64)
    if data.shape[0] < int(sr * 0.4):
        data = np.pad(data, [(0, int(sr * 0.4) - data.shape[0])] + [(0, 0)] * (data.ndim - 1))
    with np.errstate(divide="ignore"):
        val = meter.integrated_loudness(data)
    return float(val) if np.isfinite(val) else SILENCE_LUFS


def true_peak_db(audio: np.ndarray, sr: int, oversample: int = 4) -> float:
    """True peak in dBTP using 4x polyphase oversampling, computed in chunks."""
    peak = 0.0
    step = chunk_len(sr)
    pad = 64
    for ch in range(audio.shape[0]):
        x = audio[ch]
        for start in range(0, len(x), step):
            seg = x[max(start - pad, 0):start + step + pad].astype(np.float64)
            up = signal.resample_poly(seg, oversample, 1)
            peak = max(peak, float(np.max(np.abs(up))) if up.size else 0.0)
    return 20 * np.log10(max(peak, 1e-10))


def sample_peak_db(audio: np.ndarray) -> float:
    """Sample peak in dBFS."""
    return 20 * np.log10(max(float(np.max(np.abs(audio))) if audio.size else 0.0, 1e-10))


def _k_weighted_power(audio: np.ndarray, sr: int) -> np.ndarray:
    """Channel-summed power of the BS.1770 K-weighted signal (pyloudnorm filter parameters), chunked."""
    shelf = IIRfilter(4.0, 1 / np.sqrt(2), 1500.0, sr, "high_shelf")
    hp = IIRfilter(0.0, 0.5, 38.0, sr, "high_pass")
    sos = np.vstack([np.concatenate([shelf.b, shelf.a]), np.concatenate([hp.b, hp.a])])
    power = np.zeros(audio.shape[1], dtype=np.float64)
    step = chunk_len(sr)
    for ch in range(audio.shape[0]):
        zi = np.zeros((2, 2))
        for start in range(0, audio.shape[1], step):
            seg, zi = signal.sosfilt(sos, audio[ch, start:start + step], zi=zi)
            power[start:start + step] += seg * seg
    return power


def short_term_loudness(audio: np.ndarray, sr: int, window_s: float = 3.0, hop_s: float = 0.1) -> np.ndarray:
    """Short-term loudness series (3 s windows) in LUFS."""
    power = _k_weighted_power(audio, sr)
    csum = np.concatenate([[0.0], np.cumsum(power)])
    win, hop = int(sr * window_s), int(sr * hop_s)
    if len(power) < win:
        win = len(power)
    starts = np.arange(0, len(power) - win + 1, hop)
    ms = (csum[starts + win] - csum[starts]) / max(win, 1)
    return -0.691 + 10 * np.log10(np.maximum(ms, 1e-12))


def loudness_range(audio: np.ndarray, sr: int) -> float:
    """Loudness range (LRA, EBU Tech 3342): 10th..95th percentile of gated short-term loudness."""
    st = short_term_loudness(audio, sr)
    st = st[st > -70.0]
    if st.size < 2:
        return 0.0
    rel = 10 * np.log10(np.mean(10 ** (st / 10))) - 20.0
    st = st[st > rel]
    if st.size < 2:
        return 0.0
    return float(np.percentile(st, 95) - np.percentile(st, 10))


def _psd(audio: np.ndarray, sr: int, nperseg: int = 8192):
    """Welch PSD of the mono sum. Long files are analysed on evenly spread excerpts."""
    x = audio.mean(axis=0) if audio.shape[0] > 1 else audio[0]
    max_len = sr * 120
    if len(x) > max_len:
        idx = np.linspace(0, len(x) - sr * 10, 12).astype(int)
        x = np.concatenate([x[i:i + sr * 10] for i in idx])
    nperseg = min(nperseg, len(x))
    freqs, pxx = signal.welch(x.astype(np.float64), sr, nperseg=nperseg)
    return freqs, pxx


def band_balance(audio: np.ndarray, sr: int) -> dict[str, float]:
    """Energy per band in dB relative to the total (so loudness does not matter)."""
    freqs, pxx = _psd(audio, sr)
    total = np.sum(pxx[(freqs >= 20) & (freqs <= 20000)]) + 1e-20
    out = {}
    for name, (lo, hi) in BANDS_HZ.items():
        e = np.sum(pxx[(freqs >= lo) & (freqs < hi)])
        out[name] = float(10 * np.log10(e / total + 1e-12))
    return out


def band_density(audio: np.ndarray, sr: int, anchor: str = "mid") -> dict[str, float]:
    """Average spectral density per band (log-frequency mean, dB) relative to the anchor band.

    Unlike band_balance this is independent of band width, so it describes the
    spectral shape (tilt) and is used for adaptive EQ decisions.
    """
    freqs, pxx = _psd(audio, sr)
    db = 10 * np.log10(pxx + 1e-20)
    out = {}
    for name, (lo, hi) in BANDS_HZ.items():
        grid = np.geomspace(lo, hi, 24)
        out[name] = float(np.mean(np.interp(grid, freqs, db)))
    ref = out[anchor]
    return {k: v - ref for k, v in out.items()}


def spectrum_curve(audio: np.ndarray, sr: int, n_points: int = 300, smooth_oct: float = 1 / 6):
    """Smoothed spectrum for plotting: (freqs, dB), normalised to 0 dB total power."""
    freqs, pxx = _psd(audio, sr)
    keep = (freqs >= 20) & (freqs <= 20000)
    total = np.sum(pxx[keep]) + 1e-20
    grid = np.geomspace(20, 20000, n_points)
    out = np.empty_like(grid)
    half = 2 ** (smooth_oct / 2)
    for i, f in enumerate(grid):
        sel = (freqs >= f / half) & (freqs <= f * half)
        out[i] = np.mean(pxx[sel]) if np.any(sel) else np.interp(f, freqs, pxx)
    return grid, 10 * np.log10(out / total + 1e-20)


def measure(audio: np.ndarray, sr: int) -> dict:
    """Full measurement set used in the before/after tables."""
    return {
        "lufs": integrated_lufs(audio, sr),
        "true_peak_db": true_peak_db(audio, sr),
        "sample_peak_db": sample_peak_db(audio),
        "lra": loudness_range(audio, sr),
        "duration_s": audio.shape[1] / sr,
        "bands": band_balance(audio, sr),
    }


def comparison_rows(measurements: dict[str, dict]) -> tuple[list[str], list[list]]:
    """Build a table (headers, rows) comparing several measurement dicts side by side."""
    names = list(measurements)
    headers = ["Параметр"] + names
    rows = [
        ["Громкость, LUFS"] + [f"{m['lufs']:.1f}" for m in measurements.values()],
        ["True peak, dBTP"] + [f"{m['true_peak_db']:.1f}" for m in measurements.values()],
        ["LRA, LU"] + [f"{m['lra']:.1f}" for m in measurements.values()],
        ["Длина, с"] + [f"{m['duration_s']:.1f}" for m in measurements.values()],
    ]
    for band, label in BAND_LABELS.items():
        rows.append([f"{label}, дБ"] + [f"{m['bands'][band]:.1f}" for m in measurements.values()])
    return headers, rows


def band_distance(a: dict, b: dict) -> float:
    """Mean absolute difference between two band_balance dicts (dB)."""
    return float(np.mean([abs(a[k] - b[k]) for k in BANDS_HZ]))
