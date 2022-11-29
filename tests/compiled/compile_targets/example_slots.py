# COMPILE_PREFABS
from prefab_classes import prefab


@prefab(compile_prefab=True, compile_slots=True)
class Coordinate:
    x: float
    y: float


@prefab(compile_prefab=True, compile_slots=True)
class Coordinate3D(Coordinate):
    z: float
