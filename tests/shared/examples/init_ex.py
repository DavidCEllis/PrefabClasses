# COMPILE_PREFABS
from prefab_classes import prefab, attribute
from pathlib import Path


@prefab(compile_prefab=True, compile_fallback=True)
class Coordinate:
    x: float
    y: float


@prefab(compile_prefab=True, compile_fallback=True)
class KWCoordinate:
    x = attribute(kw_only=True)
    y = attribute(kw_only=True)


@prefab(compile_prefab=True, compile_fallback=True)
class CoordinateFixedY:
    x = attribute()
    y = attribute(default=2, init=False)


@prefab(compile_prefab=True, compile_fallback=True)
class CoordinateDefaults:
    x = attribute(default=0)
    y = attribute(default=0)


@prefab(compile_prefab=True, compile_fallback=True)
class MutableDefault:
    x = attribute(default=list())


@prefab(compile_prefab=True, compile_fallback=True)
class FactoryDefault:
    x = attribute(default_factory=list)


@prefab(compile_prefab=True, compile_fallback=True)
class Settings:
    """
    Global persistent settings handler
    """

    output_file = attribute(default=Path("Settings.json"))


@prefab(compile_prefab=True, compile_fallback=True)
class PreInitExample:
    init_value: bool = True

    def __prefab_pre_init__(self):
        self.pre_init_ran = True


@prefab(compile_prefab=True, compile_fallback=True)
class PostInitExample:
    init_value: bool = True

    def __prefab_post_init__(self):
        self.post_init_ran = True


@prefab(compile_prefab=True, compile_fallback=True)
class EmptyContainers:
    x: list = attribute(default_factory=list)
    y: set = attribute(default_factory=set)
    z: dict = attribute(default_factory=dict)
