# 학습용 위치 라벨 사전

**용도**: 사진/영상 보고 "여기가 어디인가" 라벨링할 때 모두가 같이 쓰는 표준 위치 이름 모음.
**원칙**: 슬러그(영문 snake_case)는 한 번 정하면 변경 금지. 새 위치 추가는 여기 먼저 등록 → `configs/classes.yaml` 반영.

표 컬럼:
- **slug**: 폴더/매니페스트에 쓰는 영문 키 (`data/raw/<slug>/...`)
- **한글명**: 사람용 표시
- **식별 단서**: 사진 라벨링 시 참고하는 특징/랜드마크 (촬영자가 추가)

---

## A. Outdoor (캠퍼스 야외) — 8개, 확정

| slug | 한글명 | 식별 단서 |
|---|---|---|
| `main_gate` | 정문 | 캠퍼스 정문 게이트 |
| `central_plaza` | 중앙광장 | 광장 중앙 |
| `central_library` | 중앙도서관 | 도서관 건물 앞 |
| `fountain` | 분수대 | 분수 |
| `outdoor_court` | 노천극장/농구장 | 농구골대, 노천 좌석 |
| `saebit` | 새빛관 (외부) | 새빛관 정문 앞 |
| `chambit` | 참빛관 (외부) | 참빛관 정문 앞 |
| `bima_smoking` | 비마관 흡연장 | 흡연 부스 |

---

## B. Indoor — 새빛관 (`saebit_*`)

| slug | 한글명 | 식별 단서 |
|---|---|---|
| `saebit_1f` | 새빛관 1층 | (입구/로비 — 단서 추가) |
| `saebit_2f` | 새빛관 2층 | (단서 추가) |
| `saebit_3f` | 새빛관 3층 | (단서 추가) |
| `saebit_8f` | 새빛관 8층 | (단서 추가) |
| `saebit_elevator` | 새빛관 엘리베이터 앞 | (단서 추가) |

> 더 세부 분류가 필요하면 `saebit_1f_lobby`, `saebit_8f_seminar` 식으로 확장.

---

## C. Indoor — 참빛관 (`chambit_*`)

| slug | 한글명 | 식별 단서 |
|---|---|---|
| `chambit_1f_clock` | 참빛관 1층 시계 앞 | 큰 시계 |
| `chambit_3f_garden` | 참빛관 3층 야외정원 | 외부 정원/식물 |
| `chambit_b101` | 참빛관 지하1층 B101호 | B101 표지 |
| `chambit_b1_study` | 참빛관 지하1층 자습공간 | 자습 책상/열람 공간 |
| `chambit_smoking` | 참빛관 흡연장 | 참빛관 부속 흡연 구역 |

---

## D. Indoor — 중앙도서관 (`central_library_*`)

| slug | 한글명 | 식별 단서 |
|---|---|---|
| `central_library_freeroom_1` | 제1자유열람실 | (단서 추가) |
| `central_library_freeroom_3` | 제3자유열람실 | (단서 추가) |
| `central_library_jiphyeonjeon` | 집현전 앞 | (단서 추가) |
| `central_library_310_front` | 310호 앞문 | (단서 추가) |
| `central_library_310_back` | 310호 뒷문 | (단서 추가) |
| `central_library_4f` | 4층 | (단서 추가) |

---

## 라벨링 규칙

1. **가장 좁은 슬러그 우선**: 사진이 "참빛관 1층 시계앞"이면 `chambit_1f_clock` (상위 `chambit` 아님).
2. **애매하면 상위 슬러그**: 어느 세부 위치인지 모르면 가장 가까운 건물 슬러그(예: `chambit`).
3. **단서 부족 = 제외**: 사람만 크게 잡혀 배경 단서가 없으면 skip.
4. **한 사진 = 한 라벨**: 두 위치가 겹치면 주된 위치 1개만.
5. **세션 단위 일관성**: 한 session 영상 안에서는 같은 슬러그 유지. 위치가 바뀌면 별 session으로 분리.

---

## 슬러그 명명 규칙

- 영문 snake_case, 단어 구분 `_` 1개
- indoor 세부: `<건물슬러그>_<위치>` (예: `chambit_1f_clock`)
- 슬러그는 폴더명/매니페스트 키 — 한 번 정하면 변경 금지

## 사용처 (이 슬러그를 어디서 쓰는가)

| 어디서 | 파일 |
|---|---|
| 분류 클래스 정의 | `configs/classes.yaml` |
| 그래프 노드 id | `configs/graph.yaml` |
| 클라이언트 분배 | `configs/clients.yaml` |
| 데이터 폴더 | `data/raw/<slug>/session_XX/`, `data/source_videos/<slug>/session_XX.mp4` |
| 매니페스트 컬럼 | `data/manifests/{train,val,test}.csv` → `class_slug` |
| 길안내 영상 | `data/route_clips/<from>__<to>.mp4` |

## 클라이언트 담당 (참고)

| 클라이언트 | 담당 슬러그 |
|---|---|
| hwang(황) | `main_gate`, `central_plaza` |
| jung(정) | `central_library`, `fountain` |
| shin(신) | `outdoor_court`, `saebit`, `saebit_*` (indoor 추가 시) |
| kim(김) | `chambit`, `bima_smoking`, `chambit_*` (indoor 추가 시) |
