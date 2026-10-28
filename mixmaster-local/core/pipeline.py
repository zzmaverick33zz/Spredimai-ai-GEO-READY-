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

from . import analysis, mastering, mixer, tuning
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
    # pitch correction
    tune: bool | None = None
    tune_key: str | None = None  # "auto" or a note name ("C#")
    tune_scale: str | None = None  # "auto" | "minor" | "major" | "chromatic"
    tune_strength: float | None = None
    tune_retune_ms: float | None = None
    tune_tolerance: float | None = None
    tune_backing: bool | None = None
    # backing vocals: list of (path, role) with role in double / harmony / adlib
    backing: list = field(default_factory=list)
    backing_level_lu: float | None = None
    backing_width: float | None = None
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
    t = pr["tuning"]
    if p.tune is not None:
        t["enabled"] = bool(p.tune)
    if p.tune_key:
        t["key"] = p.tune_key
    if p.tune_scale:
        t["scale_auto"] = p.tune_scale == "auto"
        if p.tune_scale != "auto":
            t["scale"] = p.tune_scale
    for attr, key in (("tune_strength", "strength"), ("tune_retune_ms", "retune_ms"), ("tune_tolerance", "tolerance_cents")):
        if getattr(p, attr) is not None:
            t[key] = float(getattr(p, attr))
    if p.tune_backing is not None:
        t["apply_to_backing"] = bool(p.tune_backing)
    if p.backing_level_lu is not None:
        pr["backing"]["level_offset_lu"] = float(p.backing_level_lu)
    if p.backing_width is not None:
        pr["backing"]["width"] = float(p.backing_width)
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
            p: Params, reference: np.ndarray | None, progress: Progress, cache: "StageCache | None" = None) -> Result:
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
        def ref_stats():
            return analysis.measure(reference, sr), analysis.spectrum_curve(reference, sr)
        m_ref, sp_ref = cache.get_or("m_ref", "", ref_stats) if cache is not None else ref_stats()
        res.measurements["Референс"] = m_ref
        res.spectra["Референс"] = sp_ref
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


@dataclass
class MixInputs:
    """Decoded inputs of mode 1 (kept in memory so a chat session can re-render quickly)."""

    vocal: np.ndarray
    beat: np.ndarray
    reference: np.ndarray
    backs: list  # [(audio, role)]
    stem: str
    warnings: list = field(default_factory=list)


class StageCache(dict):
    """Keeps the last `depth` results of every render stage with the settings they were made from,
    so both a new edit and an undo can reuse untouched stages."""

    depth = 2

    def get_or(self, name: str, key: str, fn: Callable, reused: list | None = None):
        entries = self.setdefault(name, [])
        for i, (k, value) in enumerate(entries):
            if k == key:
                entries.insert(0, entries.pop(i))
                if reused is not None:
                    reused.append(name)
                return value
        value = fn()
        entries.insert(0, (key, value))
        del entries[self.depth:]
        return value


def _key(*parts) -> str:
    return json.dumps(parts, sort_keys=True, default=str, ensure_ascii=False)


def load_mix_inputs(vocal_path, beat_path, reference_path, backing=None) -> MixInputs:
    """Load and validate everything mode 1 needs."""
    warnings: list = []
    vocal = _load(vocal_path, "Вокал", warnings)
    beat = _load(beat_path, "Бит", warnings)
    reference = _reference(reference_path, warnings)
    backs = [(_load(path, f"Бэк {i + 1}", warnings), role) for i, (path, role) in enumerate(backing or []) if path]
    return MixInputs(vocal, beat, reference, backs, Path(vocal_path).stem, warnings)


def render_mix(inp: MixInputs, pr: dict, p: Params, out_dir: Path, cache: StageCache | None = None,
               progress: Progress = _noop) -> Result:
    """Mode 1 render from loaded inputs and a full preset. Stages whose settings did not change
    since the previous render (same cache) are reused, so a small edit re-renders quickly."""
    cache = cache if cache is not None else StageCache()
    sr = 44100
    reused: list = []
    res = Result(out_dir=Path(out_dir), warnings=list(inp.warnings))
    res.out_dir.mkdir(parents=True, exist_ok=True)
    stem = inp.stem
    res.measurements["Вокал"] = cache.get_or("m_vocal", "", lambda: analysis.measure(inp.vocal, sr))
    res.measurements["Бит"] = cache.get_or("m_beat", "", lambda: analysis.measure(inp.beat, sr))
    ref_density = cache.get_or("ref_density", "", lambda: analysis.band_density(inp.reference, sr))
    bpm = p.bpm or None

    progress(0.04, "Подготовка дорожек")
    k_prep = _key("prep", p.offset_ms)

    def prep():
        vocal, backs = inp.vocal, inp.backs
        if p.offset_ms:
            vocal = shift(vocal, p.offset_ms, sr)
            backs = [(shift(a, p.offset_ms, sr), r) for a, r in backs]
        dry_len = max([vocal.shape[1]] + [a.shape[1] for a, _ in backs])
        return vocal, backs, dry_len

    vocal, backs, dry_len = cache.get_or("prep", k_prep, prep, reused)

    tcfg = pr["tuning"]
    k_tune = _key(k_prep, tcfg if tcfg["enabled"] else False, bool(backs))

    def tune():
        notes, trep_public = [], None
        v, bk = vocal, backs
        if tcfg["enabled"]:
            progress(0.08, "Коррекция нот: вокал")
            v, trep = tuning.tune_vocal(vocal, sr, tcfg, beat=inp.beat)
            notes.append(tuning.summary_line(trep, "Тюн лида"))
            trep_public = {k: val for k, val in trep.items() if not isinstance(val, np.ndarray)}
            if backs and tcfg["apply_to_backing"]:
                progress(0.14, "Коррекция нот: бэки")
                key = (trep["tonic"], trep["scale"])
                tuned = []
                for i, (a, r) in enumerate(backs):
                    a, brep_t = tuning.tune_vocal(a, sr, tcfg, key=key)
                    notes.append(tuning.summary_line(brep_t, f"Тюн бэка {i + 1}"))
                    tuned.append((a, r))
                bk = tuned
        return v, bk, notes, trep_public

    vocal_t, backs_t, notes, trep = cache.get_or("tune", k_tune, tune, reused)
    notes = list(notes)
    if trep:
        res.report["tuning"] = trep
        res.files["tuned"] = str(save_wav(res.out_dir / f"{stem}_vocal_tuned_24bit.wav", vocal_t, sr, 24))

    progress(0.2, "Вокальная цепочка")
    k_vocal = _key(k_tune, pr["vocal"], bpm)
    vocal_p, vrep = cache.get_or(
        "vocal", k_vocal, lambda: mixer.process_vocal(vocal_t, sr, pr, bpm=bpm, reference_density=ref_density), reused)
    if pr["vocal"]["delay"]["mix"] > 0 and not bpm:
        res.warnings.append("BPM не указан: delay выключен.")

    k_back = _key(k_vocal, pr["backing"])
    if backs_t:
        progress(0.3, "Бэк-вокал: выравнивание, панорама, баланс")
    bus, back_rep = cache.get_or(
        "backing", k_back,
        lambda: mixer.process_backing(backs_t, vocal_t, vocal_p, sr, pr, bpm, ref_density) if backs_t else (None, []),
        reused)
    if back_rep:
        notes.append(_backing_line(back_rep))

    progress(0.38, "Бит: место под вокал")
    k_beat = _key(k_vocal, pr["beat"], dry_len)
    beat_p, brep = cache.get_or("beat", k_beat,
                                lambda: mixer.prepare_beat(inp.beat, sr, vocal_p, pr, target_len=dry_len), reused)

    progress(0.45, "Баланс и сумма")
    bal = pr["balance"]
    k_mix = _key(k_back, k_beat, bal)

    def do_mix():
        vocals = mixer.sum_vocals(vocal_p, bus)
        mix, mrep = mixer.mix(vocals, beat_p, sr, bal["vocal_over_beat_lu"], bal["headroom_db"])
        stem_vocals = vocals * np.float32(10 ** (mrep["trim_db"] / 20)) if bus is not None else None
        return mix, mrep, stem_vocals, analysis.measure(mix, sr)

    mix, mrep, stem_vocals, m_mix = cache.get_or("mix", k_mix, do_mix, reused)
    if stem_vocals is not None:
        res.files["vocals"] = str(save_wav(res.out_dir / f"{stem}_vocals_stem_24bit.wav", stem_vocals, sr, 24))
    res.files["premaster"] = str(save_wav(res.out_dir / f"{stem}_mix_premaster_24bit.wav", mix, sr, 24))
    res.measurements["Сведение"] = m_mix

    def do_raw():
        raw_vocals = mixer.sum_vocals(to_stereo(vocal), _raw_bus(backs))
        raw_beat = loop_to_length(to_stereo(inp.beat), dry_len, sr)
        return mixer.mix(raw_vocals, raw_beat, sr, bal["vocal_over_beat_lu"], bal["headroom_db"])[0]

    raw = cache.get_or("raw", _key(k_prep, bal), do_raw, reused)

    progress(0.55, "Мастеринг (Matchering)")
    k_master = _key(k_mix, pr["master"])
    master, mstr = cache.get_or(
        "master", k_master, lambda: mastering.master_with_reference(mix, inp.reference, sr, pr, _target_lufs(pr)),
        reused)
    mstr = dict(mstr)
    res.warnings += list(mstr.pop("warnings", [])) + list(mstr.pop("loudness_warnings", []))
    gc.collect()
    res.report.update({"vocal": vrep, "backing": back_rep, "beat": brep, "mix": mrep, "master": mstr,
                       "stages_reused": reused})
    res = _finish(res, stem, master, raw, sr, p, inp.reference, progress, cache)
    if notes:
        res.summary += "\n" + "\n".join(notes)
    return res


def run_mix_and_master(vocal_path, beat_path, reference_path, preset: dict, p: Params,
                       out_root: Path | None = None, progress: Progress = _noop) -> Result:
    """Mode 1: vocal + beat -> vocal chain, beat carving, balance -> Matchering master."""
    pr = apply_params(preset, p)
    progress(0.02, "Загрузка и проверка файлов")
    inp = load_mix_inputs(vocal_path, beat_path, reference_path, p.backing)
    return render_mix(inp, pr, p, _out_dir(inp.stem, out_root), StageCache(), progress)


ROLE_LABELS = {"double": "дабл", "harmony": "гармония", "adlib": "адлибы"}


def _raw_bus(backs: list) -> np.ndarray | None:
    """Unprocessed backing voices summed (for the honest 'before' of the A/B)."""
    if not backs:
        return None
    n = max(a.shape[1] for a, _ in backs)
    total = np.zeros((2, n), np.float32)
    for a, _ in backs:
        st = to_stereo(a)
        total[:, :st.shape[1]] += st * np.float32(0.5)
    return total


def _backing_line(reports: list[dict]) -> str:
    """One-line Russian summary of the backing-vocal processing."""
    parts = []
    for i, r in enumerate(reports):
        side = "центр" if abs(r["pan"]) < 0.05 else ("лево" if r["pan"] < 0 else "право")
        parts.append(f"{i + 1}) {ROLE_LABELS[r['role']]}: {side} {abs(r['pan']) * 100:.0f}%, "
                     f"сдвиг {r['align_ms']:+.0f} мс")
    return "Бэк-вокал: " + "; ".join(parts) + "."


def run_tune_only(vocal_path, beat_path, preset: dict, p: Params,
                  out_root: Path | None = None, progress: Progress = _noop) -> Result:
    """Mode 4: pitch-correct a vocal (key from the optional beat) and export it dry for the DAW."""
    pr = apply_params(preset, p)
    sr = 44100
    warnings: list = []
    progress(0.05, "Загрузка и проверка файлов")
    vocal = _load(vocal_path, "Вокал", warnings)
    beat = _load(beat_path, "Бит", warnings) if beat_path else None
    stem = Path(vocal_path).stem
    res = Result(out_dir=_out_dir(stem + "_tune", out_root), warnings=warnings)
    progress(0.2, "Поиск нот и тональности")
    tuned, trep = tuning.tune_vocal(vocal, sr, pr["tuning"], beat=beat)
    progress(0.8, "Экспорт")
    d = res.out_dir
    res.files["master24"] = str(save_wav(d / f"{stem}_tuned_24bit.wav", tuned, sr, 24))
    if p.export16:
        res.files["master16"] = str(save_wav(d / f"{stem}_tuned_16bit.wav", tuned, sr, 16))
    if p.export_mp3:
        res.files["mp3"] = str(save_mp3(d / f"{stem}_tuned.mp3", tuned, sr))
    a, b, _ = mastering.ab_match(vocal, tuned, sr)
    res.files["ab_before"] = str(save_wav(d / "ab_before.wav", a, sr, 16))
    res.files["ab_after"] = str(save_wav(d / "ab_after.wav", b, sr, 16))
    res.measurements = {"Вокал": analysis.measure(vocal, sr), "После тюна": analysis.measure(tuned, sr)}
    res.spectra = {"До": analysis.spectrum_curve(vocal, sr), "Результат": analysis.spectrum_curve(tuned, sr)}
    res.report = {"tuning": trep}
    res.summary = tuning.summary_line(trep, "Вокал")
    with open(d / "report.json", "w", encoding="utf-8") as f:
        json.dump({"files": res.files, "tuning": {k: v for k, v in trep.items() if not isinstance(v, np.ndarray)},
                   "warnings": warnings}, f, ensure_ascii=False, indent=2, default=float)
    progress(1.0, "Готово")
    return res


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
