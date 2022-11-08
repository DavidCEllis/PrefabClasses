"""Test the non-init dunder methods"""
from prefab_classes import prefab, Attribute


def test_repr():
    @prefab
    class Coordinate:
        x = Attribute()
        y = Attribute()

    expected_repr = "Coordinate(x=1, y=2)"

    assert repr(Coordinate(1, 2)) == expected_repr


def test_repr_exclude():
    @prefab
    class Coordinate:
        x = Attribute(repr=False)
        y = Attribute()

    expected_repr = "Coordinate(y=2)"
    assert repr(Coordinate(1, 2) == expected_repr)


def test_iter():
    @prefab
    class Coordinate:
        x = Attribute()
        y = Attribute()

    x = Coordinate(1, 2)

    y = list(x)
    assert y == [1, 2]


def test_eq():
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
    y = Coordinate4D(1, 2, 3, 4)

    assert (x.x, x.y, x.z, x.t) == (y.x, y.y, y.z, y.t)
    assert x == y


def test_neq():
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
    y = Coordinate4D(5, 6, 7, 8)

    assert (x.x, x.y, x.z, x.t) != (y.x, y.y, y.z, y.t)
    assert x != y
