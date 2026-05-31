from pathlib import Path

from pathfinder.route.graph import Edge
from pathfinder.route.stitching import resolve_clips, stitch_clips


def _touch(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"")


def test_resolve_clips_forward_and_backward(tmp_path):
    _touch(tmp_path / "a__b.mp4")  # forward for a->b
    _touch(tmp_path / "c__b.mp4")  # backward for b->c
    clips, missing = resolve_clips([Edge("a", "b"), Edge("b", "c")], tmp_path)
    assert len(clips) == 2
    assert missing == []


def test_resolve_clips_reports_missing(tmp_path):
    clips, missing = resolve_clips([Edge("a", "b")], tmp_path)
    assert clips == []
    assert missing == [Edge("a", "b")]


def test_stitch_clips_none_when_no_clip(tmp_path):
    assert stitch_clips([], tmp_path) is None
    assert stitch_clips([Edge("a", "b")], tmp_path) is None


def test_stitch_clips_single_returns_that_path(tmp_path):
    _touch(tmp_path / "a__b.mp4")
    out = stitch_clips([Edge("a", "b")], tmp_path)
    assert out == str(tmp_path / "a__b.mp4")


def test_stitch_clips_indoor_appended(tmp_path):
    # 단일 엣지 + 실내 영상 → clip 2개 → concat 시도. ffmpeg 없으면 첫 구간 폴백.
    _touch(tmp_path / "a__b.mp4")
    _touch(tmp_path / "indoor" / "b__lobby.mp4")
    out = stitch_clips(
        [Edge("a", "b")], tmp_path, indoor_clip="indoor/b__lobby.mp4"
    )
    assert out is not None
