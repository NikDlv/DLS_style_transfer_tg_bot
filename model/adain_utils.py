import torch
from utils.image_io import load_image
from torchvision import transforms


def calc_mean_std(feat, eps=1e-5):
    """
    Calculate the channel-wise mean and standard deviation of a feature tensor.

    Args:
        feat (Tensor): Input tensor
        eps (float): Small constant to avoid division by zero.

    Returns:
        Mean and standard deviation tensors.
    """
    size = feat.size()
    assert (len(size) == 4)
    N, C = size[:2]
    feat_var = feat.view(N, C, -1).var(dim=2) + eps
    feat_std = feat_var.sqrt().view(N, C, 1, 1)
    feat_mean = feat.view(N, C, -1).mean(dim=2).view(N, C, 1, 1)
    return feat_mean, feat_std


def adaptive_instance_normalization(content_feat, style_feat):
    """
    Apply Adaptive Instance Normalization to content features using style features.

    Args:
        content_feat (Tensor): Content features
        style_feat (Tensor): Style features

    Returns:
        Tensor: Stylized feature tensor of the same shape as content_feat.
    """
    assert (content_feat.size()[:2] == style_feat.size()[:2])
    size = content_feat.size()
    style_mean, style_std = calc_mean_std(style_feat)
    content_mean, content_std = calc_mean_std(content_feat)

    normalized_feat = (content_feat - content_mean.expand(
        size)) / content_std.expand(size)
    return normalized_feat * style_std.expand(size) + style_mean.expand(size)


def _calc_feat_flatten_mean_std(feat):
    """
    Flatten 3D feature map and compute per-channel mean and std.
    """
    assert (feat.size()[0] == 3)
    assert (isinstance(feat, torch.FloatTensor))
    feat_flatten = feat.view(3, -1)
    mean = feat_flatten.mean(dim=-1, keepdim=True)
    std = feat_flatten.std(dim=-1, keepdim=True)
    return feat_flatten, mean, std


def _mat_sqrt(x):
    """
    Compute the matrix square root using SVD.
    """
    U, D, V = torch.svd(x)
    return torch.mm(torch.mm(U, D.pow(0.5).diag()), V.t())


def coral(source, target):
    """
    Perform CORAL (Correlation Alignment) to match the color distribution of the source to the target.
    """

    source_f, source_f_mean, source_f_std = _calc_feat_flatten_mean_std(source)
    source_f_norm = (source_f - source_f_mean.expand_as(
        source_f)) / source_f_std.expand_as(source_f)
    source_f_cov_eye = \
        torch.mm(source_f_norm, source_f_norm.t()) + torch.eye(3)

    target_f, target_f_mean, target_f_std = _calc_feat_flatten_mean_std(target)
    target_f_norm = (target_f - target_f_mean.expand_as(
        target_f)) / target_f_std.expand_as(target_f)
    target_f_cov_eye = \
        torch.mm(target_f_norm, target_f_norm.t()) + torch.eye(3)

    source_f_norm_transfer = torch.mm(
        _mat_sqrt(target_f_cov_eye),
        torch.mm(torch.inverse(_mat_sqrt(source_f_cov_eye)),
                 source_f_norm)
    )

    source_f_transfer = (source_f_norm_transfer *
                         target_f_std.expand_as(source_f_norm) +
                         target_f_mean.expand_as(source_f_norm))

    return source_f_transfer.view(source.size())


def style_transfer(vgg, decoder, content, style, alpha):
    """
    Perform neural style transfer using AdaIN.
    """
    assert (0.0 <= alpha <= 1.0)
    content_f = vgg(content)
    style_f = vgg(style)
    feat = adaptive_instance_normalization(content_f, style_f)
    feat = feat * alpha + content_f * (1 - alpha)
    return decoder(feat)


def process_images(net, content_bytes, style_bytes, alpha, preserve_colors=False):
    """Perform style transfer on image bytes"""
    content = load_image(content_bytes)
    style = load_image(style_bytes)

    # Apply color preservation if needed
    if preserve_colors:
        style = coral(style, content)

    # Move to device and add batch dimension
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
