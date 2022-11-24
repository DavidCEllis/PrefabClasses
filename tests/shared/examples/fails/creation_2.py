# COMPILE_PREFABS
from prefab_classes import prefab, attribute


@prefab(compile_prefab=True, compile_fallback=True)
class FailSyntax:
    x = attribute(default=0)
    y = attribute()
