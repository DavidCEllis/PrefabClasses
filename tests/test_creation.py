"""Tests for errors raised on class creation"""
from prefab import Prefab, Attribute, PrefabError, NotPrefabClassError
from smalltest.tools import raises


def test_kw_not_in_init():
    with raises(PrefabError) as e_info:
        class Construct(Prefab):
            x = Attribute(default="test", kw_only=True, init=False)

    assert e_info.value.args[0] == "Attribute cannot be keyword only if it is not in init."


def test_positional_after_kw_error():
    with raises(SyntaxError) as e_info:
        class FailSyntax(Prefab):
            x = Attribute(default=0)
            y = Attribute()

    assert e_info.value.args[0] == "non-default argument follows default argument"

    with raises(SyntaxError) as e_info:
        class FailFactorySyntax(Prefab):
            x = Attribute(default_factory=list)
            y = Attribute()

    assert e_info.value.args[0] == "non-default argument follows default argument"


def test_no_default_no_init_error():
    with raises(PrefabError) as e_info:
        class Construct(Prefab):
            x = Attribute(init=False)

    assert e_info.value.args[0] == "Must provide a default value/factory if the attribute is not in init."


def test_default_value_and_factory_error():
    """Error if defining both a value and a factory"""
    with raises(PrefabError) as e_info:
        class Construct(Prefab):
            x = Attribute(default=12, default_factory=list)

    assert e_info.value.args[0] == "Cannot define both a default value and a default factory."


def test_dumb_error():
    with raises(PrefabError) as e_info:
        class Empty(Prefab):
            pass

    assert e_info.value.args[0] == "Class must contain at least 1 attribute."


def test_not_prefab():
    with raises(RuntimeError) as e:
        class Rebuild:
            x = Attribute()

    assert isinstance(e.value.__cause__, NotPrefabClassError)
