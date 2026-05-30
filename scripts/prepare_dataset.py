#!/usr/bin/env python
from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path

import pandas as pd

from pangpang_pathfinder.config import load_classes_map, load_yaml
from pangpang_pathfinder.utils.io import ensure_dir


def split_sessions(sessions: list[str]) -> dict[str, set[str]]:
    sessions = sorted(set(sessions))
    n = len(sessions)
    if n < 3:
        raise ValueError(f"Need at least 3 sessions, got {n}: {sessions}")
    n_train = max(1, int(round(n * 0.6)))
    n_val = max(1, int(round(n * 0.2)))
    if n_train + n_val >= n:
        n_val = 1
    train = set(sessions[:n_train])
    val = set(sessions[n_train : n_train + n_val])
    test = set(sessions[n_train + n_val :])
    if not test:
        test = {sessions[-1]}
        train.discard(sessions[-1])
    return {"train": train, "val": val, "test": test}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-dir", default="data/raw")
    parser.add_argument("--out-dir", default="data/manifests")
    parser.add_argument("--classes-config", default="configs/classes.yaml")
    args = parser.parse_args()

    class_map = load_classes_map(args.classes_config)
    raw_dir = Path(args.raw_dir)
    rows = []
    sessions_per_class = defaultdict(set)

    for client_dir in sorted(p for p in raw_dir.iterdir() if p.is_dir()):
        client_id = client_dir.name
        for class_dir in sorted(p for p in client_dir.iterdir() if p.is_dir()):
            class_slug = class_dir.name
            if class_slug not in class_map:
                raise ValueError(f"Unknown class slug in raw data: {class_slug}")
            for session_dir in sorted(p for p in class_dir.iterdir() if p.is_dir()):
                session_name = session_dir.name
                sessions_per_class[class_slug].add(session_name)
                for img_path in sorted(session_dir.glob("*.jpg")):
                    rows.append(
                        {
                            "client_id": client_id,
                            "class_slug": class_slug,
                            "session_name": session_name,
                            "image_path": str(img_path),
                        }
                    )

    if not rows:
        raise ValueError("No images found under data/raw")

    split_map = {}
    for class_slug, sessions in sessions_per_class.items():
        split_map[class_slug] = split_sessions(list(sessions))

    for row in rows:
        class_slug = row["class_slug"]
        sname = row["session_name"]
        for split, sess_set in split_map[class_slug].items():
            if sname in sess_set:
                row["split"] = split
                break

    df = pd.DataFrame(rows)
    out_dir = ensure_dir(args.out_dir)
    for split in ["train", "val", "test"]:
        split_df = df[df["split"] == split].copy()
        split_df.to_csv(out_dir / f"{split}.csv", index=False)

    print("Class counts by split")
    print(df.groupby(["split", "class_slug"]).size().unstack(fill_value=0))
    print(f"Saved manifests to {out_dir}")


if __name__ == "__main__":
    main()
