import torch
import torch.nn as nn
from model.adain_net import Decoder, VGG, Net


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

    # Load weights for fine-tuned models
    decoder_picasso.load_state_dict(torch.load('model_weights/decoder_picasso.pth', map_location=device))
    decoder_van_gogh.load_state_dict(torch.load('model_weights/decoder_van_gogh.pth', map_location=device))
    decoder_monet.load_state_dict(torch.load('model_weights/decoder_monet.pth', map_location=device))

    decoder_picasso.to(device).eval()
    decoder_van_gogh.to(device).eval()
    decoder_monet.to(device).eval()

    return (Net(vgg, decoder).to(device).eval(), Net(vgg, decoder_picasso).to(device).eval(),
            Net(vgg, decoder_van_gogh).to(device).eval(), Net(vgg, decoder_monet).to(device).eval())
