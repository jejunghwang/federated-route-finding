<div align="center">

![PangPang Banner](docs/assets/kw_mascot_banner.svg)

# 🐼 PangPang PathFinder

**광운대학교 캠퍼스를 위한 폐쇄형 장소 분류 + 경로 안내 프로토타입**

![Mascot Badge](docs/assets/kw_mascot_badge.svg)

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
├── scripts/                # 실행 스크립트
├── src/pangpang_pathfinder # 라이브러리 코드
├── tests/                  # 경량 CPU 테스트
└── outputs/                # 체크포인트/리포트 출력
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
python scripts/launch_demo.py
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

## 🐾 Mascot note

README에는 광운대 마스코트 이미지를 참고한 장식용 SVG를 포함했습니다.
원본 스타일/가이드를 따르는 공식 에셋으로 교체하고 싶다면 `docs/assets/` 파일만 바꾸면 됩니다.
