from __future__ import annotations

from pathlib import Path

import gradio as gr
import torch
from PIL import Image
from torchvision import transforms

from pangpang_pathfinder.config import (
    load_classes_map,
    load_graph_config,
)
from pangpang_pathfinder.models.classifier import load_checkpoint
from pangpang_pathfinder.models.factory import build_model
from pangpang_pathfinder.route.graph import CampusGraph, validate_classes_subset
from pangpang_pathfinder.route.planner import plan_route
from pangpang_pathfinder.route.stitching import stitch_clips


def _infer_single_image(
    photo_path: str,
    checkpoint_path: str,
    model_name: str,
    class_to_idx: dict[str, int],
) -> dict:
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


def _predict_node_id_dummy(graph: CampusGraph, _photo_path: str) -> tuple[str, float]:
    # TODO: hook this into the trained classifier when no checkpoint is available.
    return graph.node_ids[0], 0.0


def _format_route_md(graph: CampusGraph, node_ids: list[str]) -> str:
    if not node_ids:
        return "**경로 없음**"
    return "**경로**\n\n" + " → ".join(graph.get_node(i).name for i in node_ids)


def create_app(checkpoint_path: str = "outputs/checkpoints/global_merged.pt"):
    graph = CampusGraph.from_config(load_graph_config())
    class_map = load_classes_map("configs/classes.yaml")
    class_slugs = list(class_map.keys())
    validate_classes_subset(graph, class_slugs)

    has_checkpoint = Path(checkpoint_path).exists()
    if has_checkpoint:
        ckpt = load_checkpoint(checkpoint_path)
        model_name = ckpt["model_name"]
        class_to_idx = ckpt["class_to_idx"]
    else:
        model_name = "resnet18"
        class_to_idx = {slug: i for i, slug in enumerate(class_slugs)}

    def _predict(photo_path: str) -> tuple[str, float, str]:
        if has_checkpoint:
            res = _infer_single_image(photo_path, checkpoint_path, model_name, class_to_idx)
            return res["predicted_class"], float(res["top3"][0][1]), res["top3_text"]
        node_id, conf = _predict_node_id_dummy(graph, photo_path)
        return node_id, conf, f"{node_id}: {conf:.3f}"

    def newbie_route(current_photo, destination_name):
        if current_photo is None:
            return "현재 위치 사진을 업로드해주세요.", "", "", "", None
        if not destination_name:
            return "목적지를 선택해주세요.", "", "", "", None

        cur_id, cur_conf, top3_text = _predict(current_photo)
        goal_id = graph.id_by_name(destination_name)
        route = plan_route(graph, cur_id, goal_id)
        cur_name = graph.get_node(cur_id).name
        clip = stitch_clips(route.edges) if not route.is_empty else None

        return (
            top3_text,
            f"{cur_name} ({cur_id}) · {cur_conf:.2f}",
            _format_route_md(graph, route.nodes),
            "" if clip is None else clip,
            clip,
        )

    def find_peer(current_photo, peer_photo):
        if current_photo is None or peer_photo is None:
            return "두 장의 사진이 모두 필요합니다.", "", "", "", None

        cur_id, cur_conf, top3_text = _predict(current_photo)
        peer_id, peer_conf, _ = _predict(peer_photo)
        route = plan_route(graph, cur_id, peer_id)
        cur_name = graph.get_node(cur_id).name
        peer_name = graph.get_node(peer_id).name
        clip = stitch_clips(route.edges) if not route.is_empty else None

        return (
            top3_text,
            f"현재: {cur_name} ({cur_conf:.2f}) / 상대: {peer_name} ({peer_conf:.2f})",
            _format_route_md(graph, route.nodes),
            "" if clip is None else clip,
            clip,
        )

    with gr.Blocks(title="Campus PathFinder") as demo:
        gr.Markdown("# Campus PathFinder\n사진 기반 캠퍼스 길찾기 데모")
        with gr.Tab("신입생 길찾기"):
            cur = gr.Image(type="filepath", label="현재 위치 사진")
            dst = gr.Dropdown(choices=graph.node_names, label="목적지")
            btn = gr.Button("길 안내 시작")
            top3 = gr.Textbox(label="Top-3 예측")
            pred = gr.Textbox(label="예측 위치")
            path = gr.Markdown(label="노드 경로")
            clips = gr.Textbox(label="안내 영상 경로")
            video = gr.Video(label="합쳐진 안내 영상")
            btn.click(newbie_route, inputs=[cur, dst], outputs=[top3, pred, path, clips, video])

        with gr.Tab("A가 B를 찾기"):
            cur2 = gr.Image(type="filepath", label="A의 현재 사진")
            peer = gr.Image(type="filepath", label="B의 현재 사진")
            btn2 = gr.Button("A에서 B로 경로 찾기")
            top3_2 = gr.Textbox(label="A Top-3 예측")
            pred2 = gr.Textbox(label="A/B 예측 요약")
            path2 = gr.Markdown(label="노드 경로")
            clips2 = gr.Textbox(label="안내 영상 경로")
            video2 = gr.Video(label="합쳐진 안내 영상")
            btn2.click(find_peer, inputs=[cur2, peer], outputs=[top3_2, pred2, path2, clips2, video2])
    return demo
