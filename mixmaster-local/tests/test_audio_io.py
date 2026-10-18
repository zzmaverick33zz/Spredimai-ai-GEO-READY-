import numpy as np
import pytest
import soundfile as sf

import synth
from core import audio_io as io

SR = 44100


def test_loop_to_length():
    beat = synth.beat(2)
    out = io.loop_to_length(beat, SR * 5)
    assert out.shape == (2, SR * 5)
    np.testing.assert_array_equal(out[:, SR * 2:SR * 3], beat[:, :SR])
    # Longer beats are not cut.
    assert io.loop_to_length(beat, SR).shape[1] == beat.shape[1]


def test_to_stereo_and_shift():
    mono = synth.sine(440, 1)
    st = io.to_stereo(mono)
    assert st.shape[0] == 2 and np.array_equal(st[0], st[1])
    assert io.shift(st, 10).shape[1] == st.shape[1] + 441
    assert io.shift(st, -10).shape[1] == st.shape[1] - 441


def test_save_load_roundtrip_24bit(tmp_path):
    x = synth.beat(2)
    p = io.save_wav(tmp_path / "a.wav", x, SR, 24)
    assert sf.info(str(p)).subtype == "PCM_24"
    y, sr = io.load_audio(p)
    assert sr == SR and y.shape == x.shape
    assert np.max(np.abs(x - y)) < 1e-5


def test_resample_on_load(tmp_path):
    x = synth.sine(1000, 2, -6, sr=48000)
    sf.write(str(tmp_path / "48k.wav"), x.T, 48000, subtype="PCM_24")
    y, sr = io.load_audio(tmp_path / "48k.wav")
    assert sr == 44100 and abs(y.shape[1] - 2 * 44100) < 50


def test_mp3_export(tmp_path):
    p = io.save_mp3(tmp_path / "a.mp3", synth.beat(2), SR)
    assert p.stat().st_size > 1000


def test_validation():
    with pytest.raises(io.AudioError):
        io.validate_audio(np.zeros((2, SR * 3), np.float32), SR, "Вокал")
    with pytest.raises(io.AudioError):
        io.validate_audio(synth.sine(440, 0.2), SR, "Вокал")
    clipped = np.clip(synth.sine(440, 3, 6), -1, 1)
    assert any("клиппинг" in w for w in io.validate_audio(clipped, SR, "Бит"))
    assert io.validate_audio(synth.beat(3), SR, "Бит") == []
    with pytest.raises(io.AudioError):
        io.load_audio("nope.wav")
