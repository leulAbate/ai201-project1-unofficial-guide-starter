"""
Milestone 5 — Gradio web interface.

Run:  python app.py
Then open http://localhost:7860
"""

import gradio as gr
from generate import ask


def handle_query(question: str):
    if not question.strip():
        return "", ""
    result = ask(question)
    sources = "\n".join(f"• {s}" for s in result["sources"]) or "No relevant documents found."
    return result["answer"], sources


with gr.Blocks(title="Specialty Coffee Guide") as demo:
    gr.Markdown("# The Unofficial Guide to Specialty Coffee\nAsk anything about espresso extraction, grinders, water chemistry, processing, or home roasting.")

    with gr.Row():
        with gr.Column(scale=3):
            question = gr.Textbox(
                label="Your question",
                placeholder="e.g. What causes channeling in espresso?",
                lines=2,
            )
            ask_btn = gr.Button("Ask", variant="primary")

    with gr.Row():
        with gr.Column(scale=3):
            answer = gr.Textbox(label="Answer", lines=10, interactive=False)
        with gr.Column(scale=1):
            sources = gr.Textbox(label="Retrieved from", lines=10, interactive=False)

    ask_btn.click(handle_query, inputs=question, outputs=[answer, sources])
    question.submit(handle_query, inputs=question, outputs=[answer, sources])


if __name__ == "__main__":
    demo.launch()
