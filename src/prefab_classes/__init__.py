from ducktools.lazyimporter import (
    LazyImporter,
    MultiFromImport,
    FromImport,
    get_module_funcs,
)

# noinspection PyUnresolvedReferences
__all__ = [
    "prefab",
    "attribute",
    "build_prefab",
    "KW_ONLY",
]

__version__ = "v0.10.0"
PREFAB_MAGIC_BYTES = b"PREFAB_CLASSES_v0.10.0"

_imports = [
    MultiFromImport(".dynamic", ["prefab", "attribute", "build_prefab"]),
    FromImport(".sentinels", "KW_ONLY")
]

_laz = LazyImporter(_imports, globs=globals())

__getattr__, __dir__ = get_module_funcs(_laz, __name__)
