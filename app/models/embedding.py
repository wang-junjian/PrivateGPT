from .model import Model

class EmbeddingModel(Model):
    def load(self, config):
        print(f'load {EmbeddingModel.__name__}')

        """
        Embeddings https://huggingface.co/
            BAAI/bge-base-zh
            sentence-transformers/paraphrase-multilingual-mpnet-base-v2
        """
        
        if config.EMBEDDING_MODEL_NAME == 'OpenAI':
            from langchain.embeddings import OpenAIEmbeddings
            embeddings = OpenAIEmbeddings()
        else:
            from langchain.embeddings import HuggingFaceEmbeddings
            encode_kwargs = {'normalize_embeddings': False}
            embeddings = HuggingFaceEmbeddings(model_name=config.EMBEDDING_MODEL_NAME, 
                                               cache_folder=config.EMBEDDING_MODEL_CACHE_DIRECTORY,
                                               encode_kwargs=encode_kwargs)
                    
        print('load_embedding_model', config.EMBEDDING_MODEL_NAME, config.EMBEDDING_MODEL_CACHE_DIRECTORY)

        self.model = embeddings
        return self.model
