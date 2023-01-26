def test_basic_repr(importer):
    from repr_func import RegularRepr

    x = RegularRepr()
    assert repr(x) == "RegularRepr(x='Hello', y='World')"


def test_basic_repr_no_fields(importer):
    from repr_func import NoReprAttributes

    x = NoReprAttributes()
    assert repr(x) == "<prefab NoReprAttributes>"


def test_one_attribute_no_repr(importer):
    from repr_func import OneAttributeNoRepr

    x = OneAttributeNoRepr()
    assert repr(x) == "<prefab OneAttributeNoRepr; y='World'>"


def test_one_attribute_no_init(importer):
    from repr_func import OneAttributeNoInit

    x = OneAttributeNoInit()
    assert repr(x) == "<prefab OneAttributeNoInit; x='Hello', y='World'>"


def test_one_attribute_exclude_field(importer):
    from repr_func import OneAttributeExcludeField

    x = OneAttributeExcludeField()
    assert repr(x) == "<prefab OneAttributeExcludeField; x='Hello'>"


def test_regular_one_arg(importer):
    from repr_func import RegularReprOneArg

    x = RegularReprOneArg()
    assert repr(x) == "RegularReprOneArg(x='Hello')"
