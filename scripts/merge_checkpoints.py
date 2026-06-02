#!/usr/bin/env python
from __future__ import annotations

from pathlib import Path

import torch

from pathfinder.config import load_yaml
from pathfinder.utils.io import ensure_dir, save_json


def main() -> None:
    cfg = load_yaml("configs/federated.yaml")
    clients_cfg = load_yaml("configs/clients.yaml")["clients"]
    weighted_states = []
    client_ids = []
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

        cid = item["client_id"]
        weighted_states.append((float(n), ckpt["model_state_dict"]))
        client_ids.append(cid)

        report_items.append({"client_id": cid, "checkpoint": str(path), "weight": n})
        if meta is None:
            meta = {k: ckpt[k] for k in ["model_name", "class_to_idx"]}

    class_to_idx = meta["class_to_idx"]
    num_classes = len(class_to_idx)
    model_name = meta["model_name"]

    # 1. We skip TSV entirely. Instead, we bundle the state dicts into an ensemble state dict.
    print(f"Bundling {len(weighted_states)} models into EnsembleClassifier...")
    merged_state = {}

    # Bundle states by prefixing with 'models.{i}.'
    for i, (_weight, state) in enumerate(weighted_states):
        for key, tensor in state.items():
            merged_state[f"models.{i}.{key}"] = tensor

    # Calculate masks for each model
    idx_to_class = {v: k for k, v in class_to_idx.items()}
    masks = []
    for cid in client_ids:
        allowed_slugs = clients_cfg.get(cid, {}).get("class_slugs", [])
        mask = [idx_to_class[i] in allowed_slugs for i in range(num_classes)]
        masks.append(mask)

    # Update meta to denote this is an ensemble
    meta["model_name"] = "ensemble"
    meta["ensemble_base_model"] = model_name
    meta["num_models"] = len(weighted_states)
    meta["masks"] = masks

    out_ckpt = Path(cfg["output_checkpoint"])
    ensure_dir(out_ckpt.parent)
    torch.save({"model_state_dict": merged_state, **meta, "client_weights": report_items}, out_ckpt)

    report = {
        "output_checkpoint": str(out_ckpt),
        "num_clients": len(report_items),
        "clients": report_items,
        "ensemble_applied": True,
    }
    out_report = Path(cfg["output_report"])
    save_json(out_report, report)
    print(f"Merged checkpoint saved to {out_ckpt}")
    print(f"Report saved to {out_report}")


if __name__ == "__main__":
    main()
