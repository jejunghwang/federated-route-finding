from __future__ import annotations

from pangpang_pathfinder.models.classifier import build_classifier


def build_model(train_cfg: dict, num_classes: int):
    model_cfg = train_cfg["model"]
    return build_classifier(
        name=model_cfg["name"],
        num_classes=num_classes,
        pretrained=model_cfg.get("pretrained", False),
    )
