import pytest
from style_transfer import init_model


def test_init_model():
    models = init_model()
    assert models is not None
