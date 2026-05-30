import torch

from pangpang_pathfinder.models.classifier import build_classifier


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
