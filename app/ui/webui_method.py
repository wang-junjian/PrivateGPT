import os
import shutil
import numpy as np
import gradio as gr

from app.config import Config
from app.models.llm import LLM
from app.models.embedding import EmbeddingModel
from app.models.search_image import SearchImageModel
from app.vectorstore import VectorStore
from app.embeddings.clip_embeddings import ClipEmbeddings


config = Config()

llm = LLM().load(config)
embeddings = EmbeddingModel().load(config)

vs_docs = VectorStore.create_with_chroma_docs(config=config, embeddings=embeddings)

search_image_model = SearchImageModel()
search_image_model.load(config)

clip_embeddings = ClipEmbeddings(search_image_model)
vs_images = VectorStore.create_with_chroma_images(config=config, embeddings=clip_embeddings)


def knowledge_query(chatbot: gr.Chatbot, prompt: str):
    if not prompt:
        return chatbot, '', ''
    
    qa = vs_docs.get_qa(llm=llm)
    result = qa({"query": prompt})
    
    completion = result["result"]
    chatbot.append((prompt, completion))

    source_docs = ''
    for source_doc in result["source_documents"]:
        source_docs += f'🟥 {source_doc.page_content}\n\n【来源文件】{source_doc.metadata["source"]}\n\n'

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

def upload_docs(doc_files):
    dir = 'data/upload_docs'
    saved_files = _save_files(dir, doc_files)
    for file in saved_files:
        vs_docs.add_file_with_txt(file)


def upload_images(image_files):
    dir = 'data/upload_images'
    saved_files = _save_files(dir, image_files)
    for file in saved_files:
        vs_images.add_file_with_image(file)


def translate_zh2en(text):
    from ..models.translate import TranslateModel
    translator = TranslateModel()
    print('*'*100, translator(text), text)
    return translator(text)


def search_image_query(search_image_textbox, search_image, is_translate):
    if search_image_textbox:
        if is_translate:
            search_image_textbox = translate_zh2en(search_image_textbox)
        vector = search_image_model.get_text_features(search_image_textbox)
        images = vs_images.similarity_search_by_vector(vector)
    elif np.any(search_image):
        vector = search_image_model.get_image_features_with_ndarray(search_image)
        images = vs_images.similarity_search_by_vector(vector)
    else:
        return [], ''

    return images, search_image_textbox


def gallery_select_image(gallery, evt: gr.SelectData):
    return gallery[evt.index]['name'], ''
