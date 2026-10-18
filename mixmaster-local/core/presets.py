"""Preset loading and saving. Every preset is deep-merged over presets/_base.json."""

from __future__ import annotations

import copy
import json
import re
from pathlib import Path

PRESET_DIR = Path(__file__).resolve().parent.parent / "presets"
BASE_NAME = "_base"


def deep_merge(base: dict, override: dict) -> dict:
    """Recursively merge override into a copy of base."""
    out = copy.deepcopy(base)
    for key, val in (override or {}).items():
        if isinstance(val, dict) and isinstance(out.get(key), dict):
            out[key] = deep_merge(out[key], val)
        else:
            out[key] = copy.deepcopy(val)
    return out


def _read(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def base_preset(preset_dir: Path = PRESET_DIR) -> dict:
    """Default values every preset inherits."""
    return _read(preset_dir / f"{BASE_NAME}.json")


def list_presets(preset_dir: Path = PRESET_DIR) -> dict[str, str]:
    """Map preset id (file stem) -> display name."""
    out = {}
    for path in sorted(preset_dir.glob("*.json")):
        if path.stem.startswith("_"):
            continue
        try:
            out[path.stem] = _read(path).get("name", path.stem)
        except (OSError, json.JSONDecodeError):
            continue
    return out


def load_preset(preset_id: str, preset_dir: Path = PRESET_DIR) -> dict:
    """Load a preset by id and merge it over the base defaults."""
    path = preset_dir / f"{preset_id}.json"
    if not path.exists():
        raise FileNotFoundError(f"Пресет не найден: {preset_id}")
    return deep_merge(base_preset(preset_dir), _read(path))


def resolve(preset: dict | None, preset_dir: Path = PRESET_DIR) -> dict:
    """Make sure a (possibly partial) preset dict has every key from the base."""
    return deep_merge(base_preset(preset_dir), preset or {})


def slugify(name: str) -> str:
    """File-safe preset id from a display name (keeps Cyrillic letters)."""
    slug = re.sub(r"[^\w\-]+", "_", name.strip().lower(), flags=re.UNICODE).strip("_")
    return slug or "my_preset"


def save_preset(name: str, preset: dict, preset_dir: Path = PRESET_DIR) -> str:
    """Save a user preset as presets/user_<slug>.json; returns its id."""
    preset = copy.deepcopy(preset)
    preset["name"] = name.strip() or "Мой пресет"
    preset_id = "user_" + slugify(preset["name"])
    with open(preset_dir / f"{preset_id}.json", "w", encoding="utf-8") as f:
        json.dump(preset, f, ensure_ascii=False, indent=2)
        f.write("\n")
    return preset_id
