"""Chat mixing session: keeps decoded tracks, the current settings, every rendered version and an
undo history, so each request in the chat re-renders only the stages it touched."""

from __future__ import annotations

import copy
import time
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from . import assistant, mastering, pipeline
from .audio_io import load_audio, save_wav


@dataclass
class Version:
    n: int
    result: pipeline.Result
    request: str
    lines: list
    seconds: float
    ab_prev: str | None = None  # previous version, loudness-matched to this one
    ab_this: str | None = None


@dataclass
class MixSession:
    inputs: pipeline.MixInputs
    state: dict  # full preset + state["params"] = {"bpm", "offset_ms"}
    out_dir: Path
    export16: bool = False
    export_mp3: bool = False
    cache: pipeline.StageCache = field(default_factory=pipeline.StageCache)
    versions: list = field(default_factory=list)
    undo_stack: list = field(default_factory=list)
    history: list = field(default_factory=list)  # chat turns for the LLM brain

    @classmethod
    def start(cls, vocal_path, beat_path, reference_path, preset: dict, p: pipeline.Params,
              out_root: Path | None = None) -> "MixSession":
        inp = pipeline.load_mix_inputs(vocal_path, beat_path, reference_path, p.backing)
        state = pipeline.apply_params(preset, p)
        state["params"] = {"bpm": p.bpm or None, "offset_ms": float(p.offset_ms or 0.0)}
        out = pipeline._out_dir(inp.stem + "_chat", out_root)
        return cls(inp, state, out, p.export16, p.export_mp3)

    # ------------------------------------------------------------------ rendering
    def params(self) -> pipeline.Params:
        pp = self.state.get("params", {})
        return pipeline.Params(bpm=pp.get("bpm"), offset_ms=float(pp.get("offset_ms") or 0.0),
                               export16=self.export16, export_mp3=self.export_mp3)

    def render(self, request: str = "", lines: list | None = None, progress=pipeline._noop) -> Version:
        t0 = time.time()
        n = len(self.versions) + 1
        preset = {k: v for k, v in self.state.items() if k != "params"}
        res = pipeline.render_mix(self.inputs, preset, self.params(), self.out_dir / f"v{n:02d}", self.cache, progress)
        ver = Version(n, res, request, lines or [], time.time() - t0)
        if self.versions:
            prev, _ = load_audio(self.versions[-1].result.files["master24"])
            cur, _ = load_audio(res.files["master24"])
            a, b, _ = mastering.ab_match(prev, cur, 44100)
            ver.ab_prev = str(save_wav(res.out_dir / "ab_prev_version.wav", a, 44100, 16))
            ver.ab_this = str(save_wav(res.out_dir / "ab_this_version.wav", b, 44100, 16))
        self.versions.append(ver)
        return ver

    @property
    def current(self) -> Version | None:
        return self.versions[-1] if self.versions else None

    def context(self) -> dict:
        """Measurements of the current version for the assistant (and the LLM prompt)."""
        ctx = {"history": self.history}
        cur = self.current
        if cur is None:
            return ctx
        m = cur.result.measurements
        master, ref, mix = m.get("Мастер"), m.get("Референс"), m.get("Сведение")
        feats = {}
        if master:
            ctx["master_lufs"] = round(master["lufs"], 1)
            feats["мастер LUFS"] = round(master["lufs"], 1)
            feats["мастер true peak dBTP"] = round(master["true_peak_db"], 1)
            feats["мастер LRA"] = round(master["lra"], 1)
            if ref:
                feats["референс LUFS"] = round(ref["lufs"], 1)
                for b in ("sub", "bass", "lowmid", "mid", "presence", "high", "air"):
                    feats[f"полоса {b}: мастер минус референс, дБ"] = round(master["bands"][b] - ref["bands"][b], 1)
        if mix:
            feats["сведение LUFS"] = round(mix["lufs"], 1)
        voc = cur.result.report.get("vocal", {})
        if voc:
            feats["де-эссер работает, % времени"] = round(voc.get("deesser_active_pct", 0.0), 1)
        tun = cur.result.report.get("tuning")
        if tun:
            feats["тюн: отклонение после, центов"] = round(tun.get("dev_after_cents", 0.0), 1)
            feats["тональность"] = tun.get("key")
        ctx["features"] = feats
        return ctx

    # ------------------------------------------------------------------ chat
    def ask(self, text: str, llm: assistant.OllamaBrain | None = None) -> tuple[assistant.Plan, list[str]]:
        """Plan and apply a request. Returns (plan, lines describing what changed). No render."""
        plan = assistant.make_plan(text, self.state, self.context(), llm)
        if plan.undo:
            ok = self.undo()
            return plan, (["• Вернул настройки предыдущей версии."] if ok else ["• Отменять нечего."])
        if not plan.changes:
            return plan, []
        self.undo_stack.append(copy.deepcopy(self.state))
        lines = assistant.apply_changes(self.state, plan.changes, self.context())
        if not any("→" in ln for ln in lines):  # nothing actually changed
            self.undo_stack.pop()
        self.history += [{"role": "user", "content": text},
                         {"role": "assistant", "content": plan.reply or "; ".join(lines)}]
        return plan, lines

    def undo(self) -> bool:
        if not self.undo_stack:
            return False
        self.state = self.undo_stack.pop()
        return True

    def settings_view(self) -> dict:
        """Current values of every assistant control (for the UI)."""
        ctx = self.context()
        return {c.label: assistant.fmt(assistant.current_value(self.state, c.name, ctx), c)
                for c in assistant.CONTROLS.values()}

    def master_audio(self) -> np.ndarray | None:
        cur = self.current
        return load_audio(cur.result.files["master24"])[0] if cur else None
