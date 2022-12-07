import pytest


def test_kw_only_basic(importer):
    from kw_only import KWBasic

    # Check the typeerror is raised for
    # trying to use positional arguments
    with pytest.raises(TypeError):
        x = KWBasic(1, 2)

    x = KWBasic(x=1, y=2)
    assert (x.x, x.y) == (1, 2)


def test_kw_only_ordering(importer):
    from kw_only import KWOrdering

    with pytest.raises(TypeError):
        x = KWOrdering(1, 2)

    x = KWOrdering(1, x=2)
    assert (x.x, x.y) == (2, 1)
    assert repr(x) == "KWOrdering(x=2, y=1)"


def test_kw_only_inheritance(importer):
    from kw_only import KWChild

    with pytest.raises(TypeError):
        x = KWChild(1, 2)

    x = KWChild(1, x=2)
    assert (x.x, x.y) == (2, 1)
    assert repr(x) == "KWChild(x=2, y=1)"
