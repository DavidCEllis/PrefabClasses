# COMPILE_PREFABS
import typing
from typing import ClassVar
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


@prefab(compile_prefab=True, compile_fallback=True, iter=True, match_args=True)
class KeepDefinedMethods:
    x: int = -1
    y: int = -1

    __match_args__ = ('x', )

    def __init__(self, x=0, y=0):
        self.x = 0
        self.y = 0

    def __repr__(self):
        return "ORIGINAL REPR"

    def __eq__(self, other):
        return False

    def __iter__(self):
        yield from ['ORIGINAL ITER']


@prefab(compile_prefab=True, compile_fallback=True)
class IgnoreClassVars:
    # Ignore v, w, x, y and z - Include actual.
    v: ClassVar = 12
    w: "ClassVar" = 24
    x: typing.ClassVar[int] = 42
    y: ClassVar[str] = "Apple"
    z: "ClassVar[float]" = 3.14
    actual: str = "Test"


@prefab(compile_prefab=True, compile_fallback=True)
class PositionalNotAfterKW:
    # y defines a default, but it is not in the signature so should be ignored
    # for the purpose of argument order.
    x: int
    y: int = attribute(default=0, init=False)
    z: int
