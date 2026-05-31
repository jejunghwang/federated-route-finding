# data/raw — 위치 인식(분류) 모델 학습용 사진 폴더

이 폴더는 **"이 사진이 어느 장소인지" 맞히는 분류 모델을 학습시키기 위한 사진(jpg)** 이 들어가는 곳입니다.
경로 재생용 영상(`data/route_clips/`)과는 **완전히 다른 용도**입니다.

- `data/raw/<노드>/` — 분류 모델 학습 (사진 → 위치 맞히기), 내용물: jpg 사진
- `data/route_clips/` — 경로 재생 (길안내 영상), 내용물: mp4 영상

---

## 폴더 구조

```text
data/raw/<노드>/<session_name>/*.jpg
```

예시:
```text
data/raw/main_gate/session_01/img001.jpg
data/raw/main_gate/session_01/img002.jpg
data/raw/main_gate/session_02/img001.jpg
data/raw/saebit/session_01/img001.jpg
```

- `<노드>` 는 8개 노드 id 중 하나 (`configs/classes.yaml` = `configs/graph.yaml` 노드와 동일):
  `main_gate, central_plaza, central_library, fountain, outdoor_court, saebit, chambit, bima_smoking`
- 데이터셋은 **고정** — 사람(client)별로 폴더를 나누지 않습니다.

## session 이란?

- `session_01`, `session_02` … 는 **한 번의 촬영(=영상 1개 또는 한 묶음)** 단위입니다.
- train/val/test 분할이 **session 단위**로 이뤄져 데이터 누수(leakage)를 막습니다.
  (같은 영상의 비슷한 프레임이 학습/시험에 섞이지 않도록)
- 그래서 **노드당 session 3개 이상**이 있어야 분할이 됩니다. (없으면 `prepare_dataset.py`가 에러)
- ⚠️ **노드당 위치 인식 영상이 1개뿐이면 session도 1개 → 분할 불가**입니다.
  - 권장: 다른 시간대/각도로 **2번 더 촬영** (= session 3개)
  - 임시방편: 한 영상을 시간 구간으로 잘라 `session_01/02/03`으로 나눔
    (단 같은 영상이라 train/test가 비슷해져 성능이 부풀려질 수 있음 — leakage 주의)

## 사진은 어떻게 채우나?

- **각 노드(장소)에서 따로 촬영한 "위치 인식용" 영상**에서 프레임을 뽑아 채웁니다 (ffmpeg).
  → 노드 간 **이동 영상(`data/route_clips/`)과는 별개의 영상**입니다.
- 노드당 최소 권장: **session 3개 이상 / session당 사진 30장 이상**.
- 시간대·각도·조명을 다양하게.

## `.gitkeep` 은?

- 빈 폴더도 git이 추적하게 만드는 **더미 파일**입니다. 사진을 넣은 뒤엔 신경 쓰지 않아도 됩니다.

## 다음 단계

사진을 채운 뒤:
```bash
python scripts/prepare_dataset.py
```
→ `data/manifests/train.csv · val.csv · test.csv` 가 생성되고, 클래스별 분할 수가 출력됩니다.
