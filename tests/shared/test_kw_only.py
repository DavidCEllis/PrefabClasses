import pytest


def test_kw_only_basic(importer):
    from kw_only import KWBasic

    # Check the typeerror is raised for
    # trying to use positional arguments
    with pytest.raises(TypeError):
        x = KWBasic(1, 2)

    x = KWBasic(x=1, y=2)
    assert (x.x, x.y) == (1, 2)


