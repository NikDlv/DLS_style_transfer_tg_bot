import pytest
from utils.functional import init_model


def test_init_model():
    models = init_model()
    assert models is not None
