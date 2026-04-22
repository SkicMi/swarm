import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))



@pytest.fixture(autouse=True)
def reset_modules():
    import importlib
    for mod_name in list(sys.modules.keys()):
        if mod_name.startswith('src.'):
            importlib.reload(sys.modules[mod_name])
    yield
