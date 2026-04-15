# PangPang PathFinder

Kwangwoon University 대상의 **폐쇄형(Closed-set) 장소 분류 + 경로 안내** 딥러닝 프로토타입입니다.

- 입력: 현재 위치 사진 1장 (또는 현재+상대 사진)
- 출력:
  1. 현재 위치 class 예측
  2. 노드 그래프 최단 경로 + edge clip 연결 결과

> 이 MVP의 핵심은 **검색 기반 retrieval 시스템이 아니라, 미리 정의된 class 공간의 분류기**입니다.

---

## 왜 Federated-inspired 방식이 의미 있나?

실제 분산 서버를 운영하지 않아도, 팀원별 로컬 데이터로 학습 후 체크포인트를 중앙에서 병합하면:
- 개인정보/원본데이터 공유 부담 감소
- 팀 병렬 작업 가능
- 10주 학생 프로젝트에서 구현 복잡도 낮음

기본 워크플로우(기본 경로):
1. 각 팀원 로컬 학습
2. 각자 체크포인트 저장
3. 중앙 병합 스크립트로 글로벌 모델 생성
4. 글로벌 평가 + 데모 사용

Flower 연동은 추후 확장 옵션이며, 현재 저장소는 Flower 없이 완전 동작합니다.

---

## 폴더 구조

```text
.
├── configs/                # 클래스, 클라이언트, 학습, 병합, 그래프 설정
├── data/                   # raw/processed/manifests/route_clips
├── docs/                   # 아키텍처/수집가이드/팀워크플로우
├── scripts/                # 실행 스크립트
├── src/pangpang_pathfinder # 라이브러리 코드
├── tests/                  # 경량 테스트
└── outputs/                # 체크포인트/리포트
```

---

## Dataset format

반드시 다음 구조를 따릅니다.

```text
data/raw/<client_id>/<class_slug>/<session_name>/*.jpg
```

예시:

```text
data/raw/hwang/bima_2f_corridor/session_01/img001.jpg
```

- `class_slug`는 `configs/classes.yaml`과 일치해야 합니다.
- `prepare_dataset.py`는 **session 단위 split**을 수행하여 leakage를 방지합니다.

---

## 설치

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
python -m pip install --upgrade pip
pip install -e .[dev]
```

---

## 실행 명령 (실제 파일과 일치)

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

### 3) 체크포인트 병합
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

## 팀 분업 가이드

- **hwang + jung**: model/training/merge
- **shin + kim**: graph/route/UI

---

## Flower 확장 노트

`src/pangpang_pathfinder/fl/flower_stub.py`에 확장 지점을 두었습니다.
현재 기본 경로는 checkpoint merge이며, Flower는 후속 단계에서 시뮬레이션 용도로 추가 가능합니다.
