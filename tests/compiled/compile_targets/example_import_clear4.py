# COMPILE_PREFABS
import functools
from prefab_classes import prefab
import collections
from prefab_classes import attribute


@prefab(compile_prefab=True)
class Z:
    x: int = attribute(default=3)
