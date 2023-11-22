import pytest
from prefab_classes.hook import prefab_compiler


@pytest.mark.usefixtures("compile_folder_modules")
def test_has_slots():
    with prefab_compiler():
        from example_slots import Coordinate

    assert hasattr(Coordinate, "__slots__")

    assert Coordinate.__slots__ == ("x", "y")


@pytest.mark.usefixtures("compile_folder_modules")
def test_slots_work():
    with prefab_compiler():
        from example_slots import Coordinate

    c = Coordinate(0.0, 0.0)

    c.x, c.y = 1.0, 2.0
    assert repr(c) == "Coordinate(x=1.0, y=2.0)"

    with pytest.raises(AttributeError):
        c.z = 3.0

    assert not hasattr(c, "__dict__")


@pytest.mark.usefixtures("compile_folder_modules")
def test_slots_inheritance():
    # Child classes should only define *NEW* slots, not all slots.
    # https://docs.python.org/3/reference/datamodel.html#notes-on-using-slots
    with prefab_compiler():
        from example_slots import Coordinate, Coordinate3D

    assert Coordinate.__slots__ == ("x", "y")
    assert Coordinate3D.__slots__ == ("z",)

    xyz = Coordinate3D(1.0, 2.0, 3.0)
    assert (xyz.x, xyz.y, xyz.z) == (1.0, 2.0, 3.0)


@pytest.mark.usefixtures("compile_folder_modules")
def test_slots_frozen():
    with prefab_compiler():
        from example_slots import FrozenExample

    assert hasattr(FrozenExample, "__slots__")

    # Make sure basics still work
    x = FrozenExample(x=0)
    assert x.x == 0
    assert x.y == "Example Data"
    assert x.z == []

    with pytest.raises(TypeError) as e1:
        x.x = 2

    with pytest.raises(TypeError) as e2:
        x.y = "Fail to change data"

    assert x.x == 0
    assert x.y == "Example Data"
