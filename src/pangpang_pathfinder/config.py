from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

CONFIG_DIR = Path(__file__).resolve().parents[2] / "configs"


def load_yaml(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data or {}


def load_classes_map(path: str | Path) -> dict[str, dict[str, Any]]:
    config = load_yaml(path)
    classes = config.get("classes", [])
    return {item["slug"]: item for item in classes}


def load_graph_config(path: str | Path | None = None) -> dict[str, Any]:
    p = Path(path) if path else CONFIG_DIR / "graph.yaml"
    return load_yaml(p)
