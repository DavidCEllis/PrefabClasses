# COMPILE_PREFABS
from prefab_classes import prefab, attribute


@prefab(compile_prefab=True, compile_fallback=True)
class FailFactorySyntax:
    x = attribute(default_factory=list)
    y = attribute()
