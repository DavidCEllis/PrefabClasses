"""Test the non-init dunder methods"""
from prefab_classes import prefab, attribute


def test_repr():
    @prefab
    class Coordinate:
        x = attribute()
        y = attribute()

    expected_repr = "Coordinate(x=1, y=2)"

    assert repr(Coordinate(1, 2)) == expected_repr


def test_repr_exclude():
    @prefab
    class Coordinate:
        x = attribute(repr=False)
        y = attribute()

    expected_repr = "Coordinate(y=2)"
    assert repr(Coordinate(1, 2) == expected_repr)


def test_iter():
    @prefab(iter=True)
    class Coordinate:
        x = attribute()
        y = attribute()

    x = Coordinate(1, 2)

    y = list(x)
    assert y == [1, 2]


def test_eq():
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
    y = Coordinate4D(1, 2, 3, 4)

    assert (x.x, x.y, x.z, x.t) == (y.x, y.y, y.z, y.t)
    assert x == y


def test_neq():
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
    y = Coordinate4D(5, 6, 7, 8)

    assert (x.x, x.y, x.z, x.t) != (y.x, y.y, y.z, y.t)
    assert x != y
