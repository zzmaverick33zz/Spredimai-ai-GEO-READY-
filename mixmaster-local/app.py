"""Gradio UI: vocal+beat+reference, finished track+reference, master without reference, vocal tuning.

Run: python app.py  (or the run.* scripts). Everything stays on this machine.
"""

from __future__ import annotations

import os

os.environ.setdefault("GRADIO_ANALYTICS_ENABLED", "False")
os.environ.setdefault("HF_HUB_OFFLINE", "1")

import inspect  # noqa: E402
import json  # noqa: E402
import traceback  # noqa: E402
from pathlib import Path  # noqa: E402

import gradio as gr  # noqa: E402
import pandas as pd  # noqa: E402

from core import analysis, assistant, pipeline  # noqa: E402
from core.session import MixSession  # noqa: E402
from core.audio_io import SUPPORTED_EXT, AudioError  # noqa: E402
from core.plots import pitch_figure, spectrum_figure  # noqa: E402
from core.tuning import NOTE_NAMES  # noqa: E402
from core.presets import PRESET_DIR, list_presets, load_preset, save_preset  # noqa: E402

ROOT = Path(__file__).resolve().parent
REF_DIR = ROOT / "references"
INPUT_DIR = ROOT / "inputs"
DEFAULT_PRESET = "trap_synthwave"

LOUD_REF = "Как у референса"
LOUD_TARGET = "Целевой LUFS"
TARGET_PRESET = "По пресету"
TARGET_REF = "По референсу (приблизительно)"
KEY_AUTO = "Авто"
SCALE_CHOICES = [("Авто (по биту/вокалу)", "auto"), ("Минор", "minor"), ("Мажор", "major"),
                 ("Хроматика (любые ноты)", "chromatic")]
ROLE_CHOICES = [("Дабл (те же слова и ноты)", "double"), ("Гармония / второй голос", "harmony"),
                ("Адлибы", "adlib")]
N_BACKING = 3
BRAIN_RULES = "Правила: мгновенно, без модели"
BRAIN_LLM = "Локальная LLM (Ollama)"
QUICK_PROMPTS = ["вокал чуть громче", "меньше реверба", "вокал резкий", "бас мутный", "жёстче автотюн",
                 "дилей в концах фраз", "трек ярче", "мастер -9 LUFS"]

CSS_PATH = ROOT / "assets" / "brutal.css"
FORCE_DARK = "() => { document.body.classList.add('dark'); }"
HEADER = """
<div id="mm-header">
  <div class="mm-top">
    <div class="mm-logo"><div><span class="mm-word">Mixmaster</span><span class="mm-word mm-out">/local</span></div>
      <small>сведение · тюн · мастер по референсу</small>
      <div class="mm-meter" aria-hidden="true"><i class="hot" style="height:83%"></i><i style="height:76%"></i><i class="hot" style="height:89%"></i><i style="height:72%"></i><i class="hot" style="height:83%"></i><i style="height:77%"></i><i style="height:67%"></i><i class="hot" style="height:79%"></i><i style="height:64%"></i><i class="clip" style="height:74%"></i><i style="height:62%"></i><i style="height:62%"></i><i style="height:70%"></i><i class="hot" style="height:80%"></i><i style="height:59%"></i><i style="height:60%"></i><i style="height:70%"></i><i style="height:78%"></i><i style="height:66%"></i><i style="height:60%"></i><i style="height:75%"></i><i style="height:48%"></i><i style="height:69%"></i><i style="height:52%"></i><i style="height:46%"></i><i style="height:44%"></i><i style="height:48%"></i><i style="height:61%"></i><i style="height:42%"></i><i style="height:52%"></i><i style="height:52%"></i><i style="height:44%"></i><i style="height:47%"></i><i style="height:32%"></i><i style="height:31%"></i><i style="height:34%"></i><i style="height:46%"></i><i style="height:37%"></i><i style="height:33%"></i><i style="height:39%"></i><i style="height:34%"></i><i style="height:29%"></i><i style="height:41%"></i><i style="height:37%"></i><i style="height:23%"></i><i style="height:31%"></i><i style="height:28%"></i><i style="height:37%"></i></div></div>
    <div class="mm-specs">
      <div class="mm-live">система<b>офлайн</b></div>
      <div>формат<b>44.1 кГц / 24 бит</b></div>
      <div>движок<b>Matchering</b></div>
      <div>dsp<b>Pedalboard</b></div>
      <div>громкость<b>BS.1770</b></div>
      <div>лицензия<b>GPLv3</b></div>
    </div>
  </div>
  <div class="mm-ticker"><span>без облака ▪ без api-ключей ▪ без подписок ▪ всё на твоём диске ▪
    вокал + бит + референс → мастер wav 24 бит ▪ a/b с выровненной громкостью: громче ≠ лучше ▪</span></div>
</div>
"""
FOOTER = """<div id="mm-footer"><span><b>■</b> mixmaster/local</span><span>исходники не перезаписываются:
результаты в outputs/</span><span>gplv3 · open source</span></div>"""


def section(title: str):
    """Small uppercase section divider."""
    return gr.Markdown(f"▍{title}", elem_classes="mm-section")


# ----------------------------------------------------------------- helpers

def audio_files(folder: Path) -> list[str]:
    """Audio file names available in a folder."""
    if not folder.exists():
        return []
    return sorted(p.name for p in folder.iterdir() if p.suffix.lower() in SUPPORTED_EXT)


def reference_choices() -> list[str]:
    return audio_files(REF_DIR)


def pick_input(upload: str | None, choice: str | None) -> str | None:
    """Uploaded file wins over a file picked from inputs/."""
    if upload:
        return upload
    if choice and (INPUT_DIR / choice).exists():
        return str(INPUT_DIR / choice)
    return None


def preset_choices() -> list[tuple[str, str]]:
    return [(name, pid) for pid, name in list_presets().items()]


def pick_reference(choice: str | None, upload: str | None) -> str:
    """Uploaded file wins over the folder selection."""
    if upload:
        return upload
    if choice:
        path = REF_DIR / choice
        if path.exists():
            return str(path)
    raise AudioError("Выбери референс из папки references/ или загрузи файл.")


def parse_preset(text: str) -> dict:
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise AudioError(f"В редакторе пресета ошибка JSON (строка {exc.lineno}): {exc.msg}") from exc


def slider_values(preset: dict) -> list:
    """Values for the mode-1 sliders taken from a preset."""
    v, m = preset["vocal"], preset["master"]
    target = m["target_lufs"] if m["target_lufs"] is not None else m["default_target_lufs"]
    return [
        preset["balance"]["vocal_over_beat_lu"],
        v["deesser"]["amount"],
        v["reverb"]["mix"],
        v["delay"]["mix"],
        v.get("brightness_db", 0.0),
        preset["beat"]["duck_db"],
        LOUD_TARGET if m.get("loudness") == "target" else LOUD_REF,
        target,
    ]


def tuning_values(preset: dict) -> list:
    """Values for the tuning widgets taken from a preset."""
    t = preset["tuning"]
    return [bool(t["enabled"]), KEY_AUTO if t["key"] == "auto" else t["key"],
            "auto" if t.get("scale_auto", True) else t["scale"], t["strength"], t["retune_ms"],
            t["tolerance_cents"], bool(t["apply_to_backing"])]


def results_to_ui(res: pipeline.Result):
    """Convert a pipeline Result into the values of the shared output components."""
    headers, rows = analysis.comparison_rows(res.measurements)
    table = pd.DataFrame(rows, columns=headers)
    msg = res.summary
    if res.warnings:
        msg += "\n\n**Предупреждения:**\n" + "\n".join(f"- {w}" for w in res.warnings)
    msg += f"\n\nПапка с результатом: `{res.out_dir}`"
    files = [res.files[k] for k in ("master24", "master16", "mp3", "premaster", "vocals", "tuned") if k in res.files]
    return (msg, res.files["master24"], files, res.files["ab_before"], res.files["ab_after"],
            table, spectrum_figure(res.spectra))


def tune_kwargs(enabled, key, scale, strength, retune, tolerance, backs=None) -> dict:
    """Params fields for pitch correction from the UI controls."""
    out = dict(tune=bool(enabled), tune_key="auto" if key in (None, KEY_AUTO) else key, tune_scale=scale or "auto",
               tune_strength=strength, tune_retune_ms=retune, tune_tolerance=tolerance)
    if backs is not None:
        out["tune_backing"] = bool(backs)
    return out


def guarded(fn):
    """Turn exceptions into readable Russian errors in the UI."""
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except AudioError as exc:
            raise gr.Error(str(exc), duration=None) from exc
        except MemoryError as exc:
            raise gr.Error("Не хватило памяти. Закрой другие программы или возьми файл короче.") from exc
        except Exception as exc:  # unexpected: show short message, full trace in console
            traceback.print_exc()
            raise gr.Error(f"Неожиданная ошибка: {type(exc).__name__}: {exc}", duration=None) from exc
    wrapper.__name__ = fn.__name__
    return wrapper


def _progress(progress):
    return lambda frac, msg: progress(frac, desc=msg)


# ----------------------------------------------------------------- handlers

@guarded
def run_mode1(vocal, vocal_in, beat, beat_in, ref_choice, ref_upload, preset_text, lu, deess, reverb, delay, bright, duck,
              loud_mode, target, bpm, offset, vtarget, exp16, mp3,
              t_on, t_key, t_scale, t_strength, t_retune, t_tol, t_backs, b_level, b_width,
              *backing_slots, progress=gr.Progress()):
    # backing_slots come in triples: (uploaded file, file from inputs/, role)
    backing = [(pick_input(a, i), r) for a, i, r in zip(backing_slots[0::3], backing_slots[1::3], backing_slots[2::3])]
    backing = [(path, r) for path, r in backing if path]
    p = pipeline.Params(
        **tune_kwargs(t_on, t_key, t_scale, t_strength, t_retune, t_tol, t_backs),
        backing=backing, backing_level_lu=b_level, backing_width=b_width,
        vocal_over_beat_lu=lu, deesser=deess, reverb=reverb, delay=delay, brightness_db=bright, duck_db=duck,
        loudness="target" if loud_mode == LOUD_TARGET else "reference", target_lufs=target,
        bpm=float(bpm) if bpm else None, offset_ms=float(offset or 0),
        vocal_target="reference" if vtarget == TARGET_REF else "preset", export16=exp16, export_mp3=mp3,
    )
    res = pipeline.run_mix_and_master(pick_input(vocal, vocal_in), pick_input(beat, beat_in), pick_reference(ref_choice, ref_upload),
                                      parse_preset(preset_text), p, progress=_progress(progress))
    return results_to_ui(res)


@guarded
def run_mode2(track, track_in, ref_choice, ref_upload, preset_text, loud_mode, target, exp16, mp3, progress=gr.Progress()):
    p = pipeline.Params(loudness="target" if loud_mode == LOUD_TARGET else "reference", target_lufs=target,
                        export16=exp16, export_mp3=mp3)
    res = pipeline.run_master_reference(pick_input(track, track_in), pick_reference(ref_choice, ref_upload), parse_preset(preset_text),
                                        p, progress=_progress(progress))
    return results_to_ui(res)


@guarded
def run_mode3(track, track_in, preset_text, target, exp16, mp3, progress=gr.Progress()):
    p = pipeline.Params(target_lufs=target, export16=exp16, export_mp3=mp3)
    res = pipeline.run_master_no_reference(pick_input(track, track_in), parse_preset(preset_text), p, progress=_progress(progress))
    return results_to_ui(res)


@guarded
def run_mode4(vocal, vocal_in, beat, beat_in, preset_text, t_key, t_scale, t_strength, t_retune, t_tol, exp16, mp3,
              progress=gr.Progress()):
    p = pipeline.Params(**tune_kwargs(True, t_key, t_scale, t_strength, t_retune, t_tol), export16=exp16, export_mp3=mp3)
    res = pipeline.run_tune_only(pick_input(vocal, vocal_in), pick_input(beat, beat_in), parse_preset(preset_text), p,
                                 progress=_progress(progress))
    msg = res.summary
    if res.warnings:
        msg += "\n\n**Предупреждения:**\n" + "\n".join(f"- {w}" for w in res.warnings)
    msg += f"\n\nПапка с результатом: `{res.out_dir}`"
    files = [res.files[k] for k in ("master24", "master16", "mp3") if k in res.files]
    return msg, res.files["master24"], files, res.files["ab_before"], res.files["ab_after"], pitch_figure(res.report["tuning"])


def on_preset(pid):
    preset = load_preset(pid)
    text = json.dumps(preset, ensure_ascii=False, indent=2)
    vals = slider_values(preset)
    tv = tuning_values(preset)
    return [text, *vals, vals[6], vals[7], vals[7], *tv, *tv[1:6]]


@guarded
def on_save_preset(name, text, lu, deess, reverb, delay, bright, duck, t_on, t_key, t_scale, t_strength, t_retune,
                   t_tol, t_backs):
    preset = parse_preset(text)
    preset.setdefault("tuning", {}).update({
        "enabled": bool(t_on), "key": "auto" if t_key == KEY_AUTO else t_key, "scale_auto": t_scale == "auto",
        "strength": t_strength, "retune_ms": t_retune, "tolerance_cents": t_tol, "apply_to_backing": bool(t_backs)})
    if t_scale != "auto":
        preset["tuning"]["scale"] = t_scale
    preset["balance"]["vocal_over_beat_lu"] = lu
    preset["vocal"]["deesser"]["amount"] = deess
    preset["vocal"]["reverb"]["mix"] = reverb
    preset["vocal"]["delay"]["mix"] = delay
    preset["vocal"]["brightness_db"] = bright
    preset["beat"]["duck_db"] = duck
    pid = save_preset(name or "Мой пресет", preset)
    gr.Info(f"Пресет сохранён: presets/{pid}.json")
    return gr.update(choices=preset_choices(), value=pid)


def refresh_refs():
    return gr.update(choices=reference_choices())


def refresh_inputs_for(n: int):
    """Handler that refreshes `n` inputs/ dropdowns at once."""
    return lambda: [gr.update(choices=audio_files(INPUT_DIR))] * n


# ----------------------------------------------------------------- chat mixing

def _brain(mode, model, url):
    if mode != BRAIN_LLM:
        return None
    return assistant.OllamaBrain(model or "qwen2.5:7b", url or "http://127.0.0.1:11434")


def _backing_from_slots(slots) -> list:
    triples = zip(slots[0::3], slots[1::3], slots[2::3])
    return [(path, r) for path, r in ((pick_input(a, i), r) for a, i, r in triples) if path]


def _session_outputs(sess: MixSession):
    """Values for the chat tab's result widgets from the current version."""
    v = sess.current
    res = v.result
    headers, rows = analysis.comparison_rows(res.measurements)
    files = [res.files[k] for k in ("master24", "master16", "mp3", "premaster", "vocals", "tuned") if k in res.files]
    if v.ab_prev:
        a = gr.update(value=v.ab_prev, label=f"A: версия {v.n - 1}")
        b = gr.update(value=v.ab_this, label=f"B: версия {v.n} (громкость выровнена)")
    else:
        a = gr.update(value=res.files["ab_before"], label="A: сырая сумма без обработки")
        b = gr.update(value=res.files["ab_after"], label=f"B: версия {v.n}")
    return (gr.update(value=res.files["master24"], label=f"Мастер · версия {v.n}"), files, a, b,
            pd.DataFrame(rows, columns=headers), spectrum_figure(res.spectra), sess.settings_view())


def _version_message(sess: MixSession, head: str) -> str:
    v = sess.current
    reused = v.result.report.get("stages_reused", [])
    stages = ["tune"] * bool(v.result.report.get("tuning")) + ["vocal"] + ["backing"] * bool(sess.inputs.backs) + \
        ["beat", "mix", "master"]
    redo = [s for s in stages if s not in reused]
    names = {"tune": "тюн", "vocal": "вокал", "backing": "бэки", "beat": "бит", "mix": "сведение", "master": "мастер"}
    msg = f"{head}\n\n**Версия {v.n}** готова за {v.seconds:.0f} с"
    if v.n > 1:
        msg += f" (пересобрано: {', '.join(names[s] for s in redo) or 'ничего'})"
    msg += ".\n" + v.result.summary
    prev = sess.versions[-2].result.warnings if len(sess.versions) > 1 else []
    new_warnings = [w for w in v.result.warnings if w not in prev]
    if new_warnings:
        msg += "\n\n" + "\n".join(f"⚠ {w}" for w in new_warnings[-3:])
    hints = assistant.suggestions(v.result.measurements, v.result.report)
    if hints:
        msg += "\n\n**Подсказки:**\n" + "\n".join(f"- {h}" for h in hints)
    return msg


def chat_start(vocal, vocal_in, beat, beat_in, ref_choice, ref_upload, preset_text, bpm, tune_on, exp16, mp3,
               *slots, progress=gr.Progress()):
    try:
        p = pipeline.Params(bpm=float(bpm) if bpm else None, tune=bool(tune_on), export16=exp16, export_mp3=mp3,
                            backing=_backing_from_slots(slots))
        sess = MixSession.start(pick_input(vocal, vocal_in), pick_input(beat, beat_in),
                                pick_reference(ref_choice, ref_upload), parse_preset(preset_text), p)
        sess.render("старт", progress=_progress(progress))
    except AudioError as exc:
        raise gr.Error(str(exc), duration=None) from exc
    except Exception as exc:
        traceback.print_exc()
        raise gr.Error(f"Неожиданная ошибка: {type(exc).__name__}: {exc}", duration=None) from exc
    intro = ("Первый микс собран. Пиши, что поменять, обычными словами, например: "
             f"«{assistant.UNDERSTOOD_EXAMPLES}».")
    history = [{"role": "assistant", "content": _version_message(sess, intro)}]
    return (sess, history, *_session_outputs(sess))


def chat_send(msg, history, sess, mode, model, url, progress=gr.Progress()):
    history = list(history or [])
    msg = (msg or "").strip()
    keep = (gr.skip(),) * 7
    if not msg:
        yield (sess, history, "", *keep)
        return
    history.append({"role": "user", "content": msg})
    if sess is None:
        history.append({"role": "assistant", "content": "Сначала загрузи дорожки и нажми «Собрать первый микс»."})
        yield (sess, history, "", *keep)
        return
    history.append({"role": "assistant", "content": "⏳ Думаю…"})
    yield (sess, history, "", *keep)
    try:
        plan, lines = sess.ask(msg, _brain(mode, model, url))
        if not lines:
            text = plan.reply or "Не понял, что поменять."
            history[-1] = {"role": "assistant", "content": f"{text}\n\nПримеры: {assistant.UNDERSTOOD_EXAMPLES}"}
            yield (sess, history, "", *keep)
            return
        head = (plan.reply + "\n" if plan.reply else "") + "\n".join(lines)
        changed = plan.undo or any("→" in ln for ln in lines)
        if not changed:
            history[-1] = {"role": "assistant", "content": head}
            yield (sess, history, "", *keep)
            return
        history[-1] = {"role": "assistant", "content": head + "\n\n⏳ Пересобираю…"}
        yield (sess, history, "", *keep)
        sess.render(msg, lines, progress=_progress(progress))
        history[-1] = {"role": "assistant", "content": _version_message(sess, head)}
        yield (sess, history, "", *_session_outputs(sess))
    except AudioError as exc:
        history[-1] = {"role": "assistant", "content": f"⚠ {exc}"}
        yield (sess, history, "", *keep)
    except Exception as exc:
        traceback.print_exc()
        history[-1] = {"role": "assistant", "content": f"⚠ Ошибка: {type(exc).__name__}: {exc}"}
        yield (sess, history, "", *keep)


def brain_status(mode, model, url):
    if mode != BRAIN_LLM:
        return "Работают встроенные правила: мгновенно и без интернета."
    ok, text = assistant.OllamaBrain(model or "qwen2.5:7b", url or "http://127.0.0.1:11434").status()
    return ("✅ " if ok else "⚠ ") + text


# ----------------------------------------------------------------- layout

def output_block():
    """Shared result widgets for every tab."""
    section("Результат")
    with gr.Group():
        status = gr.Markdown("> ожидание: загрузи файлы и нажми кнопку", elem_classes="mm-status")
        master = gr.Audio(label="Мастер (24 бит)", type="filepath", interactive=False)
        files = gr.File(label="Скачать", file_count="multiple", interactive=False)
    gr.Markdown("**A/B с выровненной громкостью** (честное сравнение: громче ≠ лучше)")
    with gr.Row():
        ab_a = gr.Audio(label="A: до", type="filepath", interactive=False)
        ab_b = gr.Audio(label="B: после", type="filepath", interactive=False)
    table = gr.Dataframe(label="Замеры до / после", interactive=False, wrap=True)
    plot = gr.Plot(label="Спектр")
    return [status, master, files, ab_a, ab_b, table, plot]


def backing_inputs():
    """Three backing-vocal slots: (upload, file from inputs/, role) each."""
    slots = []
    for i in range(N_BACKING):
        with gr.Row():
            with gr.Column(scale=3):
                b_audio, b_in = input_picker(f"Бэк {i + 1} (WAV)")
            b_role = gr.Dropdown(ROLE_CHOICES, value="double" if i < 2 else "harmony", label="Что это", scale=2)
        slots.append((b_audio, b_in, b_role))
    return slots


def input_picker(label: str):
    """Upload widget plus a dropdown with files from inputs/."""
    audio = gr.Audio(label=label, type="filepath", sources=["upload"])
    choice = gr.Dropdown(audio_files(INPUT_DIR), label="…или файл из папки inputs/", value=None)
    return audio, choice


def reference_picker():
    with gr.Row():
        choice = gr.Dropdown(reference_choices(), label="Референс из папки references/", scale=4)
        refresh = gr.Button("Обновить список", scale=1, size="sm")
    upload = gr.Audio(label="…или загрузи референс", type="filepath", sources=["upload"])
    refresh.click(refresh_refs, outputs=choice)
    return choice, upload


def loudness_controls(default_mode=LOUD_REF, default_target=-14.0, with_mode=True):
    mode = gr.Radio([LOUD_REF, LOUD_TARGET], value=default_mode, label="Громкость мастера", visible=with_mode)
    target = gr.Slider(-18, -6, value=default_target, step=0.5, label="Целевой LUFS (-14 стриминг, -9 громко)")
    return mode, target


def tuning_controls(t: dict, with_enable: bool = True, with_backs: bool = True):
    """Pitch-correction widgets: enable, key, scale, strength, retune speed, tolerance (+ apply to backing)."""
    enabled = gr.Checkbox(label="Включить коррекцию нот", value=bool(t["enabled"]), visible=with_enable)
    with gr.Row():
        key = gr.Dropdown([KEY_AUTO] + NOTE_NAMES, value=KEY_AUTO if t["key"] == "auto" else t["key"], label="Тоника")
        scale = gr.Dropdown(SCALE_CHOICES, value="auto" if t.get("scale_auto", True) else t["scale"], label="Лад")
        strength = gr.Slider(0, 1, value=t["strength"], step=0.05, label="Сила коррекции")
    with gr.Row():
        retune = gr.Slider(0, 300, value=t["retune_ms"], step=5,
                           label="Скорость, мс (0 = автотюн-эффект, 100+ = естественно)")
        tol = gr.Slider(0, 50, value=t["tolerance_cents"], step=1, label="Допуск, центов (ноты ближе не трогаются)")
    backs = gr.Checkbox(label="Тюнить и бэк-вокал", value=bool(t["apply_to_backing"]), visible=with_backs)
    return [enabled, key, scale, strength, retune, tol, backs]


def export_controls():
    with gr.Row():
        exp16 = gr.Checkbox(label="Ещё WAV 16 бит", value=False)
        mp3 = gr.Checkbox(label="Ещё MP3 (V0)", value=False)
    return exp16, mp3


def build_ui() -> gr.Blocks:
    preset0 = load_preset(DEFAULT_PRESET)
    vals0 = slider_values(preset0)
    with gr.Blocks(title="mixmaster-local") as demo:
        gr.HTML(HEADER)
        with gr.Row():
            preset_dd = gr.Dropdown(preset_choices(), value=DEFAULT_PRESET, label="Пресет", scale=3)
            refresh_in = gr.Button("Обновить inputs/", scale=1, size="sm")
        with gr.Accordion("Редактор пресета (JSON) и сохранение своего", open=False, elem_classes="mm-acc"):
            preset_text = gr.Code(json.dumps(preset0, ensure_ascii=False, indent=2), language="json", label="Значения пресета")
            with gr.Row():
                preset_name = gr.Textbox(label="Название нового пресета", placeholder="Например: Мой трэп", scale=3)
                save_btn = gr.Button("Сохранить пресет (с текущими ползунками)", scale=2)
            gr.Markdown(f"Пресеты лежат в `{PRESET_DIR}`. Свои сохраняются как `user_*.json`.", elem_classes="small-note")

        with gr.Tabs():
            with gr.Tab("00 · Чат-микс"):
                gr.Markdown("Собери первый микс, а дальше проси правки словами, как у звукорежиссёра: "
                            "«вокал тонет», «меньше реверба», «жёстче автотюн», «мастер -9 LUFS». После каждой "
                            "правки пересобираются только затронутые этапы, а A/B сравнивает с прошлой версией.",
                            elem_classes="small-note")
                section("Дорожки")
                with gr.Row():
                    with gr.Column():
                        c_vocal, c_vocal_in = input_picker("Вокал (WAV)")
                    with gr.Column():
                        c_beat, c_beat_in = input_picker("Бит (WAV)")
                c_ref, c_ref_up = reference_picker()
                with gr.Accordion("Бэк-вокал (необязательно)", open=False, elem_classes="mm-acc"):
                    c_backing = backing_inputs()
                with gr.Row():
                    c_bpm = gr.Number(value=None, label="BPM (для дилея)", precision=1)
                    c_tune = gr.Checkbox(label="Сразу включить тюн", value=False)
                    c_exp16, c_mp3 = export_controls()
                c_go = gr.Button("Собрать первый микс", variant="primary")
                section("Чат")
                c_chat = gr.Chatbot(label="Ассистент сведения", height=460, elem_classes="mm-chat")
                with gr.Row():
                    c_msg = gr.Textbox(placeholder="Например: вокал чуть громче и меньше шипящих", show_label=False,
                                       scale=6, lines=1, max_lines=4, submit_btn=False)
                    c_send = gr.Button("Отправить", variant="primary", scale=1)
                with gr.Row(elem_classes="mm-chips"):
                    c_quick = [gr.Button(q, size="sm") for q in QUICK_PROMPTS]
                    c_undo = gr.Button("↶ отменить", size="sm")
                with gr.Accordion("Мозг ассистента: правила или локальная LLM", open=False, elem_classes="mm-acc"):
                    gr.Markdown("По умолчанию работают встроенные правила: они понимают русские и английские фразы "
                                "о громкости, тоне, ревербе, дилее, тюне, бэках и мастере. Для свободных формулировок "
                                "можно подключить бесплатную локальную модель: установи Ollama (ollama.com), выполни "
                                "`ollama pull qwen2.5:7b` и выбери режим ниже. Всё остаётся на компьютере.",
                                elem_classes="small-note")
                    with gr.Row():
                        c_mode = gr.Radio([BRAIN_RULES, BRAIN_LLM], value=BRAIN_RULES, label="Режим")
                        c_model = gr.Textbox(value="qwen2.5:7b", label="Модель Ollama")
                        c_url = gr.Textbox(value="http://127.0.0.1:11434", label="Адрес Ollama")
                    c_check = gr.Button("Проверить", size="sm")
                    c_status = gr.Markdown("")
                section("Текущая версия")
                with gr.Group():
                    c_master = gr.Audio(label="Мастер", type="filepath", interactive=False)
                    c_files = gr.File(label="Скачать", file_count="multiple", interactive=False)
                with gr.Row():
                    c_ab_a = gr.Audio(label="A", type="filepath", interactive=False)
                    c_ab_b = gr.Audio(label="B", type="filepath", interactive=False)
                c_table = gr.Dataframe(label="Замеры", interactive=False, wrap=True)
                c_plot = gr.Plot(label="Спектр")
                with gr.Accordion("Текущие настройки", open=False, elem_classes="mm-acc"):
                    c_settings = gr.JSON(label="Параметры, которыми управляет ассистент")
                c_state = gr.State(None)

            with gr.Tab("01 · Вокал + бит → мастер"):
                section("Входы")
                with gr.Row():
                    with gr.Column():
                        vocal, vocal_in = input_picker("Вокал (WAV)")
                    with gr.Column():
                        beat, beat_in = input_picker("Бит (WAV)")
                ref1, ref1_up = reference_picker()
                section("Обработка")
                with gr.Accordion("Ползунки", open=True, elem_classes="mm-acc"):
                    with gr.Row():
                        lu = gr.Slider(-2, 8, value=vals0[0], step=0.5, label="Вокал над битом, LU")
                        deess = gr.Slider(0, 1, value=vals0[1], step=0.05, label="Де-эссер")
                        bright = gr.Slider(-3, 3, value=vals0[4], step=0.5, label="Яркость вокала, дБ")
                    with gr.Row():
                        reverb = gr.Slider(0, 0.4, value=vals0[2], step=0.01, label="Reverb")
                        delay = gr.Slider(0, 0.4, value=vals0[3], step=0.01, label="Delay (нужен BPM)")
                        duck = gr.Slider(0, 3, value=vals0[5], step=0.1, label="Место под вокал (duck), дБ")
                    with gr.Row():
                        bpm = gr.Number(value=None, label="BPM (пусто = delay выкл.)", precision=1)
                        offset = gr.Slider(-500, 500, value=0, step=1, label="Сдвиг вокала, мс")
                        vtarget = gr.Radio([TARGET_PRESET, TARGET_REF], value=TARGET_PRESET, label="Цель EQ вокала")
                    loud1, target1 = loudness_controls(vals0[6], vals0[7])
                    exp16_1, mp3_1 = export_controls()
                with gr.Accordion("Коррекция нот (тюн)", open=False, elem_classes="mm-acc"):
                    gr.Markdown("Поправляет «вылетевшие» ноты под тональность бита. Медленная скорость (100–200 мс) "
                                "звучит естественно и сохраняет вибрато, 0–20 мс даёт жёсткий автотюн-эффект.",
                                elem_classes="small-note")
                    tune1 = tuning_controls(preset0["tuning"])
                with gr.Accordion("Бэк-вокал: даблы, гармонии, адлибы (до 3 дорожек)", open=False, elem_classes="mm-acc"):
                    gr.Markdown("Каждая дорожка выравнивается по лиду, обрабатывается той же цепочкой, "
                                "разводится по панораме (лево/право) и ставится тише лида. Лид остаётся в центре.",
                                elem_classes="small-note")
                    backing_in = backing_inputs()
                    with gr.Row():
                        b_level = gr.Slider(-6, 6, value=0, step=0.5, label="Бэки громче/тише обычного, LU")
                        b_width = gr.Slider(0, 1, value=1.0, step=0.05, label="Ширина стерео бэков")
                go1 = gr.Button("Свести и сделать мастер", variant="primary")
                out1 = output_block()

            with gr.Tab("02 · Мастер по референсу"):
                section("Входы")
                track2, track2_in = input_picker("Готовый трек (WAV)")
                ref2, ref2_up = reference_picker()
                section("Громкость и экспорт")
                loud2, target2 = loudness_controls(vals0[6], vals0[7])
                exp16_2, mp3_2 = export_controls()
                go2 = gr.Button("Сделать мастер", variant="primary")
                out2 = output_block()

            with gr.Tab("03 · Мастер без референса"):
                section("Вход")
                track3, track3_in = input_picker("Готовый трек (WAV)")
                section("Громкость и экспорт")
                _, target3 = loudness_controls(LOUD_TARGET, vals0[7], with_mode=False)
                exp16_3, mp3_3 = export_controls()
                go3 = gr.Button("Сделать мастер", variant="primary")
                out3 = output_block()

            with gr.Tab("04 · Тюн вокала"):
                gr.Markdown("Только коррекция нот: на выходе сухой вокал WAV 24 бит, его можно забрать в свою DAW. "
                            "Бит не обязателен, он нужен только чтобы точнее определить тональность.",
                            elem_classes="small-note")
                with gr.Row():
                    with gr.Column():
                        vocal4, vocal4_in = input_picker("Вокал (WAV)")
                    with gr.Column():
                        beat4, beat4_in = input_picker("Бит для тональности (необязательно)")
                section("Коррекция")
                tune4 = tuning_controls(preset0["tuning"], with_enable=False, with_backs=False)
                exp16_4, mp3_4 = export_controls()
                go4 = gr.Button("Поправить ноты", variant="primary")
                section("Результат")
                with gr.Group():
                    status4 = gr.Markdown("> ожидание: загрузи вокал и нажми кнопку", elem_classes="mm-status")
                    tuned4 = gr.Audio(label="Вокал после тюна (24 бит)", type="filepath", interactive=False)
                    files4 = gr.File(label="Скачать", file_count="multiple", interactive=False)
                with gr.Row():
                    ab4a = gr.Audio(label="A: до", type="filepath", interactive=False)
                    ab4b = gr.Audio(label="B: после", type="filepath", interactive=False)
                plot4 = gr.Plot(label="Ноты до / после")

        sliders = [lu, deess, reverb, delay, bright, duck, loud1, target1]
        preset_dd.change(on_preset, preset_dd, [preset_text, *sliders, loud2, target2, target3, *tune1, *tune4[1:6]])
        in_dropdowns = ([vocal_in, beat_in, track2_in, track3_in, vocal4_in, beat4_in, c_vocal_in, c_beat_in]
                        + [b_in for _, b_in, _ in backing_in] + [b_in for _, b_in, _ in c_backing])
        refresh_in.click(refresh_inputs_for(len(in_dropdowns)), outputs=in_dropdowns)

        c_outs = [c_master, c_files, c_ab_a, c_ab_b, c_table, c_plot, c_settings]
        c_go.click(chat_start, [c_vocal, c_vocal_in, c_beat, c_beat_in, c_ref, c_ref_up, preset_text, c_bpm, c_tune,
                                c_exp16, c_mp3, *[c for slot in c_backing for c in slot]], [c_state, c_chat, *c_outs])
        send_in = [c_msg, c_chat, c_state, c_mode, c_model, c_url]
        send_out = [c_state, c_chat, c_msg, *c_outs]
        c_send.click(chat_send, send_in, send_out)
        c_msg.submit(chat_send, send_in, send_out)
        for btn, text in [*zip(c_quick, QUICK_PROMPTS), (c_undo, "отмени")]:
            btn.click(lambda t=text: t, None, c_msg).then(chat_send, send_in, send_out)
        c_check.click(brain_status, [c_mode, c_model, c_url], c_status)
        save_btn.click(on_save_preset, [preset_name, preset_text, lu, deess, reverb, delay, bright, duck, *tune1], preset_dd)
        go1.click(run_mode1, [vocal, vocal_in, beat, beat_in, ref1, ref1_up, preset_text, *sliders, bpm, offset, vtarget,
                              exp16_1, mp3_1, *tune1, b_level, b_width, *[c for slot in backing_in for c in slot]], out1)
        gr.HTML(FOOTER)
        go4.click(run_mode4, [vocal4, vocal4_in, beat4, beat4_in, preset_text, *tune4[1:6], exp16_4, mp3_4],
                  [status4, tuned4, files4, ab4a, ab4b, plot4])
        go2.click(run_mode2, [track2, track2_in, ref2, ref2_up, preset_text, loud2, target2, exp16_2, mp3_2], out2)
        go3.click(run_mode3, [track3, track3_in, preset_text, target3, exp16_3, mp3_3], out3)
    return demo


def theme():
    """Brutalist dark theme. IBM Plex Mono ships inside Gradio, so nothing is loaded from the internet."""
    mono = [gr.themes.LocalFont("IBM Plex Mono", weights=(400, 500, 600, 700)), "ui-monospace", "Consolas", "monospace"]
    acid, ink, bg, panel, line = "#d7ff1f", "#f1f1ee", "#0b0b0c", "#111113", "#3d3d3a"
    t = gr.themes.Base(primary_hue="lime", neutral_hue="zinc", font=mono, font_mono=mono,
                       radius_size=gr.themes.sizes.radius_none)
    colors = dict(
        body_background_fill=bg, body_text_color=ink, body_text_color_subdued="#8d8d88",
        background_fill_primary=panel, background_fill_secondary=bg, border_color_primary=line,
        block_background_fill=panel, block_border_color=line, block_label_background_fill=ink,
        block_label_text_color="#000000", block_title_text_color=ink, input_background_fill=bg,
        input_border_color=line, input_border_color_focus=acid, color_accent=acid, color_accent_soft="#2a3300",
        slider_color=acid, checkbox_background_color_selected=acid, checkbox_border_color_selected=acid,
        button_primary_background_fill=acid, button_primary_background_fill_hover=acid,
        button_primary_text_color="#000000", button_secondary_background_fill="transparent",
        button_secondary_text_color=ink, button_secondary_border_color=ink, table_even_background_fill=panel,
        table_odd_background_fill=bg, table_border_color=line, link_text_color=acid,
    )
    valid = set(inspect.signature(gr.themes.Base.set).parameters)
    dark = {f"{k}_dark": v for k, v in colors.items() if f"{k}_dark" in valid}
    return t.set(**colors, **dark,
                 block_shadow="none", block_border_width="1.5px", input_border_width="1.5px",
                 button_border_width="2px", block_label_text_weight="600")


if __name__ == "__main__":
    for d in (REF_DIR, INPUT_DIR, pipeline.OUTPUT_DIR):
        d.mkdir(exist_ok=True)
    build_ui().queue(default_concurrency_limit=1).launch(
        server_name="127.0.0.1",
        inbrowser=os.environ.get("MIXMASTER_NO_BROWSER") != "1",
        allowed_paths=[str(pipeline.OUTPUT_DIR), str(REF_DIR), str(INPUT_DIR)],
        theme=theme(), css_paths=[str(CSS_PATH)], js=FORCE_DARK, footer_links=[],
    )
