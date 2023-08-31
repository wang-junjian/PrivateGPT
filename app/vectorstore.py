import os

import sys,os
sys.path.append(os.getcwd())

from langchain.chains import RetrievalQA
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.vectorstores import Milvus


class VectorStore:
    def __init__(self, config, embeddings):
        self.config = config
        self.embeddings = embeddings
        self.vector_store = None

    def add_files(self, file_paths):
        for file_path in file_paths:
            self.add_file_with_txt(file_path)

    def add_file_with_txt(self, file_path):
        loader = TextLoader(file_path)
        documents = loader.load()
        text_splitter = CharacterTextSplitter(chunk_size=self.config.TEXT_CHUNK_SIZE, 
                                              chunk_overlap=self.config.TEXT_CHUNK_OVERLAP)
        texts = text_splitter.split_documents(documents)
        self.vector_store.add_documents(texts)

    def add_files_with_image(self, dir):
        images = self._get_images(dir)
        filenames = []
        for image in images:
            filename = f'{dir}/{image}'
            filenames.append(filename)
        
        self.vector_store.add_texts(filenames)

    def add_file_with_image(self, filename):
        self.vector_store.add_texts([filename])

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
        shutil.rmtree(self.config.VECTORSTORE_PATH, ignore_errors=True)

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
    def create_with_chroma(config, embeddings):
        vs = VectorStore(config=config, embeddings=embeddings)
        vs.vector_store = Chroma(persist_directory=config.VECTORSTORE_PATH, 
                                 embedding_function=embeddings)
        return vs
    
    @staticmethod
    def create_with_chroma_docs(config, embeddings):
        vs = VectorStore(config=config, embeddings=embeddings)
        vs.vector_store = Chroma(persist_directory='vectorstore/chroma_docs', 
                                 embedding_function=embeddings)
        return vs
    
    @staticmethod
    def create_with_chroma_images(config, embeddings):
        vs = VectorStore(config=config, embeddings=embeddings)
        vs.vector_store = Chroma(persist_directory='vectorstore/chroma_images', 
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
    vs = VectorStore.create_with_chroma(config=config, embeddings=clip_embeddings)
    vs.add_files_with_image('data/images')

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
