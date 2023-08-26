from langchain.chains import RetrievalQA
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma


class VectorStore:
    def __init__(self, config, embeddings):
        self.config = config
        self.embeddings = embeddings
        self.vectorstore = None

    def load(self):
        self.vectorstore = Chroma(persist_directory=self.config.VECTORSTORE_PATH, 
                             embedding_function=self.embeddings)

    def create_with_chroma(self, embeddings, text_file_path):
        texts = self._load_text_file(text_file_path)
        self.vectorstore = Chroma.from_documents(texts, self, embeddings, persist_directory=self.config.VECTORSTORE_PATH)

    def delete(self):
        import shutil
        shutil.rmtree(self.config.VECTORSTORE_PATH, ignore_errors=True)

    def _load_text_file(self, text_file_path):
        loader = TextLoader(text_file_path)
        documents = loader.load()
        text_splitter = CharacterTextSplitter(chunk_size=self.config.TEXT_CHUNK_SIZE, 
                                              chunk_overlap=self.config.TEXT_CHUNK_OVERLAP)
        texts = text_splitter.split_documents(documents)
        return texts

    def get_qa(self, llm, doc_k=4):
        return RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", 
                                           retriever=self.vectorstore.as_retriever(search_kwargs={'k': doc_k}), 
                                           return_source_documents=True)
