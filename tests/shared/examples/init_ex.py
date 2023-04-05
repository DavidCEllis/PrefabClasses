# COMPILE_PREFABS
from prefab_classes import prefab, attribute
from pathlib import Path
from typing import Union


@prefab(compile_prefab=True, compile_fallback=True)
class Coordinate:
    x: float
    y: float


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
class PrePostInitArguments:
    x: int = 1
    y: int = 2

    def __prefab_pre_init__(self, x, y):
        if x > y:
            raise ValueError("X must be less than Y")

    def __prefab_post_init__(self, x, y):
        self.x = 2 * x
        self.y = 3 * y


@prefab(compile_prefab=True, compile_fallback=True)
class ExcludeField:
    x = attribute(default="excluded_field", exclude_field=True)

    def __prefab_post_init__(self, x):
        self.x = x.upper()


@prefab(compile_prefab=True, compile_fallback=True)
class PostInitPartial:
    x: int
    y: int
    z: list[int] = attribute(default_factory=list)

    def __prefab_post_init__(self, z):
        z.append(1)
        self.z = z


@prefab(compile_prefab=True, compile_fallback=True)
class PostInitAnnotations:
    x: int
    y: Path

    def __prefab_post_init__(self, y: Union[str, Path]):
        self.y = Path(y)


@prefab(compile_prefab=True, compile_fallback=True)
class EmptyContainers:
    x: list = attribute(default_factory=list)
    y: set = attribute(default_factory=set)
    z: dict = attribute(default_factory=dict)


@prefab(compile_prefab=True, compile_fallback=True)
class TypeSignatureInit:
    x: int
    y: str = "Test"


@prefab(compile_prefab=True, compile_fallback=True)
class PartialTypeSignatureInit:
    x = attribute()
    y: str = attribute(default="Test")
