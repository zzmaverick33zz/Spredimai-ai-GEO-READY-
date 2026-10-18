"""Synthetic test material: vocal-like signal, beat, reference mix."""

from __future__ import annotations

import numpy as np
from scipy import signal

SR = 44100


def sine(freq: float, seconds: float, amp_db: float = -20.0, sr: int = SR) -> np.ndarray:
    """Mono sine [1, n] with given peak level."""
    t = np.arange(int(sr * seconds)) / sr
    return (10 ** (amp_db / 20) * np.sin(2 * np.pi * freq * t)).astype(np.float32)[None, :]


def _noise_band(n: int, lo: float, hi: float, rng, sr: int = SR) -> np.ndarray:
    sos = signal.butter(4, [lo / (sr / 2), min(hi / (sr / 2), 0.99)], "bandpass", output="sos")
    return signal.sosfilt(sos, rng.standard_normal(n)).astype(np.float32)


def vocal(seconds: float = 12.0, sr: int = SR, seed: int = 1, sibilance: bool = True) -> np.ndarray:
    """Mono 'rap vocal': harmonic syllables with formants plus sibilant noise bursts."""
    rng = np.random.default_rng(seed)
    n = int(sr * seconds)
    t = np.arange(n) / sr
    f0 = 140 + 25 * np.sin(2 * np.pi * 0.7 * t)
    phase = 2 * np.pi * np.cumsum(f0) / sr
    voiced = sum((0.8 / k) * np.sin(k * phase) for k in range(1, 25))
    voiced = signal.sosfilt(signal.butter(2, [300 / (sr / 2), 3500 / (sr / 2)], "bandpass", output="sos"), voiced)
    voiced += 0.6 * signal.sosfilt(signal.butter(2, 250 / (sr / 2), "lowpass", output="sos"), voiced * 3)
    syl = 0.25  # syllable length, s
    gate = np.zeros(n)
    sib = np.zeros(n)
    noise = _noise_band(n, 5000, 10000, rng, sr)
    for i in range(int(seconds / syl)):
        s0 = int(i * syl * sr)
        if rng.random() < 0.15:
            continue  # pause
        ln = int(syl * sr * rng.uniform(0.6, 0.95))
        env = np.sin(np.linspace(0, np.pi, ln)) ** 0.5 * rng.uniform(0.4, 1.0)
        gate[s0:s0 + ln] = env[: max(0, min(ln, n - s0))]
        if sibilance and rng.random() < 0.25:
            sl = int(0.08 * sr)
            sib[s0:s0 + sl] = np.hanning(sl)[: max(0, min(sl, n - s0))]
    out = voiced * gate
    out = out / np.max(np.abs(out)) * 0.5
    out = out + 0.7 * noise / np.max(np.abs(noise)) * sib
    return (out / np.max(np.abs(out)) * 10 ** (-6 / 20)).astype(np.float32)[None, :]


def beat(seconds: float = 8.0, bpm: float = 120.0, sr: int = SR, seed: int = 2, bright: float = 1.0) -> np.ndarray:
    """Stereo beat: kick, snare, hats, bass and a pad chord."""
    rng = np.random.default_rng(seed)
    n = int(sr * seconds)
    t = np.arange(n) / sr
    beat_s = 60.0 / bpm
    out = np.zeros((2, n))
    k_len = int(0.35 * sr)
    kt = np.arange(k_len) / sr
    kick = np.sin(2 * np.pi * (45 + 120 * np.exp(-kt * 30)) * kt) * np.exp(-kt * 9)
    sn_len = int(0.2 * sr)
    snare = _noise_band(sn_len, 1500, 8000, rng, sr) * np.exp(-np.arange(sn_len) / sr * 25)
    hat_len = int(0.05 * sr)
    for i in range(int(seconds / beat_s * 2)):
        pos = int(i * beat_s / 2 * sr)
        if i % 4 == 0:
            seg = kick[: max(0, min(k_len, n - pos))]
            out[:, pos:pos + len(seg)] += seg
        if i % 4 == 2:
            seg = snare[: max(0, min(sn_len, n - pos))] * 0.6
            out[:, pos:pos + len(seg)] += seg
        hat = _noise_band(hat_len, 7000, 16000, rng, sr) * np.exp(-np.arange(hat_len) / sr * 80) * 0.25 * bright
        seg = hat[: max(0, min(hat_len, n - pos))]
        out[i % 2, pos:pos + len(seg)] += seg
    bass = 0.3 * np.sin(2 * np.pi * 55 * t)
    pad = sum(0.06 * np.sin(2 * np.pi * f * t + p) for f, p in [(220, 0), (277.2, 1), (329.6, 2), (440, 3)])
    out[0] += bass + pad
    out[1] += bass + np.roll(pad, 200)
    out /= np.max(np.abs(out))
    return (out * 10 ** (-3 / 20)).astype(np.float32)


def reference(seconds: float = 40.0, sr: int = SR) -> np.ndarray:
    """A loud, bright, compressed 'finished track' to use as a reference."""
    v = vocal(seconds, sr, seed=7)
    b = beat(seconds, 140, sr, seed=8, bright=2.0)
    mix = b * 0.7 + np.repeat(v, 2, axis=0) * 0.6
    mix = np.tanh(mix * 3.0) / np.tanh(3.0)  # crude loudness
    return (mix * 0.95).astype(np.float32)


def sung(notes, offsets_cents, note_s: float = 2.0, sr: int = SR, vibrato_cents: float = 15.0) -> np.ndarray:
    """Mono 'sung' melody: harmonic tone per MIDI note, detuned by offsets, with 5.5 Hz vibrato."""
    notes, offs = np.asarray(notes, float), np.asarray(offsets_cents, float)
    n = int(sr * note_s * len(notes))
    t = np.arange(n) / sr
    idx = np.minimum((t // note_s).astype(int), len(notes) - 1)
    f = 440 * 2 ** ((notes[idx] - 69 + (offs[idx] + vibrato_cents * np.sin(2 * np.pi * 5.5 * t)) / 100) / 12)
    ph = 2 * np.pi * np.cumsum(f) / sr
    x = sum((0.6 / k) * np.sin(k * ph) for k in range(1, 15))
    # short gaps between notes, like real phrasing
    gate = np.ones(n)
    for i in range(1, len(notes)):
        s0 = int(i * note_s * sr)
        gate[s0 - int(0.04 * sr):s0 + int(0.04 * sr)] = 0.0
    x = x * gate
    return (x / np.max(np.abs(x)) * 0.5).astype(np.float32)[None, :]


def chord_beat(root_midi: int, minor: bool, seconds: float = 12.0, sr: int = SR) -> np.ndarray:
    """Stereo pad cycling i - iv - v (or I - IV - V) chords plus a bass, for key detection."""
    t = np.arange(int(sr * seconds)) / sr
    third = 3 if minor else 4
    out = np.zeros_like(t)
    seg = len(t) // 4
    for k, deg in enumerate([0, 5, 7, 0]):
        sl = slice(k * seg, (k + 1) * seg)
        for iv in (0, third, 7):
            f = 440 * 2 ** ((root_midi + deg + iv - 69) / 12)
            out[sl] += np.sin(2 * np.pi * f * t[sl]) + 0.3 * np.sin(4 * np.pi * f * t[sl])
        out[sl] += 1.5 * np.sin(2 * np.pi * 440 * 2 ** ((root_midi + deg - 12 - 69) / 12) * t[sl])
    out = out / np.max(np.abs(out)) * 0.5
    return np.stack([out, out]).astype(np.float32)
