"""Audio loading, resampling, validation and export helpers.

Internal format everywhere: float32 numpy array shaped [channels, samples] at 44100 Hz.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import soundfile as sf
from pedalboard.io import AudioFile

TARGET_SR = 44100
SUPPORTED_EXT = {".wav", ".flac", ".aif", ".aiff", ".mp3", ".ogg"}


class AudioError(Exception):
    """Error with a user-facing (Russian) message."""


def load_audio(path, target_sr: int = TARGET_SR) -> tuple[np.ndarray, int]:
    """Read an audio file, resample to target_sr, return float32 [channels, samples].

    Mono stays mono; more than two channels are folded down to stereo.
    """
    path = Path(path)
    if not path.exists():
        raise AudioError(f"Файл не найден: {path.name}")
    if path.suffix.lower() not in SUPPORTED_EXT:
        raise AudioError(f"Формат {path.suffix or '?'} не поддерживается. Нужен WAV (или FLAC/AIFF/MP3).")
    try:
        with AudioFile(str(path)) as f:
            if int(f.samplerate) != target_sr:
                f = f.resampled_to(target_sr)
            chunks = []
            step = target_sr * 30
            while f.tell() < f.frames:
                chunks.append(f.read(step))
            audio = np.concatenate(chunks, axis=1) if chunks else np.zeros((1, 0), np.float32)
    except AudioError:
        raise
    except Exception as exc:  # decoder errors from pedalboard
        raise AudioError(f"Не удалось прочитать {path.name}: файл повреждён или формат не поддерживается ({exc})") from exc
    audio = np.asarray(audio, dtype=np.float32)
    if audio.shape[0] > 2:
        left = audio[0::2].mean(axis=0)
        right = audio[1::2].mean(axis=0)
        audio = np.stack([left, right]).astype(np.float32)
    return audio, target_sr


def to_stereo(audio: np.ndarray) -> np.ndarray:
    """Duplicate mono into two channels; stereo is returned unchanged."""
    if audio.ndim == 1:
        audio = audio[None, :]
    if audio.shape[0] == 1:
        return np.repeat(audio, 2, axis=0)
    return audio[:2]


def loop_to_length(audio: np.ndarray, n_samples: int, sr: int = TARGET_SR, fade_ms: float = 10.0) -> np.ndarray:
    """Loop audio until it is at least n_samples long; longer audio is left untouched.

    A short fade-out is applied only if the last repeat had to be cut.
    """
    n = audio.shape[1]
    if n == 0:
        raise AudioError("Бит пустой: нечего зацикливать.")
    if n >= n_samples:
        return audio
    reps = int(np.ceil(n_samples / n))
    out = np.tile(audio, (1, reps))[:, :n_samples].copy()
    if n_samples % n:
        fade = min(int(sr * fade_ms / 1000.0), n_samples)
        out[:, -fade:] *= np.linspace(1.0, 0.0, fade, dtype=np.float32)
    return out


def shift(audio: np.ndarray, offset_ms: float, sr: int = TARGET_SR) -> np.ndarray:
    """Shift audio in time: positive = later (pad start), negative = earlier (trim start)."""
    k = int(round(sr * offset_ms / 1000.0))
    if k > 0:
        return np.pad(audio, ((0, 0), (k, 0)))
    if k < 0:
        return audio[:, -k:]
    return audio


def pad_to(audio: np.ndarray, n_samples: int) -> np.ndarray:
    """Zero-pad (or trim) to exactly n_samples."""
    n = audio.shape[1]
    if n >= n_samples:
        return audio[:, :n_samples]
    return np.pad(audio, ((0, 0), (0, n_samples - n)))


def save_wav(path, audio: np.ndarray, sr: int = TARGET_SR, bit_depth: int = 24) -> Path:
    """Write a WAV file (16/24-bit PCM or 32-bit float). Values are clipped to [-1, 1] for PCM."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    subtype = {16: "PCM_16", 24: "PCM_24", 32: "FLOAT"}[bit_depth]
    data = audio if bit_depth == 32 else np.clip(audio, -1.0, 1.0)
    with sf.SoundFile(str(path), "w", samplerate=sr, channels=data.shape[0], subtype=subtype) as f:
        step = sr * 30
        for start in range(0, data.shape[1], step):
            f.write(data[:, start:start + step].T)
    return path


def save_mp3(path, audio: np.ndarray, sr: int = TARGET_SR, quality: str = "V0") -> Path:
    """Write an MP3 via Pedalboard's built-in LAME encoder (VBR quality)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with AudioFile(str(path), "w", sr, audio.shape[0], quality=quality) as f:
        f.write(np.clip(audio, -1.0, 1.0))
    return path


def validate_audio(audio: np.ndarray, sr: int, name: str = "файл", min_seconds: float = 1.0) -> list[str]:
    """Check audio for obvious problems. Raises AudioError for fatal ones, returns warnings."""
    warnings = []
    if audio.size == 0 or audio.shape[1] < int(sr * min_seconds):
        raise AudioError(f"{name}: слишком короткий (меньше {min_seconds:g} с).")
    if not np.all(np.isfinite(audio[:, ::97])):
        raise AudioError(f"{name}: в файле битые значения (NaN/Inf).")
    peak = float(np.max(np.abs(audio)))
    if peak < 10 ** (-60 / 20):
        raise AudioError(f"{name}: файл тихий или пустой (пик ниже -60 dBFS).")
    if peak < 10 ** (-30 / 20):
        warnings.append(f"{name}: очень тихий (пик {20 * np.log10(peak):.1f} dBFS), проверь экспорт.")
    clipped = int(np.sum(np.abs(audio) >= 0.999))
    ratio = clipped / audio.size
    if ratio > 1e-3:
        warnings.append(f"{name}: сильный клиппинг ({ratio * 100:.2f}% сэмплов на 0 dBFS). Лучше переэкспортировать тише.")
    elif clipped > 50:
        warnings.append(f"{name}: есть клиппинг ({clipped} сэмплов на 0 dBFS).")
    if audio.shape[0] == 2:
        dc = np.abs(audio.mean(axis=1)).max()
        if dc > 0.02:
            warnings.append(f"{name}: заметное смещение постоянной составляющей (DC), будет срезано фильтром.")
    return warnings


def is_effectively_mono(audio: np.ndarray, tol_db: float = -50.0) -> bool:
    """True if the stereo side signal is negligible (mono or fake stereo)."""
    if audio.shape[0] < 2:
        return True
    step = max(audio.shape[1] // 2_000_000, 1)
    mid = (audio[0, ::step] + audio[1, ::step]) * 0.5
    side = (audio[0, ::step] - audio[1, ::step]) * 0.5
    m = np.sqrt(np.mean(mid.astype(np.float64) ** 2)) + 1e-12
    s = np.sqrt(np.mean(side.astype(np.float64) ** 2))
    return 20 * np.log10(s / m + 1e-12) < tol_db
