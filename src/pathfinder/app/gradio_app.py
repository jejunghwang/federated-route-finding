from __future__ import annotations

import hashlib
from pathlib import Path

import gradio as gr

from pathfinder.config import (
    load_classes_map,
    load_graph_config,
)
from pathfinder.inference import infer_single_image
from pathfinder.models.classifier import load_checkpoint
from pathfinder.route.graph import CampusGraph, validate_classes_subset
from pathfinder.route.planner import Route, plan_route
from pathfinder.route.stitching import _resolve_clip_for_edge, stitch_clips

PROJECT_ROOT = Path(__file__).resolve().parents[3]
ROUTE_CLIPS_DIR = PROJECT_ROOT / "data" / "route_clips"
STITCHED_OUTPUT = ROUTE_CLIPS_DIR / "_stitched" / "route.mp4"


def _predict_node_id_dummy(graph: CampusGraph, photo_path: str) -> tuple[str, float]:
    """checkpoint가 없을 때의 결정적 더미.

    이미지 바이트를 해시해 노드를 고른다. 학습된 모델이 생기면 ``_infer_single_image``로
    대체됨. (모델 없이도 데모가 여러 노드를 보여주도록)
    """
    node_ids = graph.node_ids
    h = int(hashlib.md5(Path(photo_path).read_bytes()).hexdigest(), 16)
    node_id = node_ids[h % len(node_ids)]
    conf = 0.7 + (h % 30) / 100  # 0.70 ~ 0.99
    return node_id, round(conf, 2)


def _build_route_output(graph: CampusGraph, route: Route) -> tuple[str, str | None]:
    """경로를 (구간별 안내 markdown, 이어붙인 영상 경로)로 변환.

    경로(노드 순서)는 항상 표시하고, 구간별로 영상 유무를 보여준다.
    영상이 있는 구간만 이어붙이며, 없는 구간은 건너뛰고 로그/화면에 표시.
    """
    if route.is_empty:
        print("[경로] 연결 경로 없음")
        return "**경로 없음** — 두 노드가 연결되어 있지 않습니다.", None

    node_line = " → ".join(graph.get_node(i).name for i in route.nodes)
    print(f"[경로] {node_line}")

    seg_lines = []
    for idx, edge in enumerate(route.edges, 1):
        a = graph.get_node(edge.a).name
        b = graph.get_node(edge.b).name
        clip = _resolve_clip_for_edge(edge, ROUTE_CLIPS_DIR)
        if clip is not None:
            seg_lines.append(f"{idx}. {a} → {b} — ▶ 영상 재생")
            print(f"  [{idx}] {a} → {b} : {clip}")
        else:
            seg_lines.append(f"{idx}. {a} → {b} — ⚠ 영상 없음 (건너뜀)")
            print(f"  [{idx}] {a} → {b} : (영상 없음, 건너뜀)")

    video = stitch_clips(route.edges, clips_dir=ROUTE_CLIPS_DIR, output_path=STITCHED_OUTPUT)
    if video is None:
        print("  재생할 영상이 하나도 없습니다 (경로만 표시).")

    path_md = (
        f"**경로**\n\n{node_line}\n\n"
        "**구간별 안내 영상**\n\n" + "\n".join(seg_lines)
    )
    return path_md, video


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
            res = infer_single_image(photo_path, checkpoint_path, model_name, class_to_idx)
            return res["predicted_class"], float(res["top3"][0][1]), res["top3_text"]
        node_id, conf = _predict_node_id_dummy(graph, photo_path)
        return node_id, conf, f"{node_id}: {conf:.3f} (dummy — checkpoint 없음)"

    def newbie_route(current_photo, destination_name):
        if current_photo is None:
            return "현재 위치 사진을 업로드해주세요.", "", "", "", None
        if not destination_name:
            return "목적지를 선택해주세요.", "", "", "", None

        cur_id, cur_conf, top3_text = _predict(current_photo)
        goal_id = graph.id_by_name(destination_name)
        route = plan_route(graph, cur_id, goal_id)
        cur_name = graph.get_node(cur_id).name
        path_md, video = _build_route_output(graph, route)

        return (
            top3_text,
            f"{cur_name} ({cur_id}) · {cur_conf:.2f}",
            path_md,
            "" if video is None else video,
            video,
        )

    def find_peer(current_photo, peer_photo):
        if current_photo is None or peer_photo is None:
            return "두 장의 사진이 모두 필요합니다.", "", "", "", None

        cur_id, cur_conf, top3_text = _predict(current_photo)
        peer_id, peer_conf, _ = _predict(peer_photo)
        route = plan_route(graph, cur_id, peer_id)
        cur_name = graph.get_node(cur_id).name
        peer_name = graph.get_node(peer_id).name
        path_md, video = _build_route_output(graph, route)

        return (
            top3_text,
            f"현재: {cur_name} ({cur_conf:.2f}) / 상대: {peer_name} ({peer_conf:.2f})",
            path_md,
            "" if video is None else video,
            video,
        )

    with gr.Blocks(title="Campus PathFinder") as demo:
        gr.Markdown("# Campus PathFinder\n사진 기반 캠퍼스 길찾기 데모")
        with gr.Tab("신입생 길찾기"):
            cur = gr.Image(type="filepath", label="현재 위치 사진")
            dst = gr.Dropdown(choices=graph.node_names, label="목적지")
            btn = gr.Button("길 안내 시작")
            top3 = gr.Textbox(label="Top-3 예측")
            pred = gr.Textbox(label="예측 위치")
            path = gr.Markdown(label="경로 / 구간별 안내 영상")
            clips = gr.Textbox(label="이어붙인 영상 경로")
            video = gr.Video(label="합쳐진 안내 영상")
            btn.click(newbie_route, inputs=[cur, dst], outputs=[top3, pred, path, clips, video])

        with gr.Tab("A가 B를 찾기"):
            cur2 = gr.Image(type="filepath", label="A의 현재 사진")
            peer = gr.Image(type="filepath", label="B의 현재 사진")
            btn2 = gr.Button("A에서 B로 경로 찾기")
            top3_2 = gr.Textbox(label="A Top-3 예측")
            pred2 = gr.Textbox(label="A/B 예측 요약")
            path2 = gr.Markdown(label="경로 / 구간별 안내 영상")
            clips2 = gr.Textbox(label="이어붙인 영상 경로")
            video2 = gr.Video(label="합쳐진 안내 영상")
            btn2.click(find_peer, inputs=[cur2, peer], outputs=[top3_2, pred2, path2, clips2, video2])
    return demo
