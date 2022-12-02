# COMPILE_PREFABS
from typing import ClassVar
from prefab_classes import prefab


@prefab(compile_prefab=True, compile_fallback=True)
class Empty:
    pass


@prefab(compile_prefab=True, compile_fallback=True)
class EmptyClassVars:
    x: ClassVar = 12
