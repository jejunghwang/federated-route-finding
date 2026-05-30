# Architecture

PangPang PathFinder MVP is built around a simple, local-file-first workflow:

1. Local training per client (`scripts/train_local.py`)
2. Checkpoint merge (`scripts/merge_checkpoints.py`)
3. Global evaluation (`scripts/evaluate_global.py`)
4. Prediction + routing (`scripts/predict_route.py` / Gradio)

## Core principles
- Closed-set place classification over predefined campus nodes.
- One shared global class space.
- Federated-inspired collaboration via checkpoint averaging.
- Route generation from graph shortest path + optional clip stitching.

## Why this shape
- Easy for 4 students to parallelize.
- No distributed infra required.
- Deterministic and debuggable.
