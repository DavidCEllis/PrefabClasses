import pytest

from prefab_classes import prefab, attribute, SlotAttributes


def test_basic_slotted():
    @prefab
    class SlottedPrefab:
        __slots__ = SlotAttributes(
            x=42,
            y=attribute(default=3.14, type=float, doc="Digits of pi"),
        )

    assert SlottedPrefab.__slots__ == {"x": None, "y": "Digits of pi"}
    assert SlottedPrefab.__annotations__ == {"y": float}

    ex = SlottedPrefab()

    assert ex.x == 42
    assert ex.y == 3.14


def test_class_unchanged():
    # By using slots to define the class prefab_classes does not need to create
    # a new class.
    # Dataclasses and Attrs require recreating a class and would fail this test
    # with their method of slots.
    cache = {}

    def save_class(cls):
        cache[cls.__name__] = cls
        return cls

    @prefab
    @save_class
    class Slotted:
        __slots__ = SlotAttributes(
            x="example_data"
        )

    assert Slotted is cache["Slotted"]

    ex = Slotted(x="new example data")

    assert ex.x == "new example data"


def test_actually_slotted():
    @prefab
    class Slotted:
        __slots__ = SlotAttributes(
            x=attribute(default="example_data")
        )
        x: str

    inst = Slotted()

    with pytest.raises(AttributeError):
        inst.y = "This Doesn't Work!"

    @prefab
    class UnSlotted:
        x: str = "example_data"

    inst = UnSlotted()
    inst.x = "This Works!"
