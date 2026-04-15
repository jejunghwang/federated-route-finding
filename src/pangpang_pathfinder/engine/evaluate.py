from __future__ import annotations

import torch


def predict_topk(model, image_tensor, k=3, device="cpu"):
    model.eval()
    with torch.no_grad():
        logits = model(image_tensor.to(device))
        probs = torch.softmax(logits, dim=1)
        values, indices = torch.topk(probs, k=min(k, probs.shape[1]), dim=1)
    return values[0].cpu().tolist(), indices[0].cpu().tolist()
