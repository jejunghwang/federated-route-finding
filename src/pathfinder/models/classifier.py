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
    if name == "vit_b_16":
        model = models.vit_b_16(weights=weights)
        in_features = model.heads.head.in_features
        model.heads.head = nn.Linear(in_features, num_classes)
        return model
    if name == "mobilenet_v3_small":
        model = models.mobilenet_v3_small(weights=weights)
        in_features = model.classifier[-1].in_features
        model.classifier[-1] = nn.Linear(in_features, num_classes)
        return model
    raise ValueError(f"Unsupported model: {name}")


class EnsembleClassifier(nn.Module):
    """
    Evaluates multiple base models in parallel.
    Uses masks to ignore unlearned classes per model.
    """

    def __init__(self, models: nn.ModuleList, masks: list[torch.Tensor] | None = None):
        super().__init__()
        self.models = models
        self.masks = masks

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        probs_list = []
        for i, model in enumerate(self.models):
            logits = model(x)
            if self.masks is not None:
                mask = self.masks[i].to(logits.device)
                logits = logits.masked_fill(~mask, float("-inf"))
            # Convert to probabilities within this model's domain
            probs = torch.softmax(logits, dim=1)
            probs_list.append(probs)

        # Average the probabilities across all models
        stacked = torch.stack(probs_list, dim=0)
        avg_probs = torch.mean(stacked, dim=0)

        # Return log(probs) so that when the test script applies softmax,
        # it recovers the exact avg_probs (since sum(avg_probs) = 1).
        return torch.log(avg_probs + 1e-8)


def build_model_from_checkpoint(ckpt: dict) -> nn.Module:
    class_to_idx = ckpt.get("class_to_idx")
    if not isinstance(class_to_idx, dict) or not class_to_idx:
        raise ValueError("Invalid checkpoint: missing non-empty class_to_idx")

    model_name = ckpt.get("model_name")
    num_classes = len(class_to_idx)
    if model_name == "ensemble":
        base_name = ckpt.get("ensemble_base_model")
        num_models = int(ckpt.get("num_models", 0))
        if not isinstance(base_name, str) or num_models <= 0:
            raise ValueError("Invalid ensemble checkpoint metadata")

        models = nn.ModuleList(
            [build_classifier(base_name, num_classes, pretrained=False) for _ in range(num_models)]
        )
        raw_masks = ckpt.get("masks")
        masks = None
        if raw_masks is not None:
            if len(raw_masks) != num_models:
                raise ValueError("Invalid ensemble checkpoint: masks length mismatch")
            masks = [torch.tensor(mask, dtype=torch.bool) for mask in raw_masks]
        return EnsembleClassifier(models, masks)

    if not isinstance(model_name, str):
        raise ValueError("Invalid checkpoint: missing model_name")
    return build_classifier(model_name, num_classes, pretrained=False)


def save_checkpoint(path: str, model: nn.Module, payload: dict) -> None:
    state = {"model_state_dict": model.state_dict(), **payload}
    torch.save(state, path)


def load_checkpoint(path: str, map_location: str = "cpu") -> dict:
    ckpt = torch.load(path, map_location=map_location)
    if "model_state_dict" not in ckpt:
        raise ValueError("Invalid checkpoint: missing model_state_dict")
    return ckpt
