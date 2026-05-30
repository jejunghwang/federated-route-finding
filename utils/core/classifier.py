"""Placeholder classifier used by the legacy ``utils/`` Gradio scaffold."""
from __future__ import annotations

import hashlib

from PIL import Image

from .graph import get_graph


def classify(image: Image.Image) -> tuple[str, float]:
    """Return ``(node_id, confidence)``.

    Deterministic stand-in: hashes the image bytes and picks a node id from the
    canonical graph. Real inference belongs in ``pangpang_pathfinder.models``.
    """
    node_ids = get_graph().node_ids
    h = int(hashlib.md5(image.tobytes()).hexdigest(), 16)
    node_id = node_ids[h % len(node_ids)]
    conf = 0.7 + (h % 30) / 100  # 0.70 ~ 0.99
    return node_id, round(conf, 2)
