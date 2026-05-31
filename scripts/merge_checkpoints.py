#!/usr/bin/env python
from __future__ import annotations

from pathlib import Path

import torch

from pathfinder.config import load_yaml
from pathfinder.fl.merge import merge_state_dicts
from pathfinder.utils.io import ensure_dir, save_json


def main() -> None:
    cfg = load_yaml("configs/federated.yaml")
    weighted_states = []
    meta = None
    report_items = []

    for item in cfg["local_checkpoints"]:
        path = Path(item["checkpoint_path"])
        if not path.exists():
            raise FileNotFoundError(f"Missing checkpoint: {path}")
        ckpt = torch.load(path, map_location="cpu")
        n = int(ckpt.get("num_train_samples", 0))
        if n <= 0:
            raise ValueError(f"Checkpoint missing positive num_train_samples: {path}")
        weighted_states.append((ckpt["model_state_dict"], float(n)))
        report_items.append({"client_id": item["client_id"], "checkpoint": str(path), "weight": n})
        if meta is None:
            meta = {k: ckpt[k] for k in ["model_name", "class_to_idx"]}

    merged_state = merge_state_dicts(weighted_states, include_batchnorm_buffers=bool(cfg.get("include_batchnorm_buffers", True)))

    out_ckpt = Path(cfg["output_checkpoint"])
    ensure_dir(out_ckpt.parent)
    torch.save({"model_state_dict": merged_state, **meta, "client_weights": report_items}, out_ckpt)

    report = {
        "output_checkpoint": str(out_ckpt),
        "num_clients": len(report_items),
        "clients": report_items,
        "include_batchnorm_buffers": bool(cfg.get("include_batchnorm_buffers", True)),
    }
    out_report = Path(cfg["output_report"])
    save_json(out_report, report)
    print(f"Merged checkpoint saved to {out_ckpt}")
    print(f"Report saved to {out_report}")


if __name__ == "__main__":
    main()
