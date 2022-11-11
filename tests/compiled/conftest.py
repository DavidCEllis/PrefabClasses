import sys
import shutil
from pathlib import Path

import pytest

from prefab_classes import insert_prefab_importhook, remove_prefab_importhook


@pytest.fixture(scope="module", autouse=True)
def import_hook():
    insert_prefab_importhook()
    target_path = Path(__file__).parent / "compile_targets"

    compiled_data = target_path / "__pycache__"
    if compiled_data.exists():
        shutil.rmtree(compiled_data)

    sys.path.append(str(target_path))
    yield
    sys.path.remove(str(target_path))
    remove_prefab_importhook()