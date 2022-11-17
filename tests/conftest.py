import pytest

from prefab_classes.register import prefab_register


@pytest.fixture(scope="function", autouse=True)
def clear_prefab_register():
    prefab_register.clear()
    yield
    prefab_register.clear()
