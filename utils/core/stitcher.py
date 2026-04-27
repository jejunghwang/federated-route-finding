"""Dummy stitcher — 추후 실제 영상 clip 이어붙이기로 교체."""
import os


def stitch_clips(path: list[str]) -> str | None:
    """경로 노드 리스트를 받아 영상 파일 경로 반환.
    Dummy: assets/dummy_route.mp4 가 있으면 반환, 없으면 None."""
    p = "assets/dummy_route.mp4"
    return p if os.path.exists(p) else None
