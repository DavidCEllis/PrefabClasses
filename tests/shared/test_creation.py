"""Tests for errors raised on class creation"""
from prefab_classes import PrefabError
from prefab_classes.constants import FIELDS_ATTRIBUTE
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


def test_removed_annotations(importer):
    from creation import OnlyHints

    removed_attributes = ["x", "y", "z"]
    for attrib in removed_attributes:
        assert attrib not in getattr(OnlyHints, "__dict__")
        assert attrib not in getattr(OnlyHints, "__annotations__", {})


def test_removed_only_used_annotations(importer):
    from creation import MixedHints

    assert "x" in getattr(MixedHints, "__annotations__")

    removed_attributes = ["y", "z"]
    for attrib in removed_attributes:
        assert attrib not in getattr(MixedHints, "__dict__")
        assert attrib not in getattr(MixedHints, "__annotations__", {})


def test_removed_attributes(importer):
    from creation import AllPlainAssignment

    removed_attributes = ["x", "y", "z"]
    for attrib in removed_attributes:
        assert attrib not in getattr(AllPlainAssignment, "__dict__")


def test_skipped_classvars(importer):
    from creation import IgnoreClassVars

    fields = getattr(IgnoreClassVars, FIELDS_ATTRIBUTE)
    assert "x" not in fields
    assert "y" not in fields
    assert "z" not in fields
    assert "actual" in fields

    assert "x" in getattr(IgnoreClassVars, "__dict__")
    assert "y" in getattr(IgnoreClassVars, "__dict__")
    assert "z" in getattr(IgnoreClassVars, "__dict__")


def test_non_init_doesnt_break_syntax():
    # No syntax error if an attribute with a default is defined
    # before one without - if init=False for that attribute
    from creation import PositionalNotAfterKW

    x = PositionalNotAfterKW(1, 2)
    assert repr(x) == "PositionalNotAfterKW(x=1, y=0, z=2)"
