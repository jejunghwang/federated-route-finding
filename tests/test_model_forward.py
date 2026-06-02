import torch

from pathfinder.models.classifier import (
    EnsembleClassifier,
    build_classifier,
    build_model_from_checkpoint,
)


def test_resnet18_forward_shape():
    model = build_classifier("resnet18", num_classes=15, pretrained=False)
    x = torch.randn(2, 3, 224, 224)
    y = model(x)
    assert y.shape == (2, 15)


def test_mobilenet_forward_shape():
    model = build_classifier("mobilenet_v3_small", num_classes=15, pretrained=False)
    x = torch.randn(2, 3, 224, 224)
    y = model(x)
    assert y.shape == (2, 15)


def test_build_model_from_ensemble_checkpoint_metadata():
    ckpt = {
        "model_name": "ensemble",
        "ensemble_base_model": "mobilenet_v3_small",
        "num_models": 2,
        "class_to_idx": {"a": 0, "b": 1},
        "masks": [[True, False], [False, True]],
    }

    model = build_model_from_checkpoint(ckpt)

    assert isinstance(model, EnsembleClassifier)
    assert len(model.models) == 2
