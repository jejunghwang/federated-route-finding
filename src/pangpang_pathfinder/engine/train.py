from __future__ import annotations

import torch
from tqdm import tqdm


def run_epoch(model, loader, criterion, optimizer=None, device="cpu"):
    train_mode = optimizer is not None
    model.train(train_mode)
    total_loss = 0.0
    y_true, y_pred = [], []
    for images, labels, _ in tqdm(loader, leave=False):
        images = images.to(device)
        labels = labels.to(device)
        logits = model(images)
        loss = criterion(logits, labels)

        if train_mode:
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        total_loss += float(loss.item()) * labels.size(0)
        preds = logits.argmax(dim=1)
        y_true.extend(labels.cpu().tolist())
        y_pred.extend(preds.cpu().tolist())

    avg_loss = total_loss / max(len(loader.dataset), 1)
    return avg_loss, y_true, y_pred
