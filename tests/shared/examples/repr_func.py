# COMPILE_PREFABS
from prefab_classes import prefab, attribute


@prefab(compile_prefab=True, compile_fallback=True)
class RegularRepr:
    x: str = "Hello"
    y: str = "World"


@prefab(compile_prefab=True, compile_fallback=True)
class NoReprAttributes:
    x: str = attribute(default="Hello", repr=False)
    y: str = attribute(default="World", repr=False)


@prefab(compile_prefab=True, compile_fallback=True)
class OneAttributeNoRepr:
    x: str = attribute(default="Hello", repr=False)
    y: str = "World"


@prefab(compile_prefab=True, compile_fallback=True)
class OneAttributeNoInit:
    x: str = "Hello"
    y: str = attribute(default="World", init=False)


@prefab(compile_prefab=True, compile_fallback=True)
class OneAttributeExcludeField:
    x: str = "Hello"
    y: str = attribute(default="World", exclude_field=True)

    def __prefab_post_init__(self, y):
        self.y = y


@prefab(compile_prefab=True, compile_fallback=True)
class RegularReprOneArg:
    x: str = "Hello"
    y: str = attribute(default="World", init=False, repr=False)
