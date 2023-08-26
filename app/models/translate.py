from transformers import pipeline

from .model import Model


class TranslateModel(Model):
    def load(self, config):
        print(f'load {TranslateModel.__name__}')
        self.model = pipeline("translation", model="./models/translation/Helsinki-NLP/opus-mt-zh-en")
    
    def __call__(self, text):
        try:
            result = self.model(text)
            text = result[0]['translation_text']
        except Exception as e:
            print(e)

        return text
    
    
if __name__ == "__main__":
    zh2en = TranslateModel()
    zh2en.load(None)
    print(zh2en("高空作业，背景是大海"))
