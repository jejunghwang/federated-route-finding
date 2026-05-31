#!/usr/bin/env python
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import torch
from sklearn.metrics import confusion_matrix
from torch import nn
from torch.optim import Adam
from torch.utils.data import DataLoader

from pathfinder.config import load_classes_map, load_yaml
from pathfinder.data.dataset import ManifestImageDataset
from pathfinder.data.transforms import build_transforms
from pathfinder.engine.metrics import compute_metrics
from pathfinder.engine.train import run_epoch
from pathfinder.models.classifier import save_checkpoint
from pathfinder.models.factory import build_model
from pathfinder.utils.io import ensure_dir, save_json
from pathfinder.utils.logging import console
from pathfinder.utils.reproducibility import set_seed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--client-id", required=True)
    parser.add_argument("--train-config", default="configs/train.yaml")
    parser.add_argument("--classes-config", default="configs/classes.yaml")
    parser.add_argument("--clients-config", default="configs/clients.yaml")
    args = parser.parse_args()

    train_cfg = load_yaml(args.train_config)
    classes_map = load_classes_map(args.classes_config)
    clients_cfg = load_yaml(args.clients_config)["clients"]
    client_cfg = clients_cfg[args.client_id]
    set_seed(int(train_cfg["training"]["seed"]))

    class_slugs = list(classes_map.keys())
    class_to_idx = {slug: i for i, slug in enumerate(class_slugs)}

    manifests_dir = Path(train_cfg["paths"]["manifests_dir"])
    train_df = pd.read_csv(manifests_dir / "train.csv")
    val_df = pd.read_csv(manifests_dir / "val.csv")

    allowed = set(client_cfg["class_slugs"])
    train_df = train_df[(train_df.client_id == args.client_id) & (train_df.class_slug.isin(allowed))]
    val_df = val_df[(val_df.client_id == args.client_id) & (val_df.class_slug.isin(allowed))]
    if train_df.empty or val_df.empty:
        raise ValueError("Client has empty train/val data. Check manifests and client class mapping.")

    image_size = int(train_cfg["data"]["image_size"])
    augment_cfg = train_cfg["data"].get("augment", {})
    train_ds = ManifestImageDataset(train_df, class_to_idx, build_transforms(image_size, True, augment_cfg))
    val_ds = ManifestImageDataset(val_df, class_to_idx, build_transforms(image_size, False, augment_cfg))

    loader_kwargs = {
        "batch_size": int(train_cfg["data"]["batch_size"]),
        "num_workers": int(train_cfg["data"]["num_workers"]),
        "pin_memory": bool(train_cfg["data"].get("pin_memory", False)),
    }
    train_loader = DataLoader(train_ds, shuffle=True, **loader_kwargs)
    val_loader = DataLoader(val_ds, shuffle=False, **loader_kwargs)

    model = build_model(train_cfg, len(class_slugs))
    device = train_cfg["training"].get("device", "cpu")
    model.to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = Adam(model.parameters(), lr=float(train_cfg["training"]["lr"]), weight_decay=float(train_cfg["training"]["weight_decay"]))

    best_f1 = -1.0
    history = []
    epochs = int(train_cfg["training"]["epochs"])
    ckpt_dir = ensure_dir(train_cfg["paths"]["checkpoints_dir"])
    reports_dir = ensure_dir(train_cfg["paths"]["reports_dir"])

    for epoch in range(1, epochs + 1):
        tr_loss, tr_y, tr_p = run_epoch(model, train_loader, criterion, optimizer, device)
        va_loss, va_y, va_p = run_epoch(model, val_loader, criterion, optimizer=None, device=device)
        va_metrics = compute_metrics(va_y, va_p, len(class_slugs))
        row = {
            "epoch": epoch,
            "train_loss": tr_loss,
            "val_loss": va_loss,
            "val_macro_f1": va_metrics["macro_f1"],
            "val_acc": va_metrics["top1_accuracy"],
        }
        history.append(row)
        console.print(f"[cyan]epoch {epoch}[/cyan] {row}")

        payload = {
            "model_name": train_cfg["model"]["name"],
            "class_to_idx": class_to_idx,
            "client_id": args.client_id,
            "num_train_samples": len(train_ds),
            "epoch": epoch,
        }
        save_checkpoint(str(ckpt_dir / f"{args.client_id}_last.pt"), model, payload)
        if va_metrics["macro_f1"] > best_f1:
            best_f1 = va_metrics["macro_f1"]
            save_checkpoint(str(ckpt_dir / f"{args.client_id}_best.pt"), model, payload)
            cm = confusion_matrix(va_y, va_p, labels=list(range(len(class_slugs))))
            pd.DataFrame(cm).to_csv(reports_dir / f"{args.client_id}_confusion_matrix.csv", index=False)

    save_json(reports_dir / f"{args.client_id}_metrics.json", {"history": history, "best_val_macro_f1": best_f1})
    console.print(f"[green]Done[/green] client={args.client_id} best_f1={best_f1:.4f}")


if __name__ == "__main__":
    main()
