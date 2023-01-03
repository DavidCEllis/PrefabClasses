# COMPILE_PREFABS
from prefab_classes import prefab, attribute


@prefab(compile_prefab=True, compile_slots=True)
class Coordinate:
    x: float
    y: float


@prefab(compile_prefab=True, compile_slots=True)
class Coordinate3D(Coordinate):
    z: float


@prefab(frozen=True, compile_prefab=True, compile_slots=True)
class FrozenExample:
    x: int
    y: str = "Example Data"
    z: list = attribute(default_factory=list)
