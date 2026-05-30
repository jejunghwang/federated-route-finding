# utils/ — Legacy Gradio scaffold

광운대 캠퍼스 길찾기 prototype의 **임시 데모용 Gradio 앱**.

정식 라이브러리 코드는 `src/pangpang_pathfinder/`에 있고, `utils/`는 그것을 얇게 감싸는 **레거시 스캐폴드**다. 정식 데모(`scripts/launch_demo.py`)와 동일한 그래프/플래너 코드를 공유한다.

- 입력: 현재 위치 사진 + 목적지(사진 또는 텍스트)
- 처리: 분류기 → 노드 id → F-W 최단경로 → edge 영상 clip
- 출력: 경로 텍스트 + 영상

## 설치

```bash
pip install -e ..[dev]   # 루트 pyproject 기준 editable install
```

## 실행

```bash
# 프로젝트 루트에서 실행 권장 (cwd 의존 없음)
python utils/app.py
# → http://127.0.0.1:7860
```

## 디렉토리 구조

```
utils/
├── app.py             # Gradio entry point (Scene A 만남 / Scene B 길찾기 탭)
├── ui/
│   ├── scene_a.py     # Scene A: 사진 2장 (현재 위치 + 목적지 사진)
│   ├── scene_b.py     # Scene B: 사진 1장 + 목적지 드롭다운
│   └── pipeline.py    # 탭 공통 분류 → 경로 → 영상 파이프라인
└── core/
    ├── classifier.py  # 이미지 hash 기반 deterministic dummy 분류기
    ├── graph.py       # CampusGraph 싱글톤 wrapper (configs/graph.yaml 로드)
    └── stitcher.py    # 영상 clip resolver (data/route_clips/ 절대경로 매칭)
```

## 정식 모듈과의 관계

`utils/core/*`는 정식 모듈을 import만 하는 thin wrapper다 — 실제 로직은 `src/pangpang_pathfinder/`에 있다.

- `graph.get_graph()` → `pangpang_pathfinder.route.graph.CampusGraph` (F-W precompute 포함)
- `graph.plan_route` (re-export) → `pangpang_pathfinder.route.planner.plan_route`
- `classifier.classify` → dummy. 정식 분류기는 `pangpang_pathfinder.models.classifier`
- `stitcher.stitch_clips` → `pangpang_pathfinder.route.stitching.stitch_clips` (절대경로 주입)

## 분류기는 dummy

`utils/core/classifier.py`는 **이미지 픽셀의 md5 해시**로 노드 id 1개를 deterministic하게 선택한다. 학습된 모델 안 씀. 진짜 분류기를 쓰려면 정식 앱(`scripts/launch_demo.py`)을 실행. 정식 앱은 `outputs/checkpoints/global_merged.pt` 있으면 자동 로드, 없으면 dummy fallback.

## 노드 id 기반 파이프라인

`classify()` → `(node_id, conf)` (이름 아님). 한국어 표시명은 UI 출력 직전에만 `graph.get_node(id).name`으로 변환한다. 이래서 `configs/graph.yaml`의 `name`이 바뀌어도 코드 변경 0.

## 경로 영상 (route_clips)

`stitch_clips`는 cwd와 무관하게 항상 `<repo_root>/data/route_clips/<a>__<b>.mp4`를 찾는다. 파일명 컨벤션은 `data/README.md` 참조.

> 현재 placeholder 동작: 매칭되는 첫 clip 1개만 반환 (multi-edge concat 아님). 실제 ffmpeg concat은 `pangpang_pathfinder.route.stitching.stitch_clips_ffmpeg`에 있고, 본 데모에선 호출 안 함.
