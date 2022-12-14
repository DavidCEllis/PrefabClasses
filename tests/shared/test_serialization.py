"""Tests related to serialization to JSON or Pickle"""
from pathlib import PurePosixPath, PurePath

from prefab_classes.funcs import as_dict, to_json
from pytest import raises


# Serialization tests
def test_todict(importer):
    from serialization import Coordinate

    x = Coordinate(1, 2)

    expected_dict = {"x": 1, "y": 2}

    assert as_dict(x) == expected_dict


def test_tojson(importer):
    import json

    from serialization import SystemPath

    pth = SystemPath("testfile", "path/to/test")

    # Check it's a Path internally
    assert pth.path == PurePosixPath("path/to/test")
    assert as_dict(pth)["path"] == PurePosixPath("path/to/test")

    expected_json = json.dumps(
        {"filename": "testfile", "path": "path/to/test"}
    )
    assert to_json(pth, default=str) == expected_json

    expected_json = json.dumps({"path": "path/to/test"})
    assert to_json(pth, excludes=("filename",), default=str) == expected_json


def test_tojson_recurse(importer):
    """Due to the implementation, json dumps should recurse by default"""
    import json

    from serialization import Circle

    circ = Circle()

    circ_dict = {"radius": 1, "origin": {"x": 0, "y": 0}}

    circ_json = json.dumps(circ_dict)

    assert circ_json == to_json(circ)


def test_jsonencoder_failure(importer):
    """With the encoder for Prefabs it should still typeerror on unencodable types"""

    from serialization import SystemPath

    pth = SystemPath("testfile", "path/to/test")

    with raises(TypeError):
        to_json(pth)


def test_jsonencoder_layered(importer):
    import json

    def default_for_path(o):
        if isinstance(o, PurePath):
            return str(o)
        raise TypeError(
            f"Object of type {o.__class__.__name__} is not JSON serializable"
        )

    from serialization import SystemPath, Onion

    pth = SystemPath("testfile", "path/to/test")
    x = Onion(pth=PurePosixPath("what"), syspath=pth)

    result = {
        "pth": "what",
        "syspath": {"filename": "testfile", "path": "path/to/test"},
    }

    assert json.dumps(result, indent=2) == to_json(x, default=default_for_path, indent=2)


def test_picklable(importer):
    from serialization import PicklePrefab

    picktest = PicklePrefab()

    import pickle

    pick_dump = pickle.dumps(picktest)
    pick_restore = pickle.loads(pick_dump)

    assert pick_restore == picktest
