# Team Workflow

## Suggested split
- **hwang + jung**: model / training / merge pipeline
- **shin + kim**: graph / route / UI

## Weekly loop
1. Collect or clean local images.
2. Rebuild manifests.
3. Train local checkpoints.
4. Merge global checkpoint.
5. Evaluate on pooled test split.
6. Demo with route UI.

## Branching tips
- Keep script-level changes small and reviewed quickly.
- Update README command examples whenever script arguments change.
