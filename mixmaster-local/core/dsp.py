"""Shared DSP helpers: chunked processing, filters, envelopes, dynamic band gain.

Everything here works on float32 arrays shaped [channels, samples] and processes
long signals in chunks so 10+ minute files do not blow up memory.
"""

from __future__ import annotations

import numpy as np
from scipy import signal

CHUNK_SECONDS = 20.0


def db_to_lin(db):
    """Convert dB to linear gain."""
    return np.power(10.0, np.asarray(db) / 20.0)


def lin_to_db(x, floor: float = 1e-10):
    """Convert linear amplitude to dB with a floor."""
    return 20.0 * np.log10(np.maximum(np.abs(x), floor))


def chunk_len(sr: int) -> int:
    """Chunk size in samples used for streaming processing."""
    return int(sr * CHUNK_SECONDS)


def run_board(board, audio: np.ndarray, sr: int, tail_seconds: float = 0.0) -> np.ndarray:
    """Run a Pedalboard (or single plugin) over audio in chunks.

    The plugin state is kept between chunks. Zeros are pushed at the end to flush
    plugin latency and, if requested, effect tails (reverb, delay).
    """
    board.reset()
    n = audio.shape[1]
    step = chunk_len(sr)
    flush = int(sr * max(tail_seconds, 0.0)) + int(sr * 0.5)
    out = []
    for start in range(0, n, step):
        out.append(board.process(np.ascontiguousarray(audio[:, start:start + step]), sr, reset=False))
    out.append(board.process(np.zeros((audio.shape[0], flush), np.float32), sr, reset=False))
    y = np.concatenate(out, axis=1)
    total = n + int(sr * max(tail_seconds, 0.0))
    if y.shape[1] < total:
        y = np.pad(y, ((0, 0), (0, total - y.shape[1])))
    return y[:, :total].astype(np.float32, copy=False)


def sos_filter(sos: np.ndarray, audio: np.ndarray, sr: int) -> np.ndarray:
    """Causal SOS filter applied per channel in chunks (state carried over)."""
    out = np.empty_like(audio, dtype=np.float32)
    step = chunk_len(sr)
    for ch in range(audio.shape[0]):
        zi = np.zeros((sos.shape[0], 2))
        for start in range(0, audio.shape[1], step):
            seg, zi = signal.sosfilt(sos, audio[ch, start:start + step], zi=zi)
            out[ch, start:start + step] = seg
    return out


def butter_sos(kind: str, freq, sr: int, order: int = 2) -> np.ndarray:
    """Butterworth SOS design ('highpass', 'lowpass', 'bandpass')."""
    nyq = sr / 2.0
    if np.isscalar(freq):
        wn = min(max(float(freq) / nyq, 1e-4), 0.999)
    else:
        wn = [min(max(float(f) / nyq, 1e-4), 0.999) for f in freq]
    return signal.butter(order, wn, btype=kind, output="sos")


def highpass(audio: np.ndarray, sr: int, freq: float, order: int = 2) -> np.ndarray:
    """Butterworth high-pass."""
    return sos_filter(butter_sos("highpass", freq, sr, order), audio, sr)


def lowpass(audio: np.ndarray, sr: int, freq: float, order: int = 2) -> np.ndarray:
    """Butterworth low-pass."""
    return sos_filter(butter_sos("lowpass", freq, sr, order), audio, sr)


def bandpass(audio: np.ndarray, sr: int, lo: float, hi: float, order: int = 2) -> np.ndarray:
    """Butterworth band-pass (order is per edge)."""
    return sos_filter(butter_sos("bandpass", (lo, hi), sr, order), audio, sr)


def envelope(x: np.ndarray, sr: int, attack_ms: float, release_ms: float) -> np.ndarray:
    """Look-ahead peak envelope of a mono signal (vectorised, no per-sample Python loop).

    A centred running maximum over the release window holds peaks (and starts rising
    half a window early, like a look-ahead detector); a one-pole smoother with
    tau = max(attack, release / 4) rounds the edges.
    """
    from scipy.ndimage import maximum_filter1d

    rect = np.abs(np.asarray(x, dtype=np.float32))
    hold = max(int(sr * release_ms / 1000.0), 1)
    if hold > 1:
        rect = maximum_filter1d(rect, size=hold, mode="nearest")
    tau_ms = max(attack_ms, release_ms / 4.0, 0.01)
    env = _one_pole(rect, np.exp(-1.0 / (sr * tau_ms / 1000.0)))
    return env.astype(np.float32, copy=False)


def _one_pole(x: np.ndarray, a: float) -> np.ndarray:
    """One-pole low-pass y[n] = (1-a) x[n] + a y[n-1], chunked."""
    b, den = [1.0 - a], [1.0, -a]
    out = np.empty(len(x), dtype=np.float32)
    zi = np.array([x[0] * a]) if len(x) else np.zeros(1)
    step = 1 << 21
    for start in range(0, len(x), step):
        seg, zi = signal.lfilter(b, den, x[start:start + step], zi=zi)
        out[start:start + step] = seg
    return out


def smooth_gain(gain_db: np.ndarray, sr: int, attack_ms: float, release_ms: float) -> np.ndarray:
    """Smooth a gain-reduction curve (dB, <= 0): fast when reducing, slow when recovering."""
    gr = -np.asarray(gain_db, dtype=np.float32)  # positive reduction
    return -envelope(gr, sr, attack_ms, release_ms)


def apply_band_gain(audio: np.ndarray, band: np.ndarray, gain_db: np.ndarray) -> np.ndarray:
    """Dynamic band processing: out = audio + (g - 1) * band.

    With 0 dB gain the output is bit-identical to the input, so the process only
    touches the band while it is being reduced.
    """
    g = db_to_lin(gain_db).astype(np.float32) - 1.0
    return audio + band * g[None, :]


def rms_envelope_db(x: np.ndarray, sr: int, window_ms: float = 50.0, hop_ms: float = 10.0):
    """Windowed RMS of a mono signal in dB, returned at hop resolution."""
    win = max(int(sr * window_ms / 1000.0), 1)
    hop = max(int(sr * hop_ms / 1000.0), 1)
    sq = np.asarray(x, dtype=np.float64) ** 2
    csum = np.concatenate([[0.0], np.cumsum(sq)])
    starts = np.arange(0, max(len(x) - win, 0) + 1, hop)
    if len(starts) == 0:
        return np.array([-120.0])
    ms = (csum[starts + win] - csum[starts]) / win
    return 10.0 * np.log10(np.maximum(ms, 1e-12))


def active_levels(env_db: np.ndarray, gate_below_max: float = 40.0, floor_db: float = -60.0):
    """Levels of an envelope that belong to actual signal (gates silence/noise)."""
    if env_db.size == 0:
        return env_db
    gate = max(env_db.max() - gate_below_max, floor_db)
    act = env_db[env_db > gate]
    return act if act.size else env_db


def mono(audio: np.ndarray) -> np.ndarray:
    """Mono sum (mean of channels) as float32."""
    return audio.mean(axis=0).astype(np.float32) if audio.shape[0] > 1 else audio[0].astype(np.float32)


def soft_clip(audio: np.ndarray, ceiling_db: float, knee_db: float = 6.0) -> np.ndarray:
    """Soft-knee clipper: linear below (ceiling - knee), tanh-saturates up to the ceiling.

    Transparent for everything under the knee; only the loudest peaks are rounded off.
    """
    c = float(db_to_lin(ceiling_db))
    k = float(db_to_lin(ceiling_db - knee_db))
    mag = np.abs(audio)
    over = mag > k
    if not np.any(over):
        return audio.astype(np.float32, copy=False)
    out = audio.astype(np.float32, copy=True)
    shaped = k + (c - k) * np.tanh((mag[over] - k) / (c - k))
    out[over] = np.sign(audio[over]) * shaped
    return out
