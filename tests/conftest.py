import pytest

from prefab_classes import prefab_compiler
from prefab_classes.register import prefab_register


@pytest.fixture(scope="function", autouse=True)
def clear_prefab_register():
    prefab_register.clear()
    yield
    prefab_register.clear()


@pytest.fixture(params=[True, False], ids=["Compiled", "Live"])
def importer(request):
    if request.param:
        with prefab_compiler():
            yield request.param
    else:
        yield request.param
