import os

import sys,os
sys.path.append(os.getcwd())

from typing import List
from langchain.docstore.document import Document
from langchain.chains import RetrievalQA
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.vectorstores import Milvus

from langchain.document_loaders import CSVLoader
from langchain.document_loaders import TextLoader
from langchain.document_loaders import UnstructuredWordDocumentLoader
from langchain.document_loaders import UnstructuredEPubLoader
from langchain.document_loaders import UnstructuredHTMLLoader
from langchain.document_loaders import UnstructuredMarkdownLoader
from langchain.document_loaders import UnstructuredODTLoader
from langchain.document_loaders import PyMuPDFLoader
from langchain.document_loaders import UnstructuredPowerPointLoader


LOADER_MAPPING = {
    ".csv": (CSVLoader, {}),
    ".doc": (UnstructuredWordDocumentLoader, {}),
    ".docx": (UnstructuredWordDocumentLoader, {}),
    ".epub": (UnstructuredEPubLoader, {}),
    ".html": (UnstructuredHTMLLoader, {}),
    ".md": (UnstructuredMarkdownLoader, {}),
    ".odt": (UnstructuredODTLoader, {}),
    ".pdf": (PyMuPDFLoader, {}),
    ".ppt": (UnstructuredPowerPointLoader, {}),
    ".pptx": (UnstructuredPowerPointLoader, {}),
    ".txt": (TextLoader, {"encoding": "utf8"}),
}


class VectorStore:
    def __init__(self, config, embeddings):
        self.config = config
        self.embeddings = embeddings
        self.vector_store = None

    def load_document(self, file_path) -> List[Document]:
        _, ext_name = os.path.splitext(file_path.lower())
        if ext_name in LOADER_MAPPING:
            loader_class, loader_kwargs = LOADER_MAPPING[ext_name]
            loader = loader_class(file_path, **loader_kwargs)

            if ext_name in ['.pdf', '.doc', '.docx', '.ppt', '.pptx', '.epub']:
                return loader.load_and_split() # split into pages
            else:
                return loader.load()
        
        raise ValueError(f"Unsupported file extension '{ext_name}', file_path: {file_path}")
    
    def load_documents(self, file_paths) -> List[Document]:
        documents = []
        for file_path in file_paths:
            documents.extend(self.load_document(file_path))
        return documents
    
    def process_documents(self, file_paths):
        documents = self.load_documents(file_paths)
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=self.config.TEXT_CHUNK_SIZE, 
                                                       chunk_overlap=self.config.TEXT_CHUNK_OVERLAP)
        texts = text_splitter.split_documents(documents)
        for text in texts:
            print(f'🚗 process_documents {text.page_content}')
        print(f"Split into {len(texts)} chunks of text (max. {self.config.TEXT_CHUNK_SIZE} tokens each)")
        return texts

    def add_files(self, file_paths):
        texts = self.process_documents(file_paths)
        self.vector_store.add_documents(texts)

    # def add_files_with_image(self, dir):
    #     images = self._get_images(dir)
    #     filenames = []
    #     for image in images:
    #         filename = f'{dir}/{image}'
    #         filenames.append(filename)
        
    #     self.vector_store.add_texts(filenames)

    def add_files_with_image(self, file_paths):
        self.vector_store.add_texts(file_paths)

    def _get_images(self, path):
        image_paths = []

        ext_names = ['.png', '.jpg', '.jpeg']

        for filename in os.listdir(path):
            _, ext_name = os.path.splitext(filename)
            if ext_name.lower() in ext_names:
                image_paths.append(filename)

        return image_paths

    def delete(self):
        import shutil
        shutil.rmtree(self.vector_store._persist_directory, ignore_errors=True)

    def get_qa(self, llm, doc_k=4):
        return RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", 
                                           retriever=self.vector_store.as_retriever(search_kwargs={'k': doc_k}), 
                                           return_source_documents=True)

    def similarity_search_by_vector(self, vector, k=60):
        docs = self.vector_store.similarity_search_by_vector(vector, k=k)
        filenames = []
        for doc in docs:
            filenames.append(doc.page_content)
        return filenames
    
    @staticmethod
    def create_with_chroma_docs(config, embeddings):
        vs = VectorStore(config=config, embeddings=embeddings)
        vs.vector_store = Chroma(persist_directory=config.VECTORSTORE_DOCS_PATH, 
                                 embedding_function=embeddings)
        return vs
    
    @staticmethod
    def create_with_chroma_images(config, embeddings):
        vs = VectorStore(config=config, embeddings=embeddings)
        vs.vector_store = Chroma(persist_directory=config.VECTORSTORE_IMAGES_PATH, 
                                 embedding_function=embeddings)
        return vs

    @staticmethod
    def create_with_milvus(config, embeddings):
        vs = VectorStore(config=config, embeddings=embeddings)
        vs.vector_store = Milvus(embedding_function=vs.embeddings, 
                                 collection_name=config.COLLECTION_NAME, 
                                 connection_args={"host": config.MILVUS_HOST, "port": config.MILVUS_PORT})
        return vs
    

if __name__ == '__main__':
    from app.config import Config
    from app.models.search_image import SearchImageModel
    from app.embeddings.clip_embeddings import ClipEmbeddings

    config = Config()
    search_image_model = SearchImageModel()
    search_image_model.load(config)

    clip_embeddings = ClipEmbeddings(search_image_model)
    vs = VectorStore.create_with_chroma_docs(config=config, embeddings=clip_embeddings)
    # vs.add_files_with_image('data/images')

    print(vs.vector_store._collection.count())

    embedding = search_image_model.get_image_features_with_path('data/images/20190128155421222575013.jpg')
    docs = vs.vector_store.similarity_search_by_vector(embedding, k=10)
    for doc in docs:
        print(doc.page_content)
    print()

    embedding = search_image_model.get_text_features('flower')
    docs = vs.vector_store.similarity_search_by_vector(embedding, k=10)
    for doc in docs:
        print(doc.page_content)
