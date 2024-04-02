from prefab_classes import prefab, attribute


@prefab(frozen=True)
class FrozenExample:
    x: int
    y: str = "Example Data"
    z: list = attribute(default_factory=list)
