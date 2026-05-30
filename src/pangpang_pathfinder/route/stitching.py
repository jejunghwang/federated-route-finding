from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from .graph import Edge

ROUTE_CLIPS_DIR = Path("data/route_clips")


def _resolve_clip_for_edge(edge: Edge, clips_dir: Path = ROUTE_CLIPS_DIR) -> Path | None:
    forward = clips_dir / f"{edge.a}__{edge.b}.mp4"
    backward = clips_dir / f"{edge.b}__{edge.a}.mp4"
    if forward.exists():
        return forward
    if backward.exists():
        return backward
    return None


def stitch_clips(edges: list[Edge], clips_dir: Path | str = ROUTE_CLIPS_DIR) -> str | None:
    """Resolve route edges to a single video clip path.

    Placeholder behavior: returns the first matching ``data/route_clips/{a}__{b}.mp4``
    (or the reversed variant) for the supplied edge sequence. Real frame-level
    concatenation lives in ``stitch_clips_ffmpeg`` and a follow-up PR.
    Returns ``None`` when no clip is available.
    """
    if not edges:
        return None
    base = Path(clips_dir)
    for edge in edges:
        clip = _resolve_clip_for_edge(edge, base)
        if clip is not None:
            return str(clip)
    return None


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
