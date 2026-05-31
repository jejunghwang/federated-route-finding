from __future__ import annotations

from pathlib import Path

from PIL import Image
import torch
from torch.utils.data import Dataset


class ManifestImageDataset(Dataset):
    def __init__(self, df, class_to_idx: dict[str, int], transform=None):
        self.df = df.reset_index(drop=True)
        self.class_to_idx = class_to_idx
        self.transform = transform

    def __len__(self) -> int:
        return len(self.df)

    def __getitem__(self, idx: int):
        row = self.df.iloc[idx]
        image = Image.open(Path(row.image_path)).convert("RGB")
        if self.transform:
            image = self.transform(image)
        label = self.class_to_idx[row.class_slug]
        return image, torch.tensor(label, dtype=torch.long), row.class_slug
