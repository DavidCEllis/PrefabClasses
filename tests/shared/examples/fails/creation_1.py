# COMPILE_PREFABS
from prefab_classes import prefab, attribute


@prefab(compile_prefab=True, compile_fallback=True)
class Construct:
    x = attribute(default="test", kw_only=True, init=False)
