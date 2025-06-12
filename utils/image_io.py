from PIL import Image
from torchvision import transforms
from io import BytesIO

transform = transforms.Compose([
    transforms.Resize(512),
    transforms.ToTensor()
])


def load_image(image_bytes):
    image = Image.open(BytesIO(image_bytes)).convert("RGB")
    return transform(image)
