import gradio as gr

from app import main as main_module


from app.ui.search_image import get_images_from_path, get_image_features
images_dir = 'data/images'
images_path = get_images_from_path(images_dir)
image_features = get_image_features(images_path)


def knowledge_query(chatbot: gr.Chatbot, prompt: str):
    if not prompt:
        return chatbot, '', ''
    
    result = main_module.qa({"query": prompt})
    
    completion = result["result"]
    chatbot.append((prompt, completion))

    source_docs = ''
    for source_doc in result["source_documents"]:
        source_docs += f'🟥 {source_doc.page_content}\n\n【来源文件】{source_doc.metadata["source"]}\n\n'

    return chatbot, '', source_docs


def translate_zh2en(text):
    from ..models.translate import TranslateModel
    translator = TranslateModel()
    print('*'*100, translator(text), text)
    return translator(text)


def search_image_query(search_image_textbox, search_image, is_translate):
    import numpy as np

    if search_image_textbox:
        if is_translate:
            search_image_textbox = translate_zh2en(search_image_textbox)
        from app.ui.search_image import get_images_with_similar_text
        images = get_images_with_similar_text(search_image_textbox, image_features)
    elif np.any(search_image):
        from app.ui.search_image import get_images_with_similar, get_image_feature_from_numpy
        images = get_images_with_similar(get_image_feature_from_numpy(search_image), image_features)
    else:
        return [], ''

    return images, search_image_textbox


def gallery_select_image(gallery, evt: gr.SelectData):
    return gallery[evt.index]['name'], ''
