# COMPILE_PREFABS
from prefab_classes import prefab, attribute


@prefab(compile_prefab=True, compile_fallback=True)
class B:
    x: int = 0


@prefab(compile_prefab=True, compile_fallback=True)
class C(B):
    y: int
