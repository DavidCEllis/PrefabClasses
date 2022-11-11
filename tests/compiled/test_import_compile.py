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


# noinspection PyUnresolvedReferences
def test_annotations():
    from example_annotations import X

    assert X.COMPILED

    x = X(12, y="pints")

    assert repr(x) == "X(v=12, w=Decimal('3.14'), x=[], y='pints', z=(42, 'trees'))"


# noinspection PyUnresolvedReferences
def test_mixed_annotations():
    from example_mixed_annotations import Y

    assert Y.COMPILED

    assert Y.PREFAB_FIELDS == ['w', 'x', 'y', 'z']

    y = Y(y="pints")

    assert repr(y) == "Y(w=Decimal('3.14'), x=[], y='pints', z=(42, 'trees'))"


# noinspection PyUnresolvedReferences
def test_no_annotations():
    from example_no_annotations import Z

    assert Z.COMPILED

    assert Z.PREFAB_FIELDS == ['v', 'w', 'x', 'y', 'z']

    z = Z(12, y="pints")

    assert repr(z) == "Z(v=12, w=Decimal('3.14'), x=[], y='pints', z=(42, 'trees'))"
