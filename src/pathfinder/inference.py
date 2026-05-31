from __future__ import annotations

import torch
from PIL import Image
from torchvision import transforms

from pathfinder.models.classifier import load_checkpoint
from pathfinder.models.factory import build_model


def infer_single_image(
    photo_path: str,
    checkpoint_path: str,
    model_name: str,
    class_to_idx: dict[str, int],
    top_k: int = 3,
) -> dict:
    """사진 1장으로 위치 class를 추론. predict_route.py와 gradio_app.py 공용."""
    idx_to_class = {v: k for k, v in class_to_idx.items()}
    model = build_model({"model": {"name": model_name, "pretrained": False}}, len(class_to_idx))
    ckpt = load_checkpoint(checkpoint_path)
    model.load_state_dict(ckpt["model_state_dict"], strict=True)
    model.eval()

    tfm = transforms.Compose([transforms.Resize((224, 224)), transforms.ToTensor()])
    image = Image.open(photo_path).convert("RGB")
    x = tfm(image).unsqueeze(0)

    with torch.no_grad():
        probs = torch.softmax(model(x), dim=1)
        values, indices = torch.topk(probs, k=min(top_k, probs.shape[1]), dim=1)

    top = [(idx_to_class[i], float(v)) for i, v in zip(indices[0].tolist(), values[0].tolist())]
    return {
        "predicted_class": top[0][0],
        "top3": top,
        "top3_text": "\n".join(f"{slug}: {score:.3f}" for slug, score in top),
    }
