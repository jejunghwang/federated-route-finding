#!/usr/bin/env python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from pathfinder.app.simple_demo import create_simple_app


if __name__ == "__main__":
    create_simple_app().launch()
