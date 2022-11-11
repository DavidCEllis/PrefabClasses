"""Tests for the behaviour of __init__"""
from pathlib import Path

from prefab_classes import prefab, attribute
from smalltest.tools import raises


def test_basic():
    @prefab
    class Coordinate:
        x = attribute()
        y = attribute()

    x = Coordinate(1, 2)

    assert (x.x, x.y) == (1, 2)


def test_basic_kwargs():
    @prefab
    class Coordinate:
        x = attribute()
        y = attribute()

    x = Coordinate(x=1, y=2)

    assert (x.x, x.y) == (1, 2)


def test_kw_only():
    @prefab
    class Coordinate:
        x = attribute()
        y = attribute(kw_only=True)

    # Check the typeerror is raised for trying to use y as a positional argument
    with raises(TypeError):
        x = Coordinate(1, 2)

    x = Coordinate(1, y=2)
    assert (x.x, x.y) == (1, 2)


def test_only_kw_only():
    @prefab
    class Coordinate:
        x = attribute(kw_only=True)
        y = attribute(kw_only=True)

    # Check the typeerror is raised for trying to use y as a positional argument
    with raises(TypeError):
        x = Coordinate(1, 2)

    x = Coordinate(x=1, y=2)
    assert (x.x, x.y) == (1, 2)


def test_init_exclude():
    @prefab
    class Coordinate:
        x = attribute()
        y = attribute(default=2, init=False)

    x = Coordinate(x=1)
    assert (x.x, x.y) == (1, 2)


def test_basic_with_defaults():
    @prefab
    class Coordinate:
        x = attribute(default=0)
        y = attribute(default=0)

    x = Coordinate()
    assert (x.x, x.y) == (0, 0)

    y = Coordinate(y=5)
    assert (y.x, y.y) == (0, 5)


def test_mutable_defaults_bad():
    """Test mutable defaults behave as they would in a regular class"""

    @prefab
    class MutableDefault:
        x = attribute(default=list())

    mut1 = MutableDefault()
    mut2 = MutableDefault()

    # Check the lists are the same object
    assert mut1.x is mut2.x


def test_default_factory_good():
    @prefab
    class FactoryDefault:
        x = attribute(default_factory=list)

    mut1 = FactoryDefault()
    mut2 = FactoryDefault()

    # Check the attribute is a list and is not the same list for different instances
    assert isinstance(mut1.x, list)
    assert mut1.x is not mut2.x


def test_no_default():
    @prefab
    class Coordinate:
        x = attribute()
        y = attribute()

    with raises(TypeError) as e_info:
        x = Coordinate(1)

    error_message = "__init__() missing 1 required positional argument: 'y'"
    assert e_info.value.args[0] == error_message


def test_difficult_defaults():
    @prefab
    class Settings:
        """
        Global persistent settings handler
        """

        output_file = attribute(default=Path("Settings.json"))

    x = Settings()

    assert x.output_file == Path("Settings.json")
