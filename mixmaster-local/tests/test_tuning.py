import numpy as np
import pytest

import synth
from core import tuning

SR = 44100
NOTES = [57, 60, 64, 62]  # A3 C4 E4 D4, all in A minor


def _note_medians(audio):
    midi, _, hop = tuning.detect_pitch(audio, SR)
    out = []
    for k, note in enumerate(NOTES):
        seg = midi[int((k * 2 + 0.3) / hop):int((k * 2 + 1.7) / hop)]
        d = (seg - note) * 100
        out.append(float(np.median(d[np.isfinite(d)])))
    return out


def test_nearest_note_and_scale():
    pcs = tuning.allowed_pitch_classes(9, "minor")  # A minor = C major notes
    assert sorted(pcs.tolist()) == [0, 2, 4, 5, 7, 9, 11]
    np.testing.assert_allclose(tuning.nearest_note(np.array([60.4, 61.2, 70.6]), pcs), [60, 62, 71])


def test_curve_respects_tolerance_and_unvoiced():
    pcs = tuning.allowed_pitch_classes(0, "chromatic")
    midi = np.concatenate([np.full(50, 60.1), np.full(10, np.nan), np.full(50, 62.4)])
    c = tuning.correction_curve(midi, pcs, 0.01, strength=1.0, retune_ms=100, tolerance_cents=20)
    assert abs(c[20]) < 0.01           # 10 cents off: inside tolerance, untouched
    assert c[90] == pytest.approx(-0.4, abs=0.05)  # 40 cents off: fully corrected
    assert np.all(np.abs(c) <= 1.0)


def test_natural_tuning_fixes_off_notes():
    x = synth.sung(NOTES, [-40, 10, 45, -30])
    cfg = dict(strength=1.0, retune_ms=120, tolerance_cents=20, key="A", scale="minor")
    y, rep = tuning.tune_vocal(x, SR, cfg)
    after = _note_medians(y)
    assert abs(after[0]) < 10 and abs(after[2]) < 10 and abs(after[3]) < 15
    assert abs(after[1] - 10) < 6       # in-tune-enough note kept as sung
    assert rep["dev_after_cents"] < rep["dev_before_cents"] / 2
    assert y.shape == x.shape and np.all(np.isfinite(y))


def test_hard_tune_snaps_everything():
    x = synth.sung(NOTES, [-40, 12, 30, -30])
    y, rep = tuning.tune_vocal(x, SR, dict(strength=1.0, retune_ms=0, tolerance_cents=0, key="A", scale="minor"))
    assert all(abs(d) < 12 for d in _note_medians(y))
    assert rep["corrected_pct"] > 80


def test_key_detection_from_beat_and_vocal():
    tonic, scale, _ = tuning.detect_key(synth.chord_beat(57, minor=True), SR)
    assert (tonic, scale) == (9, "minor")
    tonic, scale, _ = tuning.detect_key(synth.chord_beat(62, minor=False), SR)
    assert (tonic, scale) == (2, "major")


def test_silent_vocal_raises():
    from core.audio_io import AudioError
    with pytest.raises(AudioError):
        tuning.detect_pitch(np.zeros((1, SR * 2), np.float32), SR)
