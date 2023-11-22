import pytest

from prefab_classes.hook import prefab_compiler


@pytest.fixture(scope="package", params=[True, False], ids=["Compiled", "Dynamic"])
def importer(request):
    if request.param:
        with prefab_compiler():
            yield request.param
    else:
        yield request.param
