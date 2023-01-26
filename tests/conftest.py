import pytest

from prefab_classes_hook import prefab_compiler


@pytest.fixture(params=[True, False], ids=["Compiled", "Live"])
def importer(request):
    if request.param:
        with prefab_compiler():
            yield request.param
    else:
        yield request.param
