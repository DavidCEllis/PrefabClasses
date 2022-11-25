"""Tests for the behaviour of __init__"""
from pathlib import Path

from pytest import raises


def test_basic(importer):
    from init_ex import Coordinate

    x = Coordinate(1, 2)

    assert (x.x, x.y) == (1, 2)


def test_basic_kwargs(importer):
    from init_ex import Coordinate

    x = Coordinate(x=1, y=2)

    assert (x.x, x.y) == (1, 2)


def test_kw_only(importer):
    from init_ex import KWCoordinate

    # Check the typeerror is raised for
    # trying to use positional arguments
    with raises(TypeError):
        x = KWCoordinate(1, 2)

    x = KWCoordinate(x=1, y=2)
    assert (x.x, x.y) == (1, 2)


def test_init_exclude(importer):
    from init_ex import CoordinateFixedY

    x = CoordinateFixedY(x=1)
    assert (x.x, x.y) == (1, 2)


def test_basic_with_defaults(importer):
    from init_ex import CoordinateDefaults

    x = CoordinateDefaults()
    assert (x.x, x.y) == (0, 0)

    y = CoordinateDefaults(y=5)
    assert (y.x, y.y) == (0, 5)


def test_mutable_defaults_bad(importer):
    """Test mutable defaults behave as they would in a regular class"""

    from init_ex import MutableDefault

    mut1 = MutableDefault()
    mut2 = MutableDefault()

    # Check the lists are the same object
    assert mut1.x is mut2.x


def test_default_factory_good(importer):
    from init_ex import FactoryDefault

    mut1 = FactoryDefault()
    mut2 = FactoryDefault()

    # Check the attribute is a list and is not the same list for different instances
    assert isinstance(mut1.x, list)
    assert mut1.x is not mut2.x


def test_no_default(importer):
    from init_ex import Coordinate

    with raises(TypeError) as e_info:
        x = Coordinate(1)

    # Because the __init__ function is defined outside of the class then added for live
    # prefabs, it does not inlude the class name while Compiled prefabs do.
    if importer:
        error_message = (
            "Coordinate.__init__() missing 1 required positional argument: 'y'"
        )
    else:
        error_message = "__init__() missing 1 required positional argument: 'y'"
    assert e_info.value.args[0] == error_message


def test_difficult_defaults(importer):
    from init_ex import Settings

    x = Settings()

    assert x.output_file == Path("Settings.json")


def test_pre_init(importer):
    from init_ex import PreInitExample

    x = PreInitExample()
    assert hasattr(x, "pre_init_ran")


def test_post_init(importer):
    from init_ex import PostInitExample

    x = PostInitExample()
    assert hasattr(x, "post_init_ran")


def test_replace_factory_default(importer):
    from init_ex import FactoryDefault

    mut1 = FactoryDefault(x=[1, 2, 3])
    assert mut1.x == [1, 2, 3]
