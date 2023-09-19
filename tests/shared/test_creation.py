"""Tests for errors raised on class creation"""
from prefab_classes.exceptions import PrefabError
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
        assert "x" not in x.__dict__

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
    def test_removed_defaults(self, importer):
        from creation import OnlyHints

        removed_attributes = ["x", "y", "z"]
        for attrib in removed_attributes:
            assert attrib not in getattr(OnlyHints, "__dict__")
            assert attrib in getattr(OnlyHints, "__annotations__", {})

    def test_removed_only_used_defaults(self, importer):
        from creation import MixedHints

        assert "x" in getattr(MixedHints, "__annotations__")
        assert "y" in getattr(MixedHints, "__annotations__")

        assert "x" in getattr(MixedHints, "__dict__")

        removed_attributes = ["y", "z"]
        for attrib in removed_attributes:
            assert attrib not in getattr(MixedHints, "__dict__")

    def test_removed_attributes(self, importer):
        from creation import AllPlainAssignment

        removed_attributes = ["x", "y", "z"]
        for attrib in removed_attributes:
            assert attrib not in getattr(AllPlainAssignment, "__dict__")


@pytest.mark.usefixtures("importer")
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

        assert KeepDefinedMethods.__match_args__ == ("x",)


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



class TestExceptions:
    def test_kw_not_in_init(self, importer):
        with pytest.raises(PrefabError) as e_info:
            from fails.creation_1 import Construct

        assert (
            e_info.value.args[0]
            == "Attribute cannot be keyword only if it is not in init."
        )

    def test_positional_after_kw_error(self, importer):
        with pytest.raises(SyntaxError) as e_info:
            from fails.creation_2 import FailSyntax

        assert e_info.value.args[0] == "non-default argument follows default argument"

        with pytest.raises(SyntaxError) as e_info:
            from fails.creation_3 import FailSyntax

        assert e_info.value.args[0] == "non-default argument follows default argument"

    def test_default_value_and_factory_error(self, importer):
        """Error if defining both a value and a factory"""
        with pytest.raises(PrefabError) as e_info:
            from fails.creation_5 import Construct

        assert (
            e_info.value.args[0]
            == "Cannot define both a default value and a default factory."
        )


class TestSplitVarDef:
    # Tests for a split variable definition
    @pytest.mark.parametrize("classname", ["SplitVarDef", "SplitVarDefReverseOrder", "SplitVarRedef"])
    def test_splitvardef(self, importer, classname):
        import creation

        cls = getattr(creation, classname)

        assert cls.__annotations__['x'] == str

        inst = cls()
        assert inst.x == "test"

    def test_splitvarattribdef(self, importer):
        from creation import SplitVarAttribDef as cls

        inst = cls()

        assert 'x' in cls.PREFAB_FIELDS
        assert 'y' in cls.PREFAB_FIELDS

        assert inst.x == "test"
        assert inst.y == "test_2"

    def test_horriblemess(self, importer):
        # Nobody should make a class like this but it should behave
        # as expected
        from creation import HorribleMess as cls

        inst = cls(x="true_test")

        assert inst.x == "true_test"
        assert repr(inst) == "HorribleMess(x='true_test', y='test_2')"

        assert cls.__annotations__ == {'x': str, 'y': str}


def test_call_mistaken(importer):
    from creation import CallMistakenForAttribute as cls

    # Check that ignore_this is a class variable and use_this is not
    assert cls.ignore_this == "this is a class variable"
    assert getattr(cls, "use_this", None) is None

    inst = cls()
    assert inst.use_this == "this is an attribute"


@pytest.mark.usefixtures("importer")
class TestNonInit:
    def test_non_init_works_no_default(self):
        from creation import ConstructInitFalse

        x = ConstructInitFalse()

        assert not hasattr(x, "x")

        x.x = 12

        assert repr(x) == "<prefab ConstructInitFalse; x=12>"

    def test_non_init_doesnt_break_syntax(self):
        # No syntax error if an attribute with a default is defined
        # before one without - if init=False for that attribute
        from creation import PositionalNotAfterKW

        x = PositionalNotAfterKW(1, 2)
        assert repr(x) == "<prefab PositionalNotAfterKW; x=1, y=0, z=2>"