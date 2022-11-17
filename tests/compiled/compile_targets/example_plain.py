# COMPILE_PREFABS
from prefab_classes import prefab


@prefab(compile_prefab=True, compile_plain=True)
class Coordinate:
    x: float
    y: float
