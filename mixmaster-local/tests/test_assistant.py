import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import numpy as np
import pytest

import synth
from core import assistant, mastering, mixer, pipeline
from core.audio_io import save_wav
from core.presets import load_preset
from core.session import MixSession

SR = 44100


def _state():
    st = load_preset("trap_synthwave")
    st["params"] = {"bpm": None, "offset_ms": 0.0}
    return st


def _plan(text):
    return {(c.control, c.op): c.value for c in assistant.RuleBrain().plan(text, _state(), {}).changes}


@pytest.mark.parametrize("text, control, sign", [
    ("вокал чуть громче", "vocal_level", 1), ("сделай голос тише", "vocal_level", -1),
    ("меньше реверба", "reverb", -1), ("добавь реверба", "reverb", 1),
    ("вокал шипит", "deesser", 1), ("вокал резкий", "vocal_presence", -1),
    ("голос бубнит", "vocal_mud", -1), ("бэки тише", "backing_level", -1),
    ("больше баса", "master_bass", 1), ("больше баса в бите", "beat_bass", 1),
    ("трек ярче", "master_air", 1), ("сделай шире", "master_width", 1),
    ("бит мешает вокалу", "beat_carve", -1), ("vocal louder", "vocal_level", 1),
    ("less reverb", "reverb", -1), ("вокал плотнее", "density", 1),
])
def test_rule_brain_directions(text, control, sign):
    plan = _plan(text)
    assert (control, "add") in plan, plan
    assert np.sign(plan[(control, "add")]) == sign


def test_rule_brain_numbers_keys_and_modes():
    assert _plan("мастер -9 LUFS")[("master_lufs", "set")] == -9
    assert _plan("bpm 140")[("bpm", "set")] == 140
    assert _plan("реверб 15%")[("reverb", "set")] == pytest.approx(0.15)
    assert _plan("вокал громче на 2 дб")[("vocal_level", "add")] == 2
    assert _plan("бит громче на 2 дб")[("vocal_level", "add")] == -2
    p = _plan("тюн в ля миноре")
    assert p[("tune_key", "set")] == "A" and p[("tune_scale", "set")] == "minor"
    assert _plan("жёстче автотюн как у Kai Angel")[("tune_speed", "set")] <= 10
    assert _plan("убери тюн")[("tune_enabled", "set")] is False
    assert _plan("дилей только в концах фраз")[("delay_mode", "set")] == "throws"
    assert _plan("сдвинь вокал на 20 мс раньше")[("offset", "add")] == -20
    assert _plan("чуть громче вокал")[("vocal_level", "add")] < _plan("намного громче вокал")[("vocal_level", "add")]
    both = _plan("больше баса и чуть ярче")
    assert both[("master_bass", "add")] == 1.0 and both[("master_air", "add")] == 0.5
    assert assistant.RuleBrain().plan("отмени", _state()).undo
    assert assistant.RuleBrain().plan("фывапролд", _state()).changes == []


def test_apply_changes_clamps_and_side_effects():
    st = _state()
    lines = assistant.apply_changes(st, [assistant.Change("vocal_level", "add", 100)], {})
    assert st["balance"]["vocal_over_beat_lu"] == assistant.CONTROLS["vocal_level"].hi and "→" in lines[0]
    assistant.apply_changes(st, [assistant.Change("master_lufs", "add", 2)], {"master_lufs": -13.0})
    assert st["master"]["loudness"] == "target" and st["master"]["target_lufs"] == -11.0
    assistant.apply_changes(st, [assistant.Change("tune_speed", "set", 5)], {})
    assert st["tuning"]["enabled"] is True
    assistant.apply_changes(st, [assistant.Change("delay_mode", "set", "nonsense")], {})
    assert st["vocal"]["delay"]["mode"] in ("always", "throws")


class _FakeOllama(BaseHTTPRequestHandler):
    reply = {"reply": "Сделаю вокал громче.", "changes": [
        {"control": "vocal_level", "op": "add", "value": 1.0},
        {"control": "not_a_control", "op": "add", "value": 5}]}
    seen = []

    def log_message(self, *a):
        pass

    def _send(self, obj):
        body = json.dumps(obj).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        self._send({"models": [{"name": "qwen2.5:7b"}]})

    def do_POST(self):
        payload = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        _FakeOllama.seen.append(payload)
        self._send({"message": {"role": "assistant", "content": json.dumps(self.reply, ensure_ascii=False)}})


@pytest.fixture()
def fake_ollama():
    srv = HTTPServer(("127.0.0.1", 0), _FakeOllama)
    th = threading.Thread(target=srv.serve_forever, daemon=True)
    th.start()
    yield f"http://127.0.0.1:{srv.server_address[1]}"
    srv.shutdown()


def test_ollama_brain_json_plan(fake_ollama):
    brain = assistant.OllamaBrain("qwen2.5:7b", fake_ollama)
    assert brain.status()[0]
    assert not assistant.OllamaBrain("llama3:70b", fake_ollama).status()[0]
    plan = assistant.make_plan("сделай что-нибудь с вокалом", _state(), {"features": {"мастер LUFS": -13}}, brain)
    assert plan.brain == "llm" and [c.control for c in plan.changes] == ["vocal_level"]
    sent = _FakeOllama.seen[-1]
    assert sent["format"]["required"] == ["reply", "changes"] and sent["stream"] is False
    assert "vocal_level" in sent["messages"][0]["content"] and "мастер LUFS" in sent["messages"][0]["content"]


def test_llm_unreachable_falls_back_to_rules():
    brain = assistant.OllamaBrain("qwen2.5:7b", "http://127.0.0.1:9", timeout=1)
    plan = assistant.make_plan("меньше реверба", _state(), {}, brain)
    assert plan.brain == "rules" and plan.changes[0].control == "reverb" and "недоступна" in plan.reply


def test_chat_session_reuses_stages_and_undoes(tmp_path):
    save_wav(tmp_path / "v.wav", synth.vocal(12), SR, 24)
    save_wav(tmp_path / "b.wav", synth.beat(8, 120), SR, 24)
    save_wav(tmp_path / "r.wav", synth.reference(30), SR, 24)
    sess = MixSession.start(tmp_path / "v.wav", tmp_path / "b.wav", tmp_path / "r.wav", load_preset("rap_vocal"),
                            pipeline.Params(bpm=120), out_root=tmp_path)
    v1 = sess.render("старт")
    _, lines = sess.ask("мастер -10 LUFS")
    assert any("→" in ln for ln in lines)
    v2 = sess.render("мастер")
    assert {"vocal", "beat", "mix"} <= set(v2.result.report["stages_reused"])
    assert abs(v2.result.measurements["Мастер"]["lufs"] + 10) < 0.6
    assert v2.ab_prev and v2.ab_this
    sess.ask("отмени")
    v3 = sess.render("отмена")
    assert "master" in v3.result.report["stages_reused"]
    assert abs(v3.result.measurements["Мастер"]["lufs"] - v1.result.measurements["Мастер"]["lufs"]) < 0.05
    assert "Вокал над битом" in sess.settings_view()


def test_new_dsp_stages():
    v = synth.vocal(12, seed=3)
    v[:, :SR * 6] *= 0.3
    rms = lambda x, a, b: 20 * np.log10(np.sqrt(np.mean(x[:, a * SR:b * SR] ** 2)))  # noqa: E731
    y, _ = mixer.vocal_rider(v, SR, {"enabled": True, "range_db": 6})
    assert abs(rms(y, 6, 12) - rms(y, 0, 6)) < abs(rms(v, 6, 12) - rms(v, 0, 6)) - 5
    mask = mixer.phrase_end_mask(synth.vocal(10), SR)
    assert 0.01 < mask.mean() < 0.3
    tone = synth.sine(220, 2, -6)
    sat = mixer.saturate(tone, SR, {"drive_db": 12, "mix": 1.0})
    spec = np.abs(np.fft.rfft(sat[0]))
    assert spec[int(660 * 2)] > 10 * np.abs(np.fft.rfft(tone[0]))[int(660 * 2)]  # 3rd harmonic appears
    dens = mixer.parallel_compression(v, SR, {"mix": 0.3})
    assert np.all(np.isfinite(dens)) and dens.shape == v.shape


def test_post_tone_mono_bass_and_width():
    t = np.arange(SR * 2) / SR
    low = 0.3 * np.sin(2 * np.pi * 50 * t)
    high = 0.3 * np.sin(2 * np.pi * 2000 * t)
    x = np.stack([low + high, -low + high]).astype(np.float32)  # low end fully out of phase
    y, _ = mastering.post_tone(x, SR, {"mono_bass_hz": 120, "width_db": 0})
    side = (y[0] - y[1]) / 2
    assert np.sqrt(np.mean(side[SR // 2:] ** 2)) < 0.05
    w, _ = mastering.post_tone(np.stack([high, high * 0.5]).astype(np.float32), SR, {"width_db": 6})
    assert np.std(w[0] - w[1]) > np.std(high - high * 0.5) * 1.8
