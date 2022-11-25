# COMPILE_PREFABS
from prefab_classes import prefab, attribute


@prefab(compile_prefab=True, compile_fallback=True)
class Coordinates:
    x: float
    y: float


@prefab(compile_prefab=True, compile_fallback=True)
class Settings:
    path: str = "path/to/file"
    file_list: list = attribute(default_factory=list)


@prefab(compile_prefab=True, compile_fallback=True)
class SettingsNoHint:
    path: str = "path/to/file"
    file_list = attribute(default_factory=list)
