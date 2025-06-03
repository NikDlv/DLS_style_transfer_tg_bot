import argparse
from pathlib import Path

import torch
import torch.nn as nn
from PIL import Image
from torchvision import transforms
from torchvision.utils import save_image
from io import BytesIO

def test_transform(size, crop):
    transform_list = []
    if size != 0:
        transform_list.append(transforms.Resize(size))
    if crop:
        transform_list.append(transforms.CenterCrop(size))
    transform_list.append(transforms.ToTensor())
    transform = transforms.Compose(transform_list)
    return transform



transform = transforms.Compose([
    transforms.Resize(512),
    transforms.ToTensor()
])

def load_image(image_bytes):
    image = Image.open(BytesIO(image_bytes)).convert("RGB")
    return transform(image)