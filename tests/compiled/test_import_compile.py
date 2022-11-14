import pytest

from prefab_classes import prefab_compiler
from prefab_classes.exceptions import PrefabError


# noinspection PyUnresolvedReferences
def test_annotations():
    with prefab_compiler():
        from example_annotations import X

    assert X.COMPILED

    x = X(12, y="pints")

    assert repr(x) == "X(v=12, w=Decimal('3.14'), x=[], y='pints', z=(42, 'trees'))"


# noinspection PyUnresolvedReferences
def test_mixed_annotations():
    with prefab_compiler():
        from example_mixed_annotations import Y

    assert Y.COMPILED

    assert Y.PREFAB_FIELDS == ['w', 'x', 'y', 'z']

    y = Y(y="pints")

    assert repr(y) == "Y(w=Decimal('3.14'), x=[], y='pints', z=(42, 'trees'))"


# noinspection PyUnresolvedReferences
def test_no_annotations():
    with prefab_compiler():
        from example_no_annotations import Z

    assert Z.COMPILED

    assert Z.PREFAB_FIELDS == ['v', 'w', 'x', 'y', 'z']

    z = Z(12, y="pints")

    assert repr(z) == "Z(v=12, w=Decimal('3.14'), x=[], y='pints', z=(42, 'trees'))"


def test_not_compiled_error():
    with pytest.raises(PrefabError) as e_info:
        import example_importfail

    assert e_info.value.args[0] == "Class X has not been compiled! Dynamic code still executing!"