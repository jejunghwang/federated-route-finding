from __future__ import annotations

from pathlib import Path

import gradio as gr

from pangpang_pathfinder.config import load_classes_map, load_yaml
from pangpang_pathfinder.models.classifier import load_checkpoint
from pangpang_pathfinder.models.factory import build_model
from pangpang_pathfinder.route.graph import build_graph
from pangpang_pathfinder.route.planner import plan_route
from torchvision import transforms
from PIL import Image
import torch


def _infer_single_image(photo_path: str, checkpoint_path: str, model_name: str, class_to_idx: dict[str, int]) -> dict:
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
        "top3_text": "\n".join([f"{slug}: {score:.3f}" for slug, score in top3]),
    }


def create_app(checkpoint_path: str = "outputs/checkpoints/global_merged.pt"):
    class_map = load_classes_map("configs/classes.yaml")
    class_slugs = list(class_map.keys())
    graph = build_graph(load_yaml("configs/graph.yaml"))

    if Path(checkpoint_path).exists():
        ckpt = load_checkpoint(checkpoint_path)
        model_name = ckpt["model_name"]
        class_to_idx = ckpt["class_to_idx"]
    else:
        model_name = "resnet18"
        class_to_idx = {slug: i for i, slug in enumerate(class_slugs)}

    def newbie_route(current_photo, destination_class):
        result = _infer_single_image(current_photo, checkpoint_path, model_name, class_to_idx)
        route = plan_route(graph, result["predicted_class"], destination_class)
        predicted_ko = class_map[result["predicted_class"]]["display_name_ko"]
        return (
            result["top3_text"],
            f"{predicted_ko} ({result['predicted_class']})",
            " -> ".join(route["node_path"]),
            "\n".join(route["clips"]) if route["clips"] else "클립 없음",
            None,
        )

    def find_peer(current_photo, peer_photo):
        mine = _infer_single_image(current_photo, checkpoint_path, model_name, class_to_idx)
        peer = _infer_single_image(peer_photo, checkpoint_path, model_name, class_to_idx)
        route = plan_route(graph, mine["predicted_class"], peer["predicted_class"])
        predicted_ko = class_map[mine["predicted_class"]]["display_name_ko"]
        peer_ko = class_map[peer["predicted_class"]]["display_name_ko"]
        return (
            mine["top3_text"],
            f"현재: {predicted_ko} / 상대: {peer_ko}",
            " -> ".join(route["node_path"]),
            "\n".join(route["clips"]) if route["clips"] else "클립 없음",
            None,
        )

    with gr.Blocks(title="PangPang PathFinder") as demo:
        gr.Markdown("# 🐼 PangPang PathFinder\n사진 기반 길찾기 데모")
        with gr.Tab("신입생 길찾기"):
            cur = gr.Image(type="filepath", label="현재 위치 사진")
            dst = gr.Dropdown(choices=class_slugs, label="목적지 클래스")
            btn = gr.Button("길 안내 시작")
            top3 = gr.Textbox(label="Top-3 예측")
            pred = gr.Textbox(label="예측 위치")
            path = gr.Textbox(label="노드 경로")
            clips = gr.Textbox(label="클립 순서")
            video = gr.Video(label="합쳐진 안내 영상")
            btn.click(newbie_route, inputs=[cur, dst], outputs=[top3, pred, path, clips, video])

        with gr.Tab("A가 B를 찾기"):
            cur2 = gr.Image(type="filepath", label="A의 현재 사진")
            peer = gr.Image(type="filepath", label="B의 현재 사진")
            btn2 = gr.Button("A에서 B로 경로 찾기")
            top3_2 = gr.Textbox(label="A Top-3 예측")
            pred2 = gr.Textbox(label="A/B 예측 요약")
            path2 = gr.Textbox(label="노드 경로")
            clips2 = gr.Textbox(label="클립 순서")
            video2 = gr.Video(label="합쳐진 안내 영상")
            btn2.click(find_peer, inputs=[cur2, peer], outputs=[top3_2, pred2, path2, clips2, video2])
    return demo
