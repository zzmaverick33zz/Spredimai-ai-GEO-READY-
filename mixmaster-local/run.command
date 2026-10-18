#!/usr/bin/env bash
# macOS double-click launcher (Finder opens it in Terminal).
cd "$(dirname "$0")"
bash ./run.sh
echo
read -n 1 -s -r -p "Нажми любую клавишу, чтобы закрыть окно..."
