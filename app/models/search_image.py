import torch
import numpy as np
from PIL import Image
from transformers import AutoTokenizer, CLIPProcessor, CLIPModel

from .model import Model

class SearchImageModel(Model):

    def load(self, config):
        print(f'load {SearchImageModel.__name__}')

        self.model = CLIPModel.from_pretrained(config.CLIP_MODEL, cache_dir=config.CLIP_MODEL_CACHE_DIRECTORY, local_files_only=True)
        self.processor = CLIPProcessor.from_pretrained(config.CLIP_MODEL, cache_dir=config.CLIP_MODEL_CACHE_DIRECTORY, local_files_only=True)
        self.tokenizer = AutoTokenizer.from_pretrained(config.CLIP_MODEL, cache_dir=config.CLIP_MODEL_CACHE_DIRECTORY, local_files_only=True)

    def _get_image_features(self, image: Image):
        inputs = self.processor(images=image, return_tensors="pt", padding=True, truncation=True)
        # features = self.model.get_image_features(**inputs)
        # return features
        with torch.no_grad():
            features = self.model.get_image_features(pixel_values=inputs["pixel_values"])
        # features = features / features.norm(dim=-1, keepdim=True)
        features /= np.linalg.norm(features)
        return features.tolist()[0]
    
    def get_image_features_with_path(self, image_path: str):
        image = Image.open(image_path).convert("RGB")
        return self._get_image_features(image)
    
    def get_image_features_with_ndarray(self, image_arr: np.ndarray):
        image = Image.fromarray(image_arr).convert("RGB")
        return self._get_image_features(image)

    def get_text_features(self, text: str):
        inputs = self.tokenizer(text, return_tensors="pt")
        # features = self.model.get_text_features(**inputs)
        # return features
        with torch.no_grad():
            features = self.model.get_text_features(inputs['input_ids'])
        # features /= features.norm(dim=-1, keepdim=True)
        features /= np.linalg.norm(features)
        return features.tolist()[0]
