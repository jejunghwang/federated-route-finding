from __future__ import annotations

import hashlib
import shutil
import subprocess
from pathlib import Path

import gradio as gr

from pathfinder.config import load_classes_map, load_graph_config
from pathfinder.route.graph import CampusGraph, validate_classes_subset
from pathfinder.route.planner import Route, plan_route
from pathfinder.route.stitching import _resolve_clip_for_edge, resolve_clips

PROJECT_ROOT = Path(__file__).resolve().parents[3]
ROUTE_CLIPS_DIR = PROJECT_ROOT / "data" / "route_clips"
STITCHED_OUTPUT = ROUTE_CLIPS_DIR / "_stitched" / "route.mp4"
PROCESSED_OUTPUT = ROUTE_CLIPS_DIR / "_stitched" / "route_2x_mute.mp4"

# 도착지 전용 indoor 위치 (들어가는 영상만, 나가는 영상 없음)
# (outdoor_slug, indoor_slug, display_name)
INDOOR_TARGETS: list[tuple[str, str, str]] = [
    ("central_library", "central_library_freeroom_1", "제1자유열람실"),
    ("central_library", "central_library_freeroom_3", "제3자유열람실"),
    ("central_library", "central_library_jiphyeonjeon", "집현전"),
    ("central_library", "central_library_310_front", "310호 앞"),
    ("central_library", "central_library_310_back", "310호 뒤"),
    ("central_library", "central_library_301_front", "301호 앞"),
    ("central_library", "central_library_301_back", "301호 뒤"),
    ("central_library", "central_library_4f", "4층"),
    ("saebit", "saebit_1f", "1층"),
    ("saebit", "saebit_2f", "2층"),
    ("saebit", "saebit_3f", "3층"),
    ("saebit", "saebit_8f", "8층"),
    ("saebit", "saebit_elevator", "엘리베이터"),
    ("chambit", "chambit_1f_clock", "1층 시계 앞"),
    ("chambit", "chambit_3f_garden", "3층 야외정원"),
    ("chambit", "chambit_b101", "B101호"),
    ("chambit", "chambit_b1_study", "지하1층 자습"),
    ("chambit", "chambit_smoking", "참빛관 흡연장"),
]


# (outdoor, indoor) → 그 위치로 가기 위해 순서대로 재생할 영상 파일명(.mp4 생략)
# 영상은 route_clips 또는 route_clips/indoor 안에서 탐색됨.
INDOOR_CHAINS: dict[tuple[str, str], list[str]] = {
    ("saebit", "saebit_1f"): ["saebit__1f"],
    ("saebit", "saebit_2f"): ["saebit_1f__2f"],
    ("saebit", "saebit_3f"): ["saebit_1f__3f"],
    ("saebit", "saebit_8f"): ["saebit_1f__8f"],
    ("saebit", "saebit_elevator"): ["saebit_1f__elevator"],
    ("chambit", "chambit_1f_clock"): ["chambit__chambit_1f_clock"],
    ("chambit", "chambit_b101"): ["chambit__chambit_b101"],
    ("chambit", "chambit_3f_garden"): [
        "chambit__chambit_1f_clock",
        "chambit_1f_clock__chambit_3f_garden",
    ],
    ("central_library", "central_library_freeroom_3"): ["main_gate__central_library_freeroom_3"],
    ("central_library", "central_library_jiphyeonjeon"): ["main_gate__central_library_jiphyeonjeon"],
    ("central_library", "central_library_301_front"): ["main_gate__central_library_301_front"],
    ("central_library", "central_library_301_back"): ["main_gate__central_library_301_back"],
    ("central_library", "central_library_freeroom_1"): [
        "main_gate__central_library_jiphyeonjeon",
        "central_library_jiphyeonjeon__central_library_freeroom_1",
    ],
}


def _find_clip(name: str) -> Path | None:
    for folder in (ROUTE_CLIPS_DIR, ROUTE_CLIPS_DIR / "indoor"):
        p = folder / f"{name}.mp4"
        if p.exists():
            return p
    return None


def _resolve_indoor_chain(outdoor_slug: str, indoor_slug: str) -> list[Path]:
    chain = INDOOR_CHAINS.get((outdoor_slug, indoor_slug))
    if chain is not None:
        return [p for name in chain if (p := _find_clip(name)) is not None]
    short = indoor_slug.removeprefix(f"{outdoor_slug}_")
    for name in (f"{outdoor_slug}__{indoor_slug}", f"{outdoor_slug}__{short}"):
        p = _find_clip(name)
        if p is not None:
            return [p]
    return []


def _resolve_indoor_clip(outdoor_slug: str, indoor_slug: str) -> Path | None:
    """단일 클립 호환 헬퍼 — chain의 마지막 영상을 반환 (있으면)."""
    chain = _resolve_indoor_chain(outdoor_slug, indoor_slug)
    return chain[-1] if chain else None


def _build_dest_choices(node_names_by_id: dict[str, str]) -> tuple[list[str], dict[str, dict]]:
    """목적지 드롭다운 옵션 + 라벨→메타 매핑.

    outdoor 노드 바로 아래 그 건물의 indoor 옵션을 들여쓰기로 나열.
    """
    indoor_by_outdoor: dict[str, list[tuple[str, str]]] = {}
    for outdoor_slug, indoor_slug, display in INDOOR_TARGETS:
        indoor_by_outdoor.setdefault(outdoor_slug, []).append((indoor_slug, display))

    choices: list[str] = []
    label_meta: dict[str, dict] = {}

    for outdoor_id, outdoor_name in node_names_by_id.items():
        choices.append(outdoor_name)
        label_meta[outdoor_name] = {"outdoor": outdoor_id, "indoor": None}
        for indoor_slug, display in indoor_by_outdoor.get(outdoor_id, []):
            label = f"    └ {outdoor_name} · {display}"
            choices.append(label)
            label_meta[label] = {"outdoor": outdoor_id, "indoor": indoor_slug}

    return choices, label_meta


def _cache_key(clips: list[str], speed_x: float, target_w: int, target_h: int, target_fps: int) -> str:
    h = hashlib.md5()
    for c in clips:
        h.update(str(c).encode("utf-8"))
        h.update(b"|")
    h.update(f"{speed_x}_{target_w}_{target_h}_{target_fps}".encode())
    return h.hexdigest()[:12]


def _stitch_with_filter(
    clips: list[str],
    output_path: Path,
    speed_x: float = 4.0,
    target_w: int = 854,
    target_h: int = 480,
    target_fps: int = 30,
) -> str | None:
    """concat filter로 해상도/fps 정규화하면서 한 번에 합치고 mute + 가속 적용.

    같은 (clips, speed_x, 해상도, fps) 조합은 hash 기반 캐시 파일로 즉시 반환.
    """
    if not clips:
        return None
    if shutil.which("ffmpeg") is None:
        return clips[0] if clips else None

    output_path.parent.mkdir(parents=True, exist_ok=True)
    key = _cache_key(clips, speed_x, target_w, target_h, target_fps)
    cached = output_path.parent / f"{output_path.stem}_{key}{output_path.suffix}"
    if cached.exists():
        return str(cached)

    cmd: list[str] = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"]
    for c in clips:
        cmd += ["-i", str(c)]

    n = len(clips)
    parts: list[str] = []
    for i in range(n):
        parts.append(
            f"[{i}:v]scale={target_w}:{target_h}:force_original_aspect_ratio=decrease,"
            f"pad={target_w}:{target_h}:(ow-iw)/2:(oh-ih)/2,setsar=1,"
            f"fps={target_fps},format=yuv420p[v{i}]"
        )
    fc = ";".join(parts) + ";"
    fc += "".join(f"[v{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=0[cc]"
    if speed_x != 1.0:
        fc += f";[cc]setpts={1.0 / speed_x}*PTS[out]"
        map_label = "[out]"
    else:
        map_label = "[cc]"

    cmd += [
        "-filter_complex", fc,
        "-map", map_label,
        "-an",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-tune", "fastdecode",
        "-crf", "28",
        "-pix_fmt", "yuv420p",
        "-threads", "0",
        "-movflags", "+faststart",
        str(cached),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("[stitch] ffmpeg 실패:", result.stderr[-600:])
        return clips[0]
    return str(cached)


def _build_route_output(
    graph: CampusGraph,
    route: Route,
    indoor_clips: list[Path],
    indoor_display: str | None,
) -> tuple[str, str | None]:
    if route.is_empty and not indoor_clips:
        return "**경로 없음** — 연결되어 있지 않습니다.", None

    seg_lines: list[str] = []
    if route.is_empty:
        node_line = indoor_display or "(실내)"
    else:
        node_line = " → ".join(graph.get_node(i).name for i in route.nodes)
        if indoor_display:
            node_line += f" → {indoor_display}"
        for idx, edge in enumerate(route.edges, 1):
            a = graph.get_node(edge.a).name
            b = graph.get_node(edge.b).name
            clip = _resolve_clip_for_edge(edge, ROUTE_CLIPS_DIR)
            if clip is not None:
                seg_lines.append(f"{idx}. {a} → {b} — ▶ `{clip.name}`")
            else:
                seg_lines.append(f"{idx}. {a} → {b} — ⚠ 영상 없음 (건너뜀)")

    offset = len(route.edges)
    for j, ic in enumerate(indoor_clips, 1):
        seg_lines.append(f"{offset + j}. (실내) — ▶ `{ic.name}`")

    clip_paths, _missing = resolve_clips(route.edges, ROUTE_CLIPS_DIR)
    clip_paths.extend(str(p) for p in indoor_clips)
    video = _stitch_with_filter(clip_paths, PROCESSED_OUTPUT, speed_x=4.0)
    path_md = (
        f"**경로**\n\n{node_line}\n\n"
        "**구간별 안내 영상** (음소거 · 4배속)\n\n" + "\n".join(seg_lines)
    )
    return path_md, video


def create_simple_app():
    graph = CampusGraph.from_config(load_graph_config())
    class_map = load_classes_map(PROJECT_ROOT / "configs" / "classes.yaml")
    validate_classes_subset(graph, list(class_map.keys()))

    outdoor_names = graph.node_names  # 출발지 후보
    node_names_by_id = {nid: graph.get_node(nid).name for nid in graph.node_ids}
    dest_choices, label_meta = _build_dest_choices(node_names_by_id)

    def newbie_route(start_name: str, dest_label: str):
        if not start_name or not dest_label:
            return "현재 위치와 목적지를 모두 선택해 주세요.", None
        start_id = graph.id_by_name(start_name)
        meta = label_meta.get(dest_label)
        if meta is None:
            return f"목적지 라벨을 찾을 수 없습니다: {dest_label}", None
        goal_outdoor = meta["outdoor"]
        indoor_slug = meta["indoor"]

        route = plan_route(graph, start_id, goal_outdoor)
        indoor_clips: list[Path] = []
        indoor_display = None
        if indoor_slug is not None:
            indoor_clips = _resolve_indoor_chain(goal_outdoor, indoor_slug)
            indoor_display = dest_label.strip(" └")

        return _build_route_output(graph, route, indoor_clips, indoor_display)

    def find_peer(a_name: str, b_name: str):
        if not a_name or not b_name:
            return "A와 B 위치를 모두 선택해 주세요.", None
        route = plan_route(graph, graph.id_by_name(a_name), graph.id_by_name(b_name))
        return _build_route_output(graph, route, [], None)

    with gr.Blocks(title="Campus PathFinder (Simple)") as demo:
        gr.Markdown(
            "# Campus PathFinder — 노드 직접 선택\n"
            "- **출발**: 야외 노드만\n"
            "- **목적지**: 야외 + 실내 (실내는 도착 영상만 있고 출발은 불가)\n"
            "- 영상은 음소거 + 4배속으로 합쳐서 재생됩니다.\n"
            "- 저장: `data/route_clips/_stitched/route_2x_mute.mp4`"
        )

        with gr.Tab("신입생 길찾기"):
            start = gr.Dropdown(choices=outdoor_names, label="현재 위치 (야외만)")
            dest = gr.Dropdown(choices=dest_choices, label="목적지 (야외 + 실내)")
            btn = gr.Button("길 안내 시작")
            path = gr.Markdown(label="경로")
            video = gr.Video(label="합쳐진 안내 영상")
            btn.click(newbie_route, inputs=[start, dest], outputs=[path, video])

        with gr.Tab("A가 B를 찾기 (야외만)"):
            a = gr.Dropdown(choices=outdoor_names, label="A의 위치")
            b = gr.Dropdown(choices=outdoor_names, label="B의 위치")
            btn2 = gr.Button("A → B 경로 찾기")
            path2 = gr.Markdown(label="경로")
            video2 = gr.Video(label="합쳐진 안내 영상")
            btn2.click(find_peer, inputs=[a, b], outputs=[path2, video2])

    return demo


if __name__ == "__main__":
    create_simple_app().launch()
