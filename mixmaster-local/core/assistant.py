"""Mix assistant: turns a request in plain words ("вокал чуть громче", "меньше реверба",
"бас мутный", "-9 LUFS") into parameter changes.

Two brains share one list of controls:
- RuleBrain: built-in Russian/English phrase parser, instant and fully offline;
- OllamaBrain: optional local LLM (Ollama, free) for free-form requests. Following the
  LLM2Fx approach it gets the control list with current values and ranges, audio
  measurements of the current version and few-shot examples, and must answer with JSON.
"""

from __future__ import annotations

import copy
import json
import re
import urllib.error
import urllib.request
from dataclasses import dataclass, field

from .tuning import NOTE_NAMES


# ----------------------------------------------------------------- controls

@dataclass(frozen=True)
class Control:
    name: str
    path: tuple  # path inside the preset; ("params", "bpm") for session params
    label: str
    kind: str = "float"  # float | bool | choice
    lo: float = 0.0
    hi: float = 1.0
    step: float = 0.1
    unit: str = ""
    choices: tuple = ()


CONTROLS = {c.name: c for c in [
    Control("vocal_level", ("balance", "vocal_over_beat_lu"), "Вокал над битом", lo=-4, hi=10, step=1.0, unit="LU"),
    Control("vocal_brightness", ("vocal", "brightness_db"), "Яркость вокала", lo=-4, hi=4, step=1.0, unit="дБ"),
    Control("vocal_presence", ("vocal", "presence", "gain_db"), "Присутствие вокала (3–5 кГц)", lo=-4, hi=6, step=1.0, unit="дБ"),
    Control("vocal_air", ("vocal", "air_shelf", "gain_db"), "Воздух вокала (10 кГц+)", lo=-4, hi=6, step=1.0, unit="дБ"),
    Control("vocal_mud", ("vocal", "lowmid_cut", "gain_db"), "Срез бубнения вокала (300 Гц)", lo=-6, hi=2, step=1.5, unit="дБ"),
    Control("vocal_lowcut", ("vocal", "highpass_hz"), "Срез низа вокала", lo=40, hi=250, step=20, unit="Гц"),
    Control("deesser", ("vocal", "deesser", "amount"), "Де-эссер", lo=0, hi=1, step=0.15),
    Control("compression", ("vocal", "compressor", "ratio"), "Компрессия вокала (ratio)", lo=1.5, hi=10, step=1.0, unit=":1"),
    Control("density", ("vocal", "parallel", "mix"), "Плотность вокала (параллельная компрессия)", lo=0, hi=0.5, step=0.06),
    Control("saturation", ("vocal", "saturation", "mix"), "Сатурация вокала", lo=0, hi=0.6, step=0.1),
    Control("rider", ("vocal", "rider", "range_db"), "Выравнивание громкости фраз (райдер)", lo=0, hi=8, step=1.5, unit="дБ"),
    Control("reverb", ("vocal", "reverb", "mix"), "Реверб", lo=0, hi=0.4, step=0.04),
    Control("reverb_size", ("vocal", "reverb", "room_size"), "Размер реверба", lo=0.1, hi=0.95, step=0.12),
    Control("delay", ("vocal", "delay", "mix"), "Дилей", lo=0, hi=0.4, step=0.04),
    Control("delay_mode", ("vocal", "delay", "mode"), "Режим дилея", kind="choice", choices=("always", "throws")),
    Control("delay_note", ("vocal", "delay", "note"), "Длина дилея", kind="choice", choices=("1/4", "1/8", "1/8d", "1/16")),
    Control("space_duck", ("vocal", "space_duck_db"), "Приглушение ревера/дилея под голосом", lo=0, hi=10, step=2.0, unit="дБ"),
    Control("tune_enabled", ("tuning", "enabled"), "Коррекция нот", kind="bool"),
    Control("tune_speed", ("tuning", "retune_ms"), "Скорость тюна (меньше = жёстче)", lo=0, hi=300, step=40, unit="мс"),
    Control("tune_strength", ("tuning", "strength"), "Сила тюна", lo=0, hi=1, step=0.1),
    Control("tune_key", ("tuning", "key"), "Тоника для тюна", kind="choice", choices=("auto",) + tuple(NOTE_NAMES)),
    Control("tune_scale", ("tuning", "scale"), "Лад для тюна", kind="choice", choices=("minor", "major", "chromatic")),
    Control("backing_level", ("backing", "level_offset_lu"), "Громкость бэков", lo=-8, hi=6, step=1.5, unit="LU"),
    Control("backing_width", ("backing", "width"), "Ширина бэков", lo=0, hi=1, step=0.2),
    Control("beat_duck", ("beat", "duck_db"), "Бит приседает под вокал", lo=0, hi=4, step=0.5, unit="дБ"),
    Control("beat_carve", ("beat", "carve_db"), "Место под вокал в бите (1–4 кГц)", lo=-4, hi=0, step=0.5, unit="дБ"),
    Control("beat_bass", ("beat", "low_shelf_db"), "Низ бита", lo=-6, hi=6, step=1.5, unit="дБ"),
    Control("beat_brightness", ("beat", "high_shelf_db"), "Верх бита", lo=-6, hi=6, step=1.5, unit="дБ"),
    Control("master_lufs", ("master", "target_lufs"), "Громкость мастера", lo=-18, hi=-6, step=1.5, unit="LUFS"),
    Control("master_loudness_mode", ("master", "loudness"), "Режим громкости", kind="choice", choices=("reference", "target")),
    Control("master_bass", ("master", "post", "bass_db"), "Низ мастера", lo=-4, hi=4, step=1.0, unit="дБ"),
    Control("master_mud", ("master", "post", "lowmid_db"), "Середина-низ мастера (300 Гц)", lo=-4, hi=2, step=1.0, unit="дБ"),
    Control("master_presence", ("master", "post", "presence_db"), "Присутствие мастера (3 кГц)", lo=-3, hi=3, step=0.75, unit="дБ"),
    Control("master_air", ("master", "post", "air_db"), "Верх мастера (10 кГц+)", lo=-4, hi=4, step=1.0, unit="дБ"),
    Control("master_width", ("master", "post", "width_db"), "Ширина стерео мастера", lo=-6, hi=4, step=1.5, unit="дБ"),
    Control("mono_bass", ("master", "post", "mono_bass_hz"), "Моно-низ ниже", lo=0, hi=200, step=30, unit="Гц"),
    Control("bpm", ("params", "bpm"), "BPM (для дилея)", lo=40, hi=220, step=1, unit="BPM"),
    Control("offset", ("params", "offset_ms"), "Сдвиг вокала", lo=-500, hi=500, step=10, unit="мс"),
]}


@dataclass
class Change:
    control: str
    op: str  # "add" | "set"
    value: object
    why: str = ""


@dataclass
class Plan:
    changes: list = field(default_factory=list)
    reply: str = ""
    undo: bool = False
    brain: str = "rules"


def _get(state: dict, path: tuple):
    node = state
    for k in path:
        node = node.get(k) if isinstance(node, dict) else None
        if node is None:
            return None
    return node


def _set(state: dict, path: tuple, value) -> None:
    node = state
    for k in path[:-1]:
        node = node.setdefault(k, {})
    node[path[-1]] = value


def current_value(state: dict, name: str, ctx: dict | None = None):
    """Value of a control; master_lufs falls back to the measured loudness of the last master."""
    c = CONTROLS[name]
    v = _get(state, c.path)
    if name == "master_lufs" and (v is None or _get(state, ("master", "loudness")) != "target"):
        v = (ctx or {}).get("master_lufs", v if v is not None else -14.0)
    if name == "bpm" and not v:
        v = None
    return v


def apply_changes(state: dict, changes: list[Change], ctx: dict | None = None) -> list[str]:
    """Apply changes to a state dict {"preset":..., "params":...} in place. Returns readable lines."""
    lines = []
    for ch in changes:
        c = CONTROLS.get(ch.control)
        if c is None:
            continue
        old = current_value(state, c.name, ctx)
        if c.kind == "bool":
            new = bool(ch.value)
        elif c.kind == "choice":
            new = str(ch.value)
            if new not in c.choices:
                continue
        else:
            try:
                val = float(ch.value)
            except (TypeError, ValueError):
                continue
            base = float(old) if old is not None else (c.lo if ch.op == "add" else 0.0)
            new = base + val if ch.op == "add" else val
            new = float(min(max(new, c.lo), c.hi))
            new = round(new, 3)
        if old == new:
            lines.append(f"• {c.label}: уже {fmt(old, c)} (упёрлись в предел)" if c.kind == "float" else
                         f"• {c.label}: уже {fmt(old, c)}")
            continue
        _set(state, c.path, new)
        # side effects that make a change actually audible
        if c.name == "master_lufs":
            _set(state, ("master", "loudness"), "target")
        if c.name == "saturation" and new > 0 and (_get(state, ("vocal", "saturation", "drive_db")) or 0) < 4:
            _set(state, ("vocal", "saturation", "drive_db"), 6.0)
        if c.name in ("tune_speed", "tune_strength", "tune_key", "tune_scale") and not _get(state, ("tuning", "enabled")):
            _set(state, ("tuning", "enabled"), True)
        if c.name == "tune_scale":
            _set(state, ("tuning", "scale_auto"), False)
        if c.name in ("delay", "delay_mode", "delay_note") and not _get(state, ("params", "bpm")):
            lines.append("• Для дилея нужен BPM: напиши, например, «bpm 140».")
        lines.append(f"• {c.label}: {fmt(old, c)} → {fmt(new, c)}" + (f" ({ch.why})" if ch.why else ""))
    return lines


def fmt(v, c: Control) -> str:
    if v is None:
        return "—"
    if c.kind == "bool":
        return "вкл" if v else "выкл"
    if c.kind == "choice":
        return {"always": "всегда", "throws": "броски в концах фраз", "reference": "как у референса",
                "target": "целевой LUFS", "auto": "авто", "minor": "минор", "major": "мажор",
                "chromatic": "хроматика"}.get(str(v), str(v))
    v = float(v)
    s = f"{v:.2f}".rstrip("0").rstrip(".") if abs(v) < 10 else f"{v:.1f}".rstrip("0").rstrip(".")
    return f"{s} {c.unit}".strip()


# ----------------------------------------------------------------- rule brain

def _norm(text: str) -> str:
    return text.lower().replace("ё", "е").replace("–", "-").replace("—", "-")


T = {  # targets (checked in this order)
    "backing": r"бэк|бек|дабл|гармони|подпев|адлиб|backing|double|harmon|adlib|ad-lib",
    "deesser": r"шип|свист|эсс|сибил|de-?ess|sibil|\bс-?звук",
    "tune": r"тюн|автотюн|auto-?tune|ноты|нот\b|фальш|pitch|интонац",
    "reverb": r"ревер|reverb|хвост|зал\b|простран|room|эмбиен",
    "delay": r"дил[еэ]й|дел[еэ]й|эхо|delay|echo|повтор",
    "bass": r"\bбас|низ|саб|808|бочк|кик|\bbass|low ?end|\bsub|\bkick",
    "vocal": r"вокал|голос|\bлид|vocal|vox|voice|слова|текст",
    "beat": r"\bбит|минус|инструментал|музык|\bbeat|instrumental",
    "master": r"мастер|трек|весь|вся|общ|целиком|громкост|master|track|overall|whole|\bмикс|\bmix",
}
A = {  # attributes
    "undo": r"отмен|верни как было|назад|undo|revert",
    "louder": r"громче|погромче|вперед|выше|ярко выраж|louder|up\b|forward|boost|подними|подтяни",
    "quieter": r"тише|потише|назад в микс|ниже|quieter|softer|lower|down\b|опусти|убавь громк",
    "brighter": r"ярче|светлее|воздух|прозрачн|четче|чище|разборчив|bright|air|crisp|clear|presence",
    "darker": r"темнее|теплее|глуше|приглуш|мягче|темн|dark|warm|smooth|softer top",
    "wider": r"шире|wide|широк|стерео",
    "narrower": r"уже\b|узк|моно|narrow|mono",
    "muddy": r"мутн|бубн|каш|грязн|гудит|бухт|mud|boxy|коробк|бочкообраз",
    "harsh": r"резк|режет|колюч|пищ|harsh|piercing|sharp",
    "thin": r"тонк|худ|пуст|thin|weak|слаб",
    "fat": r"плотн|жирн|толщ|мощн|сочн|тяжел|fat|thick|dense|punch|heavy",
    "buried": r"тонет|утонул|не слышн|потерял|утоп|теряется|buried|lost|drown",
    "dry": r"сух|dry",
    "wet": r"мокр|далек|в реверб|wet|far|distant|washy",
    "hard": r"жестч|жестк|робот|кай|kai angel|hard|robot|t-?pain|сильнее тюн",
    "natural": r"естествен|натурал|мягк|natural|subtle|незаметн",
    "off": r"убери|выключи|без\b|отключи|не надо|remove|disable|turn off|off\b",
    "on": r"включи|добавь|сделай|нужен|enable|turn on|add",
    "more": r"больше|добав|усиль|сильнее|побольше|прибавь|more|increase|stronger",
    "less": r"меньше|убав|ослаб|поменьше|слабее|less|reduce|weaker|decrease",
    "throws": r"конц[ае]х? фраз|в конце|броск|throw",
}
INTENSITY = [(r"чуть|немного|слегка|капельку|чуточку|a bit|a little|slightly|bit", 0.5),
             (r"сильно|очень|намного|гораздо|значительно|прям|much|a lot|way|very|really", 2.0)]
NUM = re.compile(r"(?<![\w.])([-+]?\d+(?:[.,]\d+)?)\s*(lufs|луфс|дб|db|lu|мс|ms|bpm|бпм|%|цент\w*|cents?|гц|hz)?")
RU_NOTES = {"до": "C", "ре": "D", "ми": "E", "фа": "F", "соль": "G", "ля": "A", "си": "B"}


def _has(pattern: str, text: str) -> bool:
    return re.search(pattern, text) is not None


def _intensity(text: str) -> float:
    for pat, k in INTENSITY:
        if _has(pat, text):
            return k
    return 1.0


def _key_from_text(text: str):
    """('A', 'minor') etc. from 'ля минор', 'A minor', 'C#m', 'в ре диез мажоре'."""
    m = re.search(r"\b(до|ре|ми|фа|соль|ля|си)\s*(диез|бемоль)?\s*(минор|мажор)?", text)
    if m and (m.group(3) or _has(r"тональн|тоник|ключ", text)):
        idx = NOTE_NAMES.index(RU_NOTES[m.group(1)])
        idx += 1 if m.group(2) == "диез" else (-1 if m.group(2) == "бемоль" else 0)
        return NOTE_NAMES[idx % 12], {"минор": "minor", "мажор": "major"}.get(m.group(3) or "", None)
    m = re.search(r"\b([a-g])\s*(#|b|sharp|flat)?\s*(minor|major|min|maj|m)?\b", text)
    if m and (m.group(3) or _has(r"key|тональн|тоник", text)):
        idx = NOTE_NAMES.index(m.group(1).upper())
        idx += 1 if m.group(2) in ("#", "sharp") else (-1 if m.group(2) in ("b", "flat") else 0)
        sc = m.group(3) or ""
        scale = "minor" if sc in ("minor", "min", "m") else ("major" if sc in ("major", "maj") else None)
        return NOTE_NAMES[idx % 12], scale
    return None


def _split(text: str) -> list[str]:
    parts = re.split(r"[.;!?\n]+|,\s*(?=\D)|\s+и\s+|\s+а\s+также\s+|\s+а\s+|\s+но\s+|\s+and\s+|\s+but\s+", text)
    return [p.strip() for p in parts if p and p.strip()]


class RuleBrain:
    """Deterministic phrase parser: no model, no internet."""

    name = "rules"

    def plan(self, text: str, state: dict, ctx: dict | None = None) -> Plan:
        t = _norm(text)
        if _has(A["undo"], t) and len(t) < 40:
            return Plan(undo=True, reply="Откатываю последнюю правку.")
        changes: list[Change] = []
        last_target = None
        for clause in _split(t):
            targets = [k for k, pat in T.items() if _has(pat, clause)]
            attrs = [k for k, pat in A.items() if k != "undo" and _has(pat, clause)]
            k = _intensity(clause)
            nums = NUM.findall(clause)
            target = targets[0] if targets else last_target
            # "больше баса и чуть ярче": a tone word after a special target means the whole track
            tone = {"brighter", "darker", "muddy", "harsh", "fat", "thin", "dry", "wet", "wider", "narrower"}
            if not targets and last_target in ("bass", "reverb", "delay", "deesser", "tune") and tone & set(attrs):
                target = None
            got = self._clause(clause, target, targets, attrs, k, nums)
            if got:
                changes += got
                last_target = target
        return Plan(changes=_dedupe(changes))

    def _clause(self, clause, target, targets, attrs, k, nums) -> list[Change]:
        S = lambda c: CONTROLS[c].step * k  # noqa: E731
        ch: list[Change] = []
        a = set(attrs)

        def add(control, sign=1.0, why=""):
            ch.append(Change(control, "add", sign * S(control), why))

        # --- explicit numbers first
        for raw, unit in nums:
            v = float(raw.replace(",", "."))
            unit = unit or ""
            if unit in ("lufs", "луфс") or (v <= -5 and target in (None, "master") and not unit):
                ch.append(Change("master_lufs", "set", v, "громкость мастера"))
            elif unit in ("bpm", "бпм") or (_has(r"bpm|бпм|темп|tempo", clause) and 40 <= v <= 220):
                ch.append(Change("bpm", "set", v))
            elif unit in ("мс", "ms") and _has(r"сдвин|сдвиг|раньше|позже|offset|shift|опазд|спеш", clause):
                sign = -1 if _has(r"раньше|earlier|спеш", clause) and v > 0 else 1
                ch.append(Change("offset", "add", sign * abs(v) if _has(r"раньше|позже|earlier|later", clause) else v))
            elif unit in ("дб", "db", "lu") and target in ("vocal", "beat", "backing"):
                sign = -1 if "quieter" in a else 1
                if target == "vocal":
                    ch.append(Change("vocal_level", "add", sign * abs(v)))
                elif target == "beat":
                    ch.append(Change("vocal_level", "add", -sign * abs(v)))
                else:
                    ch.append(Change("backing_level", "add", sign * abs(v)))
            elif target in ("reverb", "delay") and not unit and 0 <= v <= 100:
                ch.append(Change(target, "set", v / 100 if v > 1 else v))
            elif unit == "%" and target in ("reverb", "delay"):
                ch.append(Change(target, "set", v / 100))
        if ch:
            return ch

        # --- beat masks the vocal ("бит мешает вокалу", "beat clashes with the vocal")
        if "beat" in targets and _has(r"мешает|забивает|перекрыва|глушит|clash|mask|fight", clause):
            add("beat_carve", -1, "место под вокал")
            add("beat_duck", 1)
            return ch

        # --- tuning
        if target == "tune" or "hard" in a and _has(T["tune"] + "|кай|kai", clause):
            key = _key_from_text(clause)
            if key:
                ch.append(Change("tune_key", "set", key[0]))
                if key[1]:
                    ch.append(Change("tune_scale", "set", key[1]))
            if "off" in a and not ("on" in a and "more" in a):
                ch.append(Change("tune_enabled", "set", False))
            elif "hard" in a:
                ch += [Change("tune_enabled", "set", True), Change("tune_speed", "set", 10 if k < 2 else 0),
                       Change("tune_strength", "set", 1.0)]
            elif "natural" in a or "less" in a:
                ch += [Change("tune_speed", "add", 60 * k), Change("tune_strength", "add", -0.15 * k)]
            elif "more" in a:
                ch += [Change("tune_enabled", "set", True), Change("tune_speed", "add", -40 * k),
                       Change("tune_strength", "add", 0.1 * k)]
            elif "on" in a or not ch:
                ch.append(Change("tune_enabled", "set", True))
            return ch
        key = _key_from_text(clause)
        if key and _has(r"тональн|key|тоник", clause):
            ch.append(Change("tune_key", "set", key[0]))
            if key[1]:
                ch.append(Change("tune_scale", "set", key[1]))
            return ch

        # --- de-esser / sibilance
        if target == "deesser":
            add("deesser", -1 if ("less" in a or "off" in a and "more" not in a) else 1, "сибилянты")
            return ch

        # --- reverb / delay
        if target == "reverb":
            if "off" in a:
                ch.append(Change("reverb", "set", 0.0))
            elif _has(r"больш\w* зал|длинн|огромн|bigger|longer|larger", clause):
                add("reverb_size", 1)
            elif _has(r"коротк|маленьк|меньше зал|shorter|smaller|tight", clause):
                add("reverb_size", -1)
            elif "less" in a or "dry" in a and "more" not in a:
                add("reverb", -1)
            else:
                add("reverb", 1)
            return ch
        if target == "delay":
            if "throws" in a:
                ch.append(Change("delay_mode", "set", "throws"))
            elif _has(r"всегда|постоян|always|везде", clause):
                ch.append(Change("delay_mode", "set", "always"))
            m = re.search(r"1/(4|8|16)\s*(d|с точкой|dotted)?", clause)
            if m:
                ch.append(Change("delay_note", "set", f"1/{m.group(1)}" + ("d" if m.group(2) and m.group(1) in "48" else "")))
            if "off" in a:
                ch.append(Change("delay", "set", 0.0))
            elif "less" in a:
                add("delay", -1)
            elif "more" in a or "on" in a or not ch:
                add("delay", 1)
            return ch

        # --- backing vocals
        if target == "backing":
            if "wider" in a:
                add("backing_width", 1)
            elif "narrower" in a:
                add("backing_width", -1)
            elif "quieter" in a or "less" in a:
                add("backing_level", -1)
            else:
                add("backing_level", 1)
            return ch

        # --- bass / low end
        if target == "bass":
            beat_only = "beat" in targets
            ctl = "beat_bass" if beat_only else "master_bass"
            if "muddy" in a:
                add("master_mud", -1, "мутный низ")
                ch.append(Change("mono_bass", "set", 140))
            elif "less" in a or "quieter" in a or "off" in a:
                add(ctl, -1)
            elif "narrower" in a:
                ch.append(Change("mono_bass", "set", 150))
            else:
                add(ctl, 1)
            return ch

        # --- vocal
        if target == "vocal":
            if "buried" in a:
                add("vocal_level", 1.5, "вокал тонет")
                add("beat_duck", 1)
            elif "louder" in a:
                add("vocal_level", 1)
            elif "quieter" in a:
                add("vocal_level", -1)
            elif "muddy" in a:
                add("vocal_mud", -1, "бубнение")
                add("vocal_lowcut", 1)
            elif "harsh" in a:
                add("vocal_presence", -1, "резкость")
                add("deesser", 0.7)
            elif "brighter" in a:
                add("vocal_brightness", 1)
            elif "darker" in a:
                add("vocal_brightness", -1)
            elif "fat" in a:
                add("density", 1)
                add("saturation", 1)
            elif "thin" in a:
                add("vocal_mud", 1, "тонкий вокал")
                add("vocal_lowcut", -1)
                add("density", 0.5)
            elif "dry" in a:
                add("reverb", 1, "слишком сухо")
            elif "wet" in a:
                add("reverb", -1, "слишком далеко")
                add("space_duck", 1)
            elif _has(r"ровн|скач|прыга|even|consistent|jump", clause):
                add("rider", 1, "скачет громкость")
            elif "more" in a and _has(r"компресс|compress|сжат", clause):
                add("compression", 1)
            elif "less" in a and _has(r"компресс|compress|сжат", clause):
                add("compression", -1)
            elif "more" in a:
                add("vocal_level", 1)
            elif "less" in a:
                add("vocal_level", -1)
            return ch

        # --- beat
        if target == "beat":
            if "louder" in a or "more" in a:
                add("vocal_level", -1, "бит громче")
            elif "quieter" in a or "less" in a:
                add("vocal_level", 1, "бит тише")
            elif "brighter" in a:
                add("beat_brightness", 1)
            elif "darker" in a or "harsh" in a:
                add("beat_brightness", -1)
            elif "muddy" in a:
                add("beat_bass", -1)
                add("master_mud", -1)
            elif _has(r"мешает|забивает|перекрыва|clash|mask|место", clause):
                add("beat_carve", -1, "место под вокал")
                add("beat_duck", 1)
            return ch

        # --- whole track / master (also the default for target-less clauses)
        if target in ("master", None):
            if "louder" in a or (target == "master" and "more" in a and not attrs[1:]):
                ch.append(Change("master_lufs", "add", 1.5 * k, "громче"))
            elif "quieter" in a:
                ch.append(Change("master_lufs", "add", -1.5 * k, "тише"))
            elif "brighter" in a:
                add("master_air", 1)
            elif "darker" in a or "harsh" in a:
                add("master_air", -1)
                if "harsh" in a:
                    add("master_presence", -1)
            elif "muddy" in a:
                add("master_mud", -1)
            elif "wider" in a:
                add("master_width", 1)
            elif "narrower" in a:
                add("master_width", -1)
            elif "fat" in a:
                add("master_bass", 1)
            elif "thin" in a:
                add("master_bass", 1)
                add("master_mud", 0.5)
            elif "dry" in a:
                add("reverb", 1)
            elif "wet" in a:
                add("reverb", -1)
            elif _has(r"стрим|spotify|youtube|ютуб|apple", clause):
                ch.append(Change("master_lufs", "set", -14.0, "стриминг"))
            elif _has(r"как у референс|like the reference|по референс", clause):
                ch.append(Change("master_loudness_mode", "set", "reference"))
        return ch


def _dedupe(changes: list[Change]) -> list[Change]:
    """Merge repeated 'add' changes of the same control; a later 'set' wins."""
    out: dict[str, Change] = {}
    for c in changes:
        prev = out.get(c.control)
        if prev and prev.op == "add" and c.op == "add":
            out[c.control] = Change(c.control, "add", float(prev.value) + float(c.value), prev.why or c.why)
        else:
            out[c.control] = c
    return list(out.values())


# ----------------------------------------------------------------- LLM brain (optional, local)

FEW_SHOT = [
    ("вокал тонет в бите и немного шипит",
     {"reply": "Подниму вокал и чуть прижму сибилянты.",
      "changes": [{"control": "vocal_level", "op": "add", "value": 1.5},
                  {"control": "beat_duck", "op": "add", "value": 0.5},
                  {"control": "deesser", "op": "add", "value": 0.1}]}),
    ("хочу звучание как у Kai Angel: жёсткий автотюн и много пространства",
     {"reply": "Включаю жёсткий тюн и добавляю реверб с дилеем.",
      "changes": [{"control": "tune_enabled", "op": "set", "value": True},
                  {"control": "tune_speed", "op": "set", "value": 5},
                  {"control": "tune_strength", "op": "set", "value": 1.0},
                  {"control": "reverb", "op": "add", "value": 0.05},
                  {"control": "delay", "op": "add", "value": 0.05}]}),
    ("мастер слишком тихий, сделай -9 и чтобы низ был плотнее",
     {"reply": "Ставлю -9 LUFS и добавляю низа после мастеринга.",
      "changes": [{"control": "master_lufs", "op": "set", "value": -9},
                  {"control": "master_bass", "op": "add", "value": 1.0}]}),
    ("слишком мутно и голос как из коробки",
     {"reply": "Срезаю бубнение вокала и чуть чищу низ-середину мастера.",
      "changes": [{"control": "vocal_mud", "op": "add", "value": -1.5},
                  {"control": "vocal_lowcut", "op": "add", "value": 20},
                  {"control": "master_mud", "op": "add", "value": -1.0}]}),
]

PLAN_SCHEMA = {
    "type": "object",
    "properties": {
        "reply": {"type": "string"},
        "changes": {"type": "array", "items": {
            "type": "object",
            "properties": {"control": {"type": "string", "enum": list(CONTROLS)},
                           "op": {"type": "string", "enum": ["add", "set"]},
                           "value": {"type": ["number", "boolean", "string"]}},
            "required": ["control", "op", "value"]}},
    },
    "required": ["reply", "changes"],
}


class OllamaBrain:
    """Local LLM through Ollama (https://ollama.com, free). Nothing leaves the computer."""

    name = "llm"

    def __init__(self, model: str = "qwen2.5:7b", url: str = "http://127.0.0.1:11434", timeout: float = 120.0):
        self.model, self.url, self.timeout = model, url.rstrip("/"), timeout

    def _post(self, path: str, payload: dict | None, timeout: float):
        req = urllib.request.Request(self.url + path, method="POST" if payload is not None else "GET",
                                     data=json.dumps(payload).encode() if payload is not None else None,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as r:  # noqa: S310 (local URL chosen by the user)
            return json.loads(r.read().decode("utf-8"))

    def status(self) -> tuple[bool, str]:
        """(ok, message) — is Ollama running and is the model downloaded?"""
        try:
            tags = self._post("/api/tags", None, 3.0)
        except (urllib.error.URLError, OSError, ValueError):
            return False, f"Ollama не запущена по адресу {self.url}. Установи с ollama.com и запусти."
        names = [m.get("name", "") for m in tags.get("models", [])]
        base = self.model.split(":")[0]
        if not any(n == self.model or n.split(":")[0] == base for n in names):
            return False, f"Модель {self.model} не скачана. В терминале: ollama pull {self.model}"
        return True, f"Ollama работает, модель {self.model} готова."

    def system_prompt(self, state: dict, ctx: dict) -> str:
        rows = []
        for c in CONTROLS.values():
            cur = fmt(current_value(state, c.name, ctx), c)
            rng = f"{c.lo}..{c.hi} {c.unit}".strip() if c.kind == "float" else (
                "true/false" if c.kind == "bool" else "|".join(c.choices))
            rows.append(f"- {c.name}: {c.label}. Сейчас: {cur}. Диапазон: {rng}. Обычный шаг: {c.step}")
        feats = "\n".join(f"- {k}: {v}" for k, v in (ctx.get("features") or {}).items())
        shots = "\n".join(f"Пользователь: {q}\nОтвет: {json.dumps(a, ensure_ascii=False)}" for q, a in FEW_SHOT)
        return (
            "Ты звукорежиссёр-ассистент локального инструмента сведения и мастеринга (рэп/трэп/синтвейв/рок). "
            "Пользователь описывает словами, что хочет изменить в миксе. Переведи просьбу в изменения параметров. "
            "Отвечай ТОЛЬКО JSON по схеме {reply, changes}. reply: одна короткая фраза по-русски. "
            "changes: список {control, op: add|set, value}. Делай небольшие шаги (обычный шаг), "
            "меняй только то, о чём просят. Тон всего трека меняй через master_* (они работают после мастеринга). "
            "Если просьба непонятна, верни пустой changes и спроси в reply.\n\n"
            f"Параметры:\n{chr(10).join(rows)}\n\nЗамеры текущей версии:\n{feats or '- нет'}\n\nПримеры:\n{shots}"
        )

    def plan(self, text: str, state: dict, ctx: dict | None = None) -> Plan:
        ctx = ctx or {}
        payload = {"model": self.model, "stream": False, "format": PLAN_SCHEMA,
                   "options": {"temperature": 0.2},
                   "messages": [{"role": "system", "content": self.system_prompt(state, ctx)}]
                   + list(ctx.get("history", []))[-6:]
                   + [{"role": "user", "content": text}]}
        data = self._post("/api/chat", payload, self.timeout)
        content = data.get("message", {}).get("content", "")
        parsed = json.loads(content)
        changes = []
        for item in parsed.get("changes", []):
            name, op = item.get("control"), item.get("op", "add")
            if name in CONTROLS and op in ("add", "set"):
                changes.append(Change(name, op, item.get("value")))
        return Plan(changes=_dedupe(changes), reply=str(parsed.get("reply", "")), brain="llm")


# ----------------------------------------------------------------- facade

UNDERSTOOD_EXAMPLES = ("вокал чуть громче · меньше реверба · бас мутный · вокал резкий · "
                       "жёстче автотюн · дилей только в концах фраз · bpm 140 · мастер -9 LUFS · отмени")


def make_plan(text: str, state: dict, ctx: dict | None = None, llm: OllamaBrain | None = None) -> Plan:
    """LLM first when enabled (falls back to rules on any error), otherwise rules."""
    rules = RuleBrain()
    if llm is not None:
        quick = rules.plan(text, state, ctx)
        if quick.undo:
            return quick
        try:
            plan = llm.plan(text, state, ctx)
            if plan.changes or plan.reply:
                return plan
        except Exception as exc:  # unreachable server, bad JSON, timeout: never break the session
            quick.reply = f"(Локальная LLM недоступна: {type(exc).__name__}. Разобрал правилами.)"
            return quick
    return rules.plan(text, state, ctx)


def suggestions(measurements: dict, report: dict) -> list[str]:
    """Up to three hints from the measurements of the current version vs the reference."""
    out = []
    m, ref = measurements.get("Мастер"), measurements.get("Референс")
    if m and ref:
        low = (m["bands"]["sub"] + m["bands"]["bass"]) / 2 - (ref["bands"]["sub"] + ref["bands"]["bass"]) / 2
        top = (m["bands"]["high"] + m["bands"]["air"]) / 2 - (ref["bands"]["high"] + ref["bands"]["air"]) / 2
        if low < -2:
            out.append(f"Низ слабее референса на {abs(low):.1f} дБ: «больше баса».")
        elif low > 2:
            out.append(f"Низа больше, чем в референсе, на {low:.1f} дБ: «меньше баса».")
        if top < -2:
            out.append(f"Верх темнее референса на {abs(top):.1f} дБ: «ярче».")
        elif top > 2:
            out.append(f"Верх ярче референса на {top:.1f} дБ: «темнее» или «мягче верх».")
    voc = report.get("vocal", {})
    if voc.get("deesser_active_pct", 0) > 15:
        out.append("В вокале много сибилянтов: «меньше шипящих».")
    tun = report.get("tuning")
    if tun and tun.get("dev_after_cents", 0) > 20:
        out.append(f"Ноты всё ещё гуляют (~{tun['dev_after_cents']:.0f} центов): «тюн сильнее».")
    return out[:3]


def snapshot(state: dict) -> dict:
    return copy.deepcopy(state)
