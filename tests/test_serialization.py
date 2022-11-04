"""Tests related to serialization to JSON or Pickle"""
from pathlib import Path, PurePosixPath, PurePath

from prefab import Prefab, Attribute, as_dict, to_json
from smalltest.tools import raises


# Serialization tests
def test_todict():
    class Coordinate(Prefab):
        x = Attribute()
        y = Attribute()

    x = Coordinate(1, 2)

    expected_dict = {'x': 1, 'y': 2}

    assert as_dict(x) == expected_dict


def test_todict_init_only():
    class Coordinate3D(Prefab):
        x = Attribute()
        y = Attribute()
        z = Attribute(default=0, init=False)

    x = Coordinate3D(1, 2)

    expected_dict = {'x': 1, 'y': 2, 'z': 0}

    assert as_dict(x) == expected_dict

    expected_dict = {'x': 1, 'y': 2}

    assert as_dict(x, init_attributes_only=True) == expected_dict


def test_tojson():
    import json

    class SystemPath(Prefab):
        filename = Attribute()
        path = Attribute(converter=PurePosixPath)

    pth = SystemPath('testfile', 'path/to/test')

    # Check it's a Path internally
    assert pth.path == PurePosixPath('path/to/test')
    assert as_dict(pth)['path'] == PurePosixPath('path/to/test')

    expected_json = json.dumps({'filename': 'testfile', 'path': 'path/to/test'}, indent=2)
    assert to_json(pth, default=str) == expected_json

    expected_json = json.dumps({'path': 'path/to/test'}, indent=2)
    assert to_json(pth, excludes=['filename'], default=str) == expected_json


def test_tojson_recurse():
    """Due to the implementation, json dumps should recurse by default"""
    import json

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

    circ_json = json.dumps(circ_dict, indent=2)

    assert circ_json == to_json(circ, indent=2)


def test_jsonencoder_failure():
    """With the encoder for Prefabs it should still typeerror on unencodable types"""

    class SystemPath(Prefab):
        filename = Attribute()
        path = Attribute(converter=PurePosixPath)

    pth = SystemPath('testfile', 'path/to/test')

    with raises(TypeError):
        to_json(pth)


def test_jsonencoder_layered():
    import json

    def default_for_path(o):
        if isinstance(o, PurePath):
            return str(o)
        raise TypeError(f"Object of type {o.__class__.__name__} is not JSON serializable")

    class Onion(Prefab):
        pth = Attribute()
        syspath = Attribute()

    class SystemPath(Prefab):
        filename = Attribute()
        path = Attribute(converter=PurePosixPath)

    pth = SystemPath('testfile', 'path/to/test')
    x = Onion(pth=PurePosixPath('what'), syspath=pth)

    result = {
        "pth": "what",
        "syspath": {
            "filename": "testfile",
            "path": "path/to/test"
        }
    }

    assert json.dumps(result, indent=2) == to_json(x, default=default_for_path)


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
