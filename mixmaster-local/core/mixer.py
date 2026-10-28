"""Vocal chain, beat processing and balance (mode 1).

Vocal chain order: high-pass -> low-mid correction -> compressor(s) -> de-esser ->
presence/air -> space (reverb + tempo delay on a filtered wet return).
"""

from __future__ import annotations

import numpy as np
from scipy.ndimage import uniform_filter1d
from pedalboard import Compressor, Delay, Distortion, HighShelfFilter, LowShelfFilter, PeakFilter, Pedalboard, Reverb

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
    info = {"reverb": float(rv["mix"]), "delay_ms": None, "space_duck_db": float(cfg.get("space_duck_db", 0.0))}
    total = out.shape[1]
    # Returns dip while the voice sings and bloom in the gaps: words stay clear (common rap move).
    duck = None
    if cfg.get("space_duck_db", 0.0) > 0:
        duck = dsp.db_to_lin(duck_curve(dry, sr, total, float(cfg["space_duck_db"]))).astype(np.float32)

    def add_return(board, lowcut, highcut, mix, source=dry):
        wet = dsp.run_board(board, source, sr, tail_seconds=SPACE_TAIL_S)
        wet = dsp.highpass(wet, sr, lowcut, order=2)
        wet = dsp.lowpass(wet, sr, highcut, order=2)
        gain = dsp.db_to_lin(dry_lufs - integrated_lufs(wet, sr))
        wet = wet * np.float32(gain * mix)
        return wet * duck[None, : wet.shape[1]] if duck is not None else wet

    if rv["mix"] > 0:
        board = Pedalboard([
            Delay(delay_seconds=0.02, feedback=0.0, mix=1.0),  # pre-delay keeps words clear
            Reverb(room_size=rv["room_size"], damping=rv["damping"], wet_level=1.0, dry_level=0.0, width=rv["width"]),
        ])
        out += add_return(board, rv["lowcut_hz"], rv["highcut_hz"], rv["mix"])
    if use_delay:
        sec = 60.0 / float(bpm) * NOTE_BEATS.get(dl["note"], 0.5)
        board = Pedalboard([Delay(delay_seconds=sec, feedback=float(dl["feedback"]), mix=1.0)])
        source = dry
        if dl.get("mode", "always") == "throws":
            # Delay "throws": only the last word of each phrase is sent to the echo.
            source = dry * phrase_end_mask(dry, sr)[None, :]
        out += add_return(board, dl.get("lowcut_hz", 300), dl["highcut_hz"],
                          dl["mix"] * (2.0 if source is not dry else 1.0), source)
        info["delay_ms"] = sec * 1000
        info["delay_mode"] = dl.get("mode", "always")
    return out, info


def vocal_rider(x: np.ndarray, sr: int, cfg: dict) -> tuple[np.ndarray, dict]:
    """Automatic fader riding before the compressor: evens out phrase-to-phrase level jumps.

    The 400 ms loudness of the active vocal is pulled toward its median by up to
    `range_db`; pauses, breaths and noise are left alone.
    """
    if not cfg.get("enabled", False) or cfg.get("range_db", 0) <= 0:
        return x, {"range_used_db": 0.0}
    hop = 0.01
    env = dsp.rms_envelope_db(dsp.mono(x), sr, 400.0, hop * 1000)
    act = dsp.active_levels(env, gate_below_max=30.0)
    target = float(np.median(act))
    rng = float(cfg["range_db"])
    gain = np.clip(target - env, -rng, rng) * float(cfg.get("amount", 1.0))
    gain[env < target - 15.0] = np.minimum(gain[env < target - 15.0], 0.0)  # never lift breaths and noise
    gain = uniform_filter1d(gain, size=max(int(0.25 / hop), 1), mode="nearest")  # offline: symmetric smoothing
    t_frames = np.arange(len(gain)) * hop + 0.2
    curve = np.interp(np.arange(x.shape[1]) / sr, t_frames, gain).astype(np.float32)
    return (x * dsp.db_to_lin(curve)[None, :]).astype(np.float32), {"range_used_db": float(np.ptp(gain))}


def parallel_compression(x: np.ndarray, sr: int, cfg: dict) -> np.ndarray:
    """New-York style parallel compression: a crushed, high-passed copy blended under the vocal."""
    mix = float(cfg.get("mix", 0.0))
    if mix <= 0:
        return x
    env = dsp.active_levels(dsp.rms_envelope_db(dsp.mono(x), sr, 50.0, 10.0))
    thr = float(np.percentile(env, 30))  # deep: 15-25 dB of gain reduction on loud words
    crushed = dsp.highpass(x, sr, cfg.get("highpass_hz", 200), order=2)
    crushed = dsp.run_board(Compressor(threshold_db=thr, ratio=cfg.get("ratio", 10.0), attack_ms=cfg.get("attack_ms", 1.0),
                                       release_ms=cfg.get("release_ms", 60.0)), crushed, sr)
    gain = dsp.db_to_lin(integrated_lufs(x, sr) - integrated_lufs(crushed, sr)) * mix
    return (x + crushed * np.float32(gain)).astype(np.float32)


def saturate(x: np.ndarray, sr: int, cfg: dict) -> np.ndarray:
    """Gentle harmonic saturation blended in parallel and level-matched (density without obvious distortion)."""
    drive, mix = float(cfg.get("drive_db", 0.0)), float(cfg.get("mix", 0.0))
    if drive <= 0 or mix <= 0:
        return x
    peak = float(np.max(np.abs(x))) + 1e-9
    wet = dsp.run_board(Distortion(drive_db=drive), x / np.float32(peak * 1.12), sr) * np.float32(peak * 1.12)
    wet = dsp.lowpass(wet, sr, cfg.get("lowpass_hz", 14000), order=2)  # tame fizz / aliasing
    wet *= np.float32(dsp.db_to_lin(integrated_lufs(x, sr) - integrated_lufs(wet, sr)))
    return ((1.0 - mix) * x + mix * wet).astype(np.float32)


def phrase_end_mask(x: np.ndarray, sr: int, tail_ms: float = 280.0, gap_ms: float = 300.0) -> np.ndarray:
    """1.0 on the last `tail_ms` of every phrase (a phrase ends with >= gap_ms of silence), else 0."""
    env = dsp.lin_to_db(dsp.envelope(dsp.mono(x), sr, 5.0, 60.0))
    act = env > (np.percentile(env[env > env.max() - 50], 30) - 6.0)
    n = len(act)
    mask = np.zeros(n, dtype=np.float32)
    gap, tail = int(sr * gap_ms / 1000), int(sr * tail_ms / 1000)
    edges = np.flatnonzero(np.diff(act.astype(np.int8)) == -1)  # phrase -> silence
    for e in edges:
        if e + gap <= n and not act[e + 1:e + gap].any() or e + gap > n:
            mask[max(0, e - tail):e + 1] = 1.0
    ramp = int(sr * 0.01)
    if ramp > 1:
        mask = np.convolve(mask, np.ones(ramp, dtype=np.float32) / ramp, mode="same").astype(np.float32)
    return mask


def pan_mono(x: np.ndarray, pan: float) -> np.ndarray:
    """Constant-power pan of a mono signal (-1 = left, +1 = right); centre keeps unity on both sides."""
    theta = (float(np.clip(pan, -1.0, 1.0)) + 1.0) * np.pi / 4.0
    m = dsp.mono(x)
    return np.stack([m * np.cos(theta), m * np.sin(theta)]).astype(np.float32) * np.float32(np.sqrt(2.0))


def process_vocal(vocal: np.ndarray, sr: int, preset: dict, bpm: float | None = None,
                  reference_density: dict | None = None, pan: float = 0.0) -> tuple[np.ndarray, dict]:
    """Full vocal chain. Returns stereo vocal (with a short effect tail) and a report.

    pan != 0 places the dry voice in the stereo field (used for doubles and harmonies);
    reverb and delay stay stereo.
    """
    cfg = preset["vocal"]
    x = dsp.highpass(vocal, sr, cfg["highpass_hz"], order=4)
    eq = adaptive_eq_gains(x, sr, cfg, reference_density)
    x = dsp.run_board(PeakFilter(cfg["lowmid_cut"]["freq_hz"], eq["lowmid"], cfg["lowmid_cut"]["q"]), x, sr)
    x, rider = vocal_rider(x, sr, cfg.get("rider", {}))

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
    x = parallel_compression(x, sr, cfg.get("parallel", {}))

    ds = cfg["deesser"]
    x, ds_stats = deess(x, sr, tuple(ds["band_hz"]), ds["amount"])

    tone = Pedalboard([
        PeakFilter(cfg["presence"]["freq_hz"], eq["presence"], cfg["presence"]["q"]),
        HighShelfFilter(cfg["air_shelf"]["freq_hz"], eq["air"], 0.7),
    ])
    x = dsp.run_board(tone, x, sr)
    x = saturate(x, sr, cfg.get("saturation", {}))
    x = pan_mono(x, pan) if pan else to_stereo(x)
    x, sp = space(x, sr, cfg, bpm)
    report = {
        "eq_lowmid_db": eq["lowmid"], "eq_presence_db": eq["presence"], "eq_air_db": eq["air"],
        "comp_threshold_db": cs["threshold_db"], "peak_comp": cs["peak_comp"],
        "deesser_max_gr_db": ds_stats["max_gr_db"], "deesser_active_pct": ds_stats["active_pct"],
        "rider_range_db": rider["range_used_db"], **sp,
    }
    return x.astype(np.float32), report


# ---------------------------------------------------------------- backing vocals

BACKING_ROLES = ("double", "harmony", "adlib")


def align_offset(lead: np.ndarray, voice: np.ndarray, sr: int, max_ms: float = 60.0) -> int:
    """Constant offset (samples) that best lines `voice` up with `lead` (envelope cross-correlation).

    Positive = the voice is late and must be moved earlier. Returns 0 when the match is weak.
    """
    hop = max(sr // 1000, 1)  # 1 ms resolution
    n = min(lead.shape[1], voice.shape[1], sr * 60)
    if n < sr:
        return 0

    def env(x):
        e = dsp.envelope(dsp.mono(x[:, :n]), sr, 2.0, 20.0)[::hop].astype(np.float64)
        e = np.diff(e, prepend=e[0]).clip(min=0)  # onsets matter more than sustain
        return (e - e.mean()) / (e.std() + 1e-12)

    a, b = env(lead), env(voice)
    max_lag = int(max_ms)
    lags = np.arange(-max_lag, max_lag + 1)
    scores = np.array([np.dot(a[max(0, -k):len(a) - max(0, k)], b[max(0, k):len(b) - max(0, -k)]) for k in lags])
    scores /= len(a)
    best = int(np.argmax(scores))
    if scores[best] < 0.15:
        return 0
    return int(lags[best] * hop)


def backing_preset(preset: dict, role: str) -> dict:
    """Vocal chain settings for a backing voice: the lead preset adjusted by its role."""
    import copy

    rc = preset["backing"]["roles"][role]
    pr = copy.deepcopy(preset)
    v = pr["vocal"]
    v["highpass_hz"] = max(v["highpass_hz"], rc["highpass_hz"])
    v["deesser"]["amount"] = float(min(1.0, v["deesser"]["amount"] + rc["deess_extra"]))
    v["brightness_db"] = v.get("brightness_db", 0.0) + rc["brightness_db"]
    v["reverb"]["mix"] = v["reverb"]["mix"] + rc["reverb_extra"]
    v["delay"]["mix"] = v["delay"]["mix"] + rc["delay_extra"]
    return pr


def process_backing(voices: list[tuple[np.ndarray, str]], lead_raw: np.ndarray, lead_processed: np.ndarray,
                    sr: int, preset: dict, bpm: float | None = None,
                    reference_density: dict | None = None) -> tuple[np.ndarray | None, list[dict]]:
    """Doubles / harmonies / ad-libs around the lead.

    Each voice is aligned to the lead (doubles and harmonies), run through the lead chain
    adjusted by its role, panned (alternating L/R) and balanced against the others by its
    role level; the group gets a glue compressor and a small presence dip so the lead's
    words stay in front, and is set `bus_level_lu` under the lead.
    """
    if not voices:
        return None, []
    from .mastering import bus_compressor

    cfg = preset["backing"]
    lead_lufs = integrated_lufs(lead_processed, sr)
    width = float(cfg["width"])
    outs, reports = [], []
    for k, (audio, role) in enumerate(voices):
        role = role if role in BACKING_ROLES else "double"
        rc = cfg["roles"][role]
        x = dsp.mono(audio)[None, :]
        shift_samples = align_offset(lead_raw, x, sr, cfg["align_max_ms"]) if rc["align"] else 0
        if shift_samples > 0:
            x = x[:, shift_samples:]
        elif shift_samples < 0:
            x = np.pad(x, ((0, 0), (-shift_samples, 0)))
        # Alternate L/R over all voices so two voices always end up on opposite sides.
        pan = rc["pan"] * width * (-1 if k % 2 == 0 else 1) * (1.0 if k < 2 else 0.5)
        y, rep = process_vocal(x, sr, backing_preset(preset, role), bpm, reference_density, pan=pan)
        gain_db = lead_lufs + rc["level_lu"] - integrated_lufs(y, sr)  # balance inside the group
        y *= np.float32(dsp.db_to_lin(gain_db))
        outs.append(y)
        reports.append({"role": role, "pan": pan, "align_ms": shift_samples / sr * 1000, "gain_db": gain_db, **rep})
    n = max(o.shape[1] for o in outs)
    bus = np.sum([pad_to(o, n) for o in outs], axis=0).astype(np.float32)
    bus = bus_compressor(bus, sr, cfg["bus_ratio"], 10.0, 120.0, percentile=80.0)
    if cfg["presence_dip_db"]:
        bus = dsp.run_board(PeakFilter(cfg["presence_dip_hz"], cfg["presence_dip_db"], 0.8), bus, sr)
    # The whole group sits a fixed distance under the lead, however many voices and however
    # correlated they are (identical doubles add up louder than separate takes).
    target = lead_lufs + cfg["bus_level_lu"] + cfg["level_offset_lu"]
    bus *= np.float32(dsp.db_to_lin(target - integrated_lufs(bus, sr)))
    return bus, reports


def sum_vocals(lead: np.ndarray, bus: np.ndarray | None) -> np.ndarray:
    """Lead + backing bus (padded to the longer one)."""
    if bus is None:
        return lead
    n = max(lead.shape[1], bus.shape[1])
    return (pad_to(lead, n) + pad_to(bus, n)).astype(np.float32)


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
    shelves = []
    if cfg.get("low_shelf_db", 0.0):
        shelves.append(LowShelfFilter(cfg.get("low_shelf_hz", 100.0), float(cfg["low_shelf_db"]), 0.7))
    if cfg.get("high_shelf_db", 0.0):
        shelves.append(HighShelfFilter(cfg.get("high_shelf_hz", 8000.0), float(cfg["high_shelf_db"]), 0.7))
    if shelves:
        b = dsp.run_board(Pedalboard(shelves), b, sr)
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
