# COMPILE_PREFABS
from prefab_classes import prefab


@prefab(compile_prefab=True, iter=True, match_args=False)
class Coordinate:
    """Coordinate Data"""

    x: float
    y: float
