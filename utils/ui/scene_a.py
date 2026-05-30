"""Scene A — 만남 (B가 A를 찾아오는 상황). 사진 2장."""
import gradio as gr

from .pipeline import run_pipeline


def build_scene_a():
    with gr.Row():
        # 좌측: 입력
        with gr.Column():
            current_img = gr.Image(type="pil", label="A의 현재 위치 사진")
            goal_img = gr.Image(type="pil", label="B의 목적지 사진")
            run_btn = gr.Button("경로 찾기", variant="primary")

        # 우측: 출력
        with gr.Column():
            result_md = gr.Markdown(label="분류 결과")
            path_md = gr.Markdown(label="경로")
            video = gr.Video(label="경로 안내")

    run_btn.click(
        fn=run_pipeline,
        inputs=[current_img, goal_img],
        outputs=[result_md, path_md, video],
    )
