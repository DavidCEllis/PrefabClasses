# COMPILE_PREFABS
from prefab_classes import prefab


@prefab(compile_prefab=True, iter=True)
class Coordinate:
    x: float
    y: float
