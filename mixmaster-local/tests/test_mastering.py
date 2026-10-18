import numpy as np
import pytest

import synth
from core import mastering
from core.analysis import band_balance, band_distance, integrated_lufs, true_peak_db
from core.audio_io import AudioError
from core.presets import load_preset

SR = 44100


@pytest.fixture(scope="module")
def track():
    v = np.repeat(synth.vocal(30, seed=3), 2, axis=0)
    return (synth.beat(30, 120) * 0.5 + v * 0.4) * 0.5


@pytest.fixture(scope="module")
def ref():
    return synth.reference(40)


@pytest.mark.parametrize("target", [-14.0, -9.0])
def test_master_without_reference_hits_target(track, target):
    out, info = mastering.master_without_reference(track, SR, load_preset("clean_streaming"), target)
    assert integrated_lufs(out, SR) == pytest.approx(target, abs=0.5)
    assert true_peak_db(out, SR) <= -1.0 + 0.05
    assert np.all(np.isfinite(out))


def test_master_with_reference_gets_closer(track, ref):
    out, info = mastering.master_with_reference(track, ref, SR, load_preset("trap_synthwave"))
    l_ref = integrated_lufs(ref, SR)
    assert abs(integrated_lufs(out, SR) - l_ref) < abs(integrated_lufs(track, SR) - l_ref)
    assert abs(integrated_lufs(out, SR) - l_ref) < 1.5
    rb = band_balance(ref, SR)
    assert band_distance(band_balance(out, SR), rb) < band_distance(band_balance(track, SR), rb)
    assert true_peak_db(out, SR) <= -0.95


def test_master_with_reference_target_lufs(track, ref):
    out, _ = mastering.master_with_reference(track, ref, SR, load_preset("trap_synthwave"), target_lufs=-14.0)
    assert integrated_lufs(out, SR) == pytest.approx(-14.0, abs=0.5)
    assert true_peak_db(out, SR) <= -0.95


def test_reference_validation():
    with pytest.raises(AudioError):
        mastering.validate_reference(synth.reference(5), SR)
    mono = np.repeat(synth.vocal(35), 2, axis=0)
    assert any("моно" in w for w in mastering.validate_reference(mono, SR))
    half = synth.reference(20)
    half[1] = 0
    with pytest.raises(AudioError):
        mastering.validate_reference(half, SR)


def test_ab_match_equal_loudness(track, ref):
    a, b, common = mastering.ab_match(track, ref, SR)
    assert integrated_lufs(a, SR) == pytest.approx(integrated_lufs(b, SR), abs=0.2)
    assert max(np.max(np.abs(a)), np.max(np.abs(b))) <= 0.991
