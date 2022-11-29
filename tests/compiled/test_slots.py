import pytest
from prefab_classes import prefab_compiler


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
