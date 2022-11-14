# COMPILE_PREFABS
from prefab_classes import prefab


@prefab(compile_prefab=True)
class Coordinate:
    x: float
    y: float

