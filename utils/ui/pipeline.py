"""Shared pipeline used by Scene A and Scene B tabs."""
from __future__ import annotations

from PIL import Image

from core import classify, get_graph, plan_route, stitch_clips


def run_pipeline(current_img, goal_input):
    """``goal_input`` is a PIL.Image (Scene A) or a node-name str (Scene B)."""
    if current_img is None:
        return "현재 위치 사진을 업로드해주세요.", "", None
    if goal_input is None or (isinstance(goal_input, str) and not goal_input.strip()):
        return "목적지를 지정해주세요.", "", None

    graph = get_graph()
    cur_id, cur_conf = classify(current_img)

    if isinstance(goal_input, Image.Image):
        goal_id, goal_conf = classify(goal_input)
    else:
        goal_id, goal_conf = graph.id_by_name(goal_input), 1.0

    route = plan_route(graph, cur_id, goal_id)
    video = stitch_clips(route.edges) if not route.is_empty else None

    cur_name = graph.get_node(cur_id).name
    goal_name = graph.get_node(goal_id).name

    result_md = (
        f"**현재 위치 (Top-1)**: {cur_name} · {cur_conf:.2f}\n\n"
        f"**목적지 (Top-1)**: {goal_name} · {goal_conf:.2f}"
    )
    if route.is_empty:
        path_md = "**경로 없음** — 두 노드가 연결되어 있지 않습니다."
    else:
        path_md = "**경로**\n\n" + " → ".join(graph.get_node(i).name for i in route.nodes)
    return result_md, path_md, video
