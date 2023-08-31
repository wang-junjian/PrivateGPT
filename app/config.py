import os
import dotenv
dotenv.load_dotenv()

class Config:
    TITLE = None
    VERSION = None

    EMBEDDING_MODEL_NAME = None
    EMBEDDING_MODEL_CACHE_DIRECTORY = None

    LLM_NAME = None
    LLM_API_BASE = None
    LLM_STREAMING = False

    VECTORSTORE_PATH = None
    TEXT_CHUNK_SIZE = 500
    TEXT_CHUNK_OVERLAP = 50

    def __init__(self):
        self.TITLE = os.environ.get("TITLE")
        self.VERSION = os.environ.get("VERSION")

        self.EMBEDDING_MODEL_NAME = os.environ.get("EMBEDDING_MODEL_NAME")
        self.EMBEDDING_MODEL_CACHE_DIRECTORY = os.environ.get("EMBEDDING_MODEL_CACHE_DIRECTORY")

        self.LLM_NAME = os.environ.get("LLM_NAME")
        self.LLM_API_BASE = os.environ.get("LLM_API_BASE")
        self.LLM_STREAMING = bool(os.environ.get("LLM_STREAMING"))

        self.VECTORSTORE_PATH = os.environ.get("VECTORSTORE_PATH")
        self.TEXT_CHUNK_SIZE = int(os.environ.get("TEXT_CHUNK_SIZE"))
        self.TEXT_CHUNK_OVERLAP = int(os.environ.get("TEXT_CHUNK_OVERLAP"))

        self.MILVUS_HOST = os.environ.get("MILVUS_HOST")
        self.MILVUS_PORT = os.environ.get("MILVUS_PORT")
        self.COLLECTION_NAME = os.environ.get("COLLECTION_NAME")

        self.CLIP_MODEL = os.environ.get("CLIP_MODEL")
