"""High-level pipelines for the three modes, shared by the UI, the CLI and the tests."""

from __future__ import annotations

import copy
import gc
import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

import numpy as np

from . import analysis, mastering, mixer
from .audio_io import AudioError, load_audio, loop_to_length, save_mp3, save_wav, shift, to_stereo, validate_audio
from .presets import resolve

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / "outputs"
Progress = Callable[[float, str], None]


@dataclass
class Params:
    """User-facing knobs (UI sliders). None means 'take the preset value'."""

    vocal_over_beat_lu: float | None = None
    deesser: float | None = None
    reverb: float | None = None
    delay: float | None = None
    brightness_db: float | None = None
    duck_db: float | None = None
    loudness: str | None = None  # "reference" | "target"
    target_lufs: float | None = None
    bpm: float | None = None
    offset_ms: float = 0.0
    vocal_target: str | None = None  # "preset" | "reference"
    export16: bool = False
    export_mp3: bool = False


@dataclass
class Result:
    """Everything a run produces: files, measurements, spectra and messages."""

    out_dir: Path
    files: dict = field(default_factory=dict)
    measurements: dict = field(default_factory=dict)
    spectra: dict = field(default_factory=dict)
    warnings: list = field(default_factory=list)
    report: dict = field(default_factory=dict)
    summary: str = ""


def apply_params(preset: dict, p: Params) -> dict:
    """Return a full preset with the UI overrides applied."""
    pr = resolve(copy.deepcopy(preset))
    v = pr["vocal"]
    if p.deesser is not None:
        v["deesser"]["amount"] = float(p.deesser)
    if p.reverb is not None:
        v["reverb"]["mix"] = float(p.reverb)
    if p.delay is not None:
        v["delay"]["mix"] = float(p.delay)
    if p.brightness_db is not None:
        v["brightness_db"] = float(p.brightness_db)
    if p.vocal_target:
        v["adaptive_eq"]["target"] = p.vocal_target
    if p.duck_db is not None:
        pr["beat"]["duck_db"] = float(p.duck_db)
    if p.vocal_over_beat_lu is not None:
        pr["balance"]["vocal_over_beat_lu"] = float(p.vocal_over_beat_lu)
    if p.loudness:
        pr["master"]["loudness"] = p.loudness
    if p.target_lufs is not None:
        pr["master"]["target_lufs"] = float(p.target_lufs)
    return pr


def _target_lufs(pr: dict) -> float | None:
    """Target loudness for reference modes: None = like the reference."""
    m = pr["master"]
    if m.get("loudness") == "target":
        return float(m["target_lufs"] if m["target_lufs"] is not None else m["default_target_lufs"])
    return None


def _noop(_f: float, _m: str) -> None:
    pass


def _load(path, name: str, warnings: list) -> np.ndarray:
    if not path:
        raise AudioError(f"Не загружен файл: {name}.")
    audio, sr = load_audio(path)
    warnings += validate_audio(audio, sr, name)
    return audio


def _out_dir(stem: str, out_root: Path | None) -> Path:
    root = Path(out_root) if out_root else OUTPUT_DIR
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in stem)[:40] or "track"
    d = root / f"{time.strftime('%Y%m%d_%H%M%S')}_{safe}"
    n = 1
    while d.exists():
        d = root / f"{time.strftime('%Y%m%d_%H%M%S')}_{safe}_{n}"
        n += 1
    d.mkdir(parents=True)
    return d


def _finish(res: Result, stem: str, master: np.ndarray, before: np.ndarray, sr: int,
            p: Params, reference: np.ndarray | None, progress: Progress) -> Result:
    """Export files, A/B pair, measurements, spectra and a human summary."""
    progress(0.85, "Экспорт файлов")
    d = res.out_dir
    res.files["master24"] = str(save_wav(d / f"{stem}_master_24bit.wav", master, sr, 24))
    if p.export16:
        res.files["master16"] = str(save_wav(d / f"{stem}_master_16bit.wav", master, sr, 16))
    if p.export_mp3:
        res.files["mp3"] = str(save_mp3(d / f"{stem}_master.mp3", master, sr))
    a, b, common = mastering.ab_match(before, master, sr)
    res.files["ab_before"] = str(save_wav(d / "ab_before.wav", a, sr, 16))
    res.files["ab_after"] = str(save_wav(d / "ab_after.wav", b, sr, 16))
    res.report["ab_lufs"] = common

    progress(0.92, "Замеры до/после")
    res.measurements["Мастер"] = analysis.measure(master, sr)
    res.spectra["До"] = analysis.spectrum_curve(before, sr)
    res.spectra["Результат"] = analysis.spectrum_curve(master, sr)
    if reference is not None:
        res.measurements["Референс"] = analysis.measure(reference, sr)
        res.spectra["Референс"] = analysis.spectrum_curve(reference, sr)
    res.summary = _summary(res)
    with open(d / "report.json", "w", encoding="utf-8") as f:
        json.dump({"files": res.files, "measurements": res.measurements, "report": res.report,
                   "warnings": res.warnings}, f, ensure_ascii=False, indent=2, default=float)
    progress(1.0, "Готово")
    return res


def _summary(res: Result) -> str:
    """Short Russian summary: loudness/peak and how close to the reference we got."""
    m = res.measurements["Мастер"]
    lines = [f"Мастер: {m['lufs']:.1f} LUFS, true peak {m['true_peak_db']:.1f} dBTP, LRA {m['lra']:.1f} LU."]
    ref = res.measurements.get("Референс")
    before_key = next((k for k in ("Сведение", "Исходник") if k in res.measurements), None)
    if ref and before_key:
        b = res.measurements[before_key]
        lines.append(
            f"Разница с референсом по громкости: было {b['lufs'] - ref['lufs']:+.1f} LU, стало {m['lufs'] - ref['lufs']:+.1f} LU."
        )
        lines.append(
            f"Отличие баланса полос от референса: было {analysis.band_distance(b['bands'], ref['bands']):.1f} дБ, "
            f"стало {analysis.band_distance(m['bands'], ref['bands']):.1f} дБ (в среднем по полосам)."
        )
    return "\n".join(lines)


def _reference(path, warnings: list) -> np.ndarray:
    ref = to_stereo(_load(path, "Референс", warnings))
    warnings += mastering.validate_reference(ref, 44100)
    return ref


def run_mix_and_master(vocal_path, beat_path, reference_path, preset: dict, p: Params,
                       out_root: Path | None = None, progress: Progress = _noop) -> Result:
    """Mode 1: vocal + beat -> vocal chain, beat carving, balance -> Matchering master."""
    pr = apply_params(preset, p)
    sr = 44100
    warnings: list = []
    progress(0.02, "Загрузка и проверка файлов")
    vocal = _load(vocal_path, "Вокал", warnings)
    beat = _load(beat_path, "Бит", warnings)
    reference = _reference(reference_path, warnings)
    stem = Path(vocal_path).stem
    res = Result(out_dir=_out_dir(stem, out_root), warnings=warnings)
    res.measurements["Вокал"] = analysis.measure(vocal, sr)
    res.measurements["Бит"] = analysis.measure(beat, sr)

    progress(0.12, "Вокальная цепочка")
    if p.offset_ms:
        vocal = shift(vocal, p.offset_ms, sr)
    dry_len = vocal.shape[1]
    ref_density = analysis.band_density(reference, sr)
    vocal_p, vrep = mixer.process_vocal(vocal, sr, pr, bpm=p.bpm or None, reference_density=ref_density)
    if pr["vocal"]["delay"]["mix"] > 0 and not p.bpm:
        warnings.append("BPM не указан: delay выключен.")

    progress(0.35, "Бит: место под вокал")
    beat_p, brep = mixer.prepare_beat(beat, sr, vocal_p, pr, target_len=dry_len)

    progress(0.45, "Баланс и сумма")
    bal = pr["balance"]
    mix, mrep = mixer.mix(vocal_p, beat_p, sr, bal["vocal_over_beat_lu"], bal["headroom_db"])
    raw_beat = loop_to_length(to_stereo(beat), dry_len, sr)
    raw, _ = mixer.mix(to_stereo(vocal), raw_beat, sr, bal["vocal_over_beat_lu"], bal["headroom_db"])
    res.files["premaster"] = str(save_wav(res.out_dir / f"{stem}_mix_premaster_24bit.wav", mix, sr, 24))
    res.measurements["Сведение"] = analysis.measure(mix, sr)
    del vocal, vocal_p, beat, beat_p, raw_beat  # free RAM before Matchering (long tracks)
    gc.collect()

    progress(0.55, "Мастеринг (Matchering)")
    master, mstr = mastering.master_with_reference(mix, reference, sr, pr, _target_lufs(pr))
    warnings += mstr.pop("warnings") + mstr.pop("loudness_warnings", [])
    res.report = {"vocal": vrep, "beat": brep, "mix": mrep, "master": mstr}
    return _finish(res, stem, master, raw, sr, p, reference, progress)


def run_master_reference(track_path, reference_path, preset: dict, p: Params,
                         out_root: Path | None = None, progress: Progress = _noop) -> Result:
    """Mode 2: finished mix + reference -> light preparation -> Matchering."""
    pr = apply_params(preset, p)
    sr = 44100
    warnings: list = []
    progress(0.05, "Загрузка и проверка файлов")
    track = to_stereo(_load(track_path, "Трек", warnings))
    reference = _reference(reference_path, warnings)
    stem = Path(track_path).stem
    res = Result(out_dir=_out_dir(stem, out_root), warnings=warnings)
    res.measurements["Исходник"] = analysis.measure(track, sr)
    progress(0.3, "Мастеринг (Matchering)")
    master, mstr = mastering.master_with_reference(track, reference, sr, pr, _target_lufs(pr))
    warnings += mstr.pop("warnings") + mstr.pop("loudness_warnings", [])
    res.report = {"master": mstr}
    return _finish(res, stem, master, track, sr, p, reference, progress)


def run_master_no_reference(track_path, preset: dict, p: Params,
                            out_root: Path | None = None, progress: Progress = _noop) -> Result:
    """Mode 3: finished mix -> preset EQ, compressor, LUFS normalisation, true-peak limiter."""
    pr = apply_params(preset, p)
    sr = 44100
    warnings: list = []
    progress(0.05, "Загрузка и проверка файлов")
    track = to_stereo(_load(track_path, "Трек", warnings))
    stem = Path(track_path).stem
    res = Result(out_dir=_out_dir(stem, out_root), warnings=warnings)
    res.measurements["Исходник"] = analysis.measure(track, sr)
    progress(0.3, "Мастеринг (цепочка пресета)")
    master, mstr = mastering.master_without_reference(track, sr, pr, p.target_lufs)
    warnings += mstr.pop("warnings") + mstr.pop("loudness_warnings", [])
    res.report = {"master": mstr}
    return _finish(res, stem, master, track, sr, p, None, progress)
