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
                    chatbot = gr.Chatbot(height=600, show_label=False, elem_id="chatbot")
                    with gr.Row():
                        prompt = gr.Textbox(show_label=False, placeholder="请输入您的问题...", elem_id="prompt_textbox")
                        submit = gr.Button("🚀", elem_id="submit_button")
                with gr.Column():
                    with gr.Accordion('高级选项', open=False):
                        doc_files = gr.File(label="上传文档", file_count="multiple", 
                                            file_types=["text", ".doc", ".docx", ".ppt", ".pptx", ".pdf",
                                                        ".epub", ".html", ".md", ".odt", ".csv"])

                    gr.Label("📌 参考文档", label='', show_label=False, elem_id="source_docs_title")
                    source_docs = gr.Markdown(elem_id="source_docs")

        with gr.Tab("图片搜索"):
            with gr.Row():
                with gr.Column(scale=2):
                    search_image_textbox = gr.Textbox(show_label=False, container=False, elem_id="search_image_textbox")
                    gr.Examples(examples=['unmanned aerial vehicle', 'Working at heights', 'robot', 'winter', 'large vehicle', 'boat', 'kite', 'marry', 
                                          'flower', 'flood', 'car', 'woman in dress', 'blue sky', 'xijinping', 'work in the fields', 'sports'], 
                                inputs=[search_image_textbox])
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
        search_image_textbox.submit(search_image_query, [search_image_textbox, search_image], [gallery])
        search_image_button.click(search_image_query, [search_image_textbox, search_image], [gallery])
        gallery.select(gallery_select_image, [gallery], [search_image, search_image_textbox])

    return demo


if __name__ == "__main__":
    title = '<h1>知识库问答</h1>'
    main(title).launch()
