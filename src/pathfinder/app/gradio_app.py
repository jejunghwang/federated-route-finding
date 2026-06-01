from __future__ import annotations

import hashlib
from pathlib import Path

import gradio as gr

from pathfinder.config import (
    load_classes_map,
    load_graph_config,
)
from pathfinder.route.graph import CampusGraph, validate_classes_subset
from pathfinder.route.planner import Route, plan_route
from pathfinder.app.simple_demo import (
    INDOOR_TARGETS,
    PROCESSED_OUTPUT,
    _build_dest_choices,
    _resolve_indoor_chain,
    _stitch_with_filter,
)

INDOOR_TO_OUTDOOR: dict[str, str] = {indoor: outdoor for outdoor, indoor, _ in INDOOR_TARGETS}
INDOOR_DISPLAY_NAME: dict[str, str] = {indoor: name for _, indoor, name in INDOOR_TARGETS}
from pathfinder.route.stitching import resolve_clips

PROJECT_ROOT = Path(__file__).resolve().parents[3]
ROUTE_CLIPS_DIR = PROJECT_ROOT / "data" / "route_clips"


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


def _build_route_output(
    graph: CampusGraph,
    route: Route,
    indoor_clips: list[Path] | None = None,
    indoor_display: str | None = None,
) -> tuple[str, str | None]:
    """경로를 (안내 markdown, 합쳐진 영상 경로)로 변환.

    영상은 concat filter로 해상도/fps 정규화 후 음소거 + 4배속 재인코딩.
    indoor_clips가 있으면 outdoor 경로 영상 뒤에 순서대로 이어붙임.
    """
    indoor_clips = indoor_clips or []
    if route.is_empty and not indoor_clips:
        return "**경로 없음** — 두 노드가 연결되어 있지 않습니다.", None

    if route.is_empty:
        node_line = indoor_display or "(실내)"
    else:
        node_line = " → ".join(graph.get_node(i).name for i in route.nodes)
        if indoor_display:
            node_line += f" → {indoor_display}"

    clip_paths, _missing = resolve_clips(route.edges, ROUTE_CLIPS_DIR)
    clip_paths.extend(str(p) for p in indoor_clips)
    video = _stitch_with_filter(clip_paths, PROCESSED_OUTPUT, speed_x=4.0)
    path_md = f"**경로** (음소거 · 4배속)\n\n{node_line}"
    return path_md, video


def create_app(checkpoint_path: str = "outputs/checkpoints/global_merged.pt"):
    graph = CampusGraph.from_config(load_graph_config())
    class_map = load_classes_map("configs/classes.yaml")
    class_slugs = list(class_map.keys())
    validate_classes_subset(graph, class_slugs)

    has_checkpoint = Path(checkpoint_path).exists()
    if has_checkpoint:
        from pathfinder.inference import infer_single_image
        from pathfinder.models.classifier import load_checkpoint

        ckpt = load_checkpoint(checkpoint_path)
        model_name = ckpt["model_name"]
        class_to_idx = ckpt["class_to_idx"]
    else:
        infer_single_image = None
        model_name = "resnet18"
        class_to_idx = {slug: i for i, slug in enumerate(class_slugs)}

    def _predict(photo_path: str) -> tuple[str, float, str]:
        if has_checkpoint:
            res = infer_single_image(photo_path, checkpoint_path, model_name, class_to_idx)
            return res["predicted_class"], float(res["top3"][0][1]), res["top3_text"]
        node_id, conf = _predict_node_id_dummy(graph, photo_path)
        return node_id, conf, f"{node_id}: {conf:.3f} (dummy — checkpoint 없음)"

    node_names_by_id = {nid: graph.get_node(nid).name for nid in graph.node_ids}
    dest_choices, label_meta = _build_dest_choices(node_names_by_id)

    def newbie_route(current_photo, dest_label):
        if current_photo is None:
            return "현재 위치 사진을 업로드해주세요.", "", "", "", None
        if not dest_label:
            return "목적지를 선택해주세요.", "", "", "", None

        meta = label_meta.get(dest_label)
        if meta is None:
            return f"목적지 라벨을 찾을 수 없습니다: {dest_label}", "", "", "", None

        cur_id, cur_conf, top3_text = _predict(current_photo)
        goal_outdoor = meta["outdoor"]
        indoor_slug = meta["indoor"]

        cur_outdoor = INDOOR_TO_OUTDOOR.get(cur_id, cur_id)
        cur_indoor_name = INDOOR_DISPLAY_NAME.get(cur_id)
        cur_outdoor_name = graph.get_node(cur_outdoor).name
        cur_name = (
            f"{cur_outdoor_name} · {cur_indoor_name}" if cur_indoor_name else cur_outdoor_name
        )

        route = plan_route(graph, cur_outdoor, goal_outdoor)

        indoor_clips: list[Path] = []
        indoor_display = None
        if indoor_slug is not None:
            indoor_clips = _resolve_indoor_chain(goal_outdoor, indoor_slug)
            indoor_display = dest_label.strip(" └")

        path_md, video = _build_route_output(graph, route, indoor_clips, indoor_display)

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
        cur_outdoor = INDOOR_TO_OUTDOOR.get(cur_id, cur_id)
        peer_outdoor = INDOOR_TO_OUTDOOR.get(peer_id, peer_id)
        route = plan_route(graph, cur_outdoor, peer_outdoor)
        cur_name = graph.get_node(cur_outdoor).name
        peer_name = graph.get_node(peer_outdoor).name
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
            dst = gr.Dropdown(choices=dest_choices, label="목적지 (야외 + 실내)")
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
