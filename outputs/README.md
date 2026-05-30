# outputs/ — 학습/평가 산출물

스크립트 실행 시 자동 생성. **git에 커밋되지 않음** (`.gitignore` 처리).

## 구조

```
outputs/
├── checkpoints/         # 모델 가중치
│   ├── <client>_best.pt    # train_local.py 산출 (client별 local)
│   └── global_merged.pt    # merge_checkpoints.py 산출 (federated 가중평균)
└── reports/             # 메타데이터/평가 결과
    ├── merge_report.json   # 병합 시 가중치, 클라이언트별 epoch 수 등
    └── eval_*.json/csv     # evaluate_global.py 산출
```

## .gitignore 처리

다음 패턴은 추적하지 않음:

- `outputs/checkpoints/*.pt`, `*.pth`
- `outputs/reports/*.json`, `*.csv`, `*.txt`

폴더 자체는 `.gitkeep`로 유지.

## 정리 (필요 시)

```bash
rm outputs/checkpoints/*.pt outputs/reports/*.json
```

학습 재현 시: `data/manifests/`와 `outputs/`를 모두 비우고 `prepare_dataset.py`부터 다시 실행.

## 참고

- `configs/federated.yaml`이 병합 입력/출력 경로를 정의
- `configs/train.yaml`의 `paths.checkpoints_dir` / `paths.reports_dir`로 학습 결과 경로 설정
- 데모(`launch_demo.py`)는 `global_merged.pt` 있으면 자동 로드, 없으면 dummy fallback
