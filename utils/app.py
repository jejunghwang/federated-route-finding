"""PangPang PathFinder — Gradio entry point."""
import gradio as gr

from ui import build_scene_a, build_scene_b


def main():
    with gr.Blocks(title="PangPang PathFinder") as demo:
        gr.Markdown("# PangPang PathFinder\n광운대 연합학습 길찾기 prototype")
        with gr.Tabs():
            with gr.Tab("Scene A · 만남"):
                build_scene_a()
            with gr.Tab("Scene B · 길찾기"):
                build_scene_b()

    demo.launch()


if __name__ == "__main__":
    main()
