# COMPILE_PREFABS
import functools
from prefab_classes import prefab, attribute, build_prefab
import collections


@prefab(compile_prefab=True)
class X:
    x: int = attribute(default=3)


Y = build_prefab("Y", [("x", attribute())])
