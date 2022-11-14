import sys
import shutil
from pathlib import Path

import pytest


@pytest.fixture(scope="module", autouse=True)
def compile_folder_path():
    # Folder with test examples to compile
    target_path = Path(__file__).parent / "compile_targets"

    # Clean out any cached .pyc files
    compiled_data = target_path / "__pycache__"
    if compiled_data.exists():
        shutil.rmtree(compiled_data)

    # Add test folder to path temporarily
    sys.path.append(str(target_path))
    try:
        yield
    finally:
        sys.path.remove(str(target_path))
