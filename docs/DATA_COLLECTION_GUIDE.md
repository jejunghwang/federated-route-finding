# Data Collection Guide

## Per class
- Capture multiple sessions (`session_01`, `session_02`, ...).
- Vary time-of-day, lighting, and angle.
- Avoid blurry photos.

## Minimum recommendation
- 3+ sessions/class/client.
- 30+ images/session.

## Naming
- Keep class slug fixed (from `configs/classes.yaml`).
- Session names should be stable (`session_01`).
- Image names can be sequential (`img001.jpg`).

## Quality check
- Run `python scripts/prepare_dataset.py`.
- Verify class count table and split integrity.
