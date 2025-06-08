import torch
import torch.nn as nn
from torchvision import transforms
from models.adain_net import vgg, decoder, Net
from models.adain_utils import coral, style_transfer
from utils.image_io import load_image

def init_model():
    """Initialize and load style transfer model"""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    decoder_model = decoder
    vgg_model = vgg

    # Load weights
    decoder_model.load_state_dict(torch.load('models_weights/decoder.pth'))
    vgg_model.load_state_dict(torch.load('models_weights/vgg_normalised.pth'))
    
    # Configure models
    vgg_model = nn.Sequential(*list(vgg_model.children())[:31])
    vgg_model.to(device).eval()
    decoder_model.to(device).eval()
    
    return Net(vgg_model, decoder_model).to(device).eval()

def process_images(net, content_bytes, style_bytes, alpha, preserve_colors=False):
    """Perform style transfer on image bytes"""
    content = load_image(content_bytes)
    style = load_image(style_bytes)
    
    # Apply color preservation if needed
    if preserve_colors:
        style = coral(style, content)
    
    # Move to GPU and add batch dimension
    device = next(net.parameters()).device
    content = content.to(device).unsqueeze(0)
    style = style.to(device).unsqueeze(0)
    
    # Perform style transfer
    with torch.no_grad():
        output = style_transfer(
            net.encode, 
            net.decoder, 
            content, 
            style, 
            alpha=alpha
        )
    
    # Convert to PIL image
    output = output.clamp(0, 1)
    return transforms.ToPILImage()(output.squeeze(0).cpu())