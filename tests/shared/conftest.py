import sys
import shutil
from pathlib import Path

import pytest


def clear_relative_modules(base_path):
    """
    Remove any modules relative to base_path from sys.modules

    :param base_path:
    :return:
    """
    for name, module in sys.modules.copy().items():
        pth = getattr(module, "__file__", None)
        if pth:
            pth = Path(pth)
            if pth.is_relative_to(base_path):
                del sys.modules[name]


def clear_pycache(base_path):
    """Clear __pycache__ for a base_path if it exists"""
    compiled_data = base_path / "__pycache__"
    if compiled_data.exists():
        shutil.rmtree(compiled_data)


@pytest.fixture(scope="module", autouse=True)
def example_modules():
    # Folder with test examples to compile
    base_path = Path(__file__).parent / "examples"

    # Clean out any loaded modules
    clear_relative_modules(base_path)
    clear_pycache(base_path)

    # Add test folder to path temporarily
    sys.path.append(str(base_path))
    try:
        yield
    finally:
        sys.path.remove(str(base_path))

    clear_pycache(base_path)
    clear_relative_modules(base_path)
