#!/usr/bin/env bash
# mixmaster-local launcher (Linux/macOS): creates .venv on first run, installs deps, starts the UI.
set -e
cd "$(dirname "$0")"

pick_python() {
  if [ -n "$PYTHON" ]; then echo "$PYTHON"; return; fi
  for c in python3.12 python3.13 python3.11 python3.10 python3; do
    if command -v "$c" >/dev/null 2>&1; then
      v=$("$c" -c 'import sys; print("%d%02d" % sys.version_info[:2])')
      if [ "$v" -ge 310 ]; then echo "$c"; return; fi
    fi
  done
  echo ""
}

if [ ! -x ".venv/bin/python" ]; then
  PY=$(pick_python)
  if [ -z "$PY" ]; then
    echo "Нужен Python 3.10 или новее."
    echo "Установи Python 3.12 с python.org (macOS: brew install python@3.12) и запусти снова."
    exit 1
  fi
  echo "Создаю окружение (.venv) на $PY ..."
  "$PY" -m venv .venv
fi

# (Re)install dependencies when requirements.txt changes.
REQ_HASH=$(cksum requirements.txt | cut -d' ' -f1)
if [ ! -f ".venv/.installed" ] || [ "$(cat .venv/.installed)" != "$REQ_HASH" ]; then
  echo "Ставлю зависимости (один раз, нужен интернет)..."
  .venv/bin/python -m pip install --upgrade pip
  .venv/bin/python -m pip install -r requirements.txt
  echo "$REQ_HASH" > .venv/.installed
fi

echo "Запускаю интерфейс: http://127.0.0.1:7860 (закрыть: Ctrl+C)"
exec .venv/bin/python app.py
