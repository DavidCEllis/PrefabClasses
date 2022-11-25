"""Tests that Prefabs handle inheritance as expected"""


def test_basic_inheritance(importer):
    from inheritance import Coordinate3D

    x = Coordinate3D(1, 2, 3)

    assert (x.x, x.y, x.z) == (1, 2, 3)


def test_layered_inheritance(importer):
    from inheritance import Coordinate4D

    x = Coordinate4D(1, 2, 3, 4)

    assert x.PREFAB_FIELDS == ["x", "y", "z", "t"]

    assert (x.x, x.y, x.z, x.t) == (1, 2, 3, 4)
