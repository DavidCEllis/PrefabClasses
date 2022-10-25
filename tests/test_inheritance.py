"""Tests that Prefabs handle inheritance as expected"""
from prefab import Prefab, Attribute


def test_basic_inheritance():
    class Coordinate(Prefab):
        x = Attribute()
        y = Attribute()

    class Coordinate3D(Coordinate):
        z = Attribute()

    x = Coordinate3D(1, 2, 3)

    assert (x.x, x.y, x.z) == (1, 2, 3)


def test_multiple_inheritance():
    class Coordinate(Prefab):
        x = Attribute()
        y = Attribute()

    class CoordinateZ(Prefab):
        z = Attribute()

    class Coordinate3D(CoordinateZ, Coordinate):
        pass

    x = Coordinate3D(1, 2, 3)

    assert (x.x, x.y, x.z) == (1, 2, 3)


def test_layered_inheritance():
    class Coordinate(Prefab):
        x = Attribute()
        y = Attribute()

    class Coordinate3D(Coordinate):
        z = Attribute()

    class CoordinateTime(Prefab):
        t = Attribute()

    class Coordinate4D(CoordinateTime, Coordinate3D):
        pass

    x = Coordinate4D(1, 2, 3, 4)

    assert (x.x, x.y, x.z, x.t) == (1, 2, 3, 4)
