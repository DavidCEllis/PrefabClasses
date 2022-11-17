"""Tests that Prefabs handle inheritance as expected"""
from prefab_classes import prefab, attribute


def test_basic_inheritance():
    @prefab
    class Coordinate:
        x = attribute()
        y = attribute()

    @prefab
    class Coordinate3D(Coordinate):
        z = attribute()

    x = Coordinate3D(1, 2, 3)

    assert (x.x, x.y, x.z) == (1, 2, 3)


def test_multiple_inheritance():
    @prefab
    class Coordinate:
        x = attribute()
        y = attribute()

    @prefab
    class CoordinateZ:
        z = attribute()

    @prefab
    class Coordinate3D(CoordinateZ, Coordinate):
        pass

    x = Coordinate3D(1, 2, 3)

    assert (x.x, x.y, x.z) == (1, 2, 3)


def test_layered_inheritance():
    @prefab
    class Coordinate:
        x = attribute()
        y = attribute()

    @prefab
    class Coordinate3D(Coordinate):
        z = attribute()

    @prefab
    class CoordinateTime:
        t = attribute()

    @prefab
    class Coordinate4D(CoordinateTime, Coordinate3D):
        pass

    x = Coordinate4D(1, 2, 3, 4)

    assert (x.x, x.y, x.z, x.t) == (1, 2, 3, 4)


def test_mixed_definition_inheritance():
    @prefab
    class Coordinate:
        x: float
        y: float

    @prefab
    class Coordinate3D(Coordinate):
        z = attribute(default=0.0)

    coord = Coordinate3D(1.0, 2.0)

    assert (coord.x, coord.y, coord.z) == (1.0, 2.0, 0.0)
