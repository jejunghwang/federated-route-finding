# pathfinder — 라이브러리 코드

PangPang PathFinder의 정식 패키지. CLI 스크립트(`scripts/`)와 Gradio 앱들이 모두 여기서 import.

## 패키지 트리

```
pathfinder/
├── config.py            # YAML 로더 (load_graph_config, load_classes_map, load_yaml)
│
├── route/               # 그래프 + 최단경로 (Floyd-Warshall)
│   ├── graph.py         # CampusGraph (F-W precompute), Node/Edge dataclass, validate_classes_subset
│   ├── planner.py       # plan_route → Route(nodes, edges)
│   └── stitching.py     # edge → mp4 clip 매칭, ffmpeg concat 헬퍼
│
├── models/              # 분류기 모델
│   ├── factory.py       # build_model (resnet18 / mobilenet_v3_small)
│   └── classifier.py    # 체크포인트 load/save
│
├── data/                # 데이터 파이프라인
│   ├── manifest.py      # CSV manifest 생성/로딩
│   ├── dataset.py       # PyTorch Dataset
│   └── transforms.py    # 학습/평가 transform
│
├── engine/              # 학습/평가 루프
│   ├── train.py         # local 학습
│   ├── evaluate.py      # accuracy/loss
│   └── metrics.py
│
├── fl/                  # 연합학습
│   ├── merge.py         # 가중평균 체크포인트 병합
│   └── flower_stub.py   # Flower 통합용 stub (선택)
│
├── app/                 # 정식 Gradio 앱
│   └── gradio_app.py    # 신입생 길찾기 / A→B 만남 두 탭
│
└── utils/               # 헬퍼 (io, logging, reproducibility)
```

## 주요 진입점

```
호출자                            사용 모듈
──────────────────────────────────────────────────────────────────────────────────────
scripts/prepare_dataset.py        data.manifest, config.load_classes_map, utils.io
scripts/train_local.py            engine.train, models.factory, data.dataset
scripts/merge_checkpoints.py      fl.merge, models.classifier
scripts/evaluate_global.py        engine.evaluate, models.classifier
scripts/predict_route.py          models.classifier, route.planner, route.stitching
scripts/launch_demo.py            app.gradio_app:create_app
```

## 모듈별 상세 README

- `route/` — `route/README.md` 참조 (Floyd-Warshall 구현 + 노드 추가 가이드)
