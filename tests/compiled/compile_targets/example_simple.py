# COMPILE_PREFABS
from prefab_classes import prefab


@prefab(compile_prefab=True, iter=True, match_args=False)
class Coordinate:
    x: float
    y: float
