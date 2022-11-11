"""Tests for errors raised on class creation"""
from prefab_classes import prefab, attribute, PrefabError
from smalltest.tools import raises


def test_kw_not_in_init():
    with raises(PrefabError) as e_info:

        @prefab
        class Construct:
            x = attribute(default="test", kw_only=True, init=False)

    assert (
        e_info.value.args[0] == "Attribute cannot be keyword only if it is not in init."
    )


def test_positional_after_kw_error():
    with raises(SyntaxError) as e_info:

        @prefab
        class FailSyntax:
            x = attribute(default=0)
            y = attribute()

    assert e_info.value.args[0] == "non-default argument follows default argument"

    with raises(SyntaxError) as e_info:

        @prefab
        class FailFactorySyntax:
            x = attribute(default_factory=list)
            y = attribute()

    assert e_info.value.args[0] == "non-default argument follows default argument"


def test_no_default_no_init_error():
    with raises(PrefabError) as e_info:

        @prefab
        class Construct:
            x = attribute(init=False)

    assert (
        e_info.value.args[0]
        == "Must provide a default value/factory if the attribute is not in init."
    )


def test_default_value_and_factory_error():
    """Error if defining both a value and a factory"""
    with raises(PrefabError) as e_info:

        @prefab
        class Construct:
            x = attribute(default=12, default_factory=list)

    assert (
        e_info.value.args[0]
        == "Cannot define both a default value and a default factory."
    )


def test_no_attributes_error():
    with raises(PrefabError) as e_info:

        @prefab
        class Empty:
            pass

    assert e_info.value.args[0] == "Class must contain at least 1 attribute."


def test_created_twice():
    @prefab
    class DejaVu:
        x = attribute()

    with raises(PrefabError) as e_info:

        @prefab
        class DejaVu:
            x = attribute()

    assert (
        e_info.value.args[0]
        == "Class with name test_created_twice.<locals>.DejaVu already registered as a prefab."
    )
