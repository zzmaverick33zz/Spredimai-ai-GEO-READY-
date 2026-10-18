"""Vocal chain, beat processing and balance (mode 1).

Vocal chain order: high-pass -> low-mid correction -> compressor(s) -> de-esser ->
presence/air -> space (reverb + tempo delay on a filtered wet return).
"""

from __future__ import annotations

import numpy as np
from pedalboard import Compressor, Delay, HighShelfFilter, PeakFilter, Pedalboard, Reverb

from . import dsp
from .analysis import band_density, integrated_lufs, true_peak_db
from .audio_io import loop_to_length, pad_to, to_stereo

NOTE_BEATS = {"1/4": 1.0, "1/8": 0.5, "1/8d": 0.75, "1/16": 0.25, "1/4d": 1.5}
SPACE_TAIL_S = 2.0


# --------------------------------------------------------------------- de-esser

def deess(audio: np.ndarray, sr: int, band_hz=(5500, 9000), amount: float = 0.6):
    """Split-band de-esser: reduces only the sibilance band while it exceeds the threshold.

    Detection uses two conditions: the band must be loud in absolute terms (percentile
    of its own envelope) and loud relative to the full-band signal (so bright vowels
    and hats are left alone). Returns (audio, stats).
    """
    amount = float(np.clip(amount, 0.0, 1.0))
    if amount <= 0.0:
        return audio, {"max_gr_db": 0.0, "active_pct": 0.0}
    lo, hi = band_hz
    band = dsp.bandpass(audio, sr, lo, hi, order=2)
    env_band = dsp.lin_to_db(dsp.envelope(np.max(np.abs(band), axis=0), sr, 1.0, 40.0))
    env_full = dsp.lin_to_db(dsp.envelope(np.max(np.abs(audio), axis=0), sr, 1.0, 40.0))
    active = env_full > env_full.max() - 45.0
    abs_thr = np.percentile(env_band[active], 70) if np.any(active) else env_band.max()
    rel_thr = env_full - (6.0 + 10.0 * amount)
    excess = np.minimum(env_band - abs_thr, env_band - rel_thr)
    ratio = 1.0 + 7.0 * amount
    max_gr = 3.0 + 9.0 * amount
    gr = np.clip(excess * (1.0 - 1.0 / ratio), 0.0, max_gr).astype(np.float32)
    gain_db = dsp.smooth_gain(-gr, sr, attack_ms=1.0, release_ms=50.0)
    out = dsp.apply_band_gain(audio, band, gain_db)
    stats = {"max_gr_db": float(-gain_db.min()), "active_pct": float(np.mean(gain_db < -1.0) * 100)}
    return out.astype(np.float32), stats


# ------------------------------------------------------------------ vocal chain

def adaptive_eq_gains(vocal: np.ndarray, sr: int, cfg: dict, reference_density: dict | None = None) -> dict:
    """Decide low-mid / presence / air gains: preset value + adaptive correction (±max_db)."""
    ad = cfg["adaptive_eq"]
    target = dict(cfg["target_curve"])
    if ad.get("target") == "reference" and reference_density:
        # Reference mix only approximates a vocal target: use its upper bands only.
        target["presence"] = reference_density["presence"]
        target["air"] = reference_density["air"]
    dens = band_density(vocal, sr)
    k, lim = float(ad["strength"]), float(ad["max_db"])
    adapt = {
        "lowmid": float(np.clip((target["lowmid"] - dens["lowmid"]) * k, -lim, 1.0)),
        "presence": float(np.clip((target["presence"] - dens["presence"]) * k, -lim, lim)),
        "air": float(np.clip((target["air"] - dens["air"]) * k, -lim, lim)),
    }
    bright = float(cfg.get("brightness_db", 0.0))
    return {
        "lowmid": cfg["lowmid_cut"]["gain_db"] + adapt["lowmid"],
        "presence": cfg["presence"]["gain_db"] + adapt["presence"] + 0.5 * bright,
        "air": cfg["air_shelf"]["gain_db"] + adapt["air"] + bright,
        "adaptive": adapt,
        "vocal_density": dens,
    }


def compressor_settings(vocal: np.ndarray, sr: int, cfg: dict) -> dict:
    """Derive compressor thresholds from the vocal's RMS envelope percentiles."""
    env = dsp.active_levels(dsp.rms_envelope_db(dsp.mono(vocal), sr, 50.0, 10.0))
    comp = cfg["compressor"]
    thr = float(np.percentile(env, comp.get("threshold_percentile", 55)))
    peak = 20 * np.log10(float(np.max(np.abs(vocal))) + 1e-10)
    crest = peak - float(np.percentile(env, 95))
    pk = cfg["peak_compressor"]
    use_peak = crest > pk["crest_trigger_db"]
    return {
        "threshold_db": thr,
        "crest_db": crest,
        "peak_comp": use_peak,
        "peak_threshold_db": max(peak - 6.0, float(np.percentile(env, 95))),
    }


def space(dry: np.ndarray, sr: int, cfg: dict, bpm: float | None) -> tuple[np.ndarray, dict]:
    """Add reverb and tempo delay as filtered wet returns. Mix values are wet level vs dry loudness."""
    rv, dl = cfg["reverb"], cfg["delay"]
    use_delay = bool(bpm) and dl["mix"] > 0
    if rv["mix"] <= 0 and not use_delay:
        return dry, {"reverb": 0.0, "delay_ms": None}
    out = pad_to(dry, dry.shape[1] + int(sr * SPACE_TAIL_S))
    dry_lufs = integrated_lufs(dry, sr)
    info = {"reverb": float(rv["mix"]), "delay_ms": None}

    def add_return(board, lowcut, highcut, mix):
        wet = dsp.run_board(board, dry, sr, tail_seconds=SPACE_TAIL_S)
        wet = dsp.highpass(wet, sr, lowcut, order=2)
        wet = dsp.lowpass(wet, sr, highcut, order=2)
        gain = dsp.db_to_lin(dry_lufs - integrated_lufs(wet, sr))
        return wet * np.float32(gain * mix)

    if rv["mix"] > 0:
        board = Pedalboard([
            Delay(delay_seconds=0.02, feedback=0.0, mix=1.0),  # pre-delay keeps words clear
            Reverb(room_size=rv["room_size"], damping=rv["damping"], wet_level=1.0, dry_level=0.0, width=rv["width"]),
        ])
        out += add_return(board, rv["lowcut_hz"], rv["highcut_hz"], rv["mix"])
    if use_delay:
        sec = 60.0 / float(bpm) * NOTE_BEATS.get(dl["note"], 0.5)
        board = Pedalboard([Delay(delay_seconds=sec, feedback=float(dl["feedback"]), mix=1.0)])
        out += add_return(board, dl.get("lowcut_hz", 300), dl["highcut_hz"], dl["mix"])
        info["delay_ms"] = sec * 1000
    return out, info


def process_vocal(vocal: np.ndarray, sr: int, preset: dict, bpm: float | None = None,
                  reference_density: dict | None = None) -> tuple[np.ndarray, dict]:
    """Full vocal chain. Returns stereo vocal (with a short effect tail) and a report."""
    cfg = preset["vocal"]
    x = dsp.highpass(vocal, sr, cfg["highpass_hz"], order=4)
    eq = adaptive_eq_gains(x, sr, cfg, reference_density)
    x = dsp.run_board(PeakFilter(cfg["lowmid_cut"]["freq_hz"], eq["lowmid"], cfg["lowmid_cut"]["q"]), x, sr)

    cs = compressor_settings(x, sr, cfg)
    comp = cfg["compressor"]
    chain = []
    if cs["peak_comp"]:
        pk = cfg["peak_compressor"]
        chain.append(Compressor(threshold_db=cs["peak_threshold_db"], ratio=pk["ratio"],
                                attack_ms=pk["attack_ms"], release_ms=pk["release_ms"]))
    chain.append(Compressor(threshold_db=cs["threshold_db"], ratio=comp["ratio"],
                            attack_ms=comp["attack_ms"], release_ms=comp["release_ms"]))
    x = dsp.run_board(Pedalboard(chain), x, sr)

    ds = cfg["deesser"]
    x, ds_stats = deess(x, sr, tuple(ds["band_hz"]), ds["amount"])

    tone = Pedalboard([
        PeakFilter(cfg["presence"]["freq_hz"], eq["presence"], cfg["presence"]["q"]),
        HighShelfFilter(cfg["air_shelf"]["freq_hz"], eq["air"], 0.7),
    ])
    x = to_stereo(dsp.run_board(tone, x, sr))
    x, sp = space(x, sr, cfg, bpm)
    report = {
        "eq_lowmid_db": eq["lowmid"], "eq_presence_db": eq["presence"], "eq_air_db": eq["air"],
        "comp_threshold_db": cs["threshold_db"], "peak_comp": cs["peak_comp"],
        "deesser_max_gr_db": ds_stats["max_gr_db"], "deesser_active_pct": ds_stats["active_pct"],
        **sp,
    }
    return x.astype(np.float32), report


# ------------------------------------------------------------------------- beat

def duck_curve(vocal: np.ndarray, sr: int, n_samples: int, duck_db: float) -> np.ndarray:
    """Gain curve (dB, <= 0) that dips by up to duck_db while the vocal is present."""
    env = dsp.lin_to_db(dsp.envelope(dsp.mono(vocal), sr, 5.0, 150.0))
    act = env[env > env.max() - 40.0]
    thr = float(np.percentile(act, 20)) if act.size else env.max()
    amt = np.clip((env - (thr - 6.0)) / 12.0, 0.0, 1.0)
    gain = (-duck_db * amt).astype(np.float32)
    gain = dsp.smooth_gain(gain, sr, attack_ms=10.0, release_ms=200.0)
    if len(gain) >= n_samples:
        return gain[:n_samples]
    return np.pad(gain, (0, n_samples - len(gain)))


def prepare_beat(beat: np.ndarray, sr: int, vocal: np.ndarray, preset: dict,
                 duck_db: float | None = None, target_len: int | None = None) -> tuple[np.ndarray, dict]:
    """Loop the beat under the vocal, carve 1-4 kHz statically and duck that band dynamically.

    target_len is the length the beat must cover (the dry vocal length, without effect tail).
    """
    cfg = preset["beat"]
    duck_db = cfg["duck_db"] if duck_db is None else duck_db
    target_len = vocal.shape[1] if target_len is None else target_len
    b = to_stereo(beat)
    looped = b.shape[1] < target_len
    b = loop_to_length(b, target_len, sr)
    if cfg["carve_db"]:
        b = dsp.run_board(PeakFilter(cfg["carve_freq_hz"], cfg["carve_db"], cfg["carve_q"]), b, sr)
    if duck_db > 0:
        lo, hi = cfg["duck_band_hz"]
        band = dsp.bandpass(b, sr, lo, hi, order=2)
        b = dsp.apply_band_gain(b, band, duck_curve(vocal, sr, b.shape[1], duck_db))
    return b.astype(np.float32), {"looped": looped, "duck_db": float(duck_db), "carve_db": cfg["carve_db"]}


# ---------------------------------------------------------------------- balance

def mix(vocal: np.ndarray, beat: np.ndarray, sr: int, vocal_over_beat_lu: float = 2.0,
        headroom_db: float = 3.0) -> tuple[np.ndarray, dict]:
    """Sum vocal and beat with vocal N LU above the beat, then set peak to -headroom dBTP."""
    n = max(vocal.shape[1], beat.shape[1])
    v, b = pad_to(vocal, n), pad_to(beat, n)
    lv, lb = integrated_lufs(vocal, sr), integrated_lufs(beat, sr)
    beat_gain_db = (lv - vocal_over_beat_lu) - lb
    out = v + b * np.float32(dsp.db_to_lin(beat_gain_db))
    tp = true_peak_db(out, sr)
    trim_db = min(-headroom_db - tp, 12.0)
    out *= np.float32(dsp.db_to_lin(trim_db))
    return out.astype(np.float32), {
        "vocal_lufs": lv, "beat_lufs": lb, "beat_gain_db": beat_gain_db,
        "trim_db": trim_db, "true_peak_db": tp + trim_db,
    }
