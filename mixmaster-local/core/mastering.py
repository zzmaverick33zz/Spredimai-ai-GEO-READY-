"""Mastering: Matchering with a reference, or a Pedalboard chain without one."""

from __future__ import annotations

import tempfile
from pathlib import Path

import matchering as mg
import numpy as np
from pedalboard import BrickwallLimiter, Compressor, HighShelfFilter, LowShelfFilter, PeakFilter, Pedalboard

from . import dsp
from .analysis import integrated_lufs, true_peak_db
from .audio_io import AudioError, is_effectively_mono, load_audio, save_wav

MIN_REFERENCE_S = 10.0
SHORT_REFERENCE_S = 30.0


def bus_compressor(audio: np.ndarray, sr: int, ratio: float, attack_ms: float, release_ms: float,
                   percentile: float = 90.0) -> np.ndarray:
    """Gentle glue compressor; threshold from the loud part of the RMS envelope."""
    env = dsp.active_levels(dsp.rms_envelope_db(dsp.mono(audio), sr, 300.0, 50.0))
    thr = float(np.percentile(env, percentile))
    comp = Compressor(threshold_db=thr, ratio=ratio, attack_ms=attack_ms, release_ms=release_ms)
    return dsp.run_board(comp, audio, sr)


def set_peak(audio: np.ndarray, sr: int, peak_db: float, max_gain_db: float = 12.0) -> tuple[np.ndarray, float]:
    """Scale audio so its true peak lands at peak_db (gain capped). Returns (audio, gain_db)."""
    gain = min(peak_db - true_peak_db(audio, sr), max_gain_db)
    return (audio * np.float32(dsp.db_to_lin(gain))).astype(np.float32), gain


def prepare_for_master(audio: np.ndarray, sr: int, preset: dict) -> tuple[np.ndarray, dict]:
    """Pre-master: ~25 Hz high-pass, very light 1.5:1 bus compression, headroom control."""
    m = preset["master"]
    x = dsp.highpass(audio, sr, m["highpass_hz"], order=2)
    x = bus_compressor(x, sr, m["bus_ratio"], m["bus_attack_ms"], m["bus_release_ms"])
    x, gain = set_peak(x, sr, -float(preset["balance"]["headroom_db"]))
    return x, {"premaster_gain_db": gain}


def validate_reference(audio: np.ndarray, sr: int) -> list[str]:
    """Reference sanity checks: length, mono/fake stereo, empty channel."""
    dur = audio.shape[1] / sr
    if dur < MIN_REFERENCE_S:
        raise AudioError(f"Референс слишком короткий ({dur:.1f} с). Нужно минимум {MIN_REFERENCE_S:.0f} с, лучше весь трек.")
    warnings = []
    if dur < SHORT_REFERENCE_S:
        warnings.append(f"Референс короткий ({dur:.0f} с): результат может быть менее точным, лучше взять весь трек.")
    if audio.shape[0] == 2:
        rms = np.sqrt(np.mean(audio[:, ::7].astype(np.float64) ** 2, axis=1))
        if rms.min() < rms.max() * 1e-3:
            raise AudioError("В референсе один канал пустой. Возьми нормальный стерео-файл.")
    if is_effectively_mono(audio):
        warnings.append("Референс фактически моно: стереобаза результата не будет подтянута. Лучше стерео-референс.")
    return warnings


def post_tone(audio: np.ndarray, sr: int, cfg: dict | None) -> tuple[np.ndarray, dict]:
    """Final tone/width moves applied AFTER Matchering, so the reference match does not undo them.

    bass_db / lowmid_db / presence_db / air_db: shelves and bells; width_db: side level;
    mono_bass_hz: below this frequency the side signal is removed (tight, mono low end).
    """
    cfg = cfg or {}
    moves = {k: float(cfg.get(k, 0.0)) for k in ("bass_db", "lowmid_db", "presence_db", "air_db", "width_db")}
    mono_hz = float(cfg.get("mono_bass_hz", 0.0) or 0.0)
    x = audio
    bands = []
    if moves["bass_db"]:
        bands.append(LowShelfFilter(100.0, moves["bass_db"], 0.7))
    if moves["lowmid_db"]:
        bands.append(PeakFilter(320.0, moves["lowmid_db"], 0.9))
    if moves["presence_db"]:
        bands.append(PeakFilter(3200.0, moves["presence_db"], 0.8))
    if moves["air_db"]:
        bands.append(HighShelfFilter(10000.0, moves["air_db"], 0.7))
    if bands:
        x = dsp.run_board(Pedalboard(bands), x, sr)
    if x.shape[0] == 2 and (moves["width_db"] or mono_hz > 0):
        mid = (x[0] + x[1]) * 0.5
        side = ((x[0] - x[1]) * 0.5)[None, :]
        if mono_hz > 0:
            side = dsp.highpass(side, sr, mono_hz, order=4)
        side = side[0] * np.float32(dsp.db_to_lin(moves["width_db"]))
        x = np.stack([mid + side, mid - side]).astype(np.float32)
    return x.astype(np.float32), {**moves, "mono_bass_hz": mono_hz}


def true_peak_guard(audio: np.ndarray, sr: int, ceiling_db: float = -1.0) -> tuple[np.ndarray, dict]:
    """Make sure true peak <= ceiling: brickwall limiter first, plain gain as the last resort."""
    tp = true_peak_db(audio, sr)
    info = {"limited": False}
    if tp > ceiling_db:
        lim = BrickwallLimiter(ceiling_db=ceiling_db - 0.3, release_ms=80.0, true_peak=True)
        audio = dsp.run_board(lim, audio, sr)
        info["limited"] = True
        tp = true_peak_db(audio, sr)
        if tp > ceiling_db:
            audio = audio * np.float32(dsp.db_to_lin(ceiling_db - 0.05 - tp))
            tp = true_peak_db(audio, sr)
    info["true_peak_db"] = tp
    return audio.astype(np.float32), info


MAX_LIMITER_GAIN_DB = 30.0


def normalize_loudness(audio: np.ndarray, sr: int, target_lufs: float, ceiling_db: float = -1.0,
                       iterations: int = 6) -> tuple[np.ndarray, dict]:
    """Gain -> soft clip -> true-peak limiter to hit target LUFS, re-measured and corrected.

    Limiting eats loudness, so each pass measures the result and corrects the gain using
    the observed slope (LUFS gained per dB of input gain).
    """
    lim = BrickwallLimiter(ceiling_db=ceiling_db - 0.3, release_ms=50.0, true_peak=True)
    gain_db = target_lufs - integrated_lufs(audio, sr)
    prev = None  # (gain_db, lufs)
    out, lufs, guard = audio, integrated_lufs(audio, sr), {}
    applied = gain_db = float(np.clip(gain_db, -40.0, MAX_LIMITER_GAIN_DB))
    for _ in range(iterations):
        applied = gain_db
        driven = dsp.soft_clip(audio * np.float32(dsp.db_to_lin(gain_db)), ceiling_db - 0.5)
        out = dsp.run_board(lim, driven, sr)
        del driven
        out, guard = true_peak_guard(out, sr, ceiling_db)
        lufs = integrated_lufs(out, sr)
        err = target_lufs - lufs
        if abs(err) < 0.2:
            break
        slope = 1.0
        if prev is not None and abs(gain_db - prev[0]) > 1e-3:
            slope = float(np.clip((lufs - prev[1]) / (gain_db - prev[0]), 0.15, 1.0))
        prev = (gain_db, lufs)
        gain_db = float(np.clip(gain_db + err / slope, -40.0, MAX_LIMITER_GAIN_DB))
        if prev[0] == MAX_LIMITER_GAIN_DB and gain_db == MAX_LIMITER_GAIN_DB:
            break
    warnings = []
    if abs(lufs - target_lufs) > 0.5:
        warnings.append(f"Цель {target_lufs:.1f} LUFS не достигнута без перегруза лимитера: получилось {lufs:.1f} LUFS.")
    return out, {"lufs": lufs, "gain_db": applied, "loudness_warnings": warnings, **guard}


def run_matchering(target: np.ndarray, reference: np.ndarray, sr: int, log: list | None = None) -> np.ndarray:
    """Run Matchering on in-memory audio (temp WAV files), return the mastered float32 audio."""
    log = log if log is not None else []
    with tempfile.TemporaryDirectory(prefix="mixmaster_") as tmp:
        tmp = Path(tmp)
        t_path, r_path, o_path = tmp / "target.wav", tmp / "reference.wav", tmp / "result.wav"
        save_wav(t_path, target, sr, 32)
        save_wav(r_path, reference, sr, 32)
        longest = max(target.shape[1], reference.shape[1]) / sr
        config = mg.Config(max_length=max(900.0, longest + 60.0), temp_folder=str(tmp))
        mg.log(warning_handler=lambda m: log.append(str(m)), info_handler=lambda m: None)
        try:
            mg.process(target=str(t_path), reference=str(r_path),
                       results=[mg.Result(str(o_path), "FLOAT", use_limiter=True)], config=config)
        except Exception as exc:
            raise AudioError(f"Matchering не смог обработать трек: {exc}") from exc
        out, _ = load_audio(o_path, sr)
    return out


def master_with_reference(audio: np.ndarray, reference: np.ndarray, sr: int, preset: dict,
                          target_lufs: float | None = None, prepare: bool = True) -> tuple[np.ndarray, dict]:
    """Prepare + Matchering. target_lufs=None keeps the reference loudness."""
    info = {"warnings": validate_reference(reference, sr)}
    if prepare:
        audio, prep = prepare_for_master(audio, sr, preset)
        info.update(prep)
    log: list = []
    out = run_matchering(audio, reference, sr, log)
    info["warnings"] += [f"Matchering: {m}" for m in log]
    out, info["post"] = post_tone(out, sr, preset["master"].get("post"))
    ceiling = float(preset["master"]["true_peak_db"])
    if target_lufs is not None:
        out, norm = normalize_loudness(out, sr, float(target_lufs), ceiling)
    else:
        out, norm = true_peak_guard(out, sr, ceiling)
    info.update(norm)
    return out, info


def master_eq(preset: dict) -> Pedalboard:
    """Build the preset's master EQ as a Pedalboard chain."""
    kinds = {"lowshelf": LowShelfFilter, "highshelf": HighShelfFilter, "peak": PeakFilter}
    bands = []
    for b in preset["master"].get("eq", []):
        cls = kinds.get(b.get("type", "peak"), PeakFilter)
        bands.append(cls(b["freq_hz"], b["gain_db"], b.get("q", 0.7)))
    return Pedalboard(bands)


def master_without_reference(audio: np.ndarray, sr: int, preset: dict,
                             target_lufs: float | None = None) -> tuple[np.ndarray, dict]:
    """Preset EQ -> compressor -> loudness normalisation -> true-peak limiter (iterated)."""
    m = preset["master"]
    target = float(target_lufs if target_lufs is not None else (m["target_lufs"] or m["default_target_lufs"]))
    x = dsp.highpass(audio, sr, m["highpass_hz"], order=2)
    x = dsp.run_board(master_eq(preset), x, sr)
    x = bus_compressor(x, sr, m["comp_ratio"], m["comp_attack_ms"], m["comp_release_ms"], percentile=80.0)
    x, post = post_tone(x, sr, m.get("post"))
    x, _ = set_peak(x, sr, -float(preset["balance"]["headroom_db"]))
    out, info = normalize_loudness(x, sr, target, float(m["true_peak_db"]))
    info["post"] = post
    info["target_lufs"] = target
    info["warnings"] = []
    return out, info


def ab_match(before: np.ndarray, after: np.ndarray, sr: int) -> tuple[np.ndarray, np.ndarray, float]:
    """Loudness-match two versions for a fair A/B: both are brought down to the quieter one's LUFS."""
    lb, la = integrated_lufs(before, sr), integrated_lufs(after, sr)
    common = min(lb, la)
    b = before * np.float32(dsp.db_to_lin(common - lb))
    a = after * np.float32(dsp.db_to_lin(common - la))
    # The quieter version may still peak above 0 dBFS (e.g. an unlimited pre-master); keep both safe.
    peak = max(np.max(np.abs(b)), np.max(np.abs(a)), 1e-9)
    if peak > 0.99:
        g = np.float32(0.99 / peak)
        b, a, common = b * g, a * g, common + 20 * np.log10(g)
    return b.astype(np.float32), a.astype(np.float32), float(common)
