"""Thin wrapper around the canonical ``stitch_clips`` placeholder."""
from __future__ import annotations

from pathlib import Path

from pangpang_pathfinder.route.graph import Edge
from pangpang_pathfinder.route.stitching import stitch_clips as _stitch_clips

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ROUTE_CLIPS_DIR = PROJECT_ROOT / "data" / "route_clips"


def stitch_clips(edges: list[Edge]) -> str | None:
    return _stitch_clips(edges, clips_dir=ROUTE_CLIPS_DIR)
