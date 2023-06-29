"""Test the non-init dunder methods"""
import pytest


def test_repr(importer):
    from dunders import Coordinate

    expected_repr = "Coordinate(x=1, y=2)"

    assert repr(Coordinate(1, 2)) == expected_repr


def test_repr_exclude(importer):
    from dunders import CoordinateNoXRepr

    expected_repr = "<prefab CoordinateNoXRepr; y=2>"
    assert repr(CoordinateNoXRepr(1, 2)) == expected_repr


def test_repr_init_exclude(importer):
    from dunders import NoXReprNoXInit

    x = NoXReprNoXInit()
    assert x._type == None

    expected_repr = "NoXReprNoXInit()"
    assert repr(NoXReprNoXInit()) == expected_repr


def test_iter():
    from dunders import CoordinateIter

    x = CoordinateIter(1, 2)

    y = list(x)
    assert y == [1, 2]


def test_eq(importer):
    from dunders import Coordinate4D

    x = Coordinate4D(1, 2, 3, 4)
    y = Coordinate4D(1, 2, 3, 4)

    assert (x.x, x.y, x.z, x.t) == (y.x, y.y, y.z, y.t)
    assert x == y


def test_neq(importer):
    from dunders import Coordinate4D

    x = Coordinate4D(1, 2, 3, 4)
    y = Coordinate4D(5, 6, 7, 8)

    assert (x.x, x.y, x.z, x.t) != (y.x, y.y, y.z, y.t)
    assert x != y


def test_match_args(importer):
    from dunders import Coordinate4D

    assert Coordinate4D.__match_args__ == ("x", "y", "z", "t")


def test_match_args_disabled(importer):
    from dunders import NoMatchArgs

    with pytest.raises(AttributeError):
        _ = NoMatchArgs.__match_args__


def test_dunders_not_overwritten(importer):
    from dunders import DundersExist

    x = DundersExist(0, 0)
    y = DundersExist(1, 1)

    # __match_args__
    assert DundersExist.__match_args__ == ("x",)

    # __init__
    assert (x.x, x.y) == (0, 0)
    assert (y.x, y.y) == (2, 3)

    # __repr__
    assert repr(x) == repr(y) == "NOT_REPLACED"

    # __eq__
    assert x == y

    # __iter__
    for item in y:
        assert item is y.x
