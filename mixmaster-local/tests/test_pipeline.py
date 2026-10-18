import json

import numpy as np
import soundfile as sf

import synth
from core import pipeline
from core.analysis import integrated_lufs, true_peak_db
from core.audio_io import load_audio, save_wav
from core.presets import list_presets, load_preset, save_preset

SR = 44100


def _files(tmp_path):
    save_wav(tmp_path / "vocal.wav", synth.vocal(20), SR, 24)
    save_wav(tmp_path / "beat.wav", synth.beat(8, 120), SR, 24)
    save_wav(tmp_path / "ref.wav", synth.reference(40), SR, 24)
    return tmp_path / "vocal.wav", tmp_path / "beat.wav", tmp_path / "ref.wav"


def test_full_mode1(tmp_path):
    v, b, r = _files(tmp_path)
    p = pipeline.Params(bpm=120, export16=True, export_mp3=True)
    res = pipeline.run_mix_and_master(v, b, r, load_preset("trap_synthwave"), p, out_root=tmp_path / "out")
    assert sf.info(res.files["master24"]).subtype == "PCM_24"
    assert sf.info(res.files["master16"]).subtype == "PCM_16"
    for k in ("mp3", "ab_before", "ab_after", "premaster"):
        assert (tmp_path / "out").exists() and res.files[k]
    master, _ = load_audio(res.files["master24"])
    ref, _ = load_audio(r)
    assert abs(integrated_lufs(master, SR) - integrated_lufs(ref, SR)) < 1.5
    assert true_peak_db(master, SR) <= -0.9
    a, _ = load_audio(res.files["ab_before"])
    bb, _ = load_audio(res.files["ab_after"])
    assert abs(integrated_lufs(a, SR) - integrated_lufs(bb, SR)) < 0.3
    assert {"Вокал", "Бит", "Сведение", "Мастер", "Референс"} <= set(res.measurements)
    assert "Мастер" in res.summary
    json.loads((res.out_dir / "report.json").read_text(encoding="utf-8"))
    # Inputs are never overwritten.
    assert v.exists() and b.exists()


def test_mode2_and_mode3(tmp_path):
    _, _, r = _files(tmp_path)
    save_wav(tmp_path / "track.wav", synth.reference(25) * 0.3, SR, 24)
    p = pipeline.Params(loudness="target", target_lufs=-12.0)
    res = pipeline.run_master_reference(tmp_path / "track.wav", r, load_preset("rock"), p, out_root=tmp_path)
    m, _ = load_audio(res.files["master24"])
    assert abs(integrated_lufs(m, SR) + 12.0) < 0.5
    res3 = pipeline.run_master_no_reference(tmp_path / "track.wav", load_preset("clean_streaming"),
                                            pipeline.Params(target_lufs=-14.0), out_root=tmp_path)
    m3, _ = load_audio(res3.files["master24"])
    assert abs(integrated_lufs(m3, SR) + 14.0) < 0.5 and true_peak_db(m3, SR) <= -0.95


def test_long_file_memory_path(tmp_path):
    """A 6-minute file goes through mode 3 (chunked processing) without trouble."""
    long = np.tile(synth.beat(10, 120), (1, 36)) * 0.5
    save_wav(tmp_path / "long.wav", long, SR, 24)
    res = pipeline.run_master_no_reference(tmp_path / "long.wav", load_preset("clean_streaming"),
                                           pipeline.Params(target_lufs=-14.0), out_root=tmp_path)
    assert res.measurements["Мастер"]["duration_s"] > 359


def test_presets_roundtrip(tmp_path):
    import shutil
    from core import presets as P
    for pid in list_presets():
        pr = load_preset(pid)
        assert {"vocal", "beat", "balance", "master"} <= set(pr)
    d = tmp_path / "presets"
    shutil.copytree(P.PRESET_DIR, d)
    pr = load_preset("rap_vocal", d)
    pr["vocal"]["reverb"]["mix"] = 0.2
    pid = save_preset("Мой трэп", pr, d)
    assert pid.startswith("user_") and load_preset(pid, d)["vocal"]["reverb"]["mix"] == 0.2
    assert list_presets(d)[pid] == "Мой трэп"


def test_params_override():
    pr = pipeline.apply_params(load_preset("rock"), pipeline.Params(deesser=0.1, reverb=0.0, vocal_over_beat_lu=4))
    assert pr["vocal"]["deesser"]["amount"] == 0.1 and pr["balance"]["vocal_over_beat_lu"] == 4
