"""Command-line runner (batch processing without the UI).

Examples:
  python cli.py mix --vocal inputs/v.wav --beat inputs/b.wav --ref references/r.wav --bpm 140
  python cli.py master --track inputs/mix.wav --ref references/r.wav --lufs -9
  python cli.py master-noref --track inputs/mix.wav --lufs -14
"""

from __future__ import annotations

import argparse
import sys

from core import pipeline
from core.audio_io import AudioError
from core.presets import list_presets, load_preset


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="mixmaster-local: сведение и мастеринг из командной строки")
    sub = ap.add_subparsers(dest="mode", required=True)
    for name in ("mix", "master", "master-noref", "chat"):
        sp = sub.add_parser(name)
        sp.add_argument("--preset", default="trap_synthwave", choices=list(list_presets()))
        sp.add_argument("--lufs", type=float, default=None, help="целевой LUFS (по умолчанию как у референса)")
        sp.add_argument("--mp3", action="store_true")
        sp.add_argument("--wav16", action="store_true")
        if name in ("mix", "chat"):
            sp.add_argument("--vocal", required=True)
            sp.add_argument("--beat", required=True)
            sp.add_argument("--bpm", type=float, default=None)
            sp.add_argument("--offset-ms", type=float, default=0.0)
            sp.add_argument("--vocal-lu", type=float, default=None, help="вокал над битом, LU")
        else:
            sp.add_argument("--track", required=True)
        if name != "master-noref":
            sp.add_argument("--ref", required=True)
        if name == "chat":
            sp.add_argument("--llm", default=None, help="модель Ollama для свободных фраз, например qwen2.5:7b")
    a = ap.parse_args(argv)

    p = pipeline.Params(export16=a.wav16, export_mp3=a.mp3, target_lufs=a.lufs,
                        loudness="target" if a.lufs is not None else "reference")
    preset = load_preset(a.preset)
    progress = lambda f, m: print(f"[{int(f * 100):3d}%] {m}", flush=True)  # noqa: E731
    if a.mode == "chat":
        return chat_loop(a, preset, p)
    try:
        if a.mode == "mix":
            p.bpm, p.offset_ms, p.vocal_over_beat_lu = a.bpm, a.offset_ms, a.vocal_lu
            res = pipeline.run_mix_and_master(a.vocal, a.beat, a.ref, preset, p, progress=progress)
        elif a.mode == "master":
            res = pipeline.run_master_reference(a.track, a.ref, preset, p, progress=progress)
        else:
            res = pipeline.run_master_no_reference(a.track, preset, p, progress=progress)
    except AudioError as exc:
        print(f"Ошибка: {exc}", file=sys.stderr)
        return 1
    print(res.summary)
    for w in res.warnings:
        print(f"! {w}")
    print(f"Результат: {res.files['master24']}")
    return 0


def chat_loop(a, preset, p) -> int:
    """Interactive chat mixing in the terminal: type a request, get a new version."""
    from core.assistant import OllamaBrain, UNDERSTOOD_EXAMPLES
    from core.session import MixSession

    p.bpm, p.offset_ms, p.vocal_over_beat_lu = a.bpm, a.offset_ms, a.vocal_lu
    llm = OllamaBrain(a.llm) if a.llm else None
    try:
        sess = MixSession.start(a.vocal, a.beat, a.ref, preset, p)
        v = sess.render("старт")
    except AudioError as exc:
        print(f"Ошибка: {exc}", file=sys.stderr)
        return 1
    print(v.result.summary)
    print(f"Версия 1: {v.result.files['master24']}")
    print(f"Пиши правки ({UNDERSTOOD_EXAMPLES}); пустая строка или «выход» — закончить.")
    while True:
        try:
            text = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not text or text.lower() in ("выход", "exit", "quit"):
            break
        plan, lines = sess.ask(text, llm)
        if plan.reply:
            print(plan.reply)
        if not lines:
            print("Не понял, что поменять.")
            continue
        print("\n".join(lines))
        if plan.undo or any("→" in ln for ln in lines):
            v = sess.render(text, lines)
            print(v.result.summary.splitlines()[0])
            print(f"Версия {v.n} ({v.seconds:.0f} с): {v.result.files['master24']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
