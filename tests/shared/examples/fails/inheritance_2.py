# COMPILE_PREFABS
from prefab_classes import prefab, attribute


@prefab(compile_prefab=True, compile_fallback=True)
class B:
    x: int
    y: int


@prefab(compile_prefab=True, compile_fallback=True)
class C(B):
    x: int = 2
