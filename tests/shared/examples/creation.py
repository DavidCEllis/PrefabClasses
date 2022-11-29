# COMPILE_PREFABS
from prefab_classes import prefab, attribute


@prefab(compile_prefab=True, compile_fallback=True)
class OnlyHints:
    # Remove all 3 hints and values
    x: int
    y: int = 42
    z: str = "Apple"


@prefab(compile_prefab=True, compile_fallback=True)
class MixedHints:
    # Remove y and z, leave x in annotations
    x: int
    y: int = attribute(default=42)
    z = attribute(default="Apple")


@prefab(compile_prefab=True, compile_fallback=True)
class AllPlainAssignment:
    # remove all 3 values
    x = attribute()
    y = attribute(default=42)
    z = attribute(default="Apple")
