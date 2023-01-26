# COMPILE_PREFABS
import functools
from prefab_classes import attribute, prefab
import collections


@prefab(compile_prefab=True)
class Y:
    x: int = attribute(default=3)
