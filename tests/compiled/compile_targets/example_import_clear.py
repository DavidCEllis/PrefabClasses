# COMPILE_PREFABS
import functools
from prefab_classes import prefab
import collections


@prefab(compile_prefab=True)
class W:
    x: int
