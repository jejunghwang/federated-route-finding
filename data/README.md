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
