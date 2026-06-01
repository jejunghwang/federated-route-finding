from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from .graph import Edge

ROUTE_CLIPS_DIR = Path("data/route_clips")

# 영상이 없는 엣지를 다른 엣지의 영상으로 대체하는 별칭 매핑.
# 방향 무관: (a, b) 키는 양방향 모두 적용.
EDGE_CLIP_ALIASES: dict[tuple[str, str], tuple[str, str]] = {
    ("fountain", "central_library"): ("fountain", "central_plaza"),
}


def _resolve_clip_for_edge(edge: Edge, clips_dir: Path = ROUTE_CLIPS_DIR) -> Path | None:
    forward = clips_dir / f"{edge.a}__{edge.b}.mp4"
    backward = clips_dir / f"{edge.b}__{edge.a}.mp4"
    if forward.exists():
        return forward
    if backward.exists():
        return backward
    alias = EDGE_CLIP_ALIASES.get((edge.a, edge.b)) or EDGE_CLIP_ALIASES.get((edge.b, edge.a))
    if alias is not None:
        a, b = alias
        af = clips_dir / f"{a}__{b}.mp4"
        ab = clips_dir / f"{b}__{a}.mp4"
        if af.exists():
            return af
        if ab.exists():
            return ab
    return None


def resolve_clips(
    edges: list[Edge], clips_dir: Path | str = ROUTE_CLIPS_DIR
) -> tuple[list[str], list[Edge]]:
    """엣지 시퀀스를 존재하는 route_clip 경로 리스트로 변환.

    각 엣지를 ``{a}__{b}.mp4`` (또는 역방향 ``{b}__{a}.mp4``)에 매칭한다.
    반환: ``(clips, missing)`` — ``clips``는 순서대로 찾은 경로, ``missing``은 영상이 없는 엣지.
    """
    base = Path(clips_dir)
    clips: list[str] = []
    missing: list[Edge] = []
    for edge in edges:
        clip = _resolve_clip_for_edge(edge, base)
        if clip is not None:
            clips.append(str(clip))
        else:
            missing.append(edge)
    return clips, missing


def stitch_clips(
    edges: list[Edge],
    clips_dir: Path | str = ROUTE_CLIPS_DIR,
    output_path: Path | str | None = None,
    indoor_clip: Path | str | None = None,
) -> str | None:
    """경로 엣지들의 route_clip을 순서대로 하나의 영상으로 이어붙인다.

    - 각 엣지를 ``data/route_clips/{a}__{b}.mp4`` (또는 역방향)로 매칭
    - ``indoor_clip``이 주어지면 마지막에 실내 영상을 이어 붙임 (건물 도착 후 재생).
      상대경로면 ``clips_dir`` 기준으로 해석 (예: ``indoor/saebit__8f_seminar.mp4``).
    - clip이 여러 개면 ffmpeg로 concat한 결과 영상 경로를 반환
    - clip이 1개뿐이면 그대로 그 경로 반환 (concat 불필요)
    - ffmpeg가 없거나 실패하면 첫 clip 경로로 폴백 (적어도 첫 구간은 재생)
    - 사용할 clip이 하나도 없으면 ``None``

    프레임 단위 concat 자체는 :func:`stitch_clips_ffmpeg`가 담당한다.
    """
    base = Path(clips_dir)
    clips, _missing = resolve_clips(edges, base)

    if indoor_clip is not None:
        indoor_path = Path(indoor_clip)
        if not indoor_path.is_absolute():
            indoor_path = base / indoor_path
        if indoor_path.exists():
            clips.append(str(indoor_path))

    if not clips:
        return None
    if len(clips) == 1:
        return clips[0]

    if output_path is None:
        output_path = base / "_stitched" / "route.mp4"
    stitched, _status = stitch_clips_ffmpeg(clips, output_path)
    if stitched is not None:
        return stitched
    return clips[0]  # ffmpeg 미설치/실패 → 첫 구간만이라도


def build_concat_file(clips: list[str], concat_txt_path: str | Path) -> Path:
    concat_path = Path(concat_txt_path)
    concat_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"file '{Path(c).resolve().as_posix()}'" for c in clips]
    concat_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return concat_path


def stitch_clips_ffmpeg(clips: list[str], output_path: str | Path) -> tuple[str | None, str]:
    if not clips:
        return None, "No clips to stitch. Returning text-only route plan."
    if shutil.which("ffmpeg") is None:
        return None, "ffmpeg is not installed. Returning text-only route plan."

    output = Path(output_path)
    concat_txt = output.with_suffix(".concat.txt")
    build_concat_file(clips, concat_txt)

    cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(concat_txt),
        "-c",
        "copy",
        str(output),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return None, f"ffmpeg stitching failed: {result.stderr.strip()}"
    return str(output), "stitched"
