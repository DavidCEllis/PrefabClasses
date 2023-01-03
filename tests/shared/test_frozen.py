import pytest
from prefab_classes.exceptions import FrozenPrefabError


def test_basic_frozen(importer):
    from frozen_prefabs import FrozenExample

    # Make sure basics still work
    x = FrozenExample(x=0)
    assert x.x == 0
    assert x.y == "Example Data"
    assert x.z == []

    with pytest.raises(FrozenPrefabError) as e1:
        x.x = 2

    with pytest.raises(FrozenPrefabError) as e2:
        x.y = "Fail to change data"

    assert x.x == 0
    assert x.y == "Example Data"


def test_mutable_default(importer):
    from frozen_prefabs import FrozenExample

    base_list = []

    x = FrozenExample(x=0, y="New Data", z=base_list)

    assert x.x == 0
    assert x.y == "New Data"
    assert x.z is base_list

    new_base_list = []

    with pytest.raises(FrozenPrefabError) as e1:
        x.z = new_base_list

    assert x.z is not new_base_list
    assert x.z is base_list
