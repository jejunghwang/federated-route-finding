<div align="center">

![연합학습 기반 길찾기 프로그램](docs/assets/kw_title_banner.svg)

# 🐼 PangPang PathFinder

**광운대학교 캠퍼스를 위한 폐쇄형 장소 분류 + 경로 안내 프로토타입**

![광운대 마스코트 네비게이터](docs/assets/kw_mascot_phone.svg)

</div>

---

## ✨ 프로젝트 소개

**PangPang PathFinder**는 사진 한 장으로 현재 위치를 분류하고,
캠퍼스 그래프에서 목적지까지 최단 경로를 안내하는 10주 학생 프로젝트용 MVP입니다.

- 입력: 현재 위치 사진 1장 (또는 현재+친구 사진 2장)
- 출력:
  1. 현재 위치 class 예측 (closed-set)
  2. 노드 기반 최단 경로 + edge clip 연결(가능 시)

> 핵심: 이 MVP는 retrieval-first가 아니라, **미리 정의된 클래스 공간의 분류기**입니다.

---

## 🧭 왜 Federated-inspired 접근인가?

실제 분산 FL 서버를 먼저 구축하지 않고, 팀 개발에 맞춘 단순하고 강력한 기본 흐름을 사용합니다.

1. 각 팀원이 로컬 데이터로 학습
2. 각자 local checkpoint 저장
3. 중앙 merge 스크립트가 가중 평균으로 global checkpoint 생성
4. global 모델 평가 후 데모에 사용

이 방식의 장점:
- 원본 이미지 공유 부담 감소
- 4명 병렬 개발에 적합
- 10주 일정에서 구현 난이도 통제 가능

> Flower는 추후 확장 가능(스텁 제공)하지만, 기본 경로를 막지 않도록 설계했습니다.

---

## 🗂️ 폴더 구조

```text
.
├── configs/                # 클래스/클라이언트/학습/병합/그래프 설정
├── data/                   # raw/processed/manifests/route_clips
├── docs/                   # 아키텍처/데이터수집/팀워크플로우 + 마스코트 에셋
├── scripts/                # 실행 스크립트 (정식 학습/평가/데모)
├── src/pangpang_pathfinder # 라이브러리 코드 (route/, models/, fl/, engine/, ...)
├── tests/                  # 경량 CPU 테스트
├── outputs/                # 체크포인트/리포트 출력
├── utils/                  # 임시 Gradio 데모 스캐폴드 (정식 모듈 wrapper)
└── _docs/                  # 작업 일지 (history/<날짜>.md)
```

---

## 📸 데이터셋 형식

반드시 아래 구조를 사용하세요.

```text
data/raw/<client_id>/<class_slug>/<session_name>/*.jpg
```

예시:

```text
data/raw/hwang/bima_2f_corridor/session_01/img001.jpg
```

- `class_slug`는 `configs/classes.yaml`에 정의되어야 합니다.
- split은 **이미지 랜덤이 아니라 session 단위**로 생성되어 leakage를 방지합니다.

---

## ⚙️ 설치

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -e .[dev]
```

---

## 🚀 실행 커맨드 (README와 실제 파일 동기화)

### 1) Dataset manifest 생성
```bash
python scripts/prepare_dataset.py
```

### 2) 클라이언트별 로컬 학습
```bash
python scripts/train_local.py --client-id hwang
python scripts/train_local.py --client-id shin
python scripts/train_local.py --client-id jung
python scripts/train_local.py --client-id kim
```

### 3) Federated-inspired checkpoint 병합
```bash
python scripts/merge_checkpoints.py
```

### 4) 글로벌 모델 평가
```bash
python scripts/evaluate_global.py
```

### 5) 예측 + 경로 (CLI)
```bash
python scripts/predict_route.py --current-photo path/to/current.jpg --destination-class bima_101_front
python scripts/predict_route.py --current-photo path/to/a.jpg --peer-photo path/to/b.jpg
```

### 6) Gradio 데모 실행
```bash
# 정식 데모 (학습된 모델 + 정식 UI)
python scripts/launch_demo.py

# 또는 임시 데모 (dummy 분류기 + 동일 graph/planner 코어)
python utils/app.py
```

---

## 👥 팀 분업 가이드

- **hwang + jung**: model / training / merge
- **shin + kim**: graph / route / UI

상세 협업 가이드는 `docs/TEAM_WORKFLOW.md`를 참고하세요.

---

## 🔮 확장 계획

- Flower simulation 기반 실험(선택)
- 클래스/노드 확장
- route clip 품질 개선 및 edge coverage 확대
- 경량화 모델 최적화(모바일 고려)

---

## 🔄 본 브랜치 주요 변경 (`codex/create-starter-repository-for-pangpang-pathfinder`)

다른 사람이 만든 정식 구조 위에 **graph/route 코어 wiring**과 **임시 Gradio 데모(`utils/`)**를 추가하면서 정리한 사항.

### 1. 그래프/최단경로 정식 구현 (Floyd-Warshall)

`src/pangpang_pathfinder/route/` 정식 모듈:
- `graph.py:CampusGraph` — `configs/graph.yaml` 로드 후 networkx 무방향 그래프 + **F-W all-pairs precompute** (`__init__`에서 1회).
- `planner.py:plan_route` — `nx.reconstruct_path`로 precomputed predecessor 행렬 lookup. 시그니처는 BFS 시절과 동일.
- 동일 unweighted 무방향 그래프에서 BFS와 결과 동일하지만, edge weight 도입/distance matrix 활용/발표 변별력에서 유리.

자세한 patch 설명: `graph_shortest_path_spec_v2.md` 끝 섹션.

### 2. `utils/` 임시 데모 — 정식 모듈 wrapper로 통일

기존 `utils/`는 `NODE_NAMES = [...]` 같은 하드코딩 dummy였음. 다음과 같이 재작성:
- `utils/core/graph.py` → `pangpang_pathfinder.route` 싱글톤 wrapper
- `utils/core/classifier.py` → `graph.node_ids` 기반 deterministic hash dummy, 반환값을 **node_id**로 통일 (이름 아님)
- `utils/core/stitcher.py` → 정식 stitcher에 **절대경로 주입** (cwd 의존 회피)
- `utils/ui/scene_b.py` 드롭다운 → `graph.node_names` 자동 로드

이래서 노드/엣지 추가는 **`configs/graph.yaml` 한 곳만** 편집하면 양쪽 데모 모두 자동 반영.

### 3. 데이터 컨벤션 명시

- `data/README.md`에 **route_clips 파일명 규칙** 섹션 추가 (`<from_id>__<to_id>.mp4`, double-underscore, 무방향이므로 한 방향만 둬도 OK).

### 4. 폴더 정리

- `*.egg-info/`, `.playwright-mcp/` `.gitignore` 추가
- `utils/assets/`(빈 폴더), `__pycache__/` 청소
- 빌드 산출물(`src/pangpang_pathfinder.egg-info/`) 제거

### 5. 검증

- `pytest tests/test_graph.py -v` → 7/7 통과
- `python utils/app.py` → http://127.0.0.1:7860 정상 동작 (Playwright E2E로 4-hop 경로 확인)
- `os.chdir('utils')` 상태에서도 `data/route_clips/` 절대경로 유지

---

## 🐾 Mascot note

README에는 광운대 마스코트 이미지를 참고한 장식용 SVG를 포함했습니다.
원본 스타일/가이드를 따르는 공식 에셋으로 교체하고 싶다면 `docs/assets/` 파일만 바꾸면 됩니다.
