"""Tests for errors raised on class creation"""
from prefab_classes import prefab, attribute, PrefabError
from pytest import raises


def test_kw_not_in_init(importer):
    with raises(PrefabError) as e_info:
        from fails.creation_1 import Construct

    assert (
        e_info.value.args[0] == "Attribute cannot be keyword only if it is not in init."
    )


def test_positional_after_kw_error(importer):
    with raises(SyntaxError) as e_info:
        from fails.creation_2 import FailSyntax

    assert e_info.value.args[0] == "non-default argument follows default argument"

    with raises(SyntaxError) as e_info:
        from fails.creation_3 import FailSyntax

    assert e_info.value.args[0] == "non-default argument follows default argument"


def test_no_default_no_init_error(importer):
    with raises(PrefabError) as e_info:
        from fails.creation_4 import Construct

    assert (
        e_info.value.args[0]
        == "Must provide a default value/factory if the attribute is not in init."
    )


def test_default_value_and_factory_error(importer):
    """Error if defining both a value and a factory"""
    with raises(PrefabError) as e_info:
        from fails.creation_5 import Construct

    assert (
        e_info.value.args[0]
        == "Cannot define both a default value and a default factory."
    )


def test_no_attributes_error(importer):
    with raises(PrefabError) as e_info:

        from fails.creation_6 import Empty

    assert e_info.value.args[0] == "Class must contain at least 1 attribute."


def test_created_twice(importer):
    with raises(PrefabError) as e_info:
        import fails.creation_7

    assert (
        e_info.value.args[0]
        == "Class fails.creation_7.DejaVu already registered as a prefab."
    )
