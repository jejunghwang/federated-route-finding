from __future__ import annotations

import torch
import torch.nn as nn
from torchvision import models


def build_classifier(name: str, num_classes: int, pretrained: bool = False) -> nn.Module:
    weights = "DEFAULT" if pretrained else None
    if name == "resnet18":
        model = models.resnet18(weights=weights)
        model.fc = nn.Linear(model.fc.in_features, num_classes)
        return model
    if name == "mobilenet_v3_small":
        model = models.mobilenet_v3_small(weights=weights)
        in_features = model.classifier[-1].in_features
        model.classifier[-1] = nn.Linear(in_features, num_classes)
        return model
    raise ValueError(f"Unsupported model: {name}")


def save_checkpoint(path: str, model: nn.Module, payload: dict) -> None:
    state = {"model_state_dict": model.state_dict(), **payload}
    torch.save(state, path)


def load_checkpoint(path: str, map_location: str = "cpu") -> dict:
    ckpt = torch.load(path, map_location=map_location)
    if "model_state_dict" not in ckpt:
        raise ValueError("Invalid checkpoint: missing model_state_dict")
    return ckpt
