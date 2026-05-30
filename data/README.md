# Data layout

Raw images must follow this exact structure:

```text
data/raw/<client_id>/<class_slug>/<session_name>/*.jpg
```

Example:

```text
data/raw/hwang/bima_2f_corridor/session_01/img001.jpg
```

## Rules
- `client_id` must exist in `configs/clients.yaml`.
- `class_slug` must exist in `configs/classes.yaml`.
- `session_name` is used for leak-free split (train/val/test split is by session).
- Keep at least 3 sessions per class for stable split.

## Outputs
- `data/manifests/train.csv`
- `data/manifests/val.csv`
- `data/manifests/test.csv`

Each CSV stores one row per image with columns:
`client_id, class_slug, session_name, image_path, split`

## Route clips

Edge별 안내 영상은 `data/route_clips/`에 둔다. 파일명 규칙:

```text
data/route_clips/<from_id>__<to_id>.mp4
```

- `from_id`, `to_id`는 `configs/graph.yaml`의 node id (snake_case)
- 구분자는 `__` (double underscore)
- 무방향 그래프이므로 한 방향만 두면 reverse 케이스도 자동 매칭됨
- 예시: `data/route_clips/bima_2f_corridor__bima_101_front.mp4`
