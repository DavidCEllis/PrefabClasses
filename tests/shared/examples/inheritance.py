# COMPILE_PREFABS
from prefab_classes import prefab, attribute


@prefab(compile_prefab=True, compile_fallback=True)
class Coordinate:
    x: float
    y: float


@prefab(compile_prefab=True, compile_fallback=True)
class Coordinate3D(Coordinate):
    z = attribute()


@prefab(compile_prefab=True, compile_fallback=True)
class CoordinateTime:
    t = attribute()


@prefab(compile_prefab=True, compile_fallback=True)
class Coordinate4D(CoordinateTime, Coordinate3D):
    pass
