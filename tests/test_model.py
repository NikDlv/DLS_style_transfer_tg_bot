from utils.functional import init_model
from model.adain_utils import process_images


def test_init_model():
    models = init_model()
    assert models is not None


def test_style_transfer_runs():
    net, net_picasso, net_van_gogh, net_monet = init_model()

    with open("test_images/content/dancing.jpg", "rb") as f:
        content_bytes = f.read()

    with open("test_images/style/picasso.jpg", "rb") as f:
        style_bytes_picasso = f.read()

    with open("test_images/style/van_gogh.jpg", "rb") as f:
        style_bytes_van_gogh = f.read()

    with open("test_images/style/monet.jpg", "rb") as f:
        style_bytes_monet = f.read()

    result_image = process_images(
        net=net,
        content_bytes=content_bytes,
        style_bytes=style_bytes_picasso,
        preserve_colors=False,
        alpha=1.0
    )
    assert result_image is not None

    result_image_preserve_colors = process_images(
        net=net,
        content_bytes=content_bytes,
        style_bytes=style_bytes_picasso,
        preserve_colors=True,
        alpha=1.0
    )
    assert result_image_preserve_colors is not None

    result_image_picasso = process_images(
        net=net_picasso,
        content_bytes=content_bytes,
        style_bytes=style_bytes_picasso,
        preserve_colors=False,
        alpha=1.0
    )
    assert result_image_picasso is not None

    result_image_van_gogh = process_images(
        net=net_van_gogh,
        content_bytes=content_bytes,
        style_bytes=style_bytes_van_gogh,
        preserve_colors=False,
        alpha=1.0
    )
    assert result_image_van_gogh is not None

    result_image_monet = process_images(
        net=net_monet,
        content_bytes=content_bytes,
        style_bytes=style_bytes_monet,
        preserve_colors=False,
        alpha=1.0
    )
    assert result_image_monet is not None
