# 길안내 영상 파일 체크리스트

경로 재생용 영상을 이 폴더에 아래 **파일명 그대로** 넣어주세요.
파일명은 `configs/graph.yaml`의 노드 id 기준이며, 구분자는 `__`(언더스코어 2개)입니다.

---

## 1) 밖 — 이동 영상 (노드 → 노드), 양방향 22개

**진행 방향마다 따로** 찍습니다.
정문→중앙광장 영상과 중앙광장→정문 영상은 화면 진행 방향이 반대이므로 **별개 파일**입니다.
파일명 = `<출발>__<도착>.mp4` (출발지가 앞). 경로: `data/route_clips/<파일명>`

정문 ↔ 중앙광장
- [ ] `main_gate__central_plaza.mp4` (정문→중앙광장)
- [ ] `central_plaza__main_gate.mp4` (중앙광장→정문)

정문 ↔ 중앙도서관
- [ ] `main_gate__central_library.mp4` (정문→중앙도서관)
- [ ] `central_library__main_gate.mp4` (중앙도서관→정문)

중앙광장 ↔ 중앙도서관
- [ ] `central_plaza__central_library.mp4` (중앙광장→중앙도서관)
- [ ] `central_library__central_plaza.mp4` (중앙도서관→중앙광장)

중앙광장 ↔ 비마관흡연장
- [ ] `central_plaza__bima_smoking.mp4` (중앙광장→비마관흡연장)
- [ ] `bima_smoking__central_plaza.mp4` (비마관흡연장→중앙광장)

중앙광장 ↔ 분수대
- [ ] `central_plaza__fountain.mp4` (중앙광장→분수대)
- [ ] `fountain__central_plaza.mp4` (분수대→중앙광장)

분수대 ↔ 중앙도서관
- [ ] `fountain__central_library.mp4` (분수대→중앙도서관)
- [ ] `central_library__fountain.mp4` (중앙도서관→분수대)

분수대 ↔ 노천극장/농구장
- [ ] `fountain__outdoor_court.mp4` (분수대→노천극장/농구장)
- [ ] `outdoor_court__fountain.mp4` (노천극장/농구장→분수대)

분수대 ↔ 새빛관
- [ ] `fountain__saebit.mp4` (분수대→새빛관)
- [ ] `saebit__fountain.mp4` (새빛관→분수대)

노천극장/농구장 ↔ 새빛관
- [ ] `outdoor_court__saebit.mp4` (노천극장/농구장→새빛관)
- [ ] `saebit__outdoor_court.mp4` (새빛관→노천극장/농구장)

새빛관 ↔ 참빛관
- [ ] `saebit__chambit.mp4` (새빛관→참빛관)
- [ ] `chambit__saebit.mp4` (참빛관→새빛관)

참빛관 ↔ 비마관흡연장
- [ ] `chambit__bima_smoking.mp4` (참빛관→비마관흡연장)
- [ ] `bima_smoking__chambit.mp4` (비마관흡연장→참빛관)

> 한쪽 방향만 찍어도 코드는 그 영상으로 폴백하지만, 화면 진행 방향이 경로와 반대가 됩니다.
> 발표에서 **한 방향만 시연**한다면 그 방향 파일만 있어도 됩니다.

## 2) 안 — 실내 영상 (건물 도착 후 재생), 데모 케이스만

분류 대상이 아니라 순수 재생용. 발표에서 보여줄 케이스만 찍으면 됩니다.
경로: `data/route_clips/indoor/<파일명>`
파일명 규칙: `<건물노드>__<실내장소>.mp4`

실내가 있는 건물: 새빛관(`saebit`) / 참빛관(`chambit`) / 중앙도서관(`central_library`)

예시 (실제 보여줄 장소에 맞게 이름 수정):
- [ ] `indoor/saebit__8f_seminar.mp4` — 새빛관 입구 → 8층 세미나실
- [ ] `indoor/saebit__1f_lounge.mp4` — 새빛관 입구 → 1층 휴게실
- [ ] `indoor/central_library__312.mp4` — 중앙도서관 입구 → 312호
- [ ] `indoor/chambit__b1_vending.mp4` — 참빛관 입구 → 지하1층 자판기

> 실내장소 이름(`8f_seminar` 등)은 영문 snake_case로 자유롭게. 위는 예시일 뿐입니다.

---

## 촬영/포맷 규칙 (중요)

- 모든 영상의 **해상도 / 코덱 / fps를 통일**해서 내보내세요.
  (이어붙이기가 `ffmpeg -c copy` 방식이라 포맷이 다르면 끊기거나 재인코딩 필요)
- 권장: `1920x1080`, `H.264(mp4)`, `30fps` 정도로 통일.

## 발표 최소 세트 (예: 정문 → 새빛관 8층 세미나실)

- `main_gate__central_plaza.mp4`
- `central_plaza__fountain.mp4`
- `fountain__saebit.mp4`
- `indoor/saebit__8f_seminar.mp4`

## 분류 학습용 프레임 (참고)

분류(위치 인식) 학습용 사진은 **이 이동 영상이 아니라, 각 노드에서 따로 촬영한
"위치 인식용" 영상**에서 뽑아 `data/raw/<노드>/`에 넣습니다.
자세한 내용은 `data/raw/README.md` 참고.
