# data/source_videos — 위치 인식 학습용 원본 영상

각 노드(장소)에서 촬영한 **위치 인식용 원본 영상**입니다 (오디오 제거됨).
이 영상에서 프레임을 뽑은 결과가 `data/raw/<노드>/<session>/*.jpg` 이며, **session 번호가 1:1로 매칭**됩니다.

- 파일명: `data/source_videos/<노드>/session_NN.mp4`
- 대응 프레임: `data/raw/<노드>/session_NN/*.jpg`
- 노드 간 이동 영상(`data/route_clips/`)과는 별개입니다.

## session ↔ 원본 촬영 장소

### main_gate (정문)
- session_01 — 정문1
- session_02 — 정문2

### central_plaza (중앙광장)
- session_01 — 중앙광장

### fountain (분수대)
- session_01 — 분수대

### outdoor_court (노천극장/농구장)
- session_01 — 노천과 농구장1
- session_02 — 노천과 농구장2
- session_03 — 노천과 농구장3

### bima_smoking (비마관흡연장)
- session_01 — 비마흡연장

### central_library (중앙도서관)
- session_01 — 1열람실 앞
- session_02 — 3열람실 앞1
- session_03 — 3열람실 앞2
- session_04 — 집현전 앞
- session_05 — 310호 앞
- session_06 — 310호 뒷문(4층)

### saebit (새빛관)
- session_01 — 1층 휴게공간
- session_02 — 2층 휴게공간
- session_03 — 8층 세미나실
- session_04 — 301호 컴퓨터실
- session_05 — 1층 보조엘리베이터1
- session_06 — 1층 보조엘리베이터2

### chambit (참빛관)
- session_01 — 참빛관 외부 흡연구역
- session_02 — b101호
- session_03 — 지하1층 자습공간
- session_04 — 1층 시계 앞
- session_05 — 3층 야외정원

## 참고

- 실내 세부 장소(열람실/세미나실 등)는 분류 class가 아니라 **소속 건물 노드**로 묶여 학습됩니다.
- split 안정화를 위해 노드당 session 3개 이상 권장. 현재 부족: main_gate(2), central_plaza(1), fountain(1), bima_smoking(1).
