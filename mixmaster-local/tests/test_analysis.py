import numpy as np
import pytest

import synth
from core import analysis

SR = 44100


def test_lufs_of_known_sine():
    # BS.1770: 997 Hz sine at 0 dBFS in one channel reads -3.01 LUFS.
    assert analysis.integrated_lufs(synth.sine(997, 5, -20), SR) == pytest.approx(-23.01, abs=0.15)


def test_lufs_stereo_sine():
    x = np.repeat(synth.sine(997, 5, -20), 2, axis=0)
    assert analysis.integrated_lufs(x, SR) == pytest.approx(-20.0, abs=0.15)


def test_silence_lufs_is_floor():
    assert analysis.integrated_lufs(np.zeros((2, SR * 2), np.float32), SR) == analysis.SILENCE_LUFS


def test_true_peak_and_lra():
    x = synth.sine(1000, 5, -6)
    assert analysis.true_peak_db(x, SR) == pytest.approx(-6.0, abs=0.1)
    assert analysis.loudness_range(x, SR) < 0.5
    # Two loudness levels 12 dB apart -> LRA close to 12 LU.
    y = np.concatenate([synth.sine(1000, 10, -6), synth.sine(1000, 10, -18)], axis=1)
    assert analysis.loudness_range(y, SR) == pytest.approx(12.0, abs=1.5)


def test_band_balance_finds_tone_band():
    bands = analysis.band_balance(synth.sine(100, 5, -10), SR)
    assert max(bands, key=bands.get) == "bass"
    assert bands["bass"] > -0.5


def test_measure_and_table():
    m = analysis.measure(synth.beat(4), SR)
    headers, rows = analysis.comparison_rows({"A": m, "B": m})
    assert headers == ["Параметр", "A", "B"]
    assert len(rows) == 4 + len(analysis.BANDS_HZ)
    f, db = analysis.spectrum_curve(synth.beat(4), SR)
    assert len(f) == len(db) and np.all(np.isfinite(db))
