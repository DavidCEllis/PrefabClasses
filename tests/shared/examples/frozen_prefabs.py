# COMPILE_PREFABS

from prefab_classes import prefab, attribute


@prefab(frozen=True, compile_prefab=True, compile_fallback=True)
class FrozenExample:
    x: int
    y: str = "Example Data"
    z: list = attribute(default_factory=list)
