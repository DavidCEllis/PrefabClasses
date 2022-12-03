"""Tests for errors raised on class creation"""
from prefab_classes import PrefabError
from prefab_classes.constants import FIELDS_ATTRIBUTE

import pytest


class TestEmptyClass:
    def test_empty(self, importer):
        from creation_empty import Empty

        x = Empty()
        y = Empty()

        assert repr(x) == "Empty()"

    def test_empty_classvar(self, importer):
        from creation_empty import EmptyClassVars

        x = EmptyClassVars()
        assert x.x == 12
        assert 'x' not in x.__dict__

    def test_empty_equal(self, importer):
        from creation_empty import Empty

        x = Empty()
        y = Empty()
        assert x == y

    def test_empty_iter(self, importer):
        from creation_empty import EmptyIter

        x = EmptyIter()
        lx = list(x)

        assert lx == []


class TestRemoveRecipe:
    def test_removed_annotations(self, importer):
        from creation import OnlyHints

        removed_attributes = ["x", "y", "z"]
        for attrib in removed_attributes:
            assert attrib not in getattr(OnlyHints, "__dict__")
            assert attrib not in getattr(OnlyHints, "__annotations__", {})

    def test_removed_only_used_annotations(self, importer):
        from creation import MixedHints

        assert "x" in getattr(MixedHints, "__annotations__")

        removed_attributes = ["y", "z"]
        for attrib in removed_attributes:
            assert attrib not in getattr(MixedHints, "__dict__")
            assert attrib not in getattr(MixedHints, "__annotations__", {})

    def test_removed_attributes(self, importer):
        from creation import AllPlainAssignment

        removed_attributes = ["x", "y", "z"]
        for attrib in removed_attributes:
            assert attrib not in getattr(AllPlainAssignment, "__dict__")


@pytest.mark.usefixtures('importer')
class TestKeepDefined:
    def test_keep_init(self):
        from creation import KeepDefinedMethods
        x = KeepDefinedMethods(42)

        assert x.x == 0

    def test_keep_repr(self):
        from creation import KeepDefinedMethods

        x = KeepDefinedMethods()
        assert repr(x) == "ORIGINAL REPR"

    def test_keep_eq(self):
        from creation import KeepDefinedMethods

        x = KeepDefinedMethods()

        assert x != x

    def test_keep_iter(self):
        from creation import KeepDefinedMethods

        x = KeepDefinedMethods()

        y = list(x)
        assert y[0] == "ORIGINAL ITER"

    def test_keep_match_args(self):
        from creation import KeepDefinedMethods

        assert KeepDefinedMethods.__match_args__ == ('x', )


def test_skipped_classvars(importer):
    from creation import IgnoreClassVars

    fields = getattr(IgnoreClassVars, FIELDS_ATTRIBUTE)
    assert "v" not in fields
    assert "w" not in fields
    assert "x" not in fields
    assert "y" not in fields
    assert "z" not in fields
    assert "actual" in fields

    assert "v" in getattr(IgnoreClassVars, "__dict__")
    assert "w" in getattr(IgnoreClassVars, "__dict__")
    assert "x" in getattr(IgnoreClassVars, "__dict__")
    assert "y" in getattr(IgnoreClassVars, "__dict__")
    assert "z" in getattr(IgnoreClassVars, "__dict__")


def test_non_init_doesnt_break_syntax():
    # No syntax error if an attribute with a default is defined
    # before one without - if init=False for that attribute
    from creation import PositionalNotAfterKW

    x = PositionalNotAfterKW(1, 2)
    assert repr(x) == "PositionalNotAfterKW(x=1, y=0, z=2)"


class TestExceptions:

    def test_kw_not_in_init(self, importer):
        with pytest.raises(PrefabError) as e_info:
            from fails.creation_1 import Construct

        assert (
            e_info.value.args[0] == "Attribute cannot be keyword only if it is not in init."
        )


    def test_positional_after_kw_error(self, importer):
        with pytest.raises(SyntaxError) as e_info:
            from fails.creation_2 import FailSyntax

        assert e_info.value.args[0] == "non-default argument follows default argument"

        with pytest.raises(SyntaxError) as e_info:
            from fails.creation_3 import FailSyntax

        assert e_info.value.args[0] == "non-default argument follows default argument"


    def test_no_default_no_init_error(self, importer):
        with pytest.raises(PrefabError) as e_info:
            from fails.creation_4 import Construct

        assert (
            e_info.value.args[0]
            == "Must provide a default value/factory if the attribute is not in init."
        )


    def test_default_value_and_factory_error(self, importer):
        """Error if defining both a value and a factory"""
        with pytest.raises(PrefabError) as e_info:
            from fails.creation_5 import Construct

        assert (
            e_info.value.args[0]
            == "Cannot define both a default value and a default factory."
        )
