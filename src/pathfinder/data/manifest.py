from __future__ import annotations

from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = ["class_slug", "session_name", "image_path", "split"]


def load_manifest(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns in manifest: {missing}")
    return df
