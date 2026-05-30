# configs/ — 설정 파일

프로젝트의 모든 정적 설정을 yaml로 관리. **데이터/노드/하이퍼파라미터를 코드에 박지 말 것** — 여기에 추가/수정만 하면 모든 모듈이 자동 반영.

## 파일 일람

```
파일               역할                                              변경 시 영향
────────────────────────────────────────────────────────────────────────────────────────────────────
graph.yaml         캠퍼스 그래프 (노드 + 엣지)                       양쪽 데모 드롭다운, 경로 계산, 분류기 후보
classes.yaml       분류기 학습 대상 클래스                           모델 출력 차원, train/eval 라벨
clients.yaml       연합학습 클라이언트 정의 (hwang/shin/jung/kim)    데이터 검증, local 학습 분배
train.yaml         학습 하이퍼파라미터 (model/data/training/paths)   scripts/train_local.py
federated.yaml     체크포인트 병합 설정                              scripts/merge_checkpoints.py
```

## graph.yaml 스키마

```yaml
version: 1

nodes:
  - id: bima_2f_corridor      # snake_case, clip 파일명/class_slug에 쓰임
    name: 비마관 2층 복도       # 한국어 표시명 (UI 출력용)
    building: 비마관           # 그룹화용 메타
    is_indoor: true           # 추후 실내/실외 transition 영상 등에 활용

edges:
  - [bima_2f_corridor, bima_101_front]   # 무방향, 한 번만 적으면 양방향
```

검증 (`from_config()` 시 자동):
- `version` 필드 필수
- node id 중복 X / name 중복 X
- self-loop X / edge 양 끝이 nodes에 존재 / 동일 edge 중복 X
- isolated 노드는 warning만 (에러 아님)

## classes.yaml 스키마

```yaml
classes:
  - slug: bima_2f_corridor          # graph.yaml의 id와 일치 필수
    display_name_ko: 비마관 2층 복도
    building: 비마관
    description: 비마관 2층 주요 복도 구간
```

**`slug` ⊆ graph.yaml의 `id`** — `validate_classes_subset()`이 시작 시 검증.

## clients.yaml 스키마

```yaml
clients:
  hwang:
    owner_name: 황
    buildings: [비마관, 새빛관]
    class_slugs: [bima_2f_corridor, bima_101_front, ...]   # classes.yaml의 slug
```

`data/raw/<client_id>/...` 의 `client_id`가 여기 키와 일치해야 함.

## 추가/수정 시 주의

1. **단일 소스**: graph 변경은 `graph.yaml`만, 분류 클래스는 `classes.yaml`만 수정.
2. **id 일관성**: snake_case 통일, `graph.yaml의 id` ≡ `classes.yaml의 slug` ≡ `data/raw/.../<class_slug>/` 폴더명.
3. **무방향 엣지**: edge는 한 방향만 적으면 됨. clip 파일도 한 방향만 두면 자동 reverse 매칭.
