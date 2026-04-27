# PangPang PathFinder

광운대 캠퍼스 내 **연합학습(Federated Learning) 기반 길찾기 시스템** prototype.

- 입력: 현재 위치 사진 + 목적지(사진 또는 텍스트)
- 처리: 사진 분류 → 위치 class → graph 상 shortest path → edge 영상 clip stitching
- 출력: 경로 영상 + 텍스트 경로

본 PR은 **Gradio UI 스캐폴드 + dummy 모듈**만 포함. 분류기 / graph / stitcher 는 모두 더미.

## 설치

```bash
pip install -r requirements.txt
```

## 실행

```bash
python app.py
# → http://127.0.0.1:7860
```

## 디렉토리 구조

```
pangpang/
├── app.py              # Gradio entry point
├── ui/
│   ├── scene_a.py      # 만남 탭 (사진 2장)
│   ├── scene_b.py      # 길찾기 탭 (사진 1장 + 드롭다운)
│   └── pipeline.py     # 탭 공통 파이프라인
├── core/
│   ├── classifier.py   # dummy classifier
│   ├── graph.py        # dummy shortest_path
│   └── stitcher.py     # dummy 영상 stitcher
└── assets/
    └── dummy_route.mp4 # (옵션) 임시 영상. 없어도 UI 동작
```

## 다음 작업

- [ ] 실제 분류기 연결 (다른 팀원)
- [ ] 실제 graph + BFS 연결 (본인)
- [ ] 실제 영상 clip stitching (신정은)
