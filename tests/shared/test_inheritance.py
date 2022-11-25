"""Tests that Prefabs handle inheritance as expected"""
import pytest


def test_basic_inheritance(importer):
    from inheritance import Coordinate3D

    x = Coordinate3D(1, 2, 3)

    assert (x.x, x.y, x.z) == (1, 2, 3)


def test_layered_inheritance(importer):
    from inheritance import Coordinate4D

    x = Coordinate4D(1, 2, 3, 4)

    assert x.PREFAB_FIELDS == ["x", "y", "z", "t"]

    assert (x.x, x.y, x.z, x.t) == (1, 2, 3, 4)


def test_two_fields_one_default(importer):
    # Incorrect default argument order should still fail
    # even with inheritance
    with pytest.raises(SyntaxError):
        import fails.inheritance_1

    with pytest.raises(SyntaxError):
        import fails.inheritance_2
