#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch
from PIL import Image
from torchvision import transforms

from pangpang_pathfinder.config import load_classes_map, load_yaml
from pangpang_pathfinder.models.classifier import load_checkpoint
from pangpang_pathfinder.models.factory import build_model
from pangpang_pathfinder.route.graph import build_graph
from pangpang_pathfinder.route.planner import plan_route
from pangpang_pathfinder.route.stitching import stitch_clips_ffmpeg


def infer_single_image(photo_path: str, checkpoint_path: str, model_name: str, class_to_idx: dict[str, int]) -> dict:
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
        values, indices = torch.topk(probs, k=min(3, probs.shape[1]), dim=1)

    top3 = [(idx_to_class[i], float(v)) for i, v in zip(indices[0].tolist(), values[0].tolist())]
    return {
        "predicted_class": top3[0][0],
        "top3": top3,
        "top3_text": "\n".join([f"{slug}: {score:.3f}" for slug, score in top3]),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--current-photo", required=True)
    parser.add_argument("--destination-class")
    parser.add_argument("--peer-photo")
    parser.add_argument("--checkpoint", default="outputs/checkpoints/global_merged.pt")
    parser.add_argument("--graph-config", default="configs/graph.yaml")
    args = parser.parse_args()

    classes_map = load_classes_map("configs/classes.yaml")
    ckpt = load_checkpoint(args.checkpoint)
    class_to_idx = ckpt["class_to_idx"]
    model_name = ckpt["model_name"]

    current = infer_single_image(args.current_photo, args.checkpoint, model_name, class_to_idx)
    src = current["predicted_class"]

    if args.peer_photo:
        peer = infer_single_image(args.peer_photo, args.checkpoint, model_name, class_to_idx)
        dst = peer["predicted_class"]
    else:
        if not args.destination_class:
            raise ValueError("Provide --destination-class or --peer-photo")
        dst = args.destination_class

    graph = build_graph(load_yaml(args.graph_config))
    route = plan_route(graph, src, dst)
    stitched, stitch_msg = stitch_clips_ffmpeg(route["clips"], "outputs/reports/stitched_route.mp4")

    payload = {
        "predicted_class": src,
        "predicted_class_ko": classes_map.get(src, {}).get("display_name_ko", src),
        "destination_class": dst,
        "top3_predictions": current["top3"],
        "node_path": route["node_path"],
        "clip_list": route["clips"],
        "missing_clips": route["missing_clips"],
        "stitched_video_path": stitched,
        "stitch_status": stitch_msg,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
