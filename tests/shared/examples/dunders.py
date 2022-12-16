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


@prefab(compile_prefab=True, compile_fallback=True)
class NoXReprNoXInit:
    _type = attribute(default=None, init=False, repr=False)


@prefab(compile_prefab=True, compile_fallback=True, iter=True)
class CoordinateIter:
    x: float
    y: float


@prefab(compile_prefab=True, compile_fallback=True, match_args=False)
class NoMatchArgs:
    x: float
    y: float


@prefab(compile_prefab=True, compile_fallback=True)
class DundersExist:
    x: int
    y: int

    __match_args__ = ("x",)

    def __init__(self, x, y):
        self.x = 2 * x
        self.y = 3 * y

    def __repr__(self):
        return "NOT_REPLACED"

    def __eq__(self, other):
        return True

    def __iter__(self):
        yield self.x
