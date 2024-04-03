from prefab_classes import prefab, attribute
from prefab_classes._shared import INTERNAL_DICT


def test_dynamic_internals():
    @prefab
    class X:
        x: int
        y: int = 2

    @prefab
    class Z(X):
        z: int = 3

    x_attrib = attribute(type=int)
    y_attrib = attribute(default=2, type=int)
    z_attrib = attribute(default=3, type=int)

    assert hasattr(X, INTERNAL_DICT)

    x_internals = getattr(X, INTERNAL_DICT)
    assert x_internals["attributes"] == x_internals["local_attributes"]
    assert x_internals["attributes"] == {"x": x_attrib, "y": y_attrib}

    z_internals = getattr(Z, INTERNAL_DICT)
    assert z_internals["attributes"] != z_internals["local_attributes"]
    assert z_internals["attributes"] == {"x": x_attrib, "y": y_attrib, "z": z_attrib}
