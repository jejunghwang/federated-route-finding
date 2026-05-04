"""Scene B — 길찾기 탭 (사진 1장 + 목적지 드롭다운)."""
import gradio as gr

from core import get_graph

from .pipeline import run_pipeline


def build_scene_b():
    node_names = get_graph().node_names
    with gr.Row():
        with gr.Column():
            current_img = gr.Image(type="pil", label="현재 위치 사진")
            goal_dd = gr.Dropdown(choices=node_names, label="목적지")
            run_btn = gr.Button("경로 찾기", variant="primary")

        with gr.Column():
            result_md = gr.Markdown(label="분류 결과")
            path_md = gr.Markdown(label="경로")
            video = gr.Video(label="경로 안내")

    run_btn.click(
        fn=run_pipeline,
        inputs=[current_img, goal_dd],
        outputs=[result_md, path_md, video],
    )
