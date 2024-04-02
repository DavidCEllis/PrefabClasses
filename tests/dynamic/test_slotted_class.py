from prefab_classes import prefab, attribute, PrefabSlots


def test_basic_slotted():
    @prefab
    class SlottedPrefab:
        __slots__ = PrefabSlots(
            x=42,
            y=attribute(default=3.14, type=float, doc="Digits of pi")
        )

    assert SlottedPrefab.__slots__ == {"x": None, "y": "Digits of pi"}
    assert SlottedPrefab.__annotations__ == {"y": float}

    x = SlottedPrefab()

    assert x.x == 42
    assert x.y == 3.14
