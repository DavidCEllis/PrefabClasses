from prefab import Prefab, Attribute, PrefabError, NotPrefabClassError

try:  # pragma: nocover
    from pytest import raises
except ImportError:  # pragma: nocover
    from smalltest.tools import raises

from pathlib import Path


def test_basic():
    class Coordinate(Prefab):
        x = Attribute()
        y = Attribute()

    x = Coordinate(1, 2)

    assert (x.x, x.y) == (1, 2)


def test_basic_kwargs():
    class Coordinate(Prefab):
        x = Attribute()
        y = Attribute()

    x = Coordinate(x=1, y=2)

    assert (x.x, x.y) == (1, 2)


def test_kw_only():
    class Coordinate(Prefab):
        x = Attribute()
        y = Attribute(kw_only=True)

    # Check the typeerror is raised for trying to use y as a positional argument
    with raises(TypeError):
        x = Coordinate(1, 2)

    x = Coordinate(1, y=2)
    assert (x.x, x.y) == (1, 2)


def test_only_kw_only():

    class Coordinate(Prefab):
        x = Attribute(kw_only=True)
        y = Attribute(kw_only=True)

    # Check the typeerror is raised for trying to use y as a positional argument
    with raises(TypeError):
        x = Coordinate(1, 2)

    x = Coordinate(x=1, y=2)
    assert (x.x, x.y) == (1, 2)


def test_kw_not_in_init():
    with raises(PrefabError) as e_info:
        class Construct(Prefab):
            x = Attribute(default="test", kw_only=True, init=False)

    assert e_info.value.args[0] == "Attribute cannot be keyword only if it is not in init."


def test_no_default_no_init_error():
    with raises(PrefabError) as e_info:
        class Construct(Prefab):
            x = Attribute(init=False)

    assert e_info.value.args[0] == "Must provide a default value/factory if the attribute is not in init."


def test_default_value_and_factory_error():
    """Error if defining both a value and a factory"""
    with raises(PrefabError) as e_info:
        class Construct(Prefab):
            x = Attribute(default=12, default_factory=list)

    assert e_info.value.args[0] == "Cannot define both a default value and a default factory."


def test_init_exclude():
    class Coordinate(Prefab):
        x = Attribute()
        y = Attribute(default=2, init=False)

    x = Coordinate(x=1)
    assert (x.x, x.y) == (1, 2)


def test_basic_with_defaults():
    class Coordinate(Prefab):
        x = Attribute(default=0)
        y = Attribute(default=0)

    x = Coordinate()
    assert (x.x, x.y) == (0, 0)

    y = Coordinate(y=5)
    assert (y.x, y.y) == (0, 5)


def test_mutable_defaults_bad():
    """Test mutable defaults behave as they would in a regular class"""
    class MutableDefault(Prefab):
        x = Attribute(default=list())

    mut1 = MutableDefault()
    mut2 = MutableDefault()

    # Check the lists are the same object
    assert mut1.x is mut2.x


def test_default_factory_good():
    class FactoryDefault(Prefab):
        x = Attribute(default_factory=list)

    mut1 = FactoryDefault()
    mut2 = FactoryDefault()

    # Check the attribute is a list and is not the same list for different instances
    assert isinstance(mut1.x, list)
    assert mut1.x is not mut2.x


def test_basic_composition():
    class Coordinate(Prefab):
        x = Attribute()
        y = Attribute()

    class CoordinateZ(Prefab):
        z = Attribute()

    class Coordinate3D(CoordinateZ, Coordinate):
        pass

    x = Coordinate3D(1, 2, 3)

    assert (x.x, x.y, x.z) == (1, 2, 3)


def test_basic_inheritance():
    class Coordinate(Prefab):
        x = Attribute()
        y = Attribute()

    class Coordinate3D(Coordinate):
        z = Attribute()

    x = Coordinate3D(1, 2, 3)

    assert (x.x, x.y, x.z) == (1, 2, 3)


def test_inheritance_and_composition():
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


def test_todict():
    class Coordinate(Prefab):
        x = Attribute()
        y = Attribute()

    x = Coordinate(1, 2)

    expected_dict = {'x': 1, 'y': 2}

    assert x.to_dict() == expected_dict


def test_todict_recurse():
    class Coordinate(Prefab):
        x = Attribute()
        y = Attribute()

    class Circle(Prefab):
        radius = Attribute(default=1)
        origin = Attribute(default=Coordinate(0, 0))

    circ = Circle()

    circ_dict = {
        "radius": 1,
        "origin": {"x": 0, "y": 0}
    }

    circ_norecurse = {
        "radius": 1,
        "origin": Coordinate(0, 0)
    }

    assert circ.to_dict(recurse=True) == circ_dict
    assert circ.to_dict(recurse=False) == circ_norecurse


def test_tojson():
    import json
    from pathlib import PurePosixPath  # Not looking to handle windows '\' issues

    class SystemPath(Prefab):
        filename = Attribute()
        path = Attribute(converter=PurePosixPath)

    pth = SystemPath('testfile', 'path/to/test')

    # Check it's a Path internally
    assert pth.path == PurePosixPath('path/to/test')
    assert pth.to_dict()['path'] == PurePosixPath('path/to/test')

    expected_json = json.dumps({'filename': 'testfile', 'path': 'path/to/test'}, indent=2)
    assert pth.to_json(default=str) == expected_json

    expected_json = json.dumps({'path': 'path/to/test'}, indent=2)
    assert pth.to_json(excludes=['filename'], default=str) == expected_json


def test_converter():
    from pathlib import Path

    class SystemPath(Prefab):
        path = Attribute(converter=Path)

    pth = SystemPath('fake/directory')

    assert pth.path == Path('fake/directory')


def test_default_converter():
    """Check the converter works on default arguments"""
    from pathlib import Path

    class SystemPath(Prefab):
        path = Attribute(default='fake/directory', converter=Path)

    pth = SystemPath()

    assert pth.path == Path('fake/directory')


def test_converter_only_init():
    """Check the converter only runs on init"""
    from pathlib import Path

    class SystemPath(Prefab):
        path = Attribute(converter=Path)

    pth = SystemPath('fake/directory')

    assert pth.path == Path('fake/directory')

    pth.path = 'alternate/directory'

    assert pth.path == 'alternate/directory'  # This has not been converted to a path.


def test_converter_always():
    """Check the converter runs every time if told to"""
    from pathlib import Path

    class SystemPath(Prefab):
        path = Attribute(converter=Path, always_convert=True)

    pth = SystemPath('fake/directory')

    assert pth.path == Path('fake/directory')

    pth.path = 'alternate/directory'

    assert pth.path == Path('alternate/directory')  # This has not been converted to a path.


def test_no_default():
    class Coordinate(Prefab):
        x = Attribute()
        y = Attribute()

    with raises(TypeError):
        x = Coordinate(1)


def test_dumb_error():
    with raises(PrefabError) as e_info:
        class Empty(Prefab):
            pass

    assert e_info.value.args[0] == "Class must contain at least 1 attribute."


def test_not_prefab():
    with raises(RuntimeError) as e:
        class Rebuild:
            x = Attribute()

    assert isinstance(e.value.__cause__, NotPrefabClassError)


def test_difficult_defaults():

    class Settings(Prefab):
        """
        Global persistent settings handler
        """
        output_file = Attribute(default=Path("Settings.json"))

    x = Settings()

    assert x.output_file == Path("Settings.json")


class PicklePrefab(Prefab):
    """Pickle doesn't work on local objects so we need a global PickleCoordinate"""
    x = Attribute(default=800)
    y = Attribute(default=Path('Settings.json'))


def test_picklable():

    picktest = PicklePrefab()

    import pickle
    pick_dump = pickle.dumps(picktest)
    pick_restore = pickle.loads(pick_dump)

    assert pick_restore == picktest
