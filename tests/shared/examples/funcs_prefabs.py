# COMPILE_PREFABS
from prefab_classes import prefab, attribute
from pathlib import Path, PurePosixPath


@prefab(compile_prefab=True, compile_fallback=True)
class Coordinate:
    x: float
    y: float


@prefab(compile_prefab=True, compile_fallback=True)
class Circle:
    radius = attribute(default=1)
    origin = attribute(default=Coordinate(0, 0))


@prefab(compile_prefab=True, compile_fallback=True)
class SystemPath:
    filename = attribute()
    path = attribute()

    def __prefab_post_init__(self, path):
        self.path = PurePosixPath(path)


@prefab(compile_prefab=True, compile_fallback=True)
class Onion:
    pth: PurePosixPath
    syspath: SystemPath


@prefab(compile_prefab=True, compile_fallback=True)
class PicklePrefab:
    x = attribute(default=800)
    y = attribute(default=Path("Settings.json"))
