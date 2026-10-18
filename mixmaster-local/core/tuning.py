"""Pitch correction (natural note fixing or hard auto-tune) and key detection.

Pitch tracking: pYIN (librosa). Shifting: Rubber Band via pedalboard.time_stretch with a
time-varying pitch curve and formant preservation, so the voice keeps its character.
"""

from __future__ import annotations

import numpy as np
from scipy.ndimage import median_filter, uniform_filter1d

from .audio_io import AudioError

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
SCALES = {
    "major": [0, 2, 4, 5, 7, 9, 11],
    "minor": [0, 2, 3, 5, 7, 8, 10],
    "chromatic": list(range(12)),
}
SCALE_LABELS = {"major": "мажор", "minor": "минор", "chromatic": "хроматика"}
# Krumhansl-Kessler key profiles.
_KK_MAJOR = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
_KK_MINOR = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])

DETECT_SR = 16000
HOP = 160  # 10 ms at 16 kHz
FRAME = 1024
CHUNK_S = 60.0
# Rubber Band applies a time-varying pitch curve ~85 ms early (measured); the curve is delayed by this.
CURVE_LEAD_S = 0.085


def key_name(tonic: int, scale: str) -> str:
    return f"{NOTE_NAMES[tonic % 12]} {SCALE_LABELS.get(scale, scale)}"


def allowed_pitch_classes(tonic: int, scale: str) -> np.ndarray:
    """Pitch classes (0..11) of a key."""
    return np.array(sorted((tonic + s) % 12 for s in SCALES[scale]))


def nearest_note(midi: np.ndarray, pcs: np.ndarray) -> np.ndarray:
    """Nearest MIDI note (float input) whose pitch class is in pcs."""
    m = np.asarray(midi, dtype=np.float64)[..., None]
    cand = pcs[None, :] + 12.0 * np.round((m - pcs[None, :]) / 12.0)
    idx = np.argmin(np.abs(m - cand), axis=-1)
    return np.take_along_axis(cand, idx[..., None], axis=-1)[..., 0]


def _mono16k(audio: np.ndarray, sr: int, max_seconds: float | None = None) -> np.ndarray:
    import librosa

    x = audio.mean(axis=0) if audio.ndim == 2 else audio
    if max_seconds and len(x) > sr * max_seconds:
        mid = len(x) // 2
        half = int(sr * max_seconds / 2)
        x = x[mid - half:mid + half]
    return librosa.resample(np.asarray(x, dtype=np.float32), orig_sr=sr, target_sr=DETECT_SR)


def detect_pitch(audio: np.ndarray, sr: int) -> tuple[np.ndarray, np.ndarray, float]:
    """pYIN pitch track: (midi per frame with NaN where unvoiced, voiced probability, hop seconds)."""
    import librosa

    y = _mono16k(audio, sr)
    if not np.any(np.abs(y) > 1e-4):
        raise AudioError("Вокал пустой: нечего тюнить.")
    f0, voiced, prob = librosa.pyin(y, fmin=65.0, fmax=1100.0, sr=DETECT_SR, frame_length=FRAME,
                                    hop_length=HOP, center=True)
    midi = np.where(voiced & (prob > 0.3), 69.0 + 12.0 * np.log2(np.maximum(f0, 1e-6) / 440.0), np.nan)
    return midi, np.nan_to_num(prob), HOP / DETECT_SR


def detect_key(beat: np.ndarray | None, sr: int, vocal_midi: np.ndarray | None = None) -> tuple[int, str, float]:
    """Estimate key (tonic, 'major'|'minor', confidence) from the beat chroma and/or vocal pitches."""
    import librosa

    profile = np.zeros(12)
    if beat is not None:
        y = librosa.resample(np.asarray((beat.mean(axis=0) if beat.ndim == 2 else beat), np.float32)
                             [: int(sr * 120)], orig_sr=sr, target_sr=22050)
        chroma = librosa.feature.chroma_cqt(y=y, sr=22050, hop_length=2048)
        c = chroma.mean(axis=1)
        profile += c / (c.sum() + 1e-12)
    if vocal_midi is not None and np.any(np.isfinite(vocal_midi)):
        pcs = np.round(vocal_midi[np.isfinite(vocal_midi)]).astype(int) % 12
        h = np.bincount(pcs, minlength=12).astype(float)
        profile += 0.5 * h / (h.sum() + 1e-12)
    if profile.sum() == 0:
        return 9, "minor", 0.0  # A minor fallback
    best, scores = None, []
    for tonic in range(12):
        for scale, prof in (("major", _KK_MAJOR), ("minor", _KK_MINOR)):
            r = float(np.corrcoef(profile, np.roll(prof, tonic))[0, 1])
            scores.append(r)
            if best is None or r > best[2]:
                best = (tonic, scale, r)
    second = sorted(scores)[-2]
    return best[0], best[1], float(best[2] - second)


def correction_curve(midi: np.ndarray, pcs: np.ndarray, hop_s: float, strength: float = 0.85,
                     retune_ms: float = 70.0, tolerance_cents: float = 20.0,
                     max_shift: float = 1.0) -> np.ndarray:
    """Pitch correction in semitones per frame.

    Each voiced run is smoothed over `retune_ms` (a running median); the note the singer is
    aiming at is judged over at least 250 ms, and vibrato faster than the window is kept. Notes whose centre is
    further than `tolerance_cents` from the scale are moved by `strength` of the distance.
    retune_ms near 0 with tolerance 0 snaps every frame: the classic hard auto-tune effect.
    """
    corr = np.zeros(len(midi))
    voiced = np.isfinite(midi)
    if not np.any(voiced):
        return corr
    w = max(int(round(retune_ms / 1000.0 / hop_s)), 1) | 1
    # The intended note is judged over >= 250 ms so vibrato does not flip it to a neighbour.
    w_note = w if retune_ms <= 15 else max(w, int(0.25 / hop_s) | 1)
    tol = tolerance_cents / 100.0
    edges = np.flatnonzero(np.diff(np.concatenate([[0], voiced.astype(int), [0]])))
    for start, stop in zip(edges[::2], edges[1::2]):
        seg = midi[start:stop]
        smooth = median_filter(seg, size=min(w, len(seg) | 1), mode="nearest") if w > 1 else seg
        centre = median_filter(seg, size=min(w_note, len(seg) | 1), mode="nearest") if w_note > 1 else seg
        dev = smooth - nearest_note(centre, pcs)
        if tol > 0:
            gate = np.clip((np.abs(dev) - tol) / max(tol * 0.5, 0.05), 0.0, 1.0)
        else:
            gate = np.ones_like(dev)
        corr[start:stop] = -dev * gate * strength
    # Soften jumps between notes / at run edges unless hard-tune was asked for.
    if retune_ms > 15:
        corr = uniform_filter1d(corr, size=max(int(0.02 / hop_s), 1), mode="nearest")
    return np.clip(corr, -max_shift, max_shift)


def apply_pitch_curve(audio: np.ndarray, sr: int, curve: np.ndarray, hop_s: float) -> np.ndarray:
    """Time-varying pitch shift (semitones per frame) with formant preservation, chunked."""
    from pedalboard import time_stretch

    if np.max(np.abs(curve)) < 0.005:
        return audio.copy()
    n = audio.shape[1]
    frame_t = np.arange(len(curve)) * hop_s
    step, ov = int(sr * CHUNK_S), int(sr * 1.0)
    out = np.zeros_like(audio)
    weight = np.zeros(n, dtype=np.float32)
    for start in range(0, n, step):
        a, b = max(start - ov, 0), min(start + step + ov, n)
        t = np.arange(a, b) / sr - CURVE_LEAD_S
        semis = np.interp(t, frame_t, curve, left=0.0).astype(np.float64)
        seg = time_stretch(np.ascontiguousarray(audio[:, a:b]), sr, 1.0, semis, high_quality=True,
                           preserve_formants=True)[:, : b - a]
        if seg.shape[1] < b - a:
            seg = np.pad(seg, ((0, 0), (0, b - a - seg.shape[1])))
        win = np.ones(b - a, dtype=np.float32)
        if a > 0:
            win[:ov] = np.linspace(0, 1, ov, dtype=np.float32)
        if b < n:
            win[-ov:] = np.linspace(1, 0, ov, dtype=np.float32)
        out[:, a:b] += seg * win
        weight[a:b] += win
    return (out / np.maximum(weight, 1e-6)).astype(np.float32)


def resolve_key(cfg: dict, beat: np.ndarray | None, sr: int, vocal_midi: np.ndarray | None):
    """(tonic, scale, how) from the tuning config: explicit key or automatic detection."""
    scale = cfg.get("scale", "minor")
    key = str(cfg.get("key", "auto"))
    if key != "auto" and key in NOTE_NAMES:
        return NOTE_NAMES.index(key), scale, "задана вручную"
    tonic, detected_scale, conf = detect_key(beat, sr, vocal_midi)
    if scale == "chromatic":
        return tonic, "chromatic", "хроматика (тональность не нужна)"
    how = "определена по биту" if beat is not None else "определена по вокалу"
    if cfg.get("scale_auto", True):
        scale = detected_scale
    return tonic, scale, how + (" (уверенность низкая, лучше задай вручную)" if conf < 0.02 else "")


def tune_vocal(audio: np.ndarray, sr: int, cfg: dict, key: tuple[int, str] | None = None,
               beat: np.ndarray | None = None) -> tuple[np.ndarray, dict]:
    """Detect pitch, pick the key, correct. Returns (audio, report with before/after stats)."""
    midi, _prob, hop_s = detect_pitch(audio, sr)
    if key is None:
        tonic, scale, how = resolve_key(cfg, beat, sr, midi)
    else:
        (tonic, scale), how = key, "общая для всех голосов"
    pcs = allowed_pitch_classes(tonic, scale)
    curve = correction_curve(midi, pcs, hop_s, cfg["strength"], cfg["retune_ms"], cfg["tolerance_cents"],
                             cfg.get("max_shift_semitones", 1.0))
    out = apply_pitch_curve(audio, sr, curve, hop_s)
    voiced = np.isfinite(midi)
    dev_before = (midi - nearest_note(np.nan_to_num(midi), pcs))[voiced] * 100
    corrected_midi = midi + curve
    dev_after = (corrected_midi - nearest_note(np.nan_to_num(corrected_midi), pcs))[voiced] * 100
    report = {
        "key": key_name(tonic, scale), "tonic": tonic, "scale": scale, "key_source": how,
        "voiced_pct": float(voiced.mean() * 100),
        "dev_before_cents": float(np.mean(np.abs(dev_before))) if dev_before.size else 0.0,
        "dev_after_cents": float(np.mean(np.abs(dev_after))) if dev_after.size else 0.0,
        "corrected_pct": float(np.mean(np.abs(curve[voiced]) > 0.05) * 100) if voiced.any() else 0.0,
        "max_shift_cents": float(np.max(np.abs(curve)) * 100) if curve.size else 0.0,
        "times": np.arange(len(midi)) * hop_s, "midi_before": midi, "midi_after": corrected_midi,
    }
    return out, report


def summary_line(rep: dict, label: str = "Вокал") -> str:
    """One-line Russian summary of a tuning report."""
    return (f"{label}: тональность {rep['key']} ({rep['key_source']}); среднее отклонение от нот "
            f"{rep['dev_before_cents']:.0f} → {rep['dev_after_cents']:.0f} центов, поправлено "
            f"{rep['corrected_pct']:.0f}% звучащих мест, максимум {rep['max_shift_cents']:.0f} центов.")
