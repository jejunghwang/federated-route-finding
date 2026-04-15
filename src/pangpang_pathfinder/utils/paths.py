from pathlib import Path


def relpath(path: str | Path) -> str:
    return str(Path(path).as_posix())
