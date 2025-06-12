import torch
import torch.nn as nn
from torchvision import transforms
from model.adain_net import Decoder, VGG, Net
from model.adain_utils import coral, style_transfer
from utils.image_io import load_image

def init_model():
    """Initialize and load style transfer model"""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    decoder = Decoder()
    vgg = VGG()

    # Load weights
    decoder.model.load_state_dict(torch.load('model_weights/decoder.pth', map_location=device))
    vgg.model.load_state_dict(torch.load('model_weights/vgg_normalised.pth', map_location=device))
    
    # Configure models
    vgg = nn.Sequential(*list(vgg.model.children())[:31])
    vgg.to(device).eval()
    decoder.to(device).eval()

    decoder_picasso = Decoder()
    decoder_van_gogh = Decoder()
    decoder_monet = Decoder()

    decoder_picasso.load_state_dict(torch.load('model_weights/decoder_picasso.pth', map_location=device))
    decoder_van_gogh.load_state_dict(torch.load('model_weights/decoder_van_gogh.pth', map_location=device))
    decoder_monet.load_state_dict(torch.load('model_weights/decoder_monet.pth', map_location=device))

    decoder_picasso.to(device).eval()
    decoder_van_gogh.to(device).eval()
    decoder_monet.to(device).eval()

    
    return Net(vgg, decoder).to(device).eval(), Net(vgg, decoder_picasso).to(device).eval(), \
           Net(vgg, decoder_van_gogh).to(device).eval(), Net(vgg, decoder_monet).to(device).eval()

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