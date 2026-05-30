#!/usr/bin/env python
from pangpang_pathfinder.app.gradio_app import create_app


if __name__ == "__main__":
    demo = create_app()
    demo.launch()
