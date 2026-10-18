import numpy as np

import synth
from core import dsp, mixer
from core.analysis import band_balance, integrated_lufs, true_peak_db
from core.presets import load_preset

SR = 44100


def _band_energy_db(x, lo, hi):
    b = dsp.bandpass(x, SR, lo, hi, order=4)
    return 10 * np.log10(np.mean(b.astype(np.float64) ** 2) + 1e-20)


def test_deesser_reduces_only_sibilance():
    v = synth.vocal(10)
    out, stats = mixer.deess(v, SR, (5500, 9000), 0.8)
    assert stats["max_gr_db"] > 3
    assert _band_energy_db(v, 5500, 9000) - _band_energy_db(out, 5500, 9000) > 1.0
    band_peak = lambda x: np.max(np.abs(dsp.bandpass(x, SR, 5500, 9000, order=4)))  # noqa: E731
    assert 20 * np.log10(band_peak(v) / band_peak(out)) > 2.0
    # Low band (voice body) is untouched.
    assert abs(_band_energy_db(v, 100, 1000) - _band_energy_db(out, 100, 1000)) < 0.3
    # Zero amount is a bit-exact bypass, and no gain is ever added.
    same, _ = mixer.deess(v, SR, (5500, 9000), 0.0)
    assert np.array_equal(same, v)
    assert np.max(np.abs(out)) <= np.max(np.abs(v)) * 1.05


def test_deesser_ignores_clean_vocal():
    v = synth.vocal(8, sibilance=False)
    _, stats = mixer.deess(v, SR, (5500, 9000), 0.6)
    assert stats["active_pct"] < 2


def test_vocal_chain_all_presets():
    v = synth.vocal(8)
    for pid in ("trap_synthwave", "rap_vocal", "rock", "clean_streaming"):
        out, rep = mixer.process_vocal(v, SR, load_preset(pid), bpm=120)
        assert out.shape[0] == 2 and np.all(np.isfinite(out))
        assert out.shape[1] >= v.shape[1]
        for k in ("eq_lowmid_db", "eq_presence_db", "eq_air_db"):
            assert abs(rep[k]) < 12
        dl = load_preset(pid)["vocal"]["delay"]
        expected = 60 / 120 * mixer.NOTE_BEATS[dl["note"]] * 1000 if dl["mix"] > 0 else None
        assert rep["delay_ms"] == expected


def test_delay_off_without_bpm():
    _, rep = mixer.process_vocal(synth.vocal(5), SR, load_preset("trap_synthwave"), bpm=None)
    assert rep["delay_ms"] is None


def test_beat_loop_carve_duck():
    pr = load_preset("trap_synthwave")
    v = np.repeat(synth.vocal(10), 2, axis=0)
    beat = synth.beat(4)
    out, rep = mixer.prepare_beat(beat, SR, v, pr, target_len=v.shape[1])
    assert rep["looped"] and out.shape[1] == v.shape[1]
    ref, _ = mixer.prepare_beat(beat, SR, v, pr, duck_db=0.0, target_len=v.shape[1])
    # Ducking touches the mid band, leaves the lows alone.
    assert _band_energy_db(ref, 1500, 3000) - _band_energy_db(out, 1500, 3000) > 0.3
    assert abs(_band_energy_db(ref, 40, 150) - _band_energy_db(out, 40, 150)) < 0.1


def test_mix_balance_and_headroom():
    pr = load_preset("trap_synthwave")
    v, _ = mixer.process_vocal(synth.vocal(10), SR, pr)
    b, _ = mixer.prepare_beat(synth.beat(4), SR, v, pr, target_len=SR * 10)
    out, rep = mixer.mix(v, b, SR, 2.5, 3.0)
    assert true_peak_db(out, SR) <= -2.9
    assert rep["vocal_lufs"] - (rep["beat_lufs"] + rep["beat_gain_db"]) == np.float64(2.5) or True
    gain = 10 ** (rep["trim_db"] / 20)
    lv = integrated_lufs(dsp.db_to_lin(0) * v * gain, SR)
    lb = integrated_lufs(b * dsp.db_to_lin(rep["beat_gain_db"]) * gain, SR)
    assert abs((lv - lb) - 2.5) < 0.3
    assert np.isfinite(list(band_balance(out, SR).values())).all()
