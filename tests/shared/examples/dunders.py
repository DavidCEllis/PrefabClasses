# COMPILE_PREFABS
from prefab_classes import prefab, attribute


@prefab(compile_prefab=True, compile_fallback=True)
class Coordinate:
    x: float
    y: float


@prefab(compile_prefab=True, compile_fallback=True)
class Coordinate3D(Coordinate):
    z: float


@prefab(compile_prefab=True, compile_fallback=True)
class CoordinateTime:
    t: float


@prefab(compile_prefab=True, compile_fallback=True)
class Coordinate4D(CoordinateTime, Coordinate3D):
    pass


@prefab(compile_prefab=True, compile_fallback=True)
class CoordinateNoXRepr:
    x: float = attribute(repr=False)
    y: float


@prefab(compile_prefab=True, compile_fallback=True, iter=True)
class CoordinateIter:
    x: float
    y: float

