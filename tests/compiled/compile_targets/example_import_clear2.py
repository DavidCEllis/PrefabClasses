# COMPILE_PREFABS
import functools
from prefab_classes import prefab, attribute
import collections

@prefab(compile_prefab=True)
class X:
    x: int = attribute(default=3)