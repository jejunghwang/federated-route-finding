#!/usr/bin/env python
from __future__ import annotations

from pathlib import Path

import pandas as pd
import torch
from torch.utils.data import DataLoader

from pathfinder.config import load_classes_map, load_yaml
from pathfinder.data.dataset import ManifestImageDataset
from pathfinder.data.transforms import build_transforms
from pathfinder.engine.metrics import compute_metrics
from pathfinder.models.classifier import load_checkpoint
from pathfinder.models.factory import build_model
from pathfinder.utils.io import save_json


def main() -> None:
    train_cfg = load_yaml("configs/train.yaml")
    classes_map = load_classes_map("configs/classes.yaml")
    class_slugs = list(classes_map.keys())

    test_df = pd.read_csv(Path(train_cfg["paths"]["manifests_dir"]) / "test.csv")
    class_to_idx = {slug: i for i, slug in enumerate(class_slugs)}
    ds = ManifestImageDataset(
        test_df,
        class_to_idx,
        transform=build_transforms(int(train_cfg["data"]["image_size"]), train=False, augment={}),
    )
    loader = DataLoader(ds, batch_size=int(train_cfg["data"]["batch_size"]), shuffle=False)

    ckpt = load_checkpoint("outputs/checkpoints/global_merged.pt")
    model = build_model({"model": {"name": ckpt["model_name"], "pretrained": False}}, len(class_slugs))
    model.load_state_dict(ckpt["model_state_dict"], strict=True)
    model.eval()

    y_true, y_pred = [], []
    with torch.no_grad():
        for images, labels, _ in loader:
            logits = model(images)
            preds = logits.argmax(dim=1)
            y_true.extend(labels.tolist())
            y_pred.extend(preds.tolist())

    metrics = compute_metrics(y_true, y_pred, len(class_slugs))
    per_class = pd.DataFrame(
        {
            "class_slug": class_slugs,
            "per_class_accuracy": metrics["per_class_accuracy"],
        }
    )
    out_csv = Path("outputs/reports/global_eval_per_class.csv")
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    per_class.to_csv(out_csv, index=False)
    save_json(
        "outputs/reports/global_eval_summary.json",
        {
            "top1_accuracy": metrics["top1_accuracy"],
            "macro_f1": metrics["macro_f1"],
            "per_class_csv": str(out_csv),
        },
    )
    print("Saved global evaluation reports")


if __name__ == "__main__":
    main()
