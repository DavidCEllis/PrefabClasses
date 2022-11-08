"""Tests that Prefabs handle inheritance as expected"""
from prefab_classes import prefab, Attribute


def test_basic_inheritance():

    @prefab
    class Coordinate:
        x = Attribute()
        y = Attribute()

    @prefab
    class Coordinate3D(Coordinate):
        z = Attribute()

    x = Coordinate3D(1, 2, 3)

    assert (x.x, x.y, x.z) == (1, 2, 3)


def test_multiple_inheritance():

    @prefab
    class Coordinate:
        x = Attribute()
        y = Attribute()

    @prefab
    class CoordinateZ:
        z = Attribute()

    @prefab
    class Coordinate3D(CoordinateZ, Coordinate):
        pass

    x = Coordinate3D(1, 2, 3)

    assert (x.x, x.y, x.z) == (1, 2, 3)


def test_layered_inheritance():
    @prefab
    class Coordinate:
        x = Attribute()
        y = Attribute()

    @prefab
    class Coordinate3D(Coordinate):
        z = Attribute()

    @prefab
    class CoordinateTime:
        t = Attribute()

    @prefab
    class Coordinate4D(CoordinateTime, Coordinate3D):
        pass

    x = Coordinate4D(1, 2, 3, 4)

    assert (x.x, x.y, x.z, x.t) == (1, 2, 3, 4)
