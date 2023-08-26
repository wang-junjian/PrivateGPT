import numpy as np
import torch
from PIL import Image
from transformers import CLIPProcessor, CLIPModel


model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")


def get_images_from_path(path: str):
    import os
    images = []
    for filename in os.listdir(path):
        if filename.endswith(".jpg"):
            images.append(os.path.join(path, filename))
    return images


def get_image_feature_from_numpy(image_arr: np.ndarray):
    image = Image.fromarray(image_arr).convert("RGB")
    processed = processor(images=image, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        image_features = model.get_image_features(pixel_values=processed["pixel_values"])
    return image_features

def get_image_feature(filename: str):
    image = Image.open(filename).convert("RGB")
    processed = processor(images=image, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        image_features = model.get_image_features(pixel_values=processed["pixel_values"])
    return image_features

def get_image_features(images):
    image_features = []
    for image in images:
        image_feature = get_image_feature(image)
        image_features.append((image, image_feature))
    return image_features

def get_text_feature(text: str):
    processed = processor(text=text, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        text_features = model.get_text_features(processed['input_ids'])
    return text_features

def cosine_similarity(tensor1, tensor2):
    tensor1_normalized = tensor1 / tensor1.norm(dim=-1, keepdim=True)
    tensor2_normalized = tensor2 / tensor2.norm(dim=-1, keepdim=True)
    return (tensor1_normalized * tensor2_normalized).sum(dim=-1)


def get_images_with_similar_text(text, image_features):
    text_feature = get_text_feature(text)
    return get_images_with_similar(text_feature, image_features)


def get_images_with_similar_image(image_path, image_features):
    image_feature = get_image_feature(image_path)
    return get_images_with_similar(image_feature, image_features)


def get_images_with_similar(text_or_image_feature, image_features):
    image_path_and_similarities = []

    for image_path, image_feature in image_features:
        similarity = cosine_similarity(image_feature, text_or_image_feature)
        image_path_and_similarities.append((image_path, similarity))

    # image_path_and_similarities sorted by similarity
    image_path_and_similarities.sort(key=lambda x: x[1], reverse=True)

    images = []
    for image_path, similarity in image_path_and_similarities:
        images.append(image_path)

    return images


if __name__ == "__main__":
    images_dir = 'data/images'
    images_path = get_images_from_path(images_dir)
    image_features = get_image_features(images_path)
    
    text = "This are two persons."
    images = get_images_with_similar_text(text, image_features)
    print(images)

    text = "blue sky"
    images = get_images_with_similar_text(text, image_features)
    print(images)

    image = 'data/images/20190128155421222575013.jpg'
    image_feature = get_image_feature(image)
    images = get_images_with_similar_image(image, image_features)
    print(images)