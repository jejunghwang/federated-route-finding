# scripts/ — CLI 실행 스크립트

학습/평가/데모/예측의 진입점. 모두 프로젝트 루트에서 실행.

## 실행 순서 (전체 파이프라인)

```bash
# 1) 이미지 → manifest CSV 생성 (session 단위 split)
python scripts/prepare_dataset.py

# 2) 클라이언트별 로컬 학습
python scripts/train_local.py --client-id hwang
python scripts/train_local.py --client-id shin
python scripts/train_local.py --client-id jung
python scripts/train_local.py --client-id kim

# 3) federated-inspired 가중평균 병합
python scripts/merge_checkpoints.py

# 4) 글로벌 모델 평가
python scripts/evaluate_global.py

# 5) 예측 + 경로 (CLI)
python scripts/predict_route.py --current-photo path/to/cur.jpg --destination-class bima_101_front
python scripts/predict_route.py --current-photo path/to/a.jpg --peer-photo path/to/b.jpg

# 6) Gradio 데모
python scripts/launch_demo.py
```

## 파일별 역할

```
스크립트                  입력                                                   출력
──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
prepare_dataset.py        data/raw/<client>/<class>/<session>/*.jpg              data/manifests/{train,val,test}.csv
train_local.py            manifests + configs/train.yaml                         outputs/checkpoints/<client>_best.pt
merge_checkpoints.py      configs/federated.yaml의 local 체크포인트들            outputs/checkpoints/global_merged.pt + outputs/reports/merge_report.json
evaluate_global.py        global 체크포인트 + test manifest                      outputs/reports/eval_*.json
predict_route.py          현재 사진 + 목적지 (class 또는 사진)                   콘솔 (예측 클래스 + 경로)
launch_demo.py            global 체크포인트 (있으면)                             Gradio 서버
```

## 참고

- `launch_demo.py`는 정식 데모 (`src/.../app/gradio_app.py`). 체크포인트 없으면 dummy 분류기 fallback.
- 임시 데모는 `python utils/app.py` (단순 hash dummy 분류기 고정).
- 학습 데이터 형식 / 폴더 규칙은 `data/README.md` 참조.
- 설정 스키마는 `configs/README.md` 참조.
