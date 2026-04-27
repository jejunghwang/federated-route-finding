"""Scene A/B 공통 파이프라인 — 분류 → shortest path → 영상 stitching."""
from PIL import Image

from core import classify, shortest_path, stitch_clips


def run_pipeline(current_img, goal_input):
    """goal_input은 PIL.Image (Scene A) 또는 str (Scene B)."""
    if current_img is None:
        return "현재 위치 사진을 업로드해주세요.", "", None
    if goal_input is None or (isinstance(goal_input, str) and not goal_input.strip()):
        return "목적지를 지정해주세요.", "", None

    cur_node, cur_conf = classify(current_img)
    if isinstance(goal_input, str):
        goal_node, goal_conf = goal_input, 1.0
    else:
        goal_node, goal_conf = classify(goal_input)
    path = shortest_path(cur_node, goal_node)
    video = stitch_clips(path)

    result_md = (
        f"**현재 위치 (Top-1)**: {cur_node} · {cur_conf:.2f}\n\n"
        f"**목적지 (Top-1)**: {goal_node} · {goal_conf:.2f}"
    )
    path_md = "**경로**\n\n" + " → ".join(path)
    return result_md, path_md, video
