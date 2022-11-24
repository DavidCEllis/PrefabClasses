# COMPILE_PREFABS
from prefab_classes import prefab, attribute
from pathlib import Path


@prefab(compile_prefab=True, compile_fallback=True)
class SystemPath:
    path = attribute(converter=Path)


@prefab(compile_prefab=True, compile_fallback=True)
class SystemPathDefault:
    path = attribute(default="fake/directory", converter=Path)
