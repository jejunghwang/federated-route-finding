#!/usr/bin/env python
"""위치 인식용 영상에서 프레임을 추출해 data/raw/<node>/<session>/ 에 저장.

분류(위치 인식) 모델 학습 데이터를 만든다. (route_clips 이동 영상이 아니라,
각 장소에서 따로 촬영한 위치 인식용 영상을 입력으로 받는다.)

예시:
    python scripts/extract_frames.py --video clips/saebit_01.mp4 --node saebit --session session_01 --count 60
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path

from pathfinder.config import load_classes_map


def _probe_duration(video: str) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", video],
        capture_output=True, text=True,
    )
    try:
        return float(out.stdout.strip())
    except ValueError:
        return 0.0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--video", required=True, help="입력 영상 경로")
    parser.add_argument("--node", required=True, help="class_slug (configs/classes.yaml의 노드 id)")
    parser.add_argument("--session", default="session_01", help="session 이름 (split 단위)")
    parser.add_argument("--count", type=int, default=60, help="추출할 프레임 수 (영상 전체에서 균등)")
    parser.add_argument("--out-root", default="data/raw")
    parser.add_argument("--classes-config", default="configs/classes.yaml")
    args = parser.parse_args()

    if shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None:
        raise SystemExit("ffmpeg/ffprobe가 필요합니다. conda 환경(pathfinder)을 activate 후 실행하세요.")

    classes = load_classes_map(args.classes_config)
    if args.node not in classes:
        raise SystemExit(
            f"알 수 없는 노드: {args.node!r}. configs/classes.yaml에 정의된 노드여야 합니다: {sorted(classes)}"
        )

    video = Path(args.video)
    if not video.exists():
        raise SystemExit(f"영상이 없습니다: {video}")

    out_dir = Path(args.out_root) / args.node / args.session
    out_dir.mkdir(parents=True, exist_ok=True)

    duration = _probe_duration(str(video))
    fps = max(args.count / duration, 0.1) if duration > 0 else 1.0

    cmd = [
        "ffmpeg", "-y", "-i", str(video),
        "-vf", f"fps={fps}",
        "-q:v", "2",
        str(out_dir / "img%03d.jpg"),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise SystemExit(f"ffmpeg 실패:\n{result.stderr[-800:]}")

    n = len(list(out_dir.glob("*.jpg")))
    print(f"[OK] {n} 프레임 추출 -> {out_dir}")
    if n < 3:
        print("주의: 프레임이 3장 미만입니다. --count를 늘리거나 더 긴 영상을 쓰세요.")
    print("팁: 같은 노드를 다른 시간대/각도로 촬영해 session_02, session_03 ... 을 추가하면 split이 안정적입니다.")


if __name__ == "__main__":
    main()
