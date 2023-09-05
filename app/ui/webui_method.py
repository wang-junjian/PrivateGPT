import os
import shutil
import numpy as np
import gradio as gr


def get_global_object():
    from app import main as app_main
    return app_main.global_object


def knowledge_query(chatbot: gr.Chatbot, prompt: str):
    if not prompt:
        return chatbot, '', ''
    
    result = get_global_object().doc_qa({"query": prompt})
    
    completion = result["result"]
    chatbot.append((prompt, completion))

    source_docs = ''
    for source_doc in result["source_documents"]:
        source_docs += f'🎯 {source_doc.page_content}\n\n📕 [{source_doc.metadata["source"]}]({source_doc.metadata["source"]})\n\n'

    return chatbot, '', source_docs


def _save_files(dir, files):
    if not os.path.exists(dir):
        os.makedirs(dir, exist_ok=True)

    output_files = []
    for file in files:
        filename = os.path.basename(file.name)
        source_file = file.name
        target_file = f'{dir}/{filename}'

        shutil.copy(source_file, target_file)
        output_files.append(target_file)

    return output_files

def _upload_files(dir, files, add_files_func):
    saved_file_paths = _save_files(dir, files)
    for file_path in saved_file_paths:
        file_deduplication = get_global_object().file_deduplication
        file_hash = file_deduplication.get_file_hash(file_path)
        if not file_deduplication.is_duplicated(file_hash):
            add_files_func([file_path])
            file_deduplication.set(file_hash, file_path)
            print(f'upload_files add {file_path}')
        else:
            print(f'upload_files duplicated {file_path}')

def upload_docs(doc_files):
    _upload_files(get_global_object().config.UPLOADED_DOC_FILES_DIRECTORY, doc_files, get_global_object().vs_docs.add_files)

def upload_images(image_files):
    _upload_files(get_global_object().config.UPLOADED_IMAGE_FILES_DIRECTORY, image_files, get_global_object().vs_images.add_files_with_image)


def translate_zh2en(text):
    from ..models.translate import TranslateModel
    translator = TranslateModel()
    return translator(text)


def search_image_query(search_image_textbox, search_image):
    if search_image_textbox:
        vector = get_global_object().search_image_model.get_text_features(search_image_textbox)
        images = get_global_object().vs_images.similarity_search_by_vector(vector)
    elif np.any(search_image):
        vector = get_global_object().search_image_model.get_image_features_with_ndarray(search_image)
        images = get_global_object().vs_images.similarity_search_by_vector(vector)
    else:
        return []

    return images


def gallery_select_image(gallery, evt: gr.SelectData):
    return gallery[evt.index]['name'], ''
