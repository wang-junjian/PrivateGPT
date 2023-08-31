# # ImportError: attempted relative import with no known parent package
# import sys,os
# sys.path.append(os.getcwd())

import gradio as gr

from .webui_method import knowledge_query, search_image_query, gallery_select_image, upload_docs, upload_images


def main(title):
    with gr.Blocks(css="asserts/custom.css") as demo:
        gr.HTML(
            title,
            elem_id="title",
        )

        with gr.Tab("知识库问答"):
            with gr.Row():
                with gr.Column(scale=2):
                    chatbot = gr.Chatbot(height=600, elem_id="chatbot")
                    with gr.Row():
                        prompt = gr.Textbox(show_label=False, placeholder="请输入您的问题...", elem_id="prompt_textbox")
                        submit = gr.Button("🚀", elem_id="submit_button")
                with gr.Column():
                    with gr.Accordion('高级选项', open=False):
                        doc_files = gr.File(label="上传文档", file_count="multiple", file_types=["text"])

                    gr.Label("🎯 参考文档", label='')
                    source_docs = gr.Markdown(elem_id="source_docs")

        with gr.Tab("图片搜索"):
            with gr.Row():
                with gr.Column(scale=2):
                    search_image_textbox = gr.Textbox(show_label=False, container=False, elem_id="search_image_textbox")
                    with gr.Accordion('高级选项', open=False):
                        with gr.Row():
                            is_translate = gr.Checkbox(label='中文自动翻译为英文', container=False, scale=0.2, elem_id="translate_checkbox")
                            translated_text = gr.Markdown('', elem_id="translated_text")
                    search_image = gr.Image(elem_id="search_image")
                with gr.Column():
                    search_image_button = gr.Button("🚀", elem_id="search_image_button")
                    with gr.Accordion('高级选项', open=False):
                        image_files = gr.File(label="上传图像", file_count="multiple", file_types=["image"])

            gallery = gr.Gallery(
                show_label=False, 
                allow_preview=False,
                height='max-content',
                columns=6,
                elem_id="gallery",
                show_share_button=False
            )
            
        doc_files.upload(upload_docs, inputs=[doc_files])
        submit.click(knowledge_query, [chatbot, prompt], [chatbot, prompt, source_docs])
        prompt.submit(knowledge_query, [chatbot, prompt], [chatbot, prompt, source_docs])

        image_files.upload(upload_images, inputs=[image_files])
        search_image_textbox.submit(search_image_query, [search_image_textbox, search_image, is_translate], [gallery, translated_text])
        search_image_button.click(search_image_query, [search_image_textbox, search_image, is_translate], [gallery, translated_text])
        gallery.select(gallery_select_image, [gallery], [search_image, search_image_textbox])

    return demo


if __name__ == "__main__":
    title = '<h1>知识库问答</h1>'
    main(title).launch()
