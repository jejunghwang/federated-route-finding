from __future__ import annotations

from torchvision import transforms


def build_transforms(image_size: int, train: bool, augment: dict) -> transforms.Compose:
    ops = [transforms.Resize((image_size, image_size))]
    if train and augment.get("horizontal_flip", False):
        ops.append(transforms.RandomHorizontalFlip())
    if train and augment.get("color_jitter", False):
        ops.append(transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2))
    ops.extend([transforms.ToTensor()])
    return transforms.Compose(ops)
