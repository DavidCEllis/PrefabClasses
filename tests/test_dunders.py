"""Test the non-init dunder methods"""
from prefab import Prefab, Attribute


def test_repr():
    class Coordinate(Prefab):
        x = Attribute()
        y = Attribute()

    expected_repr = "Coordinate(x=1, y=2)"

    assert repr(Coordinate(1, 2)) == expected_repr


def test_repr_exclude():
    class Coordinate(Prefab):
        x = Attribute(repr=False)
        y = Attribute()

    expected_repr = "Coordinate(y=2)"
    assert repr(Coordinate(1, 2) == expected_repr)


def test_iter():
    class Coordinate(Prefab):
        x = Attribute()
        y = Attribute()

    x = Coordinate(1, 2)

    y = list(x)
    assert y == [1, 2]


def test_eq():
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
    y = Coordinate4D(1, 2, 3, 4)

    assert (x.x, x.y, x.z, x.t) == (y.x, y.y, y.z, y.t)
    assert x == y


def test_neq():
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
    y = Coordinate4D(5, 6, 7, 8)

    assert (x.x, x.y, x.z, x.t) != (y.x, y.y, y.z, y.t)
    assert x != y
