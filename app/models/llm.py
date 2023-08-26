from .model import Model

class LLM(Model):
    def load(self, config):
        print(f'load {LLM.__name__}')

        """
        LLM https://huggingface.co/
            Qwen/Qwen-7B-Chat
            THUDM/chatglm2-6b
        """
        
        if config.LLM_NAME == 'OpenAI':
            from langchain.llms import OpenAI
            llm = OpenAI()
        elif config.LLM_NAME == 'ChatGLM':
            from langchain.llms import ChatGLM
            llm = ChatGLM(endpoint_url = config.LLM_API_BASE)
        else:
            from langchain.llms import OpenAIChat
            llm = OpenAIChat(model_name=config.LLM_NAME, 
                            openai_api_base=config.LLM_API_BASE, 
                            openai_api_key=None, 
                            streaming=config.LLM_STREAMING)

        print('load_llm', config.LLM_NAME, config.LLM_API_BASE, config.LLM_STREAMING)

        self.model = llm
        return self.model
